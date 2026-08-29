from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A Vercel exige que arquivos salvos temporariamente usem a pasta /tmp
DOWNLOAD_DIR = "/tmp/downloads_temp"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Configurações otimizadas do yt-dlp para emular um navegador Chrome real dentro da nuvem
YDL_OPTIONS = {
    'quiet': True,
    'no_warnings': True,
    'impersonate': 'chrome',  # Burlar detecção de robôs
}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    try:
        html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "index.html"))
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h3>Erro: Arquivo index.html nao encontrado na raiz!</h3>", status_code=500)

@app.post("/analisar")
async def analisar_video(url: str = Form(...)):
    try:
        # O próprio motor yt-dlp instalado na Vercel extrai o link direto
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or (info.get('formats')[-1]['url'] if info.get('formats') else None)
            if video_url:
                return {"media_url": video_url}
    except Exception as e:
        # Se falhar, tenta uma rota alternativa via API de backup para o TikTok
        if "tiktok.com" in url:
            try:
                res = requests.get(f"https://tikwm.com{url}", timeout=10).json()
                if res.get("code") == 0:
                    return {"media_url": res["data"]["play"]}
            except:
                pass
                
    raise HTTPException(status_code=400, detail="Não foi possível extrair a prévia. Verifique se o post é público.")

@app.post("/download-real")
async def baixar_midia_local(url: str = Form(...), tipo: str = Form(...)):
    extensao = "mp3" if tipo == "mp3" else "mp4"
    nome_do_seu_site = "meubaixador_com"
    caminho_final = os.path.join(DOWNLOAD_DIR, f"final.{extensao}")
    
    if os.path.exists(caminho_final):
        try: os.remove(caminho_final)
        except: pass

    # Injeta regras de download nativo do yt-dlp para a pasta /tmp da Vercel
    ydl_opts_dl = YDL_OPTIONS.copy()
    ydl_opts_dl['outtmpl'] = os.path.join(DOWNLOAD_DIR, 'midia_temp.%(ext)s')
    ydl_opts_dl['format'] = 'bestaudio/best' if tipo == "mp3" else 'best[ext=mp4]/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts_dl) as ydl:
            info = ydl.extract_info(url, download=True)
            filename_baixado = ydl.prepare_filename(info)
            
            # Ajuste de detecção para extensões residuais (.m4a, .webm, etc)
            if not os.path.exists(filename_baixado):
                base, _ = os.path.splitext(filename_baixado)
                for ext in ['.m4a', '.aac', '.mp3', '.mp4', '.webm']:
                    if os.path.exists(base + ext):
                        filename_baixado = base + ext
                        break

            if os.path.exists(filename_baixado):
                os.rename(filename_baixado, caminho_final)
                
                # Entrega o arquivo pronto gerado direto no servidor da Vercel
                return FileResponse(
                    path=caminho_final, 
                    filename=f"{nome_do_seu_site}.{extensao}", 
                    media_type="application/octet-stream"
                )
    except:
        # Backup alternativo via API se o yt-dlp direto falhar no TikTok
        if "tiktok.com" in url:
            try:
                res = requests.get(f"https://tikwm.com{url}", timeout=10).json()
                if res.get("code") == 0:
                    link_direto = res["data"]["music"] if tipo == "mp3" else res["data"]["play"]
                    res_stream = requests.get(link_direto, stream=True, timeout=30)
                    with open(caminho_final, "wb") as f:
                        for chunk in res_stream.iter_content(chunk_size=1024*1024):
                            if chunk: f.write(chunk)
                    return FileResponse(path=caminho_final, filename=f"{nome_do_seu_site}.{extensao}", media_type="application/octet-stream")
            except:
                pass

    raise HTTPException(status_code=400, detail="Mídia protegida ou limite de tráfego excedido na rede social.")
