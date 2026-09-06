from flask import Flask, request, jsonify
from datetime import datetime
import os
import requests

app = Flask(__name__)

# ==============================================================================
# CONFIGURAÇÕES DO NEGÓCIO
# ==============================================================================
NOME_BAR = "Churrasquinho do Gaspar"
TEMPO_PREPARO = "25 minutos"
NUMERO_COZINHA = "5582999999999"       # <-- FICTÍCIO: troque pelo número real da cozinha

# Etapas do atendimento
ETAPA_SAUDACAO = 0
ETAPA_NOME = 1
ETAPA_CATEGORIA = 2
ETAPA_ITENS = 3

# ==============================================================================
# CARDÁPIO ORGANIZADO POR CATEGORIAS
# ==============================================================================
CARDAPIO = {
    "1": {
        "nome": "Churrasquinhos",
        "itens": [
            {"item": "Churrasco de boi", "preco": 13.00},
            {"item": "Churrasco de frango", "preco": 13.00},
            {"item": "Churrasco de coração", "preco": 13.00},
            {"item": "Churrasco medalhão de frango", "preco": 13.00},
            {"item": "Churrasco de asinha", "preco": 13.00},
            {"item": "Churrasco de charque", "preco": 13.00},
            {"item": "Churrasco de queijo coalho", "preco": 13.00},
            {"item": "Churrasco filé de carneiro", "preco": 13.00},
            {"item": "Churrasco costela de carneiro", "preco": 13.00},
            {"item": "Pão de alho", "preco": 13.00},
            {"item": "Churrasco linguiça de carneiro", "preco": 13.00},
        ]
    },
    "2": {
        "nome": "Caldinhos",
        "itens": [
            {"item": "Caldinho de feijão", "preco": 13.00},
            {"item": "Caldinho de mocotó", "preco": 13.00},
            {"item": "Caldinho de dobradinha", "preco": 13.00},
        ]
    },
    "3": {
        "nome": "Acompanhamentos",
        "itens": [
            {"item": "Porção de batata frita", "preco": 25.00},
            {"item": "Porção de torresmo", "preco": 18.00},
            {"item": "Porção ovo de codorna", "preco": 8.00},
        ]
    },
    "4": {
        "nome": "Especialidades Fritas",
        "itens": [
            {"item": "Coxinha Crocante Premium", "preco": 28.00},
            {"item": "Cebola Recheada Especial", "preco": 34.00},
            {"item": "Isca Crocante do Chef", "preco": 32.00},
            {"item": "Pastelzinho de Carne", "preco": 24.00},
            {"item": "Pastelzinho de Queijo", "preco": 24.00},
        ]
    },
    "5": {
        "nome": "Sucos (Maracujá, Caju, Manga, Goiaba, Acerola, Limão e Cajá)",
        "itens": [
            {"item": "Suco Jarra 1L", "preco": 14.00},
            {"item": "Suco Copo 400ml", "preco": 7.00},
        ]
    },
    "6": {
        "nome": "Bebidas",
        "itens": [
            {"item": "Guaraná 1L", "preco": 12.00},
            {"item": "Coca-Cola 1L", "preco": 12.00},
            {"item": "Guaraná 350ml", "preco": 7.00},
            {"item": "Coca-Cola 350ml", "preco": 7.00},
            {"item": "Coca-Cola zero 350ml", "preco": 7.00},
            {"item": "Fanta laranja 350ml", "preco": 7.00},
            {"item": "Sprite 350ml", "preco": 7.00},
            {"item": "Schweppes 350ml", "preco": 7.00},
            {"item": "Refrigerante FYS/ZERO Heineken", "preco": 7.00},
            {"item": "H2OH! Limonieto", "preco": 8.00},
            {"item": "Red Bull 250ml", "preco": 15.00},
            {"item": "Energético Monster 473ml", "preco": 15.00},
            {"item": "Energético TNT 473ml", "preco": 12.00},
            {"item": "Água mineral sem gás 510ml", "preco": 3.00},
            {"item": "Água mineral com gás 510ml", "preco": 4.00},
        ]
    },
    "7": {
        "nome": "Cervejas",
        "itens": [
            {"item": "Heineken 600ml", "preco": 17.00},
            {"item": "Amstel Puro Malte 600ml", "preco": 12.00},
            {"item": "Devassa 600ml", "preco": 10.00},
            {"item": "Budweiser 600ml", "preco": 13.00},
            {"item": "Antarctica original 600ml", "preco": 13.00},
            {"item": "Heineken LN 330ml", "preco": 11.00},
            {"item": "Heineken 0.0 LN 330ml", "preco": 11.00},
            {"item": "Praya LN 330ml (s/glúten)", "preco": 11.00},
            {"item": "Amstel Ultra LN 72kcal (s/glúten)", "preco": 10.00},
            {"item": "Ice Cabaré", "preco": 11.00},
            {"item": "Vinho", "preco": 25.00},
        ]
    },
    "8": {
        "nome": "Doses",
        "itens": [
            {"item": "Conhaque de Alcatrão", "preco": 6.00},
            {"item": "Conhaque Dreher", "preco": 5.00},
            {"item": "Pitú pura", "preco": 5.00},
            {"item": "Pitú mel e limão", "preco": 6.00},
            {"item": "Campari", "preco": 9.00},
            {"item": "Montilla", "preco": 9.00},
            {"item": "Whisky Red Label", "preco": 12.00},
            {"item": "Whisky Black & White", "preco": 9.00},
            {"item": "Whisky Old Parr", "preco": 16.00},
            {"item": "Vodka Slova", "preco": 5.00},
            {"item": "Vodka Absolut", "preco": 14.00},
            {"item": "Vodka Smirnoff", "preco": 9.00},
            {"item": "Misturada cravo e canela", "preco": 5.00},
            {"item": "Licor Don Luiz", "preco": 12.00},
        ]
    },
}

