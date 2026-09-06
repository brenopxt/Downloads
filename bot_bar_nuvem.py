from flask import Flask, request, jsonify
from datetime import datetime
import os
import requests

app = Flask(__name__)

# ==============================================================================
# CONFIGURAÇÕES DO NEGÓCIO
# ==============================================================================
NUMERO_COZINHA = "5582999999999"       # <-- FICTÍCIO: troque pelo número real da cozinha
CHAVE_PIX = "00.000.000/0001-00"       # <-- FICTÍCIO: troque pela chave PIX real (CNPJ)

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


def enviar_mensagem_whatsapp(numero, texto):
    """Envia a mensagem real para o WhatsApp do cliente via Z-API"""
    payload = {
        "phone": numero,
        "message": texto
    }
    headers = {"Client-Token": CLIENT_TOKEN}
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        print(f"Status: {resp.status_code} | Resposta: {resp.text}")
    except Exception as e:
        print(f"Erro ao enviar mensagem para o WhatsApp: {e}")


def montar_texto_categorias():
    texto = "📋 *Escolha uma categoria digitando o número:*\n\n"
    for chave, cat in CARDAPIO.items():
        texto += f"*{chave}* - {cat['nome']}\n"
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


@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    """Esta rota recebe as mensagens que os clientes mandam no WhatsApp"""
    dados = request.get_json()

    # Ignora mensagens enviadas pelo próprio robô do bar para não entrar em loop infinito
    if dados.get("fromMe") == True:
        return jsonify({"status": "ignorado"})

    numero_cliente = dados.get("phone")
    mensagem_texto = dados.get("text", {}).get("message", "").strip()

    if not numero_cliente or not mensagem_texto:
        return jsonify({"status": "dados_incompletos"})

    # Inicia a conversa com a etapa 0 se o cliente for novo no atendimento
    if numero_cliente not in estados_clientes:
        estados_clientes[numero_cliente] = {
            "etapa": 0,
            "nome": "",
            "carrinho": [],
            "categoria_atual": None
        }

    usuario = estados_clientes[numero_cliente]

    # --- ETAPA 0: SAUDAÇÃO ---
    if usuario["etapa"] == 0:
        usuario["etapa"] = 1
        msg = (
            "🍻 *Olá! Bem-vindo ao Autoatendimento do Churrasquinho do Gaspar!* 🍻\n\n"
            "Para começarmos o seu pedido de *RETIRADA*, por favor, "
            "digite o seu *NOME* completo:"
        )
        enviar_mensagem_whatsapp(numero_cliente, msg)
        return jsonify({"status": "sucesso"})

    # --- ETAPA 1: RECEBER NOME E MOSTRAR CATEGORIAS ---
    elif usuario["etapa"] == 1:
        usuario["nome"] = mensagem_texto
        usuario["etapa"] = 2

        msg = f"Perfeito, {usuario['nome']}!\n\n" + montar_texto_categorias()
        enviar_mensagem_whatsapp(numero_cliente, msg)
        return jsonify({"status": "sucesso"})

    # --- ETAPA 2: RECEBER CATEGORIA ESCOLHIDA ---
    elif usuario["etapa"] == 2:
        if mensagem_texto in CARDAPIO:
            usuario["categoria_atual"] = mensagem_texto
            usuario["etapa"] = 3
            msg = montar_texto_itens(CARDAPIO[mensagem_texto])
            enviar_mensagem_whatsapp(numero_cliente, msg)
        else:
            msg = "❌ Categoria inválida.\n\n" + montar_texto_categorias()
            enviar_mensagem_whatsapp(numero_cliente, msg)
        return jsonify({"status": "sucesso"})

    # --- ETAPA 3: ESCOLHER ITENS DA CATEGORIA, VOLTAR OU FECHAR ---
    elif usuario["etapa"] == 3:
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
                f"📌 *Chave PIX:* {CHAVE_PIX}\n\n"
                f"Por favor, realize o pagamento e envie o comprovante aqui. "
                f"Seu pedido estará pronto para retirada em *25 minutos*!"
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
            msg_cozinha += f"\n💰 *Total:* R$ {total_pedido:.2f}"

            enviar_mensagem_whatsapp(NUMERO_COZINHA, msg_cozinha)

            # Reseta o cliente na memória do sistema para permitir novos pedidos futuros
            del estados_clientes[numero_cliente]
            return jsonify({"status": "sucesso"})

        elif mensagem_texto.upper() == "CATEGORIAS":
            usuario["etapa"] = 2
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


# ==============================================================================
# INICIALIZAÇÃO DO SERVIDOR PROFISSIONAL WAITRESS
# ==============================================================================
if __name__ == "__main__":
    from waitress import serve
    # Força o Python a usar a porta exata que o Render mandar
    porta = int(os.environ.get("PORT", 10000))
    print(f"🚀 Servidor do Bar ativo na porta {porta}!")
    serve(app, host="0.0.0.0", port=porta)