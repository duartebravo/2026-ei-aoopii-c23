from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from backend.app.bot.keyboards import CAMPOS, formatar_resumo, teclado_confirmacao
from backend.app.bot.state import BotState

_CHAVES: list[str] = [chave for chave, _ in CAMPOS]

_PERGUNTAS: dict[str, str] = {
    "brand_name": "🏷️ Qual é o <b>nome da marca</b>?",
    "topic": (
        "🎯 Qual é o <b>tema</b> da publicação?\n"
        "<i>(ex: lançamento de produto, promoção, dica)</i>"
    ),
    "brand_voice": (
        "🗣️ Como descreves a <b>voz da marca</b>?\n"
        "<i>(ex: jovial, profissional, irreverente)</i>"
    ),
    "target_audience": (
        "👥 Quem é o <b>público-alvo</b>?\n"
        "<i>(ex: jovens 18-30 anos, profissionais de TI)</i>"
    ),
    "objective": (
        "🎯 Qual é o <b>objetivo</b> da publicação?\n"
        "<i>(ex: aumentar seguidores, promover produto)</i>"
    ),
    "extra_notes": (
        "📝 Tens alguma <b>nota adicional</b>?\n"
        "<i>(ex: mencionar desconto, evitar certos temas)\n"
        "Envia \"—\" para saltar este campo.</i>"
    ),
}


async def iniciar_manual(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data["formulario"] = {}
    context.user_data["campo_atual"] = 0

    await query.edit_message_text(
        "✍️ Vamos preencher o formulário campo a campo.\n\n" + _PERGUNTAS[_CHAVES[0]],
        parse_mode="HTML",
    )
    return BotState.WAITING_MANUAL_FIELDS


async def receive_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()
    indice = context.user_data.get("campo_atual", 0)
    chave = _CHAVES[indice]

    valor = "" if texto in {"—", "-"} else texto
    context.user_data.setdefault("formulario", {})[chave] = valor

    proximo_indice = indice + 1
    context.user_data["campo_atual"] = proximo_indice

    if proximo_indice < len(_CHAVES):
        proxima_chave = _CHAVES[proximo_indice]
        await update.message.reply_text(_PERGUNTAS[proxima_chave], parse_mode="HTML")
        return BotState.WAITING_MANUAL_FIELDS

    resumo = formatar_resumo(context.user_data["formulario"])
    await update.message.reply_text(
        f"✅ Formulário preenchido!\n\n{resumo}\n\n"
        "Revê os campos e confirma ou edita antes de gerar conteúdo.",
        parse_mode="HTML",
        reply_markup=teclado_confirmacao(),
    )
    return BotState.WAITING_CONFIRMATION