API_URL = os.environ.get("ZAPI_API_URL")
CLIENT_TOKEN = os.environ.get("ZAPI_CLIENT_TOKEN")

# Dicionário temporário na memória para controlar as conversas de cada cliente
estados_clientes = {}

# Guarda os IDs das últimas mensagens processadas, para não responder duas vezes
# caso a Z-API reenvie o mesmo webhook (acontece em instabilidades de rede)
mensagens_processadas = []
LIMITE_MENSAGENS_GUARDADAS = 200


def log(texto):
    """Log com horário, pra facilitar achar o que aconteceu nos logs do Render"""
    agora = datetime.now().strftime("%d/%m %H:%M:%S")
    print(f"[{agora}] {texto}")


def enviar_mensagem_whatsapp(numero, texto):
    """Envia a mensagem real para o WhatsApp do cliente via Z-API"""
    if not API_URL or not CLIENT_TOKEN:
        log("⚠️ ERRO DE CONFIGURAÇÃO: ZAPI_API_URL ou ZAPI_CLIENT_TOKEN não definidos nas variáveis de ambiente.")
        return

    payload = {
        "phone": numero,
        "message": texto
    }
    headers = {"Client-Token": CLIENT_TOKEN}
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        log(f"Envio para {numero} -> Status: {resp.status_code} | Resposta: {resp.text}")
    except Exception as e:
        log(f"❌ Erro ao enviar mensagem para {numero}: {e}")


def montar_texto_categorias():
    texto = "📋 *Escolha uma categoria digitando o número:*\n\n"
    for chave, cat in CARDAPIO.items():
        texto += f"*{chave}* - {cat['nome']}\n"
    texto += "\n_Digite *MENU* a qualquer momento para reiniciar o atendimento._"
    return texto


def montar_texto_itens(categoria):
    texto = f"🍢 *{categoria['nome']}*\n\n"
    for i, info in enumerate(categoria["itens"], start=1):
        texto += f"*{i}* - {info['item']} (R$ {info['preco']:.2f})\n"
    texto += (
        "\nDigite o *NÚMERO* do item para adicionar ao pedido.\n"
        "Digite *CATEGORIAS* para voltar ao menu de categorias.\n"
        "Digite *FECHAR* para finalizar o pedido."
    )
    return texto


def iniciar_novo_cliente():
    return {"etapa": ETAPA_SAUDACAO, "nome": "", "carrinho": [], "categoria_atual": None}


