# Conversor de Vídeos para TV

Aplicação local em Flask + FFmpeg que converte vídeos para um formato compatível com a maioria das TVs (H.264 Main Profile Level 3.1 + AAC).

## Problema corrigido

A versão original sofria de **deadlock clássico de pipes** do `subprocess`:

- O progresso do FFmpeg era lido apenas de `stdout` (`-progress pipe:1`).
- `stderr` só era lido **depois** que o loop de `stdout` terminava.
- Quando o buffer do `stderr` enchia (logs do FFmpeg), o processo `ffmpeg.exe` bloqueava e ficava com 0% de CPU no Gerenciador de Tarefas, sem nunca terminar.

**Correção:** o `stderr` agora é drenado em uma thread paralela enquanto o progresso é lido de `stdout`. Também foram adicionados:

- Lock para o dicionário `jobs` compartilhado entre threads
- Limpeza de arquivos de saída parciais em caso de erro
- `CREATE_NO_WINDOW` no Windows para não abrir console do ffmpeg
- Proteção básica contra path traversal no download
- Encerramento do processo ffmpeg em caso de exceção

## Como usar

1. Instale Python 3 e marque "Add Python to PATH".
2. Coloque `ffmpeg.exe` na pasta `ffmpeg/` (ou deixe no PATH).
3. Execute `start.bat` (Windows) ou:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python app.py
```

4. Abra http://127.0.0.1:5000

Os vídeos convertidos ficam na pasta `convertidos/`.

## Configuração FFmpeg usada

```
ffmpeg -y -i entrada -c:v libx264 -profile:v main -level 3.1 -pix_fmt yuv420p \
       -c:a aac -b:a 128k -ar 44100 -movflags +faststart saida_TV.mp4
```

Processamento 100% local. Nenhum vídeo é enviado para a internet.
