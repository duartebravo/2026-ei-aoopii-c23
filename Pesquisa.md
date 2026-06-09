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
- publicacao automatica no Instagram;
- publicacao automatica no Bluesky como prova de conceito;
- rascunho guardado em `outputs/drafts/`.

Estes dados sao suficientes para construir o corpo de uma publicacao. O bloqueio
principal deixou de ser a geracao do conteudo e passou a ser a ligacao externa a
cada plataforma: em Instagram e Bluesky essa ligacao ja foi implementada; em X e
LinkedIn ficou apenas pesquisada.

## Instagram

O Instagram foi definido como rede social principal do projeto porque e a rede
mais alinhada com o objetivo do MVP: gerar uma publicacao visual, com caption,
call to action, hashtags e imagem de apoio. A pesquisa inicial tinha identificado
que a publicacao automatica dependia de requisitos externos da Meta, sobretudo
credenciais, conta profissional e URL publico para a imagem. Depois da evolucao
do projeto, estes pontos deixaram de ser apenas teoricos: a publicacao no
Instagram ja esta implementada na interface web e no bot Telegram.

### Pesquisa oficial da API

A Instagram Platform API permite publicar conteudo em contas profissionais. Para
publicar uma imagem no feed, a Meta usa um fluxo de container:

1. criar um container de media no endpoint `/media`;
2. fornecer um `image_url` publico e a caption;
3. receber o ID do container;
4. publicar esse container no endpoint `/media_publish` com `creation_id`;
5. receber o ID final da media publicada.

Este fluxo existe porque a API da Meta nao recebe a imagem local diretamente no
pedido de publicacao de imagem. A documentacao explica que a Meta faz um cURL ao
URL enviado em `image_url`; por isso, a imagem tem de estar acessivel num
servidor publico no momento da publicacao. Um ficheiro em `localhost` ou apenas
guardado no disco do projeto nao e suficiente.

Para o fluxo usado pelo projeto, a documentacao atual indica:

- a conta tem de ser uma conta profissional do Instagram;
- o login usado e Business Login for Instagram;
- o host usado no projeto e `graph.instagram.com`;
- e necessario um Instagram User access token;
- sao necessarias permissoes como `instagram_business_basic` e
  `instagram_business_content_publish`;
- a app pode usar Standard Access para contas que o programador controla ou
  Advanced Access para contas externas;
- a media precisa de estar num URL publico;
- a imagem de feed deve ser JPEG;
- imagens de feed devem respeitar proporcao entre 4:5 e 1.91:1;
- a caption pode ter ate 2200 caracteres, 30 hashtags e 20 mencoes;
- o limite de publicacao por API e de 100 posts num periodo movel de 24 horas;
- os containers podem expirar, por isso devem ser publicados pouco depois de
  criados.

### O que foi implementado

A integracao com Instagram passou a estar funcional em dois fluxos:

- interface web;
- bot Telegram.

Na interface web, o botao "Publicar no Instagram" fica disponivel depois de
existir conteudo e imagem gerada. O frontend chama o endpoint interno
`/api/publish-instagram`, enviando o `GeneratedContent` e o caminho local da
imagem. O backend resolve esse caminho dentro da pasta `outputs/`, impedindo que
seja usado um ficheiro arbitrario fora da area gerida pelo projeto.

No bot Telegram, a acao "Publicar no Instagram" usa o mesmo servico
`InstagramPublisher`. Isto e importante porque a logica de validacao, preparacao
da imagem, upload publico e chamada a API da Meta fica centralizada num unico
ponto, em vez de estar duplicada entre a web e o bot.

O servico `InstagramPublisher` executa o fluxo principal:

- verifica `INSTAGRAM_ACCOUNT_ID` e `INSTAGRAM_ACCESS_TOKEN`;
- recebe a configuracao de URL publico e o uploader de imagem;
- valida que existe imagem local antes de publicar;
- constroi a caption final;
- prepara a imagem para o formato exigido;
- cria um URL publico para a imagem;
- cria o container de media no endpoint `/media`;
- publica o container no endpoint `/media_publish`;
- devolve `media_id`, `container_id`, texto publicado e `image_url`.

### Texto publicado

O Instagram usa a caption principal gerada pelo agente, nao a
`caption_bluesky`. O publicador constroi o texto final juntando:

- `content.caption`;
- `content.call_to_action`;
- `content.hashtags`.

