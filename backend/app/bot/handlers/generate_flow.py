from __future__ import annotations

import asyncio
import html
from uuid import uuid4

from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes

from backend.app.bot.keyboards import teclado_acoes_publicacao, teclado_imagem
from backend.app.bot.state import BotState
from backend.app.config import load_settings
from backend.app.models.brand import CampaignForm
from backend.app.services.bluesky_publisher import BlueskyPublisher
from backend.app.services.content_agent import ContentAgent
from backend.app.services.draft_store import DraftStore
from backend.app.services.image_agent import ImageAgent


def _formatar_conteudo(conteudo) -> str:
    hashtags = " ".join(conteudo.hashtags) if conteudo.hashtags else "—"
    return (
        "✨ <b>Conteúdo gerado:</b>\n\n"
        f"📝 <b>Caption:</b>\n{html.escape(conteudo.caption)}\n\n"
        f"#️⃣ <b>Hashtags:</b>\n{html.escape(hashtags)}\n\n"
        f"📣 <b>CTA:</b> {html.escape(conteudo.call_to_action)}\n\n"
        f"🎭 <b>Tom utilizado:</b> {html.escape(conteudo.tone_used)}\n\n"
        f"🖼️ <b>Alt text:</b> {html.escape(conteudo.image_alt_text)}\n\n"
        f"🎨 <b>Prompt visual:</b>\n<i>{html.escape(conteudo.image_prompt)}</i>"
    )


def _construir_form(formulario_dados: dict[str, str]) -> CampaignForm:
    return CampaignForm(
        brand_name=formulario_dados.get("brand_name", ""),
        topic=formulario_dados.get("topic", ""),
        brand_voice=formulario_dados.get("brand_voice", ""),
        target_audience=formulario_dados.get("target_audience", ""),
        objective=formulario_dados.get("objective", ""),
        extra_notes=formulario_dados.get("extra_notes", ""),
    )


async def _mostrar_acoes_finais(update: Update, com_imagem: bool) -> None:
    if com_imagem:
        texto = "🚀 A publicação está pronta. O que queres fazer?"
    else:
        texto = (
            "ℹ️ A publicação está pronta sem imagem. "
            "Podes guardá-la como rascunho ou terminar."
        )

    await update.effective_chat.send_message(
        texto,
        reply_markup=teclado_acoes_publicacao(com_imagem=com_imagem),
    )


async def gerar_conteudo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    mensagem_espera = await update.effective_chat.send_message(
        "⚙️ A gerar conteúdo... Aguarda um momento."
    )

    formulario_dados = context.user_data.get("formulario", {})
    form = _construir_form(formulario_dados)

    try:
        settings = load_settings()
        agente = ContentAgent(
            api_key=settings.gemini_api_key,
            model=settings.gemini_text_model,
        )
        conteudo = await asyncio.to_thread(agente.generate, form)
        context.user_data["conteudo_gerado"] = conteudo
        context.user_data["imagem_path"] = None

        await mensagem_espera.delete()
        await update.effective_chat.send_message(
            _formatar_conteudo(conteudo),
            parse_mode="HTML",
        )
        await update.effective_chat.send_message(
            "🖼️ Queres gerar uma imagem para esta publicação?",
            reply_markup=teclado_imagem(),
        )
        return BotState.WAITING_IMAGE_CHOICE

    except Exception as exc:
        await mensagem_espera.edit_text(
            f"❌ Não foi possível gerar o conteúdo.\n\n{exc}\n\n"
            "Usa /start para tentar novamente."
        )
        return ConversationHandler.END


