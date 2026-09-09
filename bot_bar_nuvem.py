def enviar_mensagem_whatsapp(numero, texto):
    """Envia mensagem via Whapi.Cloud"""
    if not WHAPI_TOKEN:
        log("⚠️ ERRO DE CONFIGURAÇÃO: WHAPI_TOKEN não definido.")
        return

    # 🛡️ TRAVA DE SEGURANÇA: nunca envia para grupos, seja qual for a origem da chamada
    if "@g.us" in str(numero) or "-" in str(numero):
        log(f"🚫 BLOQUEADO: tentativa de enviar mensagem para possível grupo ({numero})")
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