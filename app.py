from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
import requests
import os
import re

app = FastAPI()

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
        return HTMLResponse("<h3>Erro: Arquivo index.html nao encontrado!</h3>", status_code=500)

@app.post("/analisar")
async def analisar_video(url: str = Form(...)):
    # Converte o link se for do TikTok
    if "tiktok.com" in url:
        try:
            api_res = requests.get(f"https://tikwm.com{url}", timeout=10).json()
            if api_res.get("code") == 0:
                return {
                    "video_url": api_res["data"]["play"],
                    "audio_url": api_res["data"]["music"]
                }
        except:
            pass
    
    # Se for Instagram ou Facebook, extrai via metadados estruturais
    try:
        html = requests.get(url, headers=HEADERS, timeout=10).text
        match = re.search(r'"video_url":"(.*?)"', html) or re.search(r'property="og:video" content="(.*?)"', html)
        if match:
            clean_url = match.group(1).replace(r'\u002F', '/').replace("&amp;", "&")
            return {
                "video_url": clean_url,
                "audio_url": clean_url  # Fallback caso não ache a faixa separada
            }
    except:
        pass

    raise HTTPException(status_code=400, detail="Não foi possível extrair os links deste post público.")
