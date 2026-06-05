from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from backend.app.bot.handlers.confirm_flow import (
    handle_confirmar,
    handle_editar,
    handle_editar_campo,
    handle_recomecar,
    handle_voltar_resumo,
    receive_edited_field,
)
from backend.app.bot.handlers.form_flow import iniciar_manual, receive_field
from backend.app.bot.handlers.generate_flow import (
    handle_guardar_rascunho,
    handle_imagem,
    handle_publicar_bluesky,
    handle_publicar_instagram,
    handle_terminar,
)
from backend.app.bot.handlers.start import cancel_command, start_command
from backend.app.bot.handlers.url_flow import receive_url, solicitar_url
from backend.app.bot.state import BotState
from backend.app.config import load_settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def _mensagem_inesperada(update: Update, _context) -> None:
    await update.message.reply_text(
        "⚠️ Não esperava uma mensagem aqui.\n\n"
        "Usa /start para começar ou /cancel para cancelar o fluxo atual."
    )


def _criar_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            BotState.WAITING_URL_OR_MANUAL: [
                CallbackQueryHandler(solicitar_url, pattern="^escolher_url$"),
                CallbackQueryHandler(iniciar_manual, pattern="^escolher_manual$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_url),
            ],
            BotState.WAITING_MANUAL_FIELDS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_field),
            ],
            BotState.WAITING_CONFIRMATION: [
                CallbackQueryHandler(handle_confirmar, pattern="^confirmar$"),
                CallbackQueryHandler(handle_editar, pattern="^editar$"),
                CallbackQueryHandler(handle_editar_campo, pattern="^editar_campo:"),
                CallbackQueryHandler(handle_recomecar, pattern="^recomecar$"),
                CallbackQueryHandler(handle_voltar_resumo, pattern="^voltar_resumo$"),
            ],
            BotState.EDITING_FIELD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_edited_field),
                CallbackQueryHandler(handle_voltar_resumo, pattern="^voltar_resumo$"),
            ],
            BotState.GENERATING_CONTENT: [],
            BotState.WAITING_IMAGE_CHOICE: [
                CallbackQueryHandler(handle_imagem, pattern="^gerar_imagem:"),
            ],
            BotState.WAITING_POST_ACTION: [
                CallbackQueryHandler(handle_publicar_bluesky, pattern="^publicar_bluesky$"),
                CallbackQueryHandler(handle_publicar_instagram, pattern="^publicar_instagram$"),
                CallbackQueryHandler(handle_guardar_rascunho, pattern="^guardar_rascunho$"),
                CallbackQueryHandler(handle_terminar, pattern="^terminar$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command),
            CommandHandler("start", start_command),
        ],
        allow_reentry=True,
    )


def main() -> None:
    settings = load_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN em falta. "
            "Confirma que o ficheiro .env contém o token do bot."
        )

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(_criar_conversation_handler())
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _mensagem_inesperada))

    logger.info("Bot iniciado com polling. A aguardar mensagens...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