async def handle_imagem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    opcao = query.data.split(":", 1)[1]

    if opcao == "sim":
        await query.edit_message_text("🖼️ Ótimo! A gerar imagem...")
        mensagem_espera = await update.effective_chat.send_message(
            "🎨 A gerar imagem... Isto pode demorar até 30 segundos."
        )

        conteudo = context.user_data.get("conteudo_gerado")
        if not conteudo:
            await mensagem_espera.edit_text(
                "❌ Conteúdo não encontrado. Usa /start para recomeçar."
            )
            return ConversationHandler.END

        try:
            settings = load_settings()
            agente_imagem = ImageAgent(
                api_key=settings.openai_api_key,
                model=settings.openai_image_model,
                output_dir=settings.image_output_dir,
                size=settings.image_size,
                quality=settings.openai_image_quality,
            )
            caminho = await asyncio.to_thread(
                agente_imagem.generate,
                conteudo.image_prompt,
                f"bot-generated-image-{uuid4().hex}.png",
            )
            context.user_data["imagem_path"] = str(caminho)
            await mensagem_espera.delete()
            with open(caminho, "rb") as ficheiro_imagem:
                await update.effective_chat.send_photo(
                    photo=ficheiro_imagem,
                    caption=f"🖼️ Imagem gerada!\n\n<i>{html.escape(conteudo.image_alt_text)}</i>",
                    parse_mode="HTML",
                )

        except Exception as exc:
            await mensagem_espera.edit_text(
                f"❌ Não foi possível gerar a imagem.\n\n{exc}\n\n"
                "Podes continuar e guardar o rascunho sem imagem."
            )
    else:
        await query.edit_message_text("⏭️ A continuar sem imagem.")

    await _mostrar_acoes_finais(
        update,
        com_imagem=bool(context.user_data.get("imagem_path")),
    )
    return BotState.WAITING_POST_ACTION


async def handle_publicar_bluesky(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    conteudo = context.user_data.get("conteudo_gerado")
    imagem_path = context.user_data.get("imagem_path")

    if not conteudo:
        context.user_data.clear()
        await query.edit_message_text(
            "❌ Não foi possível publicar: conteúdo não encontrado.\n\n"
            "Usa /start para recomeçar."
        )
        return ConversationHandler.END

    if not imagem_path:
        await query.edit_message_text(
            "❌ Gera primeiro uma imagem antes de publicar no Bluesky.\n\n"
            "Podes guardar o conteúdo como rascunho ou terminar.",
            reply_markup=teclado_acoes_publicacao(com_imagem=False),
        )
        return BotState.WAITING_POST_ACTION

    await query.edit_message_text("🚀 A publicar no Bluesky... Aguarda um momento.")

    try:
        settings = load_settings()
        publicador = BlueskyPublisher(
            handle=settings.bluesky_handle,
            app_password=settings.bluesky_app_password,
            service_url=settings.bluesky_service_url,
        )
        resultado = await asyncio.to_thread(
            publicador.publish,
            conteudo,
            imagem_path,
        )
        await query.edit_message_text(
            "✅ Publicação enviada para o Bluesky!\n\n"
            f"<code>{html.escape(resultado.uri)}</code>\n\n"
            "Usa /start para criar uma nova publicação.",
            parse_mode="HTML",
        )
        context.user_data.clear()
        return ConversationHandler.END

    except Exception as exc:
        await query.edit_message_text(
            f"❌ Não foi possível publicar no Bluesky.\n\n{exc}\n\n"
            "Podes tentar novamente, guardar o rascunho ou terminar.",
            reply_markup=teclado_acoes_publicacao(com_imagem=True),
        )
        return BotState.WAITING_POST_ACTION


async def handle_guardar_rascunho(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    conteudo = context.user_data.get("conteudo_gerado")
    formulario_dados = context.user_data.get("formulario", {})
    imagem_path = context.user_data.get("imagem_path")

    if not conteudo or not formulario_dados:
        context.user_data.clear()
        await query.edit_message_text(
            "❌ Não foi possível guardar o rascunho: dados incompletos.\n\n"
            "Usa /start para recomeçar."
        )
        return ConversationHandler.END

    form = _construir_form(formulario_dados)
    await query.edit_message_text("💾 A guardar o rascunho...")

    try:
        settings = load_settings()
        armazem = DraftStore(output_dir=settings.image_output_dir)
        caminho_rascunho = await asyncio.to_thread(
            armazem.save,
            form,
            conteudo,
            imagem_path,
        )
        await query.edit_message_text(
            f"✅ Rascunho guardado!\n\n<code>{html.escape(str(caminho_rascunho))}</code>\n\n"
            "Usa /start para criar uma nova publicação.",
            parse_mode="HTML",
        )
        context.user_data.clear()
        return ConversationHandler.END

    except Exception as exc:
        await query.edit_message_text(
            f"❌ Não foi possível guardar o rascunho.\n\n{exc}\n\n"
            "Podes tentar novamente ou terminar.",
            reply_markup=teclado_acoes_publicacao(com_imagem=bool(imagem_path)),
        )
        return BotState.WAITING_POST_ACTION


async def handle_terminar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text(
        "👌 Publicação terminada sem guardar.\n\n"
        "Usa /start para criar uma nova publicação."
    )
    return ConversationHandler.END