As hashtags sao normalizadas antes do envio: se uma hashtag vier sem `#`, o
codigo acrescenta automaticamente o prefixo. O resultado final e validado contra
`INSTAGRAM_CAPTION_LIMIT = 2_200`. Se o texto ultrapassar esse limite, a
publicacao e bloqueada antes de contactar a API.

Isto esta alinhado com o limite oficial de caption do Instagram. A documentacao
tambem refere limites de 30 hashtags e 20 mencoes. O projeto nao faz uma
contagem local especifica destes dois limites, mas o prompt do `ContentAgent`
pede entre 3 e 8 hashtags e nao incentiva mencoes. Assim, para o uso normal do
MVP, o risco de ultrapassar estes limites e baixo.

### Preparacao da imagem

O Instagram e mais restritivo do que o Bluesky no tratamento de imagens, porque
a API espera media acessivel publicamente e com requisitos proprios de formato.
O projeto resolveu isto em duas etapas: preparar o ficheiro local e depois
disponibiliza-lo num URL publico.

Na preparacao local, o `InstagramPublisher`:

- confirma que o caminho da imagem existe;
- confirma que a imagem esta dentro da pasta `outputs/`;
- abre o ficheiro com Pillow;
- converte imagens com transparencia para RGB com fundo branco;
- valida a proporcao entre 4:5 e 1.91:1;
- grava uma versao JPEG em `outputs/instagram/`;
- usa qualidade JPEG 92 com `optimize=True`.

Esta conversao e importante porque a documentacao da Meta indica JPEG como o
formato suportado para imagens de feed. A validacao de proporcao tambem esta
alinhada com o intervalo oficial. Como o projeto gera por omissao imagens
`1024x1280`, a proporcao e 4:5, que fica no limite aceite pelo Instagram.

Depois de preparar o JPEG, o projeto precisa de transformar esse ficheiro num
URL publico. A classe `InstagramPublisher` suporta duas estrategias:

- usar `SupabaseStorageUploader`, quando existem `SUPABASE_URL`,
  `SUPABASE_SERVICE_ROLE_KEY` e `SUPABASE_BUCKET`;
- construir um URL a partir de `PUBLIC_MEDIA_BASE_URL`, por exemplo com um
  tunnel publico apontado para `/outputs`.

Na configuracao atual da interface web e do bot Telegram, o caminho usado e o
Supabase, porque ambos instanciam o publicador com `SupabaseStorageUploader`. O
fallback por `PUBLIC_MEDIA_BASE_URL` continua disponivel na classe, mas so e
usado se o publicador for criado sem uploader.

No caminho com Supabase, o ficheiro e enviado para o bucket configurado com
`Content-Type: image/jpeg`, `Cache-Control: 3600` e `x-upsert: true`. O uploader
devolve o URL publico do objeto em Storage, e esse URL e enviado a Meta como
`image_url`.

### Chamada a API da Meta

Depois de ter a caption e o URL publico da imagem, o projeto faz duas chamadas
HTTP em formato `application/x-www-form-urlencoded`:

1. `POST /{ig_user_id}/media`

```text
image_url=<URL_PUBLICO_DA_IMAGEM>
caption=<TEXTO_FINAL>
access_token=<INSTAGRAM_ACCESS_TOKEN>
```

Esta chamada devolve um ID de container. O codigo aceita tanto `id` como
`creation_id`, para ser tolerante a respostas diferentes.

2. `POST /{ig_user_id}/media_publish`

```text
creation_id=<ID_DO_CONTAINER>
access_token=<INSTAGRAM_ACCESS_TOKEN>
```

Esta segunda chamada publica efetivamente o post e devolve o `media_id`. O
endpoint `/api/publish-instagram` devolve esse ID ao frontend, que mostra a
mensagem "Publicado no Instagram".

O publicador tambem trata erros de forma explicita. Se a Meta devolver erro HTTP,
o codigo tenta extrair `message`, `code` e `error_subcode` da resposta JSON e
mostra uma mensagem util ao utilizador. Isto ajuda a diagnosticar problemas como
token invalido, permissao em falta, URL inacessivel, formato de imagem rejeitado
ou container expirado.

### Requisitos de configuracao

Para publicar no Instagram, o projeto precisa das seguintes variaveis no `.env`:

```env
INSTAGRAM_ACCOUNT_ID=...
INSTAGRAM_ACCESS_TOKEN=...
INSTAGRAM_API_VERSION=v22.0
INSTAGRAM_BASE_URL=https://graph.instagram.com

PUBLIC_MEDIA_BASE_URL=...

SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_BUCKET=instagram-posts
```

