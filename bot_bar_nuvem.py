from flask import Flask, request, jsonify
from datetime import datetime
import os
import requests

app = Flask(__name__)

# ==============================================================================
# CONFIGURAÇÃO DO CARDÁPIO REAL DO BAR
# ==============================================================================
CARDAPIO = {
    "1": {"item": "Cerveja Skol Latão", "preco": 8.50},
    "2": {"item": "Cerveja Heineken", "preco": 12.00},
    "3": {"item": "Porção de Batata Frita", "preco": 28.00},
    "4": {"item": "Calabresa Acebolada", "preco": 32.00},
    "5": {"item": "Refrigerante Lata", "preco": 6.00}
}

# SUA LINHA 20 CONFIGURADA CORRETAMENTE COM SEU ID E TOKEN REAIS:
API_URL = "https://z-api.io/instance/3F8B7081877EB18520FB260BF05B3023/3F8B7081877EB18520FB260BF05B3023/send-text"

# Dicionário temporário na memória para controlar as conversas de cada cliente
estados_clientes = {}

def enviar_mensagem_whatsapp(numero, texto):
    """Envia a mensagem real para o WhatsApp do cliente via Z-API"""
    payload = {
        "phone": numero,
        "message": texto
    }
    try:
        requests.post(API_URL, json=payload, timeout=10)
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