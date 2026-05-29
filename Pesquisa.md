# Evidencias de integracao com redes sociais

Este documento justifica os proximos passos do projeto:

1. Sincronizar o projeto com uma rede social.
2. Publicar automaticamente o texto e a imagem gerados.

O objetivo nao foi provar que as redes sociais nao suportam publicacao por API.
Pelo contrario: varias redes suportam publicacao automatica, mas exigem contas,
tokens, permissoes, revisao de aplicacao, alojamento publico dos ficheiros ou
configuracoes externas que nao podem ser fornecidas diretamente pelo repositorio.

## Estado atual do projeto

O Social Media Autopilot ja gera os dados necessarios para preparar uma
publicacao:

- `caption`;
- `hashtags`;
- `call_to_action`;
- `image_alt_text`;
- imagem gerada localmente;
- publicacao automatica no Bluesky como prova de conceito;
- rascunho guardado em `outputs/drafts/`.

Estes dados sao suficientes para construir o corpo de uma publicacao. O bloqueio
principal esta na ligacao externa a cada plataforma.

## Instagram

O Instagram foi definido como rede social principal do projeto.

A API oficial da Meta para publicacao de conteudo permite publicar media em
contas profissionais atraves de um fluxo em dois passos:

1. criar um container de media;
2. publicar esse container.

O projeto ja gera os dados necessarios para essa integracao:

- legenda (`caption`);
- hashtags;
- chamada para acao (`call_to_action`);
- texto alternativo (`image_alt_text`);
- imagem gerada.

Bloqueios encontrados:

- a imagem gerada fica guardada localmente e a API precisa de aceder ao ficheiro
  atraves de um URL publico;
- a publicacao exige uma conta Instagram profissional;
- sao necessarias credenciais OAuth e permissoes da app Meta, incluindo permissao
  de publicacao de conteudo;
- para uso fora de testes, a app Meta pode precisar de revisao/aprovacao.

Conclusao:

A integracao com Instagram esta preparada ao nivel dos dados gerados pelo MVP,
mas a publicacao automatica ficou como proximo passo devido aos requisitos de
autenticacao, permissoes, conta profissional e alojamento publico da imagem.

Fonte oficial:

- https://developers.facebook.com/docs/instagram-platform/content-publishing/

## X

A API do X permite criar posts atraves do endpoint `POST /2/tweets`, usando um
token OAuth 2.0 do utilizador autenticado. O corpo do pedido inclui o campo
`text` e tambem permite associar media previamente carregado.

Bloqueios para este projeto:

- e necessario criar/configurar uma app no portal de developers do X;
- e necessario obter autorizacao OAuth com permissoes de escrita;
- a imagem teria de ser carregada previamente pela API de media e depois
  associada ao post;
- o X nao foi escolhido como rede principal do MVP, que esta orientado para
  conteudo visual de Instagram.

Conclusao:

A publicacao automatica no X e tecnicamente possivel, mas exigiria uma
integracao OAuth propria e um fluxo adicional de upload de media.

Fonte oficial:

- https://docs.x.com/x-api/posts/create-post

## Bluesky

O Bluesky permite criar posts atraves do protocolo AT Protocol. Um post e um
registo `app.bsky.feed.post` com texto e data de criacao. Para imagens, o
ficheiro e carregado primeiro como `blob` e depois referenciado no post.

Estado no projeto:

- a publicacao automatica no Bluesky foi implementada na pagina web;
- o utilizador gera o texto e a imagem no fluxo normal do projeto;
- depois de existir imagem gerada, o botao "Publicar no Bluesky" fica ativo;
- o frontend chama o endpoint `/api/publish-bluesky`;
- o backend usa o servico `BlueskyPublisher` para autenticar e publicar;
- a autenticacao usa `BLUESKY_HANDLE` e `BLUESKY_APP_PASSWORD`;
- a imagem local e preparada/comprimida, enviada para o Bluesky e associada ao
  post;
- o texto publicado junta caption, call to action e hashtags.

Requisitos de configuracao:

- conta Bluesky;
- app password criada nas definicoes da conta Bluesky;
- variaveis no ficheiro `.env`:

```env
BLUESKY_HANDLE=exemplo.bsky.social
BLUESKY_APP_PASSWORD=...
BLUESKY_SERVICE_URL=https://bsky.social
```

Limites encontrados:

- o Bluesky tem limite de caracteres por post;
- como o conteudo gerado foi pensado originalmente para Instagram, captions
  longas podem ultrapassar esse limite;
- neste MVP, a publicacao no Bluesky e feita como um unico post, por isso o
  texto e encurtado automaticamente quando necessario;
- a imagem tem limites proprios de tamanho, por isso o projeto usa Pillow para
  preparar/comprimir a imagem antes do envio.

Conclusao:

O Bluesky deixou de estar apenas analisado e passou a estar integrado como prova
de conceito funcional na interface web. Foi escolhido porque permite publicar
texto e imagem local com menos requisitos externos do que Instagram, TikTok ou
LinkedIn: nao exige URL publico para a imagem, conta profissional, revisao da
app ou permissoes complexas.
Fontes oficiais:

- https://docs.bsky.app/docs/tutorials/creating-a-post
- https://docs.bsky.app/docs/advanced-guides/posts
