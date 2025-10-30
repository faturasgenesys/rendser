from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()

# 🔗 Link direto para o arquivo endpoint_atual.txt no Google Drive
DRIVE_ENDPOINT_URL = "https://drive.google.com/uc?export=download&id=1tKH95snEwYts-TiuRJWdxbEHTleunsaO"

def get_current_endpoint():
    try:
        # 1️⃣ tenta seguir redirecionamentos automáticos (Drive faz isso)
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            resp = client.get(DRIVE_ENDPOINT_URL)

        if resp.status_code == 200:
            # 2️⃣ remove tags HTML (Drive pode embutir o texto em <pre> ou <html>)
            text = re.sub(r"<[^>]*>", "", resp.text).strip()

            # 3️⃣ tenta detectar se há um link válido de tunnel
            if "trycloudflare.com" in text:
                return text
            else:
                print(f"Conteúdo inesperado: {text[:100]}...")
                return None
        else:
            print(f"Status HTTP inesperado: {resp.status_code}")
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
