# Conversor de Vídeos para TV

Aplicação local em Flask + FFmpeg que converte vídeos para um formato compatível
com a maioria das TVs, telões e pendrives (H.264 Main Profile Level 3.1 + AAC).

Todo o processamento acontece **na sua máquina**. Nenhum vídeo é enviado para a internet.

---

## Como usar (Windows)

### 1. Clone o repositório

```bash
git clone https://github.com/MottaGustavo/ConversorTV.git
cd ConversorTV
```

### 2. Dê duplo-clique em `start.bat`

Na **primeira execução**, o script faz tudo sozinho:

- Baixa o FFmpeg (~80 MB) para a pasta `ffmpeg/`
- Cria o ambiente virtual Python (`.venv/`)
- Instala as dependências do `requirements.txt`
- Abre o navegador em `http://127.0.0.1:5000`

Isso acontece **só uma vez**. Depois disso, é só abrir o `start.bat`
e o programa sobe direto.

### 3. Use a interface

- Arraste um vídeo (ou clique em **Selecionar vídeo**)
- Clique em **Converter para TV**
- Quando terminar, o arquivo estará em `convertidos/`

O servidor se encerra sozinho quando você fecha a aba do navegador.

---

## Requisitos

- **Windows 10 ou 11**
- **Python 3.9+** — [baixar aqui](https://www.python.org/downloads/)
  - Marque **"Add Python to PATH"** na instalação
- **Internet** apenas na primeira execução (para baixar o FFmpeg)

---

## Formatos suportados

**Entrada:** MP4, MOV, M4V, AVI, MKV, WMV
**Saída:** MP4 (H.264 + AAC)

---

## Estrutura do projeto

```
ConversorTV/
├── app.py                    # Servidor Flask
├── templates/
│   └── index.html            # Interface (abas Converter / Como usar)
├── static/
│   ├── logo.png              # Logo + favicon
│   ├── script.js             # Lógica do front-end
│   └── style.css             # Estilos
├── start.bat                 # Inicializador (Windows)
├── start_oculto.vbs          # Roda sem janela do console
├── requirements.txt          # Dependências Python
├── ffmpeg/                   # Baixado na 1ª execução (não versionado)
├── uploads/                  # Temporário (não versionado)
└── convertidos/              # Arquivos finais (não versionado)
```

---

## Configuração do FFmpeg

```
ffmpeg -y -i entrada \
       -c:v libx264 -profile:v main -level 3.1 -pix_fmt yuv420p \
       -c:a aac -b:a 128k -ar 44100 \
       -movflags +faststart \
       saida_TV.mp4
```

Essa configuração é compatível com praticamente toda TV, telão e pendrive.

---

## Sobre o desenvolvimento

Alguns detalhes técnicos que valem registrar:

- **stderr do FFmpeg é drenado em thread paralela** enquanto o progresso é lido de stdout — sem isso, o buffer enche e o processo trava em 0% de CPU (deadlock clássico de pipes).
- **Lock no dicionário de jobs** para evitar race conditions entre threads do Flask e threads de conversão.
- **`CREATE_NO_WINDOW` no Windows** para não abrir console do `ffmpeg.exe` durante a conversão.
- **Auto-shutdown** via heartbeat: o navegador pinga a cada 3s e, se parar, o servidor se encerra sozinho.
- **Path traversal protection** no endpoint de download.

---

## Licença

Uso livre.