from __future__ import annotations

from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes

from backend.app.bot.keyboards import teclado_inicio
from backend.app.bot.state import BotState

_BOAS_VINDAS = (
    "👋 Olá! Sou o assistente de social media autopilot.\n\n"
    "Posso ajudar-te a criar publicações para Instagram de forma rápida e eficiente.\n\n"
    "Como queres começar?"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(_BOAS_VINDAS, reply_markup=teclado_inicio())
    return BotState.WAITING_URL_OR_MANUAL


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Fluxo cancelado. Os dados temporários foram apagados.\n\n"
        "Usa /start para começar de novo."
    )
    return ConversationHandler.END
