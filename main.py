from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "/tmp/downloads_temp"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    try:
        html_path = os.path.join(os.path.dirname(__file__), "../index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h3>Erro: Arquivo index.html nao encontrado!</h3>", status_code=500)

@app.post("/analisar")
async def analisar_video(url: str = Form(...)):
    try:
        api_url = f"https://tikwm.com{url}" if "tiktok.com" in url else f"https://insta-downloader.net{url}"
        res = requests.get(api_url, headers=HEADERS, timeout=10).json()
        
        if "tiktok.com" in url and res.get("code") == 0:
            return {"media_url": res["data"]["play"]}
        elif "video_url" in res:
            return {"media_url": res["video_url"]}
            
        return {"media_url": url}
    except:
        return {"media_url": url}

@app.post("/download-real")
async def baixar_midia_local(url: str = Form(...), tipo: str = Form(...)):
    extensao = "mp3" if tipo == "mp3" else "mp4"
    caminho_final = os.path.join(DOWNLOAD_DIR, f"final.{extensao}")
    
    if os.path.exists(caminho_final):
        try: os.remove(caminho_final)
        except: pass

    link_direto = None
    try:
        if "tiktok.com" in url:
            res = requests.get(f"https://tikwm.com{url}", timeout=10).json()
            if res.get("code") == 0:
                link_direto = res["data"]["music"] if tipo == "mp3" else res["data"]["play"]
        else:
            res = requests.get(f"https://insta-downloader.net{url}", timeout=10).json()
            if "video_url" in res:
                link_direto = res["video_url"]

        if link_direto:
            res_stream = requests.get(link_direto, headers=HEADERS, stream=True, timeout=45)
            with open(caminho_final, "wb") as f:
                for chunk in res_stream.iter_content(chunk_size=1024*1024):
                    if chunk: f.write(chunk)
            
            return FileResponse(path=caminho_final, filename=f"meubaixador.{extensao}", media_type="application/octet-stream")
    except:
        pass

    raise HTTPException(status_code=400, detail="Mídia temporariamente protegida ou indisponível.")
