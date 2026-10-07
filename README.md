# Conversor de Vídeos para TV

Aplicação local em Flask + FFmpeg que converte vídeos para um formato compatível
com a maioria das TVs, telões e pendrives (H.264 Main Profile Level 3.1 + AAC).

Todo o processamento acontece **na sua máquina**. Nenhum vídeo é enviado para a internet.

---

## Como usar

### Passo 1 — Baixar o projeto

Você pode baixar de duas formas. **Escolha uma:**

**Opção A — Clonar com Git:**
```bash
git clone https://github.com/MottaGustavo/ConversorTV.git
```

**Opção B — Baixar o ZIP:**
- No topo desta página, clique no botão verde **Code** → **Download ZIP**
- Extraia o ZIP em qualquer pasta (ex: `C:\ConversorTV`)

### Passo 2 — Rodar o `start.bat`

Dê **duplo-clique** no arquivo `start.bat` dentro da pasta do projeto.

**Na primeira execução**, ele faz tudo automaticamente:

| O que ele faz | Onde fica |
|---|---|
| Baixa o FFmpeg (~80 MB) | pasta `ffmpeg/` |
| Cria o ambiente virtual Python | pasta `.venv/` |
| Instala as dependências do `requirements.txt` | dentro do `.venv/` |
| Abre o navegador em `http://127.0.0.1:5000` | — |

> **Você não precisa criar nenhuma pasta manualmente.**
> O `start.bat` e o `app.py` criam tudo que for necessário.

A primeira execução demora alguns minutos (download do FFmpeg).
**Depois disso, é só abrir o `start.bat` e o programa sobe em segundos.**

### Passo 3 — Usar a interface

- Arraste um vídeo para a área pontilhada (ou clique em **Selecionar vídeo**)
- Clique em **Converter para TV**
- Quando terminar, o arquivo convertido estará na pasta `convertidos/`

O servidor se encerra sozinho quando você fecha a aba do navegador.

---

## Requisitos

- **Windows 10 ou 11**
- **Python 3.9 ou superior** — [baixar aqui](https://www.python.org/downloads/)
  - ⚠️ Durante a instalação, marque a opção **"Add Python to PATH"**
- **Internet** apenas na primeira execução (para baixar o FFmpeg)

---

## Limites e considerações

- **Tamanho máximo por vídeo:** 10 GB
- **Espaço em disco necessário:** cerca do dobro do tamanho do vídeo original
  (ele é salvo em `uploads/`, convertido, e o resultado vai pra `convertidos/`)
- **Tempo de conversão:** aproximadamente o tempo real do vídeo.
  Um vídeo de 2h pode levar de 1h a 2h pra converter, dependendo do PC
- **Processamento sequencial:** uma conversão por vez. Se você iniciar outra
  antes da primeira terminar, ambas rodam em paralelo e podem ficar lentas

---

## Formatos suportados

**Entrada:** MP4, MOV, M4V, AVI, MKV, WMV
**Saída:** MP4 (H.264 + AAC)

---

## O que é criado automaticamente

Essas pastas **não vêm** no download do GitHub — são criadas na primeira execução:

- `ffmpeg/` — binários do FFmpeg (baixados pelo `start.bat`)
- `.venv/` — ambiente virtual do Python (criado pelo `start.bat`)
- `uploads/` — arquivos temporários durante a conversão (criado pelo `app.py`)
- `convertidos/` — arquivos finais convertidos (criado pelo `app.py`)

Por isso elas ficam no `.gitignore` e não são enviadas pro repositório.

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
├── ffmpeg/                   # Criado na 1ª execução (não versionado)
├── uploads/                  # Criado automaticamente (não versionado)
└── convertidos/              # Criado automaticamente (não versionado)
```

---

## Configuração do FFmpeg usada

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