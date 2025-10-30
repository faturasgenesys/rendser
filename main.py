from fastapi import FastAPI, Request, Response
import httpx
import re

app = FastAPI()

# 🔗 Link direto para o arquivo endpoint_atual.txt no Google Drive
DRIVE_ENDPOINT_URL = "https://drive.google.com/uc?export=download&id=1tKH95snEwYts-TiuRJWdxbEHTleunsaO"

# ------------------------------
# 🔍 Função auxiliar para obter endpoint Cloudflare atual
# ------------------------------
def get_current_endpoint():
    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            resp = client.get(DRIVE_ENDPOINT_URL)

        if resp.status_code != 200:
            print(f"⚠️ HTTP {resp.status_code} ao acessar o Drive.")
            return None

        # Remove tags HTML e caracteres indesejados
        text = re.sub(r"<[^>]*>", "", resp.text)
        clean_text = text.encode("ascii", "ignore").decode().strip()
        clean_text = clean_text.replace("\r", "").replace("\n", "").replace("\ufeff", "").strip()

        if clean_text.startswith("http"):
            print(f"✅ Endpoint válido detectado: {clean_text}")
            return clean_text
        else:
            print(f"⚠️ Conteúdo inválido no arquivo: {clean_text}")
            return None

    except Exception as e:
        print(f"❌ Erro ao buscar endpoint: {e}")
        return None


# ------------------------------
# 🧭 Proxy universal — redireciona qualquer rota para o Flask local
# ------------------------------
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, full_path: str):
    base_url = get_current_endpoint()
    if not base_url:
        return Response(
            content='{"erro": "endpoint_atual.txt não encontrado ou inacessível"}',
            status_code=503,
            media_type="application/json",
        )

    target_url = f"{base_url}/{full_path}"
    method = request.method
    headers = dict(request.headers)

    print(f"🔁 Encaminhando requisição {method} → {target_url}")

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            resp = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                content=await request.body(),
            )

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            media_type=resp.headers.get("content-type"),
        )

    except Exception as e:
        print(f"❌ Erro ao encaminhar requisição para {target_url}: {e}")
        return Response(
            content=f'{{"erro": "falha ao conectar ao Flask: {e}"}}',
            status_code=500,
            media_type="application/json",
        )


# ------------------------------
# 🩺 Status do proxy
# ------------------------------
@app.get("/")
def status():
    base_url = get_current_endpoint()
    return {
        "proxy_status": "ativo 🚀",
        "tunnel_destino": base_url or "não definido"
    }
