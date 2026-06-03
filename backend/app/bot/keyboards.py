from __future__ import annotations

import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

CAMPOS: list[tuple[str, str]] = [
    ("brand_name", "Nome da marca"),
    ("topic", "Tema"),
    ("brand_voice", "Voz da marca"),
    ("target_audience", "Público-alvo"),
    ("objective", "Objetivo"),
    ("extra_notes", "Notas adicionais"),
]

CAMPO_LABELS: dict[str, str] = {chave: label for chave, label in CAMPOS}


def formatar_resumo(formulario: dict[str, str]) -> str:
    linhas = ["📋 <b>Resumo do formulário:</b>\n"]
    for chave, label in CAMPO_LABELS.items():
        valor = formulario.get(chave) or "—"
        linhas.append(f"<b>{label}:</b> {html.escape(valor)}")
    return "\n".join(linhas)


def teclado_inicio() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌐 Enviar URL", callback_data="escolher_url"),
            InlineKeyboardButton("✍️ Preencher manualmente", callback_data="escolher_manual"),
        ]
    ])


def teclado_confirmacao() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirmar e gerar", callback_data="confirmar")],
        [InlineKeyboardButton("✏️ Editar um campo", callback_data="editar")],
        [InlineKeyboardButton("🔄 Recomeçar", callback_data="recomecar")],
    ])


def teclado_editar_campo() -> InlineKeyboardMarkup:
    botoes = [
        [InlineKeyboardButton(f"✏️ {label}", callback_data=f"editar_campo:{chave}")]
        for chave, label in CAMPOS
    ]
    botoes.append([InlineKeyboardButton("← Voltar ao resumo", callback_data="voltar_resumo")])
    return InlineKeyboardMarkup(botoes)


def teclado_imagem() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼️ Sim, gerar imagem", callback_data="gerar_imagem:sim"),
            InlineKeyboardButton("⏭️ Não, continuar", callback_data="gerar_imagem:nao"),
        ]
    ])


def teclado_acoes_publicacao(com_imagem: bool) -> InlineKeyboardMarkup:
    botoes = []
    if com_imagem:
        botoes.append([
            InlineKeyboardButton("🚀 Publicar no Bluesky", callback_data="publicar_bluesky")
        ])
    botoes.extend([
        [InlineKeyboardButton("💾 Guardar rascunho", callback_data="guardar_rascunho")],
        [InlineKeyboardButton("❌ Terminar", callback_data="terminar")],
    ])
    return InlineKeyboardMarkup(botoes)
