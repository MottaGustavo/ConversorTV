# Conversor de Vídeos para TV

> Aplicativo web local que converte vídeos para um formato otimizado e compatível com a maioria das TVs.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-H.264%20%2B%20AAC-green?logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Sobre o projeto

Ferramenta simples e objetiva para quem precisa preparar vídeos para reprodução em TVs antigas ou com suporte limitado a codecs.

O processamento é **100% local** — nenhum arquivo é enviado para a internet.

### Formato de saída

| Parâmetro        | Valor              |
|------------------|--------------------|
| Vídeo            | H.264 (libx264)    |
| Profile / Level  | Main / 3.1         |
| Pixel format     | yuv420p            |
| Áudio            | AAC 128 kbps       |
| Sample rate      | 44.1 kHz           |
| Container        | MP4 (+faststart)   |

Essa combinação é amplamente aceita por Smart TVs, TVs de tubo com conversor e players embarcados.

---

## Demonstração

1. Arraste ou selecione um vídeo (MP4, MOV, MKV, AVI, WMV…)
2. Clique em **Converter para TV**
3. Acompanhe o progresso em tempo real
4. O arquivo convertido é salvo automaticamente na pasta `convertidos/`

---

## Destaques técnicos

### Resolução de deadlock de pipes

A versão inicial sofria de um **deadlock clássico** ao usar `subprocess.Popen`:

- O progresso do FFmpeg era lido apenas de `stdout` (`-progress pipe:1`)
- O `stderr` só era consumido **depois** que o loop de `stdout` terminava
- Quando o buffer do `stderr` enchia, o processo `ffmpeg` bloqueava e ficava com 0% de CPU

**Solução aplicada:**

- Thread dedicada para drenar o `stderr` em paralelo
- Leitura segura do progresso via `stdout`
- `threading.Lock` no dicionário de jobs compartilhado entre threads
- Limpeza de arquivos parciais em caso de erro
- `CREATE_NO_WINDOW` no Windows (evita janela de console do ffmpeg)
- Encerramento correto do processo em caso de exceção

### Outros detalhes de implementação

- Progresso em tempo real via polling (`/status/<job_id>`)
- Conversões rodam em threads daemon (não bloqueiam a interface)
- Nomes de arquivo de saída únicos (evita sobrescrita)
- Interface responsiva com drag-and-drop

---

## Tecnologias

- **Backend:** Python 3 + Flask
- **Processamento de vídeo:** FFmpeg
- **Frontend:** HTML, CSS e JavaScript vanilla
- **Concorrência:** `threading` + `subprocess`

---

## Como rodar

### Pré-requisitos

- Python 3.10 ou superior
- FFmpeg (`ffmpeg.exe` no Windows)

### Windows (mais fácil)

1. Clone ou baixe o repositório
2. Coloque o `ffmpeg.exe` dentro da pasta `ffmpeg/`
3. Execute o arquivo `start.bat`
4. O navegador abrirá automaticamente em [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Manual (qualquer SO)

```bash
# 1. Clone
git clone https://github.com/MottaGustavo/ConversorTV.git
cd ConversorTV

# 2. Ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# 3. Dependências
pip install -r requirements.txt

# 4. FFmpeg
# Coloque o binário em ./ffmpeg/  ou deixe no PATH do sistema

# 5. Executar
python app.py
```

Acesse: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Estrutura do projeto

```
ConversorTV/
├── app.py              # Backend Flask + lógica de conversão
├── requirements.txt   # Dependências Python
├── start.bat          # Atalho de inicialização (Windows)
├── static/            # CSS e JavaScript
├── templates/         # HTML
├── ffmpeg/            # Binário do FFmpeg (não versionado)
├── uploads/           # Arquivos temporários (criado em runtime)
└── convertidos/       # Vídeos convertidos (criado em runtime)
```

---

## Aprendizados

Este projeto foi útil para praticar:

- Gerenciamento correto de `subprocess` e pipes
- Concorrência com threads em aplicações web
- Feedback de progresso em tempo real
- Interface simples e funcional sem frameworks front-end pesados
- Atenção a detalhes de UX (drag-and-drop, estados de loading/erro/sucesso)

---

## Licença

Este projeto está sob a licença MIT. Sinta-se à vontade para usar, modificar e distribuir.

---

Desenvolvido por [Gustavo Motta](https://github.com/MottaGustavo)