No fluxo atual da web e do bot, as variaveis de Supabase sao as mais importantes
para a publicacao, porque o uploader e passado ao `InstagramPublisher`.
`PUBLIC_MEDIA_BASE_URL` fica como alternativa tecnica da classe para casos em
que se queira servir diretamente a pasta `outputs/` atraves de um URL publico.

### Limites encontrados

Os principais limites do Instagram foram parcialmente resolvidos pelo codigo:

- a imagem nao pode ser apenas local: resolvido com Supabase Storage ou URL
  publico configurado;
- a imagem tem de ser JPEG: resolvido com conversao para JPEG;
- a proporcao tem de estar entre 4:5 e 1.91:1: validado antes do upload;
- a caption tem limite de 2200 caracteres: validado antes da chamada a API;
- e obrigatorio existir imagem: validado na web, no bot e no publicador.

Ainda ha limites que o projeto nao controla totalmente:

- nao verifica localmente o limite de 30 hashtags;
- nao verifica localmente o limite de 20 mencoes;
- nao consulta `/content_publishing_limit` antes de publicar;
- nao faz polling de `status_code` do container;
- nao implementa refresh automatico do token;
- nao implementa OAuth/Business Login dentro da propria aplicacao;
- nao envia ainda `alt_text`, apesar de o projeto gerar `image_alt_text`;
- nao suporta Reels, Stories, product tags ou collaborators.

O ponto do `alt_text` e uma melhoria importante: o projeto ja gera texto
alternativo para acessibilidade, e a API da Meta suporta `alt_text` para posts
de imagem. Neste momento esse campo ainda nao e enviado no pedido `/media`, por
isso pode ser acrescentado como evolucao direta da integracao.

### Porque Instagram foi mais complexo do que Bluesky

Embora Instagram seja a rede principal do projeto, foi mais complexo de integrar
do que Bluesky por tres motivos:

- a Meta nao aceita ficheiros locais diretamente para posts de imagem;
- a publicacao depende de token, permissoes e tipo de conta;
- o processo exige dois passos, container e publicacao.

No Bluesky, o backend consegue enviar a imagem local como blob diretamente pelo
SDK. No Instagram, foi necessario criar uma ponte adicional: converter a imagem,
coloca-la num URL publico e so depois pedir a publicacao. Por isso, a integracao
com Instagram e uma prova mais forte de maturidade do MVP, porque resolve o
problema real que inicialmente bloqueava a rede principal.

### Limitacoes que ainda ficam

A publicacao no Instagram esta funcional, mas ainda ha melhorias possiveis:

- implementar login OAuth/Business Login para gerar tokens dentro da app;
- renovar tokens automaticamente quando aplicavel;
- enviar `image_alt_text` como `alt_text`;
- consultar o limite de publicacao antes de publicar;
- adicionar validacao local de hashtags e mencoes;
- fazer preflight do URL publico da imagem antes de chamar a Meta;
- adicionar testes automatizados para sucesso, erro da Meta, imagem invalida e
  caption acima do limite;
- suportar carrosseis e Reels como funcionalidades futuras.

Conclusao:

A integracao com Instagram deixou de estar apenas preparada e passou a estar
implementada. O projeto ja gera o conteudo, gera a imagem, prepara JPEG,
disponibiliza a imagem publicamente, cria o container de media e publica esse
container no Instagram. A principal dependencia externa continua a ser a
configuracao correta de credenciais, permissoes e armazenamento publico, mas o
fluxo tecnico essencial da publicacao automatica ja esta demonstrado no MVP.

Fontes oficiais:

- https://developers.facebook.com/docs/instagram-platform/content-publishing/
- https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/content-publishing/
- https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media/
- https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media_publish/
- https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api

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

## Redes sociais apenas pesquisadas

As redes seguintes nao foram implementadas no MVP. Foram analisadas para
perceber se seriam alternativas viaveis a Instagram e Bluesky, que dificuldades
tecnicas poderiam surgir, que requisitos externos seriam necessarios e se haveria
custos adicionais de API.

### X

O X permite publicacao automatica atraves da X API v2. O endpoint principal para
criar uma publicacao e `POST /2/tweets`, que recebe o texto e pode receber uma
lista de `media_ids` previamente carregados. Assim, para publicar texto e imagem,
o fluxo teria de ser:

