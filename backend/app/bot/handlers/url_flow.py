from __future__ import annotations

import asyncio
import re

from telegram import Update
from telegram.ext import ContextTypes

from backend.app.bot.keyboards import formatar_resumo, teclado_confirmacao
from backend.app.bot.state import BotState
from backend.app.config import load_settings
from backend.app.services.business_url_agent import BusinessUrlAgent

_PADRAO_URL = re.compile(r"^(https?://|www\.|[a-z0-9-]+\.[a-z]{2,})", re.IGNORECASE)


def _parece_url(texto: str) -> bool:
    return bool(_PADRAO_URL.match(texto.strip()))


async def solicitar_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🌐 Envia o URL do site do teu negócio e eu preencho o formulário automaticamente.\n\n"
        "Exemplo: https://www.exemplo.pt"
    )
    return BotState.WAITING_URL_OR_MANUAL


async def receive_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()

    if not _parece_url(texto):
        await update.message.reply_text(
            "⚠️ Isso não parece ser um URL válido.\n\n"
            "Envia um URL completo (ex: https://www.exemplo.pt) ou usa /start para escolher "
            "outra opção."
        )
        return BotState.WAITING_URL_OR_MANUAL

    mensagem_espera = await update.message.reply_text(
        "⏳ A analisar o URL... Isto pode demorar alguns segundos."
    )

    try:
        settings = load_settings()
        agente = BusinessUrlAgent(
            api_key=settings.gemini_api_key,
            model=settings.gemini_text_model,
        )
        sugestao = await asyncio.to_thread(agente.generate, texto)
        formulario_obj = sugestao.to_campaign_form()

        context.user_data["formulario"] = {
            "brand_name": formulario_obj.brand_name,
            "topic": formulario_obj.topic,
            "brand_voice": formulario_obj.brand_voice,
            "target_audience": formulario_obj.target_audience,
            "objective": formulario_obj.objective,
            "extra_notes": formulario_obj.extra_notes,
        }

        resumo = formatar_resumo(context.user_data["formulario"])
        await mensagem_espera.edit_text(
            f"✅ Formulário preenchido com base no URL!\n\n{resumo}\n\n"
            "Revê os campos e confirma ou edita antes de gerar conteúdo.",
            parse_mode="HTML",
            reply_markup=teclado_confirmacao(),
        )
        return BotState.WAITING_CONFIRMATION

    except Exception as exc:
        await mensagem_espera.edit_text(
            f"❌ Não foi possível analisar o URL.\n\n{exc}\n\n"
            "Tenta de novo ou usa /start para preencher manualmente."
        )
        return BotState.WAITING_URL_OR_MANUAL
