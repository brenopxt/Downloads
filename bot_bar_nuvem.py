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

# ==============================================================================
# CONFIGURAÇÕES DA WHAPI.CLOUD
# ==============================================================================
WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN")
WHAPI_URL = "https://gate.whapi.cloud/messages/text"


def log(texto):
    agora = datetime.now().strftime("%d/%m %H:%M:%S")
    print(f"[{agora}] {texto}")


def enviar_mensagem_whatsapp(numero, texto):
    """Envia mensagem via Whapi.Cloud"""
    if not WHAPI_TOKEN:
        log("⚠️ ERRO DE CONFIGURAÇÃO: WHAPI_TOKEN não definido.")
        return

    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"to": numero, "body": texto}

    try:
        resp = requests.post(WHAPI_URL, json=payload, headers=headers, timeout=10)
        log(f"Envio para {numero} -> Status: {resp.status_code} | Resposta: {resp.text}")
    except Exception as e:
        log(f"❌ Erro ao enviar mensagem para {numero}: {e}")


@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    try:
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"status": "corpo_invalido"})

        # Só nos interessa evento de mensagens
        if dados.get("event", {}).get("type") != "messages":
            return jsonify({"status": "ignorado"})

        lista_mensagens = dados.get("messages", [])
        if not lista_mensagens:
            return jsonify({"status": "sem_mensagens"})

        mensagem = lista_mensagens[0]

        # Ignora mensagens enviadas pelo próprio bot (evita loop)
        if mensagem.get("from_me"):
            return jsonify({"status": "ignorado"})

        # 🚫 BLOQUEIO DE GRUPO: chat_id de grupo sempre termina em "@g.us"
        chat_id = mensagem.get("chat_id", "")
        if chat_id.endswith("@g.us"):
            log(f"🚫 Mensagem de grupo ignorada (chat_id: {chat_id})")
            return jsonify({"status": "grupo_ignorado"})

        numero_cliente = mensagem.get("from")
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


@app.route("/webhook-pedido", methods=["POST"])
def receber_pedido_site():
    """Endpoint que o oxemenu chama quando um pedido novo é feito no site"""
    try:
        dados = request.get_json(silent=True)
        log(f"📦 Payload recebido do oxemenu: {dados}")

        if not dados:
            return jsonify({"status": "corpo_invalido"})

        telefone_cliente = dados.get("telefone") or dados.get("phone")
        nome_cliente = dados.get("nome_cliente") or dados.get("customer_name", "Cliente")
        itens = dados.get("itens") or dados.get("items", [])
        total = dados.get("total", 0)

        if not telefone_cliente:
            log("⚠️ Pedido recebido sem telefone do cliente.")
            return jsonify({"status": "sem_telefone"})

        itens_txt = ", ".join(str(i) for i in itens) if itens else "detalhes no painel do oxemenu"

        msg_cliente = (
            f"✅ *Pedido confirmado, {nome_cliente}!*\n\n"
            f"🛒 *Itens:* {itens_txt}\n"
            f"💰 *Total:* R$ {float(total):.2f}\n\n"
            f"Seu pedido já está sendo preparado e fica pronto em *{TEMPO_PREPARO}*! 🍻"
        )
        enviar_mensagem_whatsapp(telefone_cliente, msg_cliente)
        log(f"✅ Pedido do site confirmado para {nome_cliente} ({telefone_cliente})")

        return jsonify({"status": "sucesso"})

    except Exception as e:
        log(f"🔥 ERRO INESPERADO no /webhook-pedido: {e}")
        return jsonify({"status": "erro_interno"})


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "online", "bot": NOME_BAR})


if __name__ == "__main__":
    from waitress import serve
    porta = int(os.environ.get("PORT", 10000))
    log(f"🚀 Servidor do {NOME_BAR} ativo na porta {porta}!")
    serve(app, host="0.0.0.0", port=porta)