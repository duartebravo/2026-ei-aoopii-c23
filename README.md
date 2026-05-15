# 2026-ei-aoopii-c23

Agent: Social Media Autopilot

Alunos:
- Duarte Bravo Nª31385 duartebravo@ipvc.pt
- Tomas Felicissimo Nº31375 tomasfelicissimo@ipvc.pt

## Objetivo

O projeto implementa um agente de social media que recebe um tema, voz da marca
e publico-alvo, gera uma publicacao para Instagram, agenda a publicacao, publica
automaticamente e acompanha metricas de engagement para melhorar publicacoes
futuras.

Na fase atual, o projeto ja permite preencher a campanha a partir do URL de um
negocio, gera o texto da publicacao e gera uma imagem sem texto:

```text
URL ou formulario manual -> Gemini -> formulario editavel
Formulario confirmado -> Gemini -> texto da publicacao + prompt visual -> OpenAI -> imagem
```

## Fase atual

O sistema pode analisar o URL de um negocio para preencher os dados principais
da campanha de forma automatica. O utilizador tambem pode preencher tudo
manualmente. Depois de confirmar ou editar os campos, usa Gemini para gerar o
texto da publicacao e um prompt visual, e usa OpenAI para gerar a imagem final
do post.
O texto da publicacao nao e inserido na imagem; a imagem gerada serve como visual
do post e fica guardada localmente.

Input inicial:

- URL do negocio; ou
- preenchimento manual.

Formulario da campanha:

- nome da marca;
- tema do post;
- voz da marca;
- publico-alvo;
- objetivo do post;
- notas adicionais.

Output:

- caption;
- hashtags;
- call to action;
- tom usado;
- prompt visual para gerar imagem;
- alt text da imagem;
- imagem gerada em `outputs/generated-post-image.png`.

## Estrutura

```text
backend/
  app/
    main.py
    config.py
    models/
      brand.py
      post.py
    services/
      content_agent.py
      image_agent.py
```

## Como usar

1. Criar um ficheiro `.env` com base em `.env.example`.
2. Preencher a chave do Gemini:

```env
GEMINI_API_KEY=...
GEMINI_TEXT_MODEL=gemini-2.5-flash
OPENAI_API_KEY=...
OPENAI_IMAGE_MODEL=gpt-image-2
OPENAI_IMAGE_QUALITY=medium
IMAGE_SIZE=1024x1280
```

Nota: a geracao de imagem usa creditos da OpenAI API. Para controlar custos, recomenda-se
usar `OPENAI_IMAGE_QUALITY=medium` durante testes.

Neste projeto, foi carregado um saldo inicial de 10 euros em `https://platform.openai.com`
para permitir a utilizacao do modelo `gpt-image-2` na geracao de imagens.

3. Instalar dependencias:

```bash
pip install -e .
```

4. Executar:

```bash
python -m backend.app.main
```

### Usar com pagina web local

O fluxo do terminal continua disponivel, mas tambem pode ser usado no browser:

```bash
python -m backend.app.web
```

Depois abrir:

```text
http://127.0.0.1:8000
```

A pagina permite colocar o URL de um negocio para preencher a campanha,
preencher manualmente quando nao existe URL, gerar o texto, editar o resultado,
gerar a imagem e guardar um rascunho local em `outputs/drafts/`.

## Fluxo atual

```text
web.py
  recebe um URL ou preenchimento manual
        ↓
BusinessUrlAgent
  pode preencher o formulario editavel com Gemini
        ↓
ContentAgent
  gera texto e prompt visual com Gemini
        ↓
GeneratedContent
  devolve conteudo estruturado
        ↓
ImageAgent
  gera imagem sem texto com OpenAI
```

## Proximos passos

1. Sincronizar o projeto com uma rede social.
2. Publicar automaticamente o texto e a imagem gerados.
3. Guardar os posts gerados como rascunhos antes da publicacao.
4. Adicionar agendamento de publicacoes.
5. Adicionar metricas e feedback loop para melhorar publicacoes futuras.
