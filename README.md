# ☁️ MyObsidian Proxy (Render)

Este proxy redireciona as requisições do agente GPT para o túnel Cloudflare local do servidor Flask.

## 🔧 Como funciona
1. O servidor local Flask gera um novo link `.trycloudflare.com` e o salva em `endpoint_atual.txt`;
2. Esse arquivo está no Google Drive e é compartilhado publicamente;
3. O proxy lê o conteúdo do arquivo e encaminha as requisições recebidas para o túnel atual.

## 🌐 Endpoints
- `GET /` → Mostra o status e o túnel atual.
- Outros caminhos (`/search`, `/list`, etc.) → São redirecionados automaticamente para o Flask local.

## 🧩 Deploy no Render
1. Crie um serviço web no [Render](https://render.com);
2. Conecte este repositório GitHub;
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
4. Clique em “Deploy”.

## ✅ Resultado
O Render fornecerá um domínio fixo, como: