# Evidencias de integracao com redes sociais

Data de analise: 2026-05-25

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

Bloqueios para este projeto:

- seria necessario implementar autenticacao AT Protocol;
- a imagem local teria de ser convertida/carregada como `blob`;
- as imagens tem limites proprios da plataforma, incluindo limite de tamanho;
- nao foi escolhida como rede principal porque o objetivo do projeto esta focado
  em Instagram.

Conclusao:

O Bluesky e uma alternativa tecnicamente simples para publicacao automatica e
foi escolhido como prova de conceito por permitir publicar texto e imagem local
com menos requisitos externos do que Instagram, TikTok ou LinkedIn. Ainda assim,
nao substitui o Instagram como rede social principal definida para o produto
final.

Fonte oficial:

- https://docs.bsky.app/docs/tutorials/creating-a-post