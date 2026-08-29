from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h3>Erro critico: O arquivo index.html nao foi encontrado.</h3>", status_code=500)

@app.post("/analisar")
async def analisar_video(url: str = Form(...)):
    # Clean input queries and formats
    clean_url = url.strip().split("?")[0]
    
    # List of open global API gateway mirrors optimized for network scraping
    api_mirrors = [
        "https://wuk.sh",
        "https://cobalt.tools",
        "https://cobalt.tools"
    ]
    
    payload = {
        "url": clean_url,
        "videoQuality": "720",
        "downloadMode": "auto"
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Cycle through clusters to bypass cloud network rate limiting
    for api_endpoint in api_mirrors:
        try:
            response = requests.post(api_endpoint, json=payload, headers=headers, timeout=8)
            if response.status_code == 200:
                data = response.json()
                
                # Handling single media stream tracks (YouTube, Twitter, Facebook, Reels)
                if data.get("status") == "stream":
                    return {
                        "success": True,
                        "video_url": data.get("url"),
                        "audio_url": data.get("url")
                    }
                # Handling carousel assets/pickers (TikTok photos, Instagram slides)
                elif data.get("status") == "picker" and len(data.get("picker", [])) > 0:
                    first_asset = data["picker"][0].get("url")
                    return {
                        "success": True,
                        "video_url": first_asset,
                        "audio_url": first_asset
                    }
        except:
            continue

    # Emergency scraping bypass specifically for TikTok structural tags
    if "tiktok.com" in url:
        try:
            res = requests.get(f"https://tikwm.com{url}", timeout=8).json()
            if res.get("code") == 0:
                return {
                    "success": True,
                    "video_url": res["data"]["play"],
                    "audio_url": res["data"]["music"]
                }
        except:
            pass

    raise HTTPException(status_code=400, detail="Nao foi possivel descriptografar este link. Verifique se o post e publico.")
