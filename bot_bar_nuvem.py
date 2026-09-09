from flask import Flask, request, jsonify
from datetime import datetime
import os
import requests

app = Flask(__name__)

# ==============================================================================
# CONFIGURAÇÕES DO NEGÓCIO
# ==============================================================================
NOME_BAR = "Churrasquinho do Gaspar"
LINK_SITE = "https://balcao.oxemenu.com.br/churrasquinho_do_gaspar"
TEMPO_PREPARO = "25 minutos"

API_URL = os.environ.get("ZAPI_API_URL")
CLIENT_TOKEN = os.environ.get("ZAPI_CLIENT_TOKEN")

# Chave secreta simples para validar que a chamada em /webhook-pedido veio mesmo do oxemenu
# (troque por um valor aleatório seu e configure o mesmo valor no oxemenu, se ele permitir enviar headers)
OXEMENU_SECRET = os.environ.get("OXEMENU_SECRET", "")


def log(texto):
    agora = datetime.now().strftime("%d/%m %H:%M:%S")
    print(f"[{agora}] {texto}")


def enviar_mensagem_whatsapp(numero, texto):
    """Envia a mensagem real para o WhatsApp via Z-API"""
    if not API_URL or not CLIENT_TOKEN:
        log("⚠️ ERRO DE CONFIGURAÇÃO: ZAPI_API_URL ou ZAPI_CLIENT_TOKEN não definidos.")
        return

    payload = {"phone": numero, "message": texto}
    headers = {"Client-Token": CLIENT_TOKEN}
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        log(f"Envio para {numero} -> Status: {resp.status_code} | Resposta: {resp.text}")
    except Exception as e:
        log(f"❌ Erro ao enviar mensagem para {numero}: {e}")


# ==============================================================================
# PARTE 1: mensagens recebidas no WhatsApp -> manda o link do site
# ==============================================================================
@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    try:
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"status": "corpo_invalido"})

        if dados.get("fromMe") == True:
            return jsonify({"status": "ignorado"})

        numero_cliente = dados.get("phone")
        if not numero_cliente:
            return jsonify({"status": "dados_incompletos"})

        msg = (
            f"🍻 *Olá! Bem-vindo ao {NOME_BAR}!* 🍻\n\n"
            f"Agora os pedidos são feitos direto pelo nosso site, é rapidinho:\n"
            f"👉 {LINK_SITE}\n\n"
            f"Assim que seu pedido for feito, eu te aviso aqui mesmo! 😉"
        )
        enviar_mensagem_whatsapp(numero_cliente, msg)
        return jsonify({"status": "sucesso"})

    except Exception as e:
        log(f"🔥 ERRO INESPERADO no /webhook: {e}")
        return jsonify({"status": "erro_interno"})


# ==============================================================================
# PARTE 2: notificação vinda do oxemenu quando um pedido é feito no site
# ==============================================================================
@app.route("/webhook-pedido", methods=["POST"])
def receber_pedido_site():
    """
    Endpoint que o OXEMENU deve chamar quando um pedido novo é criado no site.
    ATENÇÃO: o formato exato do JSON que o oxemenu envia (nomes dos campos)
    é desconhecido ainda — os nomes abaixo (telefone, nome_cliente, itens, total)
    são um PALPITE e quase certamente vão precisar ser ajustados depois que
    você configurar o webhook no painel do oxemenu e ver o payload real chegando
    (basta olhar o log no Render).
    """
    try:
        dados = request.get_json(silent=True)
        log(f"📦 Payload recebido do oxemenu: {dados}")

        if not dados:
            return jsonify({"status": "corpo_invalido"})

        # Validação simples de segurança (opcional, se o oxemenu permitir enviar um header/token)
        if OXEMENU_SECRET:
            token_recebido = request.headers.get("X-Webhook-Secret", "")
            if token_recebido != OXEMENU_SECRET:
                log("⚠️ Tentativa de chamada em /webhook-pedido com token inválido.")
                return jsonify({"status": "nao_autorizado"}), 401

        # --- Ajustar estes campos assim que soubermos o formato real do oxemenu ---
        telefone_cliente = dados.get("telefone") or dados.get("phone")
        nome_cliente = dados.get("nome_cliente") or dados.get("customer_name", "Cliente")
        itens = dados.get("itens") or dados.get("items", [])
        total = dados.get("total", 0)

        if not telefone_cliente:
            log("⚠️ Pedido recebido sem telefone do cliente — não é possível avisar no WhatsApp.")
            return jsonify({"status": "sem_telefone"})

        itens_txt = ", ".join(str(i) for i in itens) if itens else "detalhes no painel do oxemenu"

        msg_cliente = (
            f"✅ *Pedido confirmado, {nome_cliente}!*\n\n"
            f"🛒