1. autenticar o utilizador com OAuth;
2. carregar a imagem para a API de media;
3. receber um `media_id`;
4. opcionalmente associar metadata/alt text a esse media;
5. criar o post com `POST /2/tweets`, usando o texto e o `media_id`.

Do ponto de vista tecnico, isto seria possivel para o projeto. A imagem gerada
localmente nao precisa de estar num URL publico, ao contrario do Instagram,
porque o X tem endpoint proprio de upload de media. O problema principal nao e a
possibilidade tecnica, mas sim a autenticacao, custos, limites e adaptacao do
conteudo ao formato da plataforma.

#### Requisitos tecnicos

Para implementar X no projeto, seria necessario:

- criar uma conta de developer no X;
- criar um Project/App no Developer Console;
- ativar permissoes de leitura e escrita;
- implementar OAuth 2.0 Authorization Code with PKCE ou OAuth 1.0a User Context;
- pedir scopes como `tweet.read`, `tweet.write`, `users.read` e, para imagens,
  `media.write`;
- guardar e renovar tokens de forma segura, usando `offline.access` se fosse
  necessario manter a sessao ativa;
- carregar a imagem via `POST /2/media/upload`;
- usar `media_category=tweet_image`;
- criar metadata em `POST /2/media/metadata` para aproveitar o
  `image_alt_text`;
- publicar com `POST /2/tweets`.

O endpoint de criacao de post tambem tem o campo `made_with_ai`, que pode marcar
conteudo com media gerada por IA. Como a imagem do projeto e gerada com OpenAI,
este campo teria de ser avaliado para manter transparencia sobre conteudo
gerado por IA.

#### Limites encontrados

O limite de texto no X e mais apertado do que no Instagram e ate mais delicado
do que no Bluesky. A documentacao indica que posts podem ter ate 280 caracteres,
mas a contagem nao e simplesmente `len(text)`: o X usa uma contagem ponderada,
em que emojis, CJK e alguns caracteres Unicode contam de forma diferente. A
propria documentacao recomenda usar a biblioteca `twitter-text` para contar
corretamente.

Isto significa que a `caption` de Instagram seria demasiado longa e a
`caption_bluesky` tambem nao seria ideal, porque esta limitada a 300 caracteres,
enquanto X precisa de 280 caracteres ponderados. Para integrar bem, o projeto
deveria criar um novo campo, por exemplo `caption_x`, com regras proprias:

- maximo de 280 caracteres ponderados;
- uma ou duas frases curtas;
- uma chamada para acao muito curta;
- no maximo uma a tres hashtags;
- compatibilidade com links encurtados e contagem especial de URLs;
- validacao com `twitter-text` antes da chamada a API.

Na imagem, o X aceita imagens ate 5 MB via API. Como as imagens do projeto podem
ser PNG e podem ultrapassar esse tamanho dependendo da geracao, seria necessario
adicionar uma preparacao semelhante a do Bluesky/Instagram: converter ou
comprimir a imagem, garantir formato aceite e bloquear o envio caso continue
acima do limite.

Tambem existem rate limits oficiais relevantes:

- `POST /2/tweets`: 10,000 pedidos por 24 horas por app e 100 por 15 minutos por
  utilizador;
- `POST /2/media/upload`: 50,000 pedidos por 24 horas por app e 500 por 15
  minutos por utilizador;
- `POST /2/media/metadata`: 50,000 pedidos por 24 horas por app e 500 por 15
  minutos por utilizador.

Para este MVP, estes limites seriam mais do que suficientes. O problema maior
seria custo e configuracao.

#### Custos

A X API usa pricing pay-per-use com creditos comprados no Developer Console. A
documentacao oficial indica que nao ha subscricao fixa obrigatoria, mas cada
operacao consome creditos. Os valores publicados incluem:

- leitura de posts: $0.005 por recurso;
- leitura de media: $0.005 por recurso;
- criacao de conteudo: $0.015 por pedido;
- criacao de conteudo com URL: $0.200 por pedido;
- metadata de media: $0.005 por pedido.

Assim, um post simples no X teria pelo menos o custo de criacao de conteudo. Se
fosse usado alt text via metadata, haveria tambem custo desse pedido. A
documentacao tambem indica que diferentes endpoints podem ter custos diferentes
e que os valores atuais devem ser confirmados no Developer Console.

