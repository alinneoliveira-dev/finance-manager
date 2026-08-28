import os
import re
import logging
from pathlib import Path
from datetime import date

import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ["ALLOWED_TELEGRAM_USER_ID"])
API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

PADRAO_LANCAMENTO = re.compile(r"^\s*(\+)?\s*(\d+(?:[.,]\d{1,2})?)\s+(.+?)\s*$")

lancamentos_pendentes = {}


def usuario_autorizado(update: Update) -> bool:
    return update.effective_user is not None and update.effective_user.id == ALLOWED_USER_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not usuario_autorizado(update):
        return
    await update.message.reply_text(
        "Oi! Me manda um lançamento assim:\n\n"
        "`45.90 mercado` → registra como *saída*\n"
        "`+3000 salário` → registra como *entrada* (repare no +)\n\n"
        "Use vírgula ou ponto no valor.",
        parse_mode="Markdown",
    )


async def receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not usuario_autorizado(update):
        logger.warning(
            "Mensagem ignorada de usuário não autorizado: %s",
            update.effective_user.id if update.effective_user else "desconhecido",
        )
        return

    texto = update.message.text or ""
    match = PADRAO_LANCAMENTO.match(texto)

    if not match:
        await update.message.reply_text(
            "Não entendi. Manda assim: `45.90 mercado`", parse_mode="Markdown"
        )
        return

    sinal_mais, valor_str, descricao = match.groups()
    valor = float(valor_str.replace(",", "."))
    tipo = "entrada" if sinal_mais else "saida"

    try:
        resposta = requests.get(
            f"{API_URL}/api/categorias", params={"tipo": tipo}, timeout=5
        )
        resposta.raise_for_status()
        categorias = resposta.json()
    except requests.RequestException as e:
        logger.error("Erro ao buscar categorias: %s", e)
        await update.message.reply_text(
            "Não consegui falar com o sistema agora. Confira se o Flask está rodando."
        )
        return

    if not categorias:
        await update.message.reply_text(
            f"Você ainda não tem categorias de {tipo} cadastradas no sistema."
        )
        return

    lancamentos_pendentes[update.effective_user.id] = {
        "valor": valor,
        "descricao": descricao,
        "tipo": tipo,
    }

    rotulo = "Entrada" if tipo == "entrada" else "Saída"
    botoes = [
        [InlineKeyboardButton(cat["nome"], callback_data=f"cat:{cat['id']}")]
        for cat in categorias
    ]
    await update.message.reply_text(
        f"{rotulo}: R$ {valor:.2f} — {descricao}\nEm qual categoria?",
        reply_markup=InlineKeyboardMarkup(botoes),
    )


async def escolher_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not usuario_autorizado(update):
        return

    usuario_id = update.effective_user.id
    pendente = lancamentos_pendentes.get(usuario_id)

    if not pendente:
        await query.edit_message_text("Esse lançamento expirou, manda de novo.")
        return

    categoria_id = int(query.data.split(":")[1])

    try:
        resposta = requests.post(
            f"{API_URL}/api/transacoes",
            json={
                "descricao": pendente["descricao"],
                "valor": pendente["valor"],
                "tipo": pendente["tipo"],
                "categoria_id": categoria_id,
                "data_transacao": date.today().isoformat(),
            },
            timeout=5,
        )
        resposta.raise_for_status()
    except requests.RequestException as e:
        logger.error("Erro ao registrar transação: %s", e)
        detalhe = ""
        if e.response is not None:
            detalhe = f" ({e.response.text[:200]})"
        await query.edit_message_text(f"Não consegui salvar a despesa.{detalhe}")
        return

    lancamentos_pendentes.pop(usuario_id, None)
    rotulo = "Entrada" if pendente["tipo"] == "entrada" else "Saída"
    await query.edit_message_text(
        f"✅ {rotulo} registrada: R$ {pendente['valor']:.2f} — {pendente['descricao']}"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_mensagem))
    app.add_handler(CallbackQueryHandler(escolher_categoria))

    logger.info("Bot iniciado, escutando mensagens via long polling...")
    app.run_polling()


if __name__ == "__main__":
    main()