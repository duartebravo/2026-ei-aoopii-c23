# Custos de geracao de imagens por IA

## Justificacao da escolha do OpenAI `gpt-image-2`

O `gpt-image-2` foi escolhido porque oferece o melhor equilibrio para este MVP:
qualidade visual alta, controlo de custo por nivel de qualidade, tamanhos
flexiveis e integracao direta com o fluxo Python/OpenAI ja usado pelo projeto.
Como o objetivo e gerar uma imagem final para acompanhar uma publicacao em redes
sociais, a prioridade nao e apenas o menor preco absoluto por imagem, mas sim a
relacao entre custo, qualidade, consistencia visual e facilidade de integracao.

A OpenAI apresenta o `gpt-image-2` como o seu modelo de geracao de imagem mais
avancado, com desempenho classificado como "Highest", suporte a geracao e
edicao, tamanhos flexiveis e processamento de imagens de entrada em alta
fidelidade. Isto torna o modelo superior para este caso de uso porque permite
gerar imagens com melhor qualidade final e maior controlo sobre a relacao entre
preco e resultado. A qualidade `medium`, usada atualmente no projeto, fica num
ponto intermedio: e mais cara do que alternativas muito baratas como Stable
Image Core ou Imagen 4 Fast, mas e mais barata do que opcoes como Nano Banana 2
em 1K e Nano Banana Pro, mantendo um nivel de qualidade mais adequado para
conteudo visual de marca.

As alternativas continuam relevantes:

- Gemini/Nano Banana e forte em rapidez, volume e fluxos conversacionais;
- Imagen 4 e competitivo em custo por imagem;
- Stability AI tem opcoes muito baratas para geracao simples.

Mesmo assim, para este projeto, `gpt-image-2` e a escolha mais equilibrada
porque combina qualidade, controlo de qualidade (`low`, `medium`, `high`),
formatos flexiveis e menor esforco de integracao com o backend existente.

Valores consultados em 2026-06-03. Os custos estao em USD e referem-se a uso
por API no plano pago, sem impostos. O projeto esta configurado para usar
`OPENAI_IMAGE_MODEL=gpt-image-2`, `OPENAI_IMAGE_QUALITY=medium` e
`IMAGE_SIZE=1024x1280`; como esse tamanho nao aparece diretamente em todas as
tabelas oficiais, os valores abaixo usam referencias de 1024x1024 ou 1K quando
necessario. O custo final pode incluir tambem tokens de texto de entrada e,
em edicoes, tokens de imagens de referencia.

| Fornecedor / modelo | Qualidade ou referencia | Custo aproximado por imagem | Observacoes |
| --- | --- | ---: | --- |
| OpenAI `gpt-image-2` | Low, 1024x1024 | $0.006 | Modelo usado pelo projeto; para 1024x1536/1536x1024 a referencia oficial e $0.005. |
| OpenAI `gpt-image-2` | Medium, 1024x1024 | $0.053 | Qualidade configurada atualmente no projeto; para 1024x1536/1536x1024 a referencia oficial e $0.041. |
| OpenAI `gpt-image-2` | High, 1024x1024 | $0.211 | Para 1024x1536/1536x1024 a referencia oficial e $0.165. |
| Google Nano Banana 2 / `gemini-3.1-flash-image` | 1K, 1024x1024 | $0.067 | Alternativa Gemini mais eficiente; tambem ha 0.5K a $0.045, 2K a $0.101 e 4K a $0.151. |
| Google Nano Banana Pro / `gemini-3-pro-image` | 1K/2K | $0.134 | Modelo Gemini orientado para assets profissionais; 4K custa $0.24. |
| Google Nano Banana / `gemini-2.5-flash-image` | Ate 1024x1024 | $0.039 | Modelo anterior focado em rapidez e volume; cada imagem ate 1024x1024 consome 1290 tokens. |
| Google Imagen 4 Fast | Por imagem | $0.02 | Alternativa Google de baixo custo. |
| Google Imagen 4 Standard | Por imagem | $0.04 | Alternativa Google equilibrada. |
| Google Imagen 4 Ultra | Por imagem | $0.06 | Alternativa Google com maior qualidade na familia Imagen 4. |
| Stability AI Stable Image Core | 3 creditos | $0.03 | 1 credito equivale a $0.01. |
| Stability AI Stable Image Ultra | 8 creditos | $0.08 | Opcao Stability AI de maior qualidade. |

Fontes oficiais:

- https://developers.openai.com/api/docs/guides/image-generation
- https://developers.openai.com/api/docs/pricing
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/image-generation
- https://platform.stability.ai/pricing

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
- `caption_bluesky`;
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

