# 2026-ei-aoopii-c23

Agent: Social Media Autopilot

Alunos:
- Duarte Bravo Nª31385 duartebravo@ipvc.pt
- Tomas Felicissimo Nº31375 tomasfelicissimo@ipvc.pt

## Objetivo

O projeto implementa um agente de social media que recebe um tema, voz da marca e publico-alvo, gera uma publicacao para Instagram, agenda a publicacao, publica automaticamente e acompanha metricas de engagement para melhorar publicacoes futuras.

Nesta fase inicial, o foco e apenas o primeiro passo do sistema:

```text
Formulario do utilizador -> Gemini -> texto da publicacao
```

## Fase 1

Input:

- nome da marca;
- tema do post;
- voz da marca;
- publico-alvo;
- objetivo do post;
- notas adicionais.

Output:

- caption;
- hashtags;
- texto curto para imagem futura;
- call to action;
- tom usado.

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
```

## Como usar

1. Criar um ficheiro `.env` com base em `.env.example`.
2. Preencher a chave do Gemini:

```env
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-pro
```

3. Instalar dependencias:

```bash
pip install -e .
```

4. Executar:

```bash
python -m backend.app.main
```

## Fluxo da fase 1

```text
main.py
  recolhe o formulario
        ↓
ContentAgent
  envia o pedido para o Gemini
        ↓
GeneratedContent
  devolve conteudo estruturado
```

## Proximos passos

1. Melhorar o formulario se forem necessarios mais campos.
2. Guardar os posts gerados como rascunhos.
3. Criar geracao de imagem.
4. Integrar publicacao na Meta Instagram API.
5. Adicionar metricas e feedback loop.
