from telegram import Bot
import os

TOKEN = "8360009816:AAHioAjWLjp4yfyiLi1ry1pvmLYb40Qa9s0"
CHAT_ID = "@marcussarmanho"

bot = Bot(token=TOKEN)

def enviar_alerta(titulo, preco, loja, link):
    mensagem = f"🔥 PROMOÇÃO!\nProduto: {titulo}\nPreço: {preco}\nLoja: {loja}\nLink: {link}"
    bot.send_message(chat_id=CHAT_ID, text=mensagem)
