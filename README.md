# 2026-ei-aoopii-c23

Agent: Social Media Autopilot

Alunos:
- Duarte Bravo Nª31385 duartebravo@ipvc.pt
- Tomás Felicíssimo Nº31375 tomasfelicissimo@ipvc.pt

## Objetivo

O Social Media Autopilot e um MVP academico de um agente de social media para
ajudar pequenos negocios a criar publicacoes para Instagram. O projeto recolhe
informacao sobre a marca/campanha, gera texto com IA, cria um prompt visual e
pode gerar uma imagem sem texto para acompanhar a publicacao.

O objetivo final do projeto e evoluir para um agente capaz de publicar,
agendar e acompanhar metricas de engagement. Na fase atual, o foco esta na
criacao assistida de conteudo e na preparacao de rascunhos locais.

## Fase atual

Nesta fase, o sistema ja permite iniciar uma campanha de duas formas:

- inserir um URL de um negocio/campanha para preencher o formulario com Gemini;
- preencher manualmente os dados da campanha.

Depois de o formulario estar preenchido, o utilizador pode rever e editar os
campos antes de gerar o texto. A geracao de texto devolve caption, hashtags,
call to action, tom usado, alt text e prompt visual. A partir desse prompt, o
sistema pode gerar uma imagem com OpenAI. A imagem nao contem texto; serve como
visual de apoio para a publicacao.

O projeto tem atualmente tres interfaces de utilizacao:

- terminal, para testar o fluxo base;
- pagina web local, para usar o fluxo completo no browser;
- bot Telegram, para conversar com o Social Media Autopilot via `/start`.

## Input

Input inicial:

- URL do negocio/campanha; ou
- preenchimento manual.

Formulario da campanha:

- nome da marca;
- tema do post;
- voz da marca;
- publico-alvo;
- objetivo do post;
- notas adicionais.

## Output

O sistema pode produzir:

- caption para Instagram;
- hashtags;
- call to action;
- tom usado;
- prompt visual para gerar imagem;
- alt text da imagem;
- imagem gerada localmente;
- rascunho guardado em `outputs/drafts/`.

## Estrutura

```text
backend/
  app/
    main.py
    web.py
    config.py
    bot/
      bot.py
      state.py
      keyboards.py
      handlers/
        start.py
        url_flow.py
        form_flow.py
        confirm_flow.py
        generate_flow.py
    models/
      brand.py
      post.py
    services/
      business_url_agent.py
      content_agent.py
      image_agent.py
      draft_store.py
    static/
      app.css
      app.js
    templates/
      index.html
```

## Como usar

1. Criar um ficheiro `.env` com base em `.env.example`.

2. Preencher as variaveis necessarias:

```env
APP_ENV=development

GEMINI_API_KEY=...
GEMINI_TEXT_MODEL=gemini-2.5-flash

OPENAI_API_KEY=...
OPENAI_IMAGE_MODEL=gpt-image-2
OPENAI_IMAGE_QUALITY=medium
IMAGE_SIZE=1024x1280

IMAGE_OUTPUT_DIR=outputs

TELEGRAM_BOT_TOKEN=...
```

Nota: `TELEGRAM_BOT_TOKEN` so e necessario para correr o bot Telegram.

3. Instalar dependencias:

```bash
pip install -e .
```

### Usar no terminal

```bash
python -m backend.app.main
```

### Usar com pagina web local

```bash
python -m backend.app.web
```

Depois abrir:

```text
http://127.0.0.1:8000
```

Na pagina web, o utilizador pode inserir um URL, escolher "Nao tenho URL",
preencher/editar o formulario, gerar texto, gerar imagem e guardar rascunho.

### Usar com bot Telegram

```bash
python -m backend.app.bot.bot
```

No Telegram, iniciar conversa com:

```text
/start
```

O bot permite escolher entre enviar URL ou preencher manualmente. Depois mostra
um resumo editavel, gera o conteudo, pergunta se deve gerar imagem e permite
guardar o resultado como rascunho local.

## Fluxo web atual

```text
URL ou preenchimento manual
        ↓
BusinessUrlAgent
  preenche formulario editavel com Gemini
        ↓
ContentAgent
  gera texto e prompt visual com Gemini
        ↓
ImageAgent
  gera imagem sem texto com OpenAI
        ↓
DraftStore
  guarda rascunho local
```

## Fluxo do bot Telegram

```text
/start
        ↓
Escolher URL ou preenchimento manual
        ↓
Confirmar ou editar formulario
        ↓
Gerar conteudo
        ↓
Escolher se gera imagem
        ↓
Guardar ou descartar rascunho
```

## Notas

- A geracao de imagem usa creditos da OpenAI API.
- Para controlar custos, recomenda-se usar `OPENAI_IMAGE_QUALITY=medium`
  durante testes.
- O preenchimento por URL depende de o site estar publico e acessivel. Se o
  site bloquear leitura automatica, o utilizador pode preencher manualmente.
- O texto nao e inserido dentro da imagem gerada.

## Proximos passos

1. Sincronizar o projeto com uma rede social.
2. Publicar automaticamente o texto e a imagem gerados.

Foi criada uma analise separada com evidencias das APIs e dos bloqueios de
publicacao automatica em cada rede social:

- [README_REDES_SOCIAIS.md](README_REDES_SOCIAIS.md)