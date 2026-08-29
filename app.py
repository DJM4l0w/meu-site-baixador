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

# Identidade visual humana para passar pelos filtros básicos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
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
        # Rota focada em links do TikTok
        if "tiktok.com" in url:
            api_res = requests.get(f"https://tikwm.com{url}", timeout=10).json()
            if api_res.get("code") == 0:
                return {"media_url": api_res["data"]["play"]}
        
        # Rota de raspagem nativa via tags meta para Instagram e Facebook
        html = requests.get(url, headers=HEADERS, timeout=10).text
        match = re.search(r'"video_url":"(.*?)"', html) or re.search(r'property="og:video" content="(.*?)"', html)
        
        if match:
            clean_url = match.group(1).replace(r'\u002F', '/').replace("&amp;", "&")
            return {"media_url": clean_url}
            
        # Player fallback
        return {"media_url": url}
    except:
        return {"media_url": url}

@app.post("/download-real")
async def baixar_midia_local(url: str = Form(...), tipo: str = Form(...)):
    extensao = "mp3" if tipo == "mp3" else "mp4"
    nome_do_seu_site = "meubaixador_com"
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
            html = requests.get(url, headers=HEADERS, timeout=10).text
            match = re.search(r'"video_url":"(.*?)"', html) or re.search(r'property="og:video" content="(.*?)"', html)
            if match:
                link_direto = match.group(1).replace(r'\u002F', '/').replace("&amp;", "&")

        if link_direto:
            # Baixa o fluxo do arquivo na pasta temporária /tmp da Vercel
            res_stream = requests.get(link_direto, headers=HEADERS, stream=True, timeout=45)
            with open(caminho_final, "wb") as f:
                for chunk in res_stream.iter_content(chunk_size=1024*1024):
                    if chunk: f.write(chunk)
            
            # Entrega para o usuário com o nome customizado
            return FileResponse(path=caminho_final, filename=f"{nome_do_seu_site}.{extensao}", media_type="application/octet-stream")
    except:
        pass

    raise HTTPException(status_code=400, detail="Mídia temporariamente protegida ou indisponível.")