O Bluesky foi a rede escolhida para a prova de conceito de publicacao automatica
porque a sua API permite publicar texto e imagem sem exigir uma conta
profissional, revisao de aplicacao ou alojamento publico previo da imagem. Ao
contrario do Instagram, onde a imagem precisa de estar acessivel por URL publico
antes da publicacao, o Bluesky permite carregar o ficheiro diretamente para o
servidor atraves do AT Protocol.

Do ponto de vista tecnico, o Bluesky funciona sobre o AT Protocol. Um post e um
record do tipo `app.bsky.feed.post`, com pelo menos os campos `text` e
`createdAt`. Quando existe imagem, o ficheiro nao e enviado dentro do JSON do
post; primeiro e carregado como `blob` atraves de `com.atproto.repo.uploadBlob`
e depois esse `blob` fica referenciado no embed `app.bsky.embed.images`. Este
modelo encaixa bem no projeto, porque a imagem gerada pela OpenAI ja existe
localmente em `outputs/` e pode ser lida pelo backend antes do envio.

### O que foi implementado

A integracao deixou de ser apenas teorica e passou a estar funcional em dois
fluxos do MVP:

- interface web;
- bot Telegram.

Na interface web, o utilizador preenche o formulario, gera o conteudo, gera a
imagem e so depois fica disponivel a acao de publicar. O botao "Publicar no
Bluesky" chama o endpoint interno `/api/publish-bluesky`, enviando o objeto
`GeneratedContent` e o caminho da imagem gerada. Antes da publicacao, o backend
valida que o caminho da imagem fica dentro da pasta de outputs do projeto, para
evitar publicar ficheiros arbitrarios fora dessa area.

No bot Telegram, o fluxo e semelhante: depois de gerar o texto e a imagem, o
utilizador pode escolher "Publicar no Bluesky". O handler do bot nao publica
diretamente; reutiliza o mesmo servico `BlueskyPublisher`, garantindo que a
logica de autenticacao, validacao do texto, preparacao da imagem e envio e a
mesma nos dois canais.

O servico `BlueskyPublisher` e o ponto central da integracao:

- recebe `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` e `BLUESKY_SERVICE_URL`;
- cria um cliente `atproto.Client`;
- autentica no servico configurado, por omissao `https://bsky.social`;
- constroi o texto final a partir de `content.caption_bluesky`;
- valida se a caption esta vazia ou acima do limite local;
- prepara a imagem local antes de enviar;
- publica com `client.send_image(...)`;
- devolve `uri`, `cid` e texto publicado.

Este desenho evita duplicacao: a web e o Telegram sao interfaces diferentes,
mas a publicacao real passa sempre pelo mesmo publicador.

### Texto publicado

O projeto nao reutiliza diretamente a caption no Bluesky. Em vez
disso, o agente de conteudo gera o campo `caption_bluesky`, uma versao escrita
de raiz para a plataforma. Esta escolha e importante porque o Bluesky tem uma
logica de consumo mais curta e conversacional do que uma legenda tipica de
Instagram.

No prompt do `ContentAgent`, o Gemini recebe regras especificas para este campo:

- escrever em portugues de Portugal;
- criar uma caption propria para Bluesky;
- limitar o texto a 300 caracteres;
- incluir uma chamada para acao;
- usar entre uma e tres hashtags;
- manter frases completas;
- nao inventar dados, estatisticas ou promessas falsas.

O modelo `GeneratedContent` tambem reforca este limite com
`caption_bluesky: str = Field(max_length=300)`. Isto significa que a resposta
estruturada do Gemini ja deve chegar ao backend com uma caption curta. Alem
disso, o frontend tem `maxlength="300"` no campo "Caption para Bluesky", e o
`BlueskyPublisher` faz uma ultima validacao antes do envio.

### Limites encontrados

O limite oficial do record `app.bsky.feed.post` e mais especifico do que "300
caracteres": o campo `text` aceita ate 300 grafemas e ate 3000 bytes. Na pratica,
para texto normal em portugues, isto corresponde ao limite que o projeto trata
como 300 caracteres. A diferenca so se torna relevante em casos com emojis
compostos, combinacoes Unicode ou texto muito especial, porque um grafema visual
pode ocupar varios code points ou varios bytes.

Depois de analisar o codigo, a conclusao e que o limite de texto nao esta a ser
ultrapassado no fluxo normal do projeto. Pelo contrario, ele e controlado em
quatro camadas:

- prompt do Gemini: pede `caption_bluesky` com no maximo 300 caracteres;
- schema Pydantic: `GeneratedContent.caption_bluesky` tem `max_length=300`;
- interface web: o textarea tem `maxlength="300"`;
- publicador: `_build_post_text()` rejeita textos com `len(text) > 300`.