Comparando com Bluesky, o X seria menos apelativo para o MVP porque introduz
custo direto por uso. Comparando com Instagram, a vantagem seria nao precisar de
URL publico para a imagem, mas a desvantagem seria o modelo de creditos e a
necessidade de implementar OAuth mais completo.

#### Dificuldades de implementacao

As principais dificuldades seriam:

- implementar OAuth e refresh de tokens;
- guardar tokens de forma segura;
- adaptar a geracao de texto ao limite ponderado de 280 caracteres;
- adicionar validacao com `twitter-text`;
- preparar imagens ate 5 MB;
- adicionar upload de media antes do post;
- adicionar metadata/alt text;
- controlar custos por pedido;
- monitorizar rate limits e saldo de creditos;
- decidir se o campo `made_with_ai` deve ser enviado.

Conclusao:

A integracao com X e tecnicamente possivel, mas nao foi priorizada porque o MVP
esta focado em conteudo visual para Instagram e ja tem publicacao funcional em
Instagram e Bluesky. X exigiria uma caption propria, upload de media, OAuth com
scopes de escrita, validacao especial de caracteres e controlo de custos por
credito. Seria uma boa terceira integracao se o objetivo fosse publicar tambem
conteudo curto e conversacional, mas acrescentaria custo operacional que Bluesky
nao acrescenta.

Fontes oficiais:

- https://docs.x.com/x-api/posts/create-post
- https://docs.x.com/x-api/posts/manage-tweets/introduction
- https://docs.x.com/x-api/media/introduction
- https://docs.x.com/x-api/media/upload-media
- https://docs.x.com/x-api/media/create-media-metadata
- https://docs.x.com/fundamentals/counting-characters
- https://docs.x.com/fundamentals/authentication/oauth-2-0/authorization-code
- https://docs.x.com/fundamentals/authentication/guides/v2-authentication-mapping
- https://docs.x.com/x-api/fundamentals/rate-limits
- https://docs.x.com/x-api/getting-started/pricing

### LinkedIn

O LinkedIn tambem permite publicacao automatica, mas a integracao e diferente de
Instagram, Bluesky e X porque a plataforma separa varios produtos e permissoes:
partilhas de membros, posts organicos, posts de organizacoes, posts patrocinados
e APIs de marketing. Para o projeto, o caso mais provavel seria publicar uma
versao profissional do conteudo como post organico, com texto e imagem, numa
conta de membro ou numa pagina de organizacao.

Existem duas vias principais na documentacao:

- `Share on LinkedIn`, mais orientado para publicar em nome de um membro
  autenticado, usando `POST /v2/ugcPosts`;
- `Posts API`, mais recente, que permite criar posts organicos e patrocinados em
  `POST /rest/posts`.

A propria documentacao indica que a Posts API substitui progressivamente APIs
mais antigas como `ugcPosts`. Para uma implementacao nova, faria sentido estudar
diretamente a Posts API.

#### Requisitos tecnicos

Para publicar no LinkedIn, seria necessario:

- criar uma app no LinkedIn Developer Portal;
- adicionar o produto correto a app;
- implementar OAuth 2.0;
- obter um access token do membro autenticado;
- pedir `w_member_social` para publicar em nome de um membro;
- pedir `w_organization_social` para publicar em nome de uma organizacao;
- garantir que o membro autenticado tem permissao adequada na pagina da empresa;
- usar headers obrigatorios como `Linkedin-Version` e
  `X-Restli-Protocol-Version: 2.0.0`;
- construir URNs corretamente, por exemplo `urn:li:person:{id}` ou
  `urn:li:organization:{id}`;
- enviar o post para `POST /rest/posts`.

Para publicar com imagem, seria necessario um fluxo adicional com a Images API:

1. chamar `POST /rest/images?action=initializeUpload`;
2. indicar o owner da imagem, por exemplo uma organizacao;
3. receber um `uploadUrl` e um `urn:li:image:{id}`;
4. enviar o ficheiro para o `uploadUrl`;
5. criar o post com `content.media.id` igual ao Image URN;
6. opcionalmente enviar `altText` no bloco de media.

Ao contrario do Instagram, o LinkedIn nao exige que o projeto crie previamente um
URL publico proprio para a imagem. A plataforma devolve um `uploadUrl` para onde
o ficheiro deve ser enviado. Isto reduziria a dependencia de Supabase ou tunnels,
mas exigiria implementar o fluxo de upload da Images API.

#### Adaptacao ao conteudo do projeto

