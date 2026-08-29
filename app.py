from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

# Abre o arquivo HTML que está na mesma pasta raiz do servidors
@app.get("/", response_class=HTMLResponse)
async def read_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h3>Erro crítico: O arquivo index.html não foi encontrado na raiz.</h3>", status_code=500)

@app.post("/analisar")
async def analisar_video(url: str = Form(...)):
    try:
        # Envia a requisição para uma das instâncias mais robustas e atualizadas do Cobalt
        payload = {
            "url": url,
            "videoQuality": "720",
            "downloadMode": "auto"
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Usando a API de processamento estável que não bloqueia servidores de nuvem
        response = requests.post("https://wuk.sh", json=payload, headers=headers, timeout=15)
        data = response.json()
        
        # Se a API retornou o link direto do vídeo
        if data.get("status") == "stream":
            return {
                "success": True,
                "video_url": data.get("url"),
                "audio_url": data.get("url")  # Fallback padrão
            }
        # Se a API retornou múltiplos formatos ou fotos
        elif data.get("status") == "picker" and len(data.get("picker", [])) > 0:
            return {
                "success": True,
                "video_url": data["picker"][0].get("url"),
                "audio_url": data["picker"][0].get("url")
            }
            
        raise Exception()
    except:
        # Fallback 2: Se a primeira API falhar, tenta o motor alternativo do Tikwm para o TikTok
        if "tiktok.com" in url:
            try:
                res = requests.get(f"https://tikwm.com{url}", timeout=10).json()
                if res.get("code") == 0:
                    return {
                        "success": True,
                        "video_url": res["data"]["play"],
                        "audio_url": res["data"]["music"]
                    }
            except:
                pass
                
        raise HTTPException(status_code=400, detail="Não foi possível descriptografar este link. Verifique se o post é público.")
