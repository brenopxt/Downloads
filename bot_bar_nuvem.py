from flask import Flask, request, jsonify
from datetime import datetime
import os
import requests

app = Flask(__name__)

# ==============================================================================
# CONFIGURAÇÃO DO CARDÁPIO REAL DO BAR
# ==============================================================================
CARDAPIO = {
    # --- CHURRASQUINHOS ---
    "1": {"item": "Churrasco de boi", "preco": 13.00},
    "2": {"item": "Churrasco de frango", "preco": 13.00},
    "3": {"item": "Churrasco de coração", "preco": 13.00},
    "4": {"item": "Churrasco medalhão de frango", "preco": 13.00},
    "5": {"item": "Churrasco de asinha", "preco": 13.00},
    "6": {"item": "Churrasco de charque", "preco": 13.00},
    "7": {"item": "Churrasco de queijo coalho", "preco": 13.00},
    "8": {"item": "Churrasco filé de carneiro", "preco": 13.00},
    "9": {"item": "Churrasco costela de carneiro", "preco": 13.00},
    "10": {"item": "Pão de alho", "preco": 13.00},
    "11": {"item": "Churrasco linguiça de carneiro", "preco": 13.00},

    # --- CALDINHOS ---
    "12": {"item": "Caldinho de feijão", "preco": 13.00},
    "13": {"item": "Caldinho de mocotó", "preco": 13.00},
    "14": {"item": "Caldinho de dobradinha", "preco": 13.00},

    # --- ACOMPANHAMENTOS ---
    "15": {"item": "Porção de batata frita", "preco": 25.00},
    "16": {"item": "Porção de torresmo", "preco": 18.00},
    "17": {"item": "Porção ovo de codorna", "preco": 8.00},

    # --- ESPECIALIDADES FRITAS ---
    "18": {"item": "Coxinha Crocante Premium", "preco": 28.00},
    "19": {"item": "Cebola Recheada Especial", "preco": 34.00},
    "20": {"item": "Isca Crocante do Chef", "preco": 32.00},
    "21": {"item": "Pastelzinho de Carne", "preco": 24.00},
    "22": {"item": "Pastelzinho de Queijo", "preco": 24.00},

    # --- SUCOS (sabores: Maracujá, Caju, Manga, Goiaba, Acerola, Limão e Cajá) ---
    "23": {"item": "Suco Jarra 1L", "preco": 14.00},
    "24": {"item": "Suco Copo 400ml", "preco": 7.00},

    # --- BEBIDAS ---
    "25": {"item": "Guaraná 1L", "preco": 12.00},
    "26": {"item": "Coca-Cola 1L", "preco": 12.00},
    "27": {"item": "Guaraná 350ml", "preco": 7.00},
    "28": {"item": "Coca-Cola 350ml", "preco": 7.00},
    "29": {"item": "Coca-Cola zero 350ml", "preco": 7.00},
    "30": {"item": "Fanta laranja 350ml", "preco": 7.00},
    "31": {"item": "Sprite 350ml", "preco": 7.00},
    "32": {"item": "Schweppes 350ml", "preco": 7.00},
    "33": {"item": "Refrigerante FYS/ZERO Heineken", "preco": 7.00},
    "34": {"item": "H2OH! Limonieto", "preco": 8.00},
    "35": {"item": "Red Bull 250ml", "preco": 15.00},
    "36": {"item": "Energético Monster 473ml", "preco": 15.00},
    "37": {"item": "Energético TNT 473ml", "preco": 12.00},
    "38": {"item": "Água mineral sem gás 510ml", "preco": 3.00},
    "39": {"item": "Água mineral com gás 510ml", "preco": 4.00},

    # --- CERVEJAS ---
    "40": {"item": "Heineken 600ml", "preco": 17.00},
    "41": {"item": "Amstel Puro Malte 600ml", "preco": 12.00},
    "42": {"item": "Devassa 600ml", "preco": 10.00},
    "43": {"item": "Budweiser 600ml", "preco": 13.00},
    "44": {"item": "Antarctica original 600ml", "preco": 13.00},
    "45": {"item": "Heineken LN 330ml", "preco": 11.00},
    "46": {"item": "Heineken 0.0 LN 330ml", "preco": 11.00},
    "47": {"item": "Praya LN 330ml (s/glúten)", "preco": 11.00},
    "48": {"item": "Amstel Ultra LN 72kcal (s/glúten)", "preco": 10.00},
    "49": {"item": "Ice Cabaré", "preco": 11.00},
    "50": {"item": "Vinho", "preco": 25.00},

    # --- DOSES ---
    "51": {"item": "Conhaque de Alcatrão", "preco": 6.00},
    "52": {"item": "Conhaque Dreher", "preco": 5.00},
    "53": {"item": "Pitú pura", "preco": 5.00},
    "54": {"item": "Pitú mel e limão", "preco": 6.00},
    "55": {"item": "Campari", "preco": 9.00},
    "56": {"item": "Montilla", "preco": 9.00},
    "57": {"item": "Whisky Red Label", "preco": 12.00},
    "58": {"item": "Whisky Black & White", "preco": 9.00},
    "59": {"item": "Whisky Old Parr", "preco": 16.00},
    "60": {"item": "Vodka Slova", "preco": 5.00},
    "61": {"item": "Vodka Absolut", "preco": 14.00},
    "62": {"item": "Vodka Smirnoff", "preco": 9.00},
    "63": {"item": "Misturada cravo e canela", "preco": 5.00},
    "64": {"item": "Licor Don Luiz", "preco": 12.00},
}