def enviar_saudacao(numero):
    msg = (
        f"🍻 *Olá! Bem-vindo ao Autoatendimento do {NOME_BAR}!* 🍻\n\n"
        "Para começarmos o seu pedido de *RETIRADA*, por favor, "
        "digite o seu *NOME* completo:"
    )
    enviar_mensagem_whatsapp(numero, msg)


@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    """Esta rota recebe as mensagens que os clientes mandam no WhatsApp"""
    try:
        dados = request.get_json(silent=True)

        if not dados:
            return jsonify({"status": "corpo_invalido"})

        # Ignora mensagens enviadas pelo próprio robô do bar para não entrar em loop infinito
        if dados.get("fromMe") == True:
            return jsonify({"status": "ignorado"})

        # Evita processar a mesma mensagem duas vezes (reenvio de webhook)
        message_id = dados.get("messageId")
        if message_id:
            if message_id in mensagens_processadas:
                return jsonify({"status": "duplicado_ignorado"})
            mensagens_processadas.append(message_id)
            if len(mensagens_processadas) > LIMITE_MENSAGENS_GUARDADAS:
                mensagens_processadas.pop(0)

        numero_cliente = dados.get("phone")
        mensagem_texto = dados.get("text", {}).get("message", "").strip()

        if not numero_cliente:
            return jsonify({"status": "dados_incompletos"})

        # Mensagem sem texto (áudio, figurinha, imagem, etc.)
        if not mensagem_texto:
            enviar_mensagem_whatsapp(
                numero_cliente,
                "🙏 Por enquanto só consigo entender mensagens de *texto*. Pode digitar, por favor?"
            )
            return jsonify({"status": "mensagem_sem_texto"})

        # Comando global: reinicia o atendimento a qualquer momento
        if mensagem_texto.upper() in ("MENU", "REINICIAR", "OI", "OLÁ", "OLA"):
            estados_clientes[numero_cliente] = iniciar_novo_cliente()
            estados_clientes[numero_cliente]["etapa"] = ETAPA_NOME
            enviar_saudacao(numero_cliente)
            return jsonify({"status": "sucesso"})

        # Inicia a conversa com a etapa 0 se o cliente for novo no atendimento
        if numero_cliente not in estados_clientes:
            estados_clientes[numero_cliente] = iniciar_novo_cliente()

        usuario = estados_clientes[numero_cliente]

        # --- ETAPA 0: SAUDAÇÃO ---
        if usuario["etapa"] == ETAPA_SAUDACAO:
            usuario["etapa"] = ETAPA_NOME
            enviar_saudacao(numero_cliente)
            return jsonify({"status": "sucesso"})

        # --- ETAPA 1: RECEBER NOME E MOSTRAR CATEGORIAS ---
        elif usuario["etapa"] == ETAPA_NOME:
            nome_digitado = mensagem_texto.strip()
            if len(nome_digitado) < 2:
                enviar_mensagem_whatsapp(numero_cliente, "Por favor, digite um nome válido:")
                return jsonify({"status": "sucesso"})

            usuario["nome"] = nome_digitado.title()
            usuario["etapa"] = ETAPA_CATEGORIA

            msg = f"Perfeito, {usuario['nome']}!\n\n" + montar_texto_categorias()
            enviar_mensagem_whatsapp(numero_cliente, msg)
            return jsonify({"status": "sucesso"})

        # --- ETAPA 2: RECEBER CATEGORIA ESCOLHIDA ---
        elif usuario["etapa"] == ETAPA_CATEGORIA:
            if mensagem_texto in CARDAPIO:
                usuario["categoria_atual"] = mensagem_texto
                usuario["etapa"] = ETAPA_ITENS
                msg = montar_texto_itens(CARDAPIO[mensagem_texto])
                enviar_mensagem_whatsapp(numero_cliente, msg)
            else:
                msg = "❌ Categoria inválida.\n\n" + montar_texto_categorias()
                enviar_mensagem_whatsapp(numero_cliente, msg)
            return jsonify({"status": "sucesso"})

        # --- ETAPA 3: ESCOLHER ITENS DA CATEGORIA, VOLTAR OU FECHAR ---
        elif usuario["etapa"] == ETAPA_ITENS:
            categoria = CARDAPIO[usuario["categoria_atual"]]

            if mensagem_texto.upper() == "FECHAR":
                if not usuario["carrinho"]:
                    enviar_mensagem_whatsapp(numero_cliente, "❌ Seu carrinho está vazio! Escolha um item antes de fechar.")
                    return jsonify({"status": "sucesso"})

                total_pedido = sum([item["preco"] for item in usuario["carrinho"]])
                itens_txt = ", ".join([item["item"] for item in usuario["carrinho"]])
                horario = datetime.now().strftime("%H:%M")

                # Mensagem para o cliente
                msg_cliente = (
                    f"📝 *RESUMO DO SEU PEDIDO*, {usuario['nome']}:\n\n"
                    f"🛒 *Itens:* {itens_txt}\n"
                    f"💰 *Total:* R$ {total_pedido:.2f}\n\n"
                    f"💵 *Pagamento na retirada* (dinheiro, PIX ou cartão).\n\n"
                    f"Seu pedido estará pronto para retirada em *{TEMPO_PREPARO}*! 🍻"
                )
                enviar_mensagem_whatsapp(numero_cliente, msg_cliente)

                # Mensagem para a cozinha
                msg_cozinha = (
                    f"🔔 *NOVO PEDIDO* ({horario})\n\n"
                    f"👤 *Cliente:* {usuario['nome']}\n"
                    f"📱 *Telefone:* {numero_cliente}\n\n"
                    f"🛒 *Itens:*\n"
                )
                for item in usuario["carrinho"]:
                    msg_cozinha += f"- {item['item']}\n"
                msg_cozinha += (
                    f"\n💰 *Total (cobrar na retirada):* R$ {total_pedido:.2f}"
                )

                enviar_mensagem_whatsapp(NUMERO_COZINHA, msg_cozinha)
                log(f"✅ Pedido fechado - {usuario['nome']} ({numero_cliente}) - R$ {total_pedido:.2f}")

                # Reseta o cliente na memória do sistema para permitir novos pedidos futuros
                del estados_clientes[numero_cliente]
                return jsonify({"status": "sucesso"})

            elif mensagem_texto.upper() == "CATEGORIAS":
                usuario["etapa"] = ETAPA_CATEGORIA
                usuario["categoria_atual"] = None
                enviar_mensagem_whatsapp(numero_cliente, montar_texto_categorias())
                return jsonify({"status": "sucesso"})

            elif mensagem_texto.isdigit() and 1 <= int(mensagem_texto) <= len(categoria["itens"]):
                item_escolhido = categoria["itens"][int(mensagem_texto) - 1]
                usuario["carrinho"].append(item_escolhido)
                msg = (
                    f"✅ *{item_escolhido['item']}* adicionado!\n\n"
                    "Quer mais alguma coisa dessa categoria? Digite outro número.\n"
                    "Digite *CATEGORIAS* para ver outras opções ou *FECHAR* para finalizar."
                )
                enviar_mensagem_whatsapp(numero_cliente, msg)
            else:
                msg = "❌ Opção inválida.\n\n" + montar_texto_itens(categoria)
                enviar_mensagem_whatsapp(numero_cliente, msg)

        return jsonify({"status": "sucesso"})

    except Exception as e:
        # Se algo inesperado quebrar, isso registra o erro em vez de derrubar o servidor
        log(f"🔥 ERRO INESPERADO no webhook: {e}")
        return jsonify({"status": "erro_interno"})


@app.route("/", methods=["GET"])
def health_check():
    """Rota simples só pra confirmar que o serviço está de pé (útil pra testar no navegador)"""
    return jsonify({"status": "online", "bot": NOME_BAR})


# ==============================================================================
# INICIALIZAÇÃO DO SERVIDOR PROFISSIONAL WAITRESS
# ==============================================================================
if __name__ == "__main__":
    from waitress import serve
    # Força o Python a usar a porta exata que o Render mandar
    porta = int(os.environ.get("PORT", 10000))
    log(f"🚀 Servidor do {NOME_BAR} ativo na porta {porta}!")
    serve(app, host="0.0.0.0", port=porta)