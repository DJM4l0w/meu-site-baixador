from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
import requests
import json

app = FastAPI()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h3>Erro critico: O arquivo index.html nao foi encontrado.</h3>", status_code=500)

@app.post("/analisar")
async def analisar_video(url: str = Form(...)):
    url_limpa = url.strip()

    # 🚀 CAMADA 1: Processador Multi-Plataforma via API de Alta Tolerância (SnapSave/AIO Engine)
    try:
        payload = {"url": url_limpa}
        # API pública distribuída de scraping que gerencia rotação de IPs comerciais automaticamente
        response = requests.post("https://download.online", json=payload, headers=HEADERS, timeout=12)
        
        if response.status_code == 200:
            data = response.json()
            # Estrutura padrão de retorno de arquivos de vídeo e áudio diretos
            if "download_url" in data:
                return {
                    "success": True,
                    "video_url": data["download_url"],
                    "audio_url": data.get("audio_url", data["download_url"])
                }
            elif "links" in data and len(data["links"]) > 0:
                # Pega o link com a melhor qualidade disponível na lista
                melhor_link = data["links"][0].get("url")
                return {
                    "success": True,
                    "video_url": melhor_link,
                    "audio_url": melhor_link
                }
    except:
        pass

    # 📱 CAMADA 2: Backup dedicado e exclusivo para o TikTok (Tikwm)
    if "tiktok.com" in url_limpa:
        try:
            res_tk = requests.get(f"https://tikwm.com{url_limpa}", timeout=10).json()
            if res_tk.get("code") == 0 and "data" in res_tk:
                return {
                    "success": True,
                    "video_url": res_tk["data"]["play"],
                    "audio_url": res_tk["data"]["music"]
                }
        except:
            pass

    # 📸 CAMADA 3: Backup de contingência para Instagram via API Pública Aberta (SnapInsta Proxy)
    if "instagram.com" in url_limpa:
        try:
            res_ig = requests.post("https://snapinsta.app", data={"url": url_limpa, "lang": "pt"}, headers=HEADERS, timeout=10).text
            # Extrai o link do arquivo mp4 bruto de dentro do container de resposta deles
            import re
            match_ig = re.search(r'href="(https://[^"]+mp4[^"]+)"', res_ig)
            if match_ig:
                video_url = match_ig.group(1).replace("&amp;", "&")
                return {
                    "success": True,
                    "video_url": video_url,
                    "audio_url": video_url
                }
        except:
            pass

    raise HTTPException(status_code=400, detail="Não foi possível descriptografar este link multimídia.")