# Dicionário temporário na memória para controlar as conversas de cada cliente
estados_clientes = {}

API_URL = "https://api.z-api.io/instances/3F8B7081877EB18520FB260BF05B3023/token/0EC998A354971A6CF2550B50/send-text"
CLIENT_TOKEN = os.environ.get("ZAPI_CLIENT_TOKEN")

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
        estados_clientes[numero_cliente] = {"etapa": 0, "nome": "", "carrinho": []}
        
    usuario = estados_clientes[numero_cliente]
    
    # --- ETAPA 0: SAUDAÇÃO ---
    if usuario["etapa"] == 0:
        usuario["etapa"] = 1
        msg = (
            "🍻 *Olá! Bem-vindo ao Autoatendimento do Bar!* 🍻\n\n"
            "Para começarmos o seu pedido de *RETIRADA*, por favor, "
            "digite o seu *NOME* completo:"
        )
        enviar_mensagem_whatsapp(numero_cliente, msg)
        return jsonify({"status": "sucesso"})

    # --- ETAPA 1: RECEBER NOME E MOSTRAR CARDÁPIO ---
    elif usuario["etapa"] == 1:
        usuario["nome"] = mensagem_texto
        usuario["etapa"] = 2
        
        texto_cardapio = ""
        for chave, info in CARDAPIO.items():
            texto_cardapio += f"*{chave}* - {info['item']} (R$ {info['preco']:.2f})\n"
            
        msg = (
            f"Perfeito, {usuario['nome']}! Aqui está o nosso cardápio de hoje:\n\n"
            f"{texto_cardapio}\n"
            "Digite o *NÚMERO* do item que você deseja adicionar ao pedido.\n"
            "(Quando terminar de escolher tudo, digite *FECHAR*)"
        )
        enviar_mensagem_whatsapp(numero_cliente, msg)
        return jsonify({"status": "sucesso"})

    # --- ETAPA 2: ADICIONAR ITENS OU FINALIZAR ---
    elif usuario["etapa"] == 2:
        if mensagem_texto.upper() == "FECHAR":
            if not usuario["carrinho"]:
                enviar_mensagem_whatsapp(numero_cliente, "❌ Seu carrinho está vazio! Digite um número do cardápio.")
                return jsonify({"status": "sucesso"})
                
            total_pedido = sum([item["preco"] for item in usuario["carrinho"]])
            itens_txt = ", ".join([item["item"] for item in usuario["carrinho"]])
            
            # Mensagem de fechamento consistente gerada automaticamente
            msg = (
                f"📝 *RESUMO DO SEU PEDIDO*, {usuario['nome']}:\n\n"
                f"🛒 *Itens:* {itens_txt}\n"
                f"💰 *Total:* R$ {total_pedido:.2f}\n\n"
                f"📌 *Chave PIX (CNPJ):* [INSERIR_CNPJ_AQUI]\n\n"
                f"Por favor, realize o pagamento e envie o comprovante aqui. "
                f"Seu pedido estará pronto para retirada em *25 minutos*!"
            )
            enviar_mensagem_whatsapp(numero_cliente, msg)
            
            # Reseta o cliente na memória do sistema para permitir novos pedidos futuros
            del estados_clientes[numero_cliente]
            return jsonify({"status": "sucesso"})
            
        elif mensagem_texto in CARDAPIO:
            item_escolhido = CARDAPIO[mensagem_texto]
            usuario["carrinho"].append(item_escolhido)
            msg = f"✅ *{item_escolhido['item']}* adicionado!\n\nQuer mais alguma coisa? Digite outro número ou digite *FECHAR* para finalizar."
            enviar_mensagem_whatsapp(numero_cliente, msg)
        else:
            enviar_mensagem_whatsapp(numero_cliente, "❌ Opção inválida. Digite um número do cardápio ou *FECHAR*.")
            
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