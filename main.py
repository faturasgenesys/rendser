from fastapi import FastAPI, Request, Response
import httpx
import re

app = FastAPI()

# 🔗 Link direto para o arquivo endpoint_atual.txt no Google Drive
DRIVE_ENDPOINT_URL = "https://drive.google.com/uc?export=download&id=1tKH95snEwYts-TiuRJWdxbEHTleunsaO"

def get_current_endpoint():
    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            resp = client.get(DRIVE_ENDPOINT_URL)

        if resp.status_code != 200:
            print(f"⚠️ HTTP {resp.status_code} ao acessar o Drive.")
            return None

        # 🔹 Remove tags HTML, espaços e caracteres invisíveis
        text = re.sub(r"<[^>]*>", "", resp.text)
        clean_text = text.encode('ascii', 'ignore').decode().strip()

        # 🔹 Corrige possíveis \r\n, BOM, espaços extras
        clean_text = clean_text.replace("\r", "").replace("\n", "").replace("\ufeff", "").strip()

        # 🔹 Log para depuração
        print(f"🧾 Conteúdo final processado: '{clean_text}'")

        if clean_text.startswith("http"):
            print(f"✅ Endpoint válido detectado: {clean_text}")
            return clean_text
        else:
            print(f"⚠️ Conteúdo inválido no arquivo: {clean_text}")
            return None

    except Exception as e:
        print(f"❌ Erro ao buscar endpoint: {e}")
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