Esta validacao local e conservadora. Ela protege o MVP de tentar publicar uma
caption longa, mas nao implementa uma contagem perfeita de grafemas como a
definicao oficial do AT Protocol. Para o uso atual, com texto curto em portugues
e poucas hashtags, isso e suficiente. Se o projeto evoluir para muitos emojis,
links complexos, mencoes ou threads, o ideal sera acrescentar uma validacao de
grafemas/bytes mais alinhada com o lexicon oficial.

Quanto a imagens, a documentacao oficial consultada indica que um post pode ter
ate quatro imagens, cada uma com alt text. A documentacao tambem mostra que as
imagens sao carregadas como blobs e depois referenciadas no post. Neste projeto,
o MVP publica apenas uma imagem por post. O codigo define
`BLUESKY_IMAGE_LIMIT_BYTES = 2_000_000` e usa Pillow para tentar comprimir a
imagem caso seja maior:

- abre a imagem gerada localmente;
- converte imagens com transparencia para RGB com fundo branco;
- tenta manter ou reduzir o lado maximo da imagem;
- guarda como JPEG com qualidades decrescentes;
- devolve a primeira versao abaixo do limite;
- se nao conseguir, bloqueia a publicacao com erro claro.

Existe uma diferenca a registar nas fontes oficiais: o tutorial "Creating a
post" refere 2 MB por imagem, enquanto o guia avancado "Posts" ainda refere
1,000,000 bytes. O projeto esta alinhado com o valor de 2 MB e, se a API rejeitar
alguma imagem no futuro, o erro sera apanhado pelo `BlueskyPublisher`.

### Requisitos de configuracao

Para publicar no Bluesky, o projeto precisa de:

- conta Bluesky;
- app password criada nas definicoes da conta;
- variaveis no ficheiro `.env`:

```env
BLUESKY_HANDLE=exemplo.bsky.social
BLUESKY_APP_PASSWORD=...
BLUESKY_SERVICE_URL=https://bsky.social
```

### Porque Bluesky foi mais viavel no MVP

O Bluesky foi mais simples de integrar do que outras redes analisadas porque:

- aceita publicacao automatica de posts por API;
- permite upload direto da imagem local como blob;
- nao exige URL publico da imagem;
- nao exige conta profissional;
- nao exige revisao de aplicacao para uma prova de conceito local;
- permite usar uma app password em vez de implementar um fluxo OAuth completo;
- tem SDK Python disponivel atraves da biblioteca `atproto`;
- devolve identificadores claros da publicacao (`uri` e `cid`).

Isto tornou o Bluesky adequado para demonstrar o objetivo principal do projeto:
gerar texto e imagem automaticamente e publicar ambos numa rede social real a
partir da aplicacao.

### Limitacoes que ainda ficam

O Bluesky deixou de estar apenas analisado e passou a estar integrado como prova
de conceito funcional, mas ainda ha melhorias possiveis:

- a publicacao e feita como post unico; nao existe criacao automatica de threads;
- o projeto nao implementa manualmente facets para links, mencoes ou hashtags;
- a validacao local usa contagem simples de caracteres, nao uma biblioteca de
  grafemas;
- o fluxo web e Telegram exigem imagem antes de publicar, embora o publicador
  suporte tambem texto sem imagem;
- a compressao da imagem resolve o limite de tamanho, mas pode reduzir qualidade
  visual em imagens muito grandes;
- nao ha ainda testes automatizados que simulem respostas reais da API do
  Bluesky.

Conclusao:

A integracao com Bluesky esta funcional e representa a prova mais completa de
publicacao automatica do MVP. O codigo confirma que os limites de caracteres nao
estao a ser ignorados: a caption curta e gerada, validada no schema, limitada na
interface e verificada antes do envio. A principal ressalva tecnica e que o
limite oficial e de grafemas e bytes, enquanto o projeto usa uma validacao
simplificada de 300 caracteres. Para o estado atual do projeto, isso e adequado;
para producao, a melhoria natural seria contar grafemas/bytes de acordo com o
lexicon `app.bsky.feed.post` e, se necessario, criar threads automaticamente
quando o texto ultrapassar o limite de um post.

Fontes oficiais:

- https://docs.bsky.app/docs/tutorials/creating-a-post
- https://docs.bsky.app/docs/advanced-guides/posts
- https://docs.bsky.app/docs/advanced-guides/api-directory
- https://docs.bsky.app/docs/advanced-guides/rate-limits
- https://atproto.com/guides/images-and-video
- https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/feed/post.json
- https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/embed/images.json
