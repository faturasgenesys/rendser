from fastapi import FastAPI
import httpx
import re

app = FastAPI(title="MyObsidian Proxy", version="1.0.0")

# 🔗 Link direto para o arquivo endpoint_atual.txt no Google Drive
DRIVE_ENDPOINT_URL = "https://drive.google.com/uc?export=download&id=1tKH95snEwYts-TiuRJWdxbEHTleunsaO"


def get_current_endpoint():
    """
    Faz o download do arquivo endpoint_atual.txt no Google Drive,
    limpa caracteres invisíveis e retorna o link do túnel Cloudflare.
    """
    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            resp = client.get(DRIVE_ENDPOINT_URL)

        if resp.status_code != 200:
            print(f"⚠️ HTTP {resp.status_code} ao acessar o Drive.")
            return None

        # 🔹 Remove tags HTML e caracteres não visíveis
        text = re.sub(r"<[^>]*>", "", resp.text)
        clean_text = text.encode("ascii", "ignore").decode().strip()
        clean_text = clean_text.replace("\r", "").replace("\n", "").replace("\ufeff", "").strip()

        # 🔹 Log detalhado
        print(f"🧾 Conteúdo bruto recebido do Drive: {text[:80]}...")
        print(f"🧹 Conteúdo final processado: '{clean_text}'")

        if clean_text.startswith("http"):
            print(f"✅ Endpoint válido detectado: {clean_text}")
            return clean_text
        else:
            print(f"⚠️ Conteúdo inválido no arquivo: {clean_text}")
            return None

    except Exception as e:
        print(f"❌ Erro ao buscar endpoint: {e}")
        return None


@app.get("/")
def status():
    """
    Retorna o status do proxy e o último endpoint válido do Drive.
    (Não tenta se conectar ao túnel — apenas lê e repassa o link.)
    """
    base_url = get_current_endpoint()
    return {
        "proxy_status": "ativo 🚀",
        "tunnel_destino": base_url or "não definido (Drive acessível, túnel externo não testado)"
    }


@app.get("/debug")
def debug():
    """
    Endpoint auxiliar para depuração.
    Exibe os primeiros 100 caracteres retornados pelo arquivo no Drive.
    """
    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            resp = client.get(DRIVE_ENDPOINT_URL)

        preview = re.sub(r"<[^>]*>", "", resp.text)[:200]
        return {"preview_conteudo_drive": preview}

    except Exception as e:
        return {"erro": f"Falha ao acessar Drive: {e}"}
