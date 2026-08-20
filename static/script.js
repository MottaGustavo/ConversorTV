const videoInput = document.getElementById("videoInput");
const dropZone = document.getElementById("dropZone");
const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const removeFile = document.getElementById("removeFile");
const convertButton = document.getElementById("convertButton");

const progressArea = document.getElementById("progressArea");
const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");
const progressPercent = document.getElementById("progressPercent");

const successArea = document.getElementById("successArea");
const resultName = document.getElementById("resultName");

const errorArea = document.getElementById("errorArea");
const errorText = document.getElementById("errorText");

const openFolderButton = document.getElementById("openFolderButton");
const newVideoButton = document.getElementById("newVideoButton");

let selectedFile = null;
let currentJob = null;
let polling = null;

function formatBytes(bytes) {
    if (!bytes) return "0 B";

    const units = ["B", "KB", "MB", "GB", "TB"];
    const index = Math.floor(Math.log(bytes) / Math.log(1024));

    return `${(bytes / Math.pow(1024, index)).toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function chooseFile(file) {
    if (!file) return;

    if (!file.type.startsWith("video/") && !/\.(mp4|mov|m4v|avi|mkv|wmv)$/i.test(file.name)) {
        showError("Selecione um arquivo de vídeo compatível.");
        return;
    }

    selectedFile = file;

    fileName.textContent = file.name;
    fileSize.textContent = formatBytes(file.size);

    fileInfo.classList.remove("hidden");
    convertButton.disabled = false;

    successArea.classList.add("hidden");
    errorArea.classList.add("hidden");
    progressArea.classList.add("hidden");
    newVideoButton.classList.add("hidden");
}

videoInput.addEventListener("change", () => {
    chooseFile(videoInput.files[0]);
});

["dragenter", "dragover"].forEach(eventName => {
    dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.add("dragover");
    });
});

["dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.remove("dragover");
    });
});

dropZone.addEventListener("drop", (event) => {
    const file = event.dataTransfer.files[0];
    chooseFile(file);
});

removeFile.addEventListener("click", clearSelection);

function clearSelection() {
    selectedFile = null;
    videoInput.value = "";
    fileInfo.classList.add("hidden");
    convertButton.disabled = true;
    progressArea.classList.add("hidden");
    successArea.classList.add("hidden");
    errorArea.classList.add("hidden");
}

convertButton.addEventListener("click", async () => {
    if (!selectedFile) return;

    convertButton.disabled = true;
    progressArea.classList.remove("hidden");
    successArea.classList.add("hidden");
    errorArea.classList.add("hidden");

    setProgress(0, "Enviando vídeo...");

    const formData = new FormData();
    formData.append("video", selectedFile);

    try {
        const response = await fetch("/convert", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Não foi possível iniciar a conversão.");
        }

        currentJob = data.job_id;
        setProgress(0, "Convertendo vídeo...");

        pollStatus();
    } catch (error) {
        showError(error.message);
        convertButton.disabled = false;
    }
});

async function pollStatus() {
    if (!currentJob) return;

    try {
        const response = await fetch(`/status/${currentJob}`);
        const data = await response.json();

        if (data.status === "queued") {
            setProgress(0, "Preparando conversão...");
        } else if (data.status === "converting") {
            setProgress(data.progress || 0, "Convertendo vídeo...");
        } else if (data.status === "done") {
            setProgress(100, "Conversão concluída!");
            showSuccess(data.filename);
            return;
        } else if (data.status === "error") {
            showError(data.error || "Erro desconhecido no FFmpeg.");
            return;
        }

        polling = setTimeout(pollStatus, 500);
    } catch (error) {
        showError("Não foi possível consultar o andamento da conversão.");
    }
}

function setProgress(value, text) {
    const rounded = Math.round(value);
    progressBar.style.width = `${rounded}%`;
    progressPercent.textContent = `${rounded}%`;
    progressText.textContent = text;
}

function showSuccess(filename) {
    successArea.classList.remove("hidden");
    resultName.textContent = `${filename} foi salvo na pasta "convertidos".`;
    newVideoButton.classList.remove("hidden");
    convertButton.disabled = true;
}

function showError(message) {
    progressArea.classList.add("hidden");
    errorArea.classList.remove("hidden");
    errorText.textContent = message;
}

openFolderButton.addEventListener("click", async () => {
    await fetch("/open-folder", { method: "POST" });
});

newVideoButton.addEventListener("click", () => {
    clearSelection();
    newVideoButton.classList.add("hidden");
});
