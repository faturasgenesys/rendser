from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()

# 🔗 Link direto para o arquivo endpoint_atual.txt no Google Drive
DRIVE_ENDPOINT_URL = "https://drive.google.com/uc?export=download&id=1tKH95snEwYts-TiuRJWdxbEHTleunsaO"

def get_current_endpoint():
    try:
        resp = httpx.get(DRIVE_ENDPOINT_URL, timeout=10)
        # Google Drive pode retornar HTML — extraímos o conteúdo entre <pre>...</pre> ou linhas simples de texto
        if resp.status_code == 200:
            # Remove tags HTML, se houver
            text = re.sub(r"<[^>]*>", "", resp.text).strip()
            # Valida se parece um endpoint .trycloudflare.com
            if "trycloudflare.com" in text:
                return text
        return None
    except Exception as e:
        print(f"Erro ao buscar endpoint: {e}")
        return None


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):
    base_url = get_current_endpoint()
    if not base_url:
        return {"erro": "Arquivo endpoint_atual.txt não encontrado ou inacessível"}

    target_url = f"{base_url}/{path}"
    method = request.method
    headers = dict(request.headers)

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method,
            target_url,
            headers=headers,
            content=await request.body(),
            timeout=60.0,
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
        media_type=resp.headers.get("content-type")
    )


@app.get("/")
def status():
    base_url = get_current_endpoint()
    return {
        "proxy_status": "ativo 🚀",
        "tunnel_destino": base_url or "não definido"
    }
