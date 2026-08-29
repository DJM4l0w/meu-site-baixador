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
    # 🚀 MOTOR 1: Sistema focado em links do TikTok usando API estável de contingência
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

    # 📸 MOTOR 2: Sistema focado em Instagram usando um servidor proxy aberto alternativo (CoCobalt)
    try:
        payload = {"url": url, "videoQuality": "720", "downloadMode": "auto"}
        # Usando a rota aberta oficial estável de processamento em nuvem pública
        res = requests.post("https://wuk.sh", json=payload, headers={"Accept": "application/json", "Content-Type": "application/json"}, timeout=12).json()
        
        if res.get("status") == "stream":
            return {
                "video_url": res.get("url"),
                "audio_url": res.get("url")
            }
    except:
        pass

    # 🛠️ MOTOR 3: Raspagem estrutural nativa de emergência via Regex HTML
    try:
        html = requests.get(url, headers=HEADERS, timeout=10).text
        match = re.search(r'"video_url":"(.*?)"', html) or re.search(r'property="og:video" content="(.*?)"', html)
        if match:
            clean_url = match.group(1).replace(r'\u002F', '/').replace("&amp;", "&")
            return {
                "video_url": clean_url,
                "audio_url": clean_url
            }
    except:
        pass

    raise HTTPException(status_code=400, detail="Não foi possível extrair os links deste post público.")
