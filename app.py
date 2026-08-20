from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path
import subprocess
import threading
import uuid
import re
import os
import sys

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "convertidos"
FFMPEG_DIR = BASE_DIR / "ffmpeg"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024 * 1024  # 10 GB

# Shared jobs state protected by a lock (Flask threads + worker threads)
jobs = {}
jobs_lock = threading.Lock()


def find_binary(name):
    exe = name + ".exe" if os.name == "nt" else name

    local = FFMPEG_DIR / exe
    if local.exists():
        return str(local)

    return exe  # Uses PATH


FFMPEG = find_binary("ffmpeg")


def get_duration(input_file):
    """Reads duration from FFmpeg output without requiring ffprobe."""
    cmd = [FFMPEG, "-hide_banner", "-i", str(input_file)]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    match = re.search(
        r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)",
        result.stderr,
    )

    if not match:
        return None

    h, m, s = match.groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def update_job(job_id, **kwargs):
    """Thread-safe update of a job dict."""
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id].update(kwargs)


def convert_job(job_id, input_file, output_file):
    process = None
    try:
        duration = get_duration(input_file)
        update_job(job_id, status="converting", duration=duration)

        # EXACT configuration confirmed by the user as working on the TV.
        command = [
            FFMPEG,
            "-y",
            "-i", str(input_file),
            "-c:v", "libx264",
            "-profile:v", "main",
            "-level", "3.1",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-movflags", "+faststart",
            "-progress", "pipe:1",
            "-nostats",
            str(output_file),
        ]

        # On Windows, hide the console window that ffmpeg.exe would open
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NO_WINDOW

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=creationflags,
        )

        # ---------------------------------------------------------------
        # CRITICAL FIX: drain stderr in a parallel thread.
        # If stderr is not consumed while we read stdout, the OS pipe
        # buffer fills up and ffmpeg blocks forever (deadlock).
        # ---------------------------------------------------------------
        stderr_chunks = []

        def drain_stderr():
            try:
                for line in process.stderr:
                    stderr_chunks.append(line)
            except Exception:
                pass

        stderr_thread = threading.Thread(target=drain_stderr, daemon=True)
        stderr_thread.start()

        # FFmpeg progress is sent to stdout as key=value lines.
        for line in process.stdout:
            line = line.strip()

            if line.startswith("out_time_ms="):
                try:
                    out_time_us = int(line.split("=", 1)[1])
                    current_seconds = out_time_us / 1_000_000

                    if duration and duration > 0:
                        percent = min(99, max(0, (current_seconds / duration) * 100))
                        update_job(job_id, progress=round(percent, 1))
                except ValueError:
                    pass

            elif line == "progress=end":
                update_job(job_id, progress=100)

        # Wait for process and for the stderr collector to finish
        return_code = process.wait()
        stderr_thread.join(timeout=10)
        stderr = "".join(stderr_chunks)

        if return_code != 0:
            # Remove partial / failed output so the folder stays clean
            try:
                output_file.unlink(missing_ok=True)
            except Exception:
                pass

            update_job(
                job_id,
                status="error",
                error=(
                    "O FFmpeg encontrou um erro durante a conversão.\n\n"
                    + (stderr[-4000:] if stderr else "(sem saída de erro)")
                ),
            )
            return

        update_job(
            job_id,
            status="done",
            progress=100,
            filename=output_file.name,
        )

    except Exception as exc:
        if process is not None and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass

        # Clean partial output on unexpected errors
        try:
            output_file.unlink(missing_ok=True)
        except Exception:
            pass

        update_job(job_id, status="error", error=str(exc))

    finally:
        # Always remove the uploaded original after the job finishes
        try:
            input_file.unlink(missing_ok=True)
        except Exception:
            pass


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/convert")
def convert():
    file = request.files.get("video")

    if not file or not file.filename:
        return jsonify({"error": "Nenhum vídeo foi selecionado."}), 400

    original_name = Path(file.filename).name
    extension = Path(original_name).suffix.lower()

    if extension not in {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".wmv"}:
        return jsonify({
            "error": "Formato não suportado. Selecione um vídeo MP4, MOV, M4V, AVI, MKV ou WMV."
        }), 400

    job_id = uuid.uuid4().hex
    safe_stem = Path(original_name).stem
    input_file = UPLOAD_DIR / f"{job_id}_{original_name}"
    output_file = OUTPUT_DIR / f"{safe_stem}_TV.mp4"

    # Avoid overwriting an existing result.
    if output_file.exists():
        counter = 2
        while True:
            candidate = OUTPUT_DIR / f"{safe_stem}_TV_{counter}.mp4"
            if not candidate.exists():
                output_file = candidate
                break
            counter += 1

    file.save(input_file)

    with jobs_lock:
        jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "filename": output_file.name,
        }

    thread = threading.Thread(
        target=convert_job,
        args=(job_id, input_file, output_file),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id})


@app.get("/status/<job_id>")
def status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            return jsonify({"error": "Conversão não encontrada."}), 404
        # Return a shallow copy so the caller can't mutate the live dict
        return jsonify(dict(job))


@app.get("/download/<filename>")
def download(filename):
    # Basic path-traversal protection
    safe_name = Path(filename).name
    return send_from_directory(
        OUTPUT_DIR,
        safe_name,
        as_attachment=True,
    )


@app.post("/open-folder")
def open_folder():
    try:
        if os.name == "nt":
            os.startfile(str(OUTPUT_DIR))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(OUTPUT_DIR)])
        else:
            subprocess.Popen(["xdg-open", str(OUTPUT_DIR)])

        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


if __name__ == "__main__":
    print()
    print("=" * 55)
    print(" CONVERSOR DE VÍDEOS PARA TV")
    print("=" * 55)
    print("Abra no navegador: http://127.0.0.1:5000")
    print("Pressione CTRL+C para encerrar.")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True,
    )
