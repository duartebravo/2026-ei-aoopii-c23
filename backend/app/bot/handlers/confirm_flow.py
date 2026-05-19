from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from backend.app.bot.keyboards import (
    CAMPO_LABELS,
    formatar_resumo,
    teclado_confirmacao,
    teclado_editar_campo,
    teclado_inicio,
)
from backend.app.bot.state import BotState


async def handle_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from backend.app.bot.handlers.generate_flow import gerar_conteudo

    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    return await gerar_conteudo(update, context)


async def handle_editar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✏️ Qual campo queres editar?",
        reply_markup=teclado_editar_campo(),
    )
    return BotState.WAITING_CONFIRMATION


async def handle_editar_campo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    chave = query.data.split(":", 1)[1]
    context.user_data["campo_a_editar"] = chave
    label = CAMPO_LABELS.get(chave, chave)
    await query.edit_message_text(
        f"✏️ Envia o novo valor para <b>{label}</b>:",
        parse_mode="HTML",
    )
    return BotState.EDITING_FIELD


async def handle_recomecar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text(
        "🔄 A recomeçar... Como queres começar?",
        reply_markup=teclado_inicio(),
    )
    return BotState.WAITING_URL_OR_MANUAL


async def handle_voltar_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    formulario = context.user_data.get("formulario", {})
    resumo = formatar_resumo(formulario)
    await query.edit_message_text(
        f"{resumo}\n\nRevê os campos e confirma ou edita.",
        parse_mode="HTML",
        reply_markup=teclado_confirmacao(),
    )
    return BotState.WAITING_CONFIRMATION


async def receive_edited_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chave = context.user_data.get("campo_a_editar")
    texto = update.message.text.strip()
    valor = "" if texto in {"—", "-"} else texto

    if chave:
        context.user_data.setdefault("formulario", {})[chave] = valor
        label = CAMPO_LABELS.get(chave, chave)
        await update.message.reply_text(f"✅ <b>{label}</b> atualizado.", parse_mode="HTML")

    formulario = context.user_data.get("formulario", {})
    resumo = formatar_resumo(formulario)
    await update.message.reply_text(
        f"{resumo}\n\nRevê os campos e confirma ou edita antes de gerar conteúdo.",
        parse_mode="HTML",
        reply_markup=teclado_confirmacao(),
    )
    return BotState.WAITING_CONFIRMATION