O conteudo atual do projeto foi pensado sobretudo para Instagram: caption
promocional, call to action, hashtags e imagem visual. Para LinkedIn, a
publicacao deveria ser adaptada para um tom mais profissional e menos
promocional. O ideal seria acrescentar um novo campo ao modelo, por exemplo
`caption_linkedin`, com regras diferentes:

- tom mais profissional e informativo;
- menos hashtags;
- foco em valor, contexto e credibilidade;
- chamada para acao mais discreta;
- possibilidade de mencionar empresa/pagina, se houver URN e permissao;
- texto preparado para `commentary` da Posts API.

O LinkedIn suporta texto, imagem, video, documentos, artigos, multi-image e
polls em posts organicos. Para este MVP, a opcao mais simples seria post organico
com uma imagem unica, usando o `image_alt_text` do projeto como `altText`.

#### Limites e restricoes encontrados

A documentacao do LinkedIn e mais fragmentada do que a do Bluesky, porque ha
varios produtos e versoes de API. As restricoes mais relevantes seriam:

- necessidade de OAuth 2.0 e produto correto no Developer Portal;
- necessidade de scopes especificos;
- para organizacoes, necessidade de papel adequado na pagina;
- obrigatoriedade de headers de versao;
- uso de URNs em vez de IDs simples;
- upload de imagem separado antes da criacao do post;
- possivel necessidade de acesso aprovado para APIs de Community Management ou
  Marketing;
- rate limits por aplicacao e por membro;
- rate limits diarios que nao sao publicados de forma fixa na documentacao e
  devem ser consultados no Developer Portal;
- possivel erro por campos demasiado longos, embora o limite pratico dependa do
  campo e da API usada.

A Images API suporta JPG, GIF e PNG, imagens com menos de 36,152,320 pixels e
alt text. A documentacao recomenda alt text com menos de 120 caracteres, embora
o maximo indicado seja 4,086 caracteres. O projeto ja gera `image_alt_text`, mas
teria de garantir que esse texto ficava adequado para acessibilidade no LinkedIn.

#### Custos

Nas fontes oficiais consultadas, o LinkedIn nao apresenta um modelo publico de
preco por pedido equivalente ao X. A limitacao principal nao parece ser custo
por request, mas sim acesso, permissoes, produtos aprovados e rate limits. A
documentacao de rate limiting indica limites diarios por aplicacao e por membro,
que reiniciam a meia-noite UTC, mas tambem indica que os limites standard nao
sao publicados e devem ser consultados no Developer Portal.

Se a integracao fosse apenas para publicacao organica, o custo direto de API nao
fica claro nas fontes oficiais e nao parece existir uma tabela publica de
creditos por chamada. Se o projeto evoluisse para conteudo patrocinado,
Advertising API ou campanhas, passariam a existir custos de publicidade e uma
camada adicional de acesso/tier. A documentacao oficial da Advertising API
refere tiers Development e Standard, com revisao e qualificacao para expandir o
uso.

#### Dificuldades de implementacao

As principais dificuldades seriam:

- escolher entre Share on LinkedIn, Posts API e APIs de marketing;
- configurar produto e permissoes corretas no Developer Portal;
- implementar OAuth 2.0;
- obter e guardar tokens;
- resolver o autor correto (`person` ou `organization`);
- validar se o utilizador tem papel adequado numa pagina;
- implementar o upload de imagem com `initializeUpload`;
- lidar com headers e versoes da API;
- adaptar a caption para um tom profissional;
- monitorizar rate limits no Developer Portal;
- tratar erros de permissao, URN invalido, imagem ainda nao disponivel ou campo
  demasiado longo.

Conclusao:

LinkedIn seria uma rede interessante para uma versao profissional do Social Media
Autopilot, sobretudo se o projeto fosse usado por empresas B2B, marcas pessoais,
consultores ou negocios que comunicam com publico profissional. No entanto, nao
foi implementado no MVP porque a rede principal era Instagram e porque LinkedIn
exigiria uma adaptacao editorial propria, OAuth, permissoes especificas, URNs,
headers de versao e upload de imagem via Images API. Em termos de custos, parece
menos previsivel que Bluesky e menos diretamente tarifado que X; a maior barreira
esta no acesso e na aprovacao/gestao de permissoes, nao num custo por post
claramente publicado.

Fontes oficiais:

- https://learn.microsoft.com/en-us/linkedin/
- https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin
- https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api
- https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api
- https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits
- https://learn.microsoft.com/en-us/linkedin/marketing/integrations/marketing-tiers
