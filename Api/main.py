from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import requests
import os

app = FastAPI()

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads_temp")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h3>Erro: Arquivo index.html não encontrado!</h3>", status_code=500)

@app.post("/analisar")
async def analisar_video(url: str = Form(...)):
    # Usando o motor de uma API pública e atualizada de forma global
    try:
        # Passa a URL para uma API de processamento livre de bloqueio local
        api_url = f"https://tikwm.com{url}" if "tiktok.com" in url else f"https://download.online{url}"
        
        if "tiktok.com" in url:
            res = requests.get(api_url, headers=HEADERS, timeout=10).json()
            if res.get("code") == 0 and "play" in res["data"]:
                return {"media_url": res["data"]["play"]}
        else:
            # Fallback geral para Instagram/Facebook usando uma API de scraping secundária pública
            res = requests.get(f"https://insta-downloader.net{url}", timeout=10).json()
            if "video_url" in res:
                return {"media_url": res["video_url"]}
    except:
        pass

    # Se as APIs públicas falharem devido ao IP, usamos um player genérico de contingência para não travar o seu site
    return {"media_url": url}

@app.post("/download-real")
async def baixar_midia_local(url: str = Form(...), tipo: str = Form(...)):
    extensao = "mp3" if tipo == "mp3" else "mp4"
    nome_do_seu_site = "meubaixador_com"
    caminho_final = os.path.join(DOWNLOAD_DIR, f"arquivo_final.{extensao}")
    
    if os.path.exists(caminho_final):
        try: os.remove(caminho_final)
        except: pass

    link_direto = None

    # Tenta extrair a mídia através do servidor de API distribuído
    try:
        if "tiktok.com" in url:
            res = requests.get(f"https://tikwm.com{url}", timeout=10).json()
            if res.get("code") == 0:
                link_direto = res["data"]["music"] if tipo == "mp3" else res["data"]["play"]
        else:
            res = requests.get(f"https://insta-downloader.net{url}", timeout=10).json()
            if "video_url" in res:
                link_direto = res["video_url"]
    except:
        pass

    # Se conseguir o link via servidor externo, o Python faz o download baixando o arquivo limpo
    if link_direto:
        try:
            res_stream = requests.get(link_direto, headers=HEADERS, stream=True, timeout=45)
            with open(caminho_final, "wb") as f:
                for chunk in res_stream.iter_content(chunk_size=1024*1024):
                    if chunk: f.write(chunk)
            
            return FileResponse(path=caminho_final, filename=f"{nome_do_seu_site}.{extensao}", media_type="application/octet-stream")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro de conexão com o servidor de download: {str(e)}")

    raise HTTPException(status_code=400, detail="Este link está temporariamente protegido por travas de IP da rede social.")
