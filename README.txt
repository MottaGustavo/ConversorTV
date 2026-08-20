CONVERSOR DE VIDEOS PARA TV
============================

O programa usa Flask + FFmpeg e funciona localmente no computador.

1. INSTALAR O PYTHON
--------------------
Instale Python 3 no Windows.

Durante a instalacao, marque:
"Add Python to PATH"

2. COLOCAR O FFMPEG
--------------------
Copie o arquivo ffmpeg.exe para:

    ffmpeg\ffmpeg.exe

O executavel pode ser obtido no site oficial do FFmpeg:
https://ffmpeg.org/download.html

Se o FFmpeg ja estiver configurado no PATH do Windows, ele tambem pode ser encontrado automaticamente.

3. EXECUTAR
-----------
Dê dois cliques em:

    start.bat

O navegador abrira em:

    http://127.0.0.1:5000

4. COMO FUNCIONA
----------------
Selecione ou arraste um video.

Clique em:
"Converter para TV"

O arquivo convertido sera salvo em:

    convertidos\

Exemplo:

    PrimaveraVeraoTV.mp4
    ->
    PrimaveraVeraoTV_TV.mp4

5. CONFIGURACAO DO FFMPEG
-------------------------
O programa usa exatamente:

ffmpeg -i "entrada.mp4" -c:v libx264 -profile:v main -level 3.1 -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -movflags +faststart "saida_TV.mp4"

O processamento acontece localmente.
Os videos nao sao enviados para a internet.
