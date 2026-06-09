# Custos de geração de imagens por IA

## Justificação da escolha do OpenAI `gpt-image-2`

O modelo `gpt-image-2` foi selecionado por apresentar uma relação adequada entre
qualidade visual, controlo de custo, flexibilidade de tamanhos e facilidade de
integração com o backend Python/OpenAI já utilizado no projeto. Como o objetivo
do MVP é gerar uma imagem final para acompanhar publicações em redes sociais, o
critério de escolha não se limita ao menor preço por imagem; inclui também a
consistência visual, a qualidade do resultado e o esforço técnico de integração.

Segundo a documentação da OpenAI, o `gpt-image-2` é o modelo de geração de imagem
mais avançado da plataforma, com desempenho classificado como "Highest", suporte
a geração e edição, tamanhos flexíveis e processamento de imagens de entrada em
alta fidelidade. Para este caso de uso, estas características tornam o modelo
particularmente adequado, uma vez que o projeto precisa de imagens com qualidade
suficiente para comunicação visual de marca. A qualidade `medium`, usada
atualmente, representa um compromisso intermédio: tem custo superior a opções de
baixo custo, como Stable Image Core ou Imagen 4 Fast, mas mantém preço inferior a
alternativas como Nano Banana 2 em 1K e Nano Banana Pro.

As alternativas analisadas continuam relevantes:

- Gemini/Nano Banana é forte em rapidez, volume e fluxos conversacionais;
- Imagen 4 é competitivo em custo por imagem;
- Stability AI tem opções muito baratas para geração simples.

Face aos requisitos específicos deste MVP, o `gpt-image-2` apresenta a opção
mais equilibrada, pois combina qualidade visual, níveis configuráveis
(`low`, `medium`, `high`), formatos flexíveis e menor esforço de integração com
o backend existente.

Valores consultados em 2026-06-03. Os custos estão em USD e referem-se a uso
por API no plano pago, sem impostos. O projeto está configurado para usar
`OPENAI_IMAGE_MODEL=gpt-image-2`, `OPENAI_IMAGE_QUALITY=medium` e
`IMAGE_SIZE=1024x1280`; como esse tamanho não aparece diretamente em todas as
tabelas oficiais, os valores abaixo usam referências de 1024x1024 ou 1K quando
necessário. O custo final pode incluir também tokens de texto de entrada e,
em edições, tokens de imagens de referência.

| Fornecedor / modelo | Qualidade ou referência | Custo aproximado por imagem | Observações |
| --- | --- | ---: | --- |
| OpenAI `gpt-image-2` | Low, 1024x1024 | $0.006 | Modelo usado pelo projeto; para 1024x1536/1536x1024 a referência oficial é $0.005. |
| OpenAI `gpt-image-2` | Medium, 1024x1024 | $0.053 | Qualidade configurada atualmente no projeto; para 1024x1536/1536x1024 a referência oficial é $0.041. |
| OpenAI `gpt-image-2` | High, 1024x1024 | $0.211 | Para 1024x1536/1536x1024 a referência oficial é $0.165. |
| Google Nano Banana 2 / `gemini-3.1-flash-image` | 1K, 1024x1024 | $0.067 | Alternativa Gemini mais eficiente; também há 0.5K a $0.045, 2K a $0.101 e 4K a $0.151. |
| Google Nano Banana Pro / `gemini-3-pro-image` | 1K/2K | $0.134 | Modelo Gemini orientado para assets profissionais; 4K custa $0.24. |
| Google Nano Banana / `gemini-2.5-flash-image` | Até 1024x1024 | $0.039 | Modelo anterior focado em rapidez e volume; cada imagem até 1024x1024 consome 1290 tokens. |
| Google Imagen 4 Fast | Por imagem | $0.02 | Alternativa Google de baixo custo. |
| Google Imagen 4 Standard | Por imagem | $0.04 | Alternativa Google equilibrada. |
| Google Imagen 4 Ultra | Por imagem | $0.06 | Alternativa Google com maior qualidade na família Imagen 4. |
| Stability AI Stable Image Core | 3 créditos | $0.03 | 1 crédito equivale a $0.01. |
| Stability AI Stable Image Ultra | 8 créditos | $0.08 | Opção Stability AI de maior qualidade. |

Fontes oficiais:

- https://developers.openai.com/api/docs/guides/image-generation
- https://developers.openai.com/api/docs/pricing
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/image-generation
- https://platform.stability.ai/pricing

# Evidências de integração com redes sociais

Este documento sistematiza a investigação realizada sobre publicação automática
em redes sociais no contexto do projeto Social Media Autopilot. A análise tem
dois objetivos principais:

1. Sincronizar o projeto com uma rede social.
2. Publicar automaticamente o texto e a imagem gerados.

O objetivo da pesquisa não foi demonstrar que as redes sociais não suportam
publicação por API. Pelo contrário, várias plataformas disponibilizam mecanismos
de publicação automática. No entanto, esses mecanismos exigem requisitos externos
ao repositório, como contas específicas, tokens, permissões, revisão de
aplicação, alojamento público de ficheiros ou configuração adicional no portal de
developers de cada plataforma.

## Estado atual do projeto

O Social Media Autopilot já gera os dados necessários para preparar uma
publicação:

- `caption`;
- `caption_bluesky`;
- `hashtags`;
- `call_to_action`;
- `image_alt_text`;
- imagem gerada localmente;
- publicação automática no Instagram;
- publicação automática no Bluesky como prova de conceito;
- rascunho guardado em `outputs/drafts/`.

Estes dados são suficientes para construir o corpo de uma publicação. Assim, o
principal desafio técnico deixou de ser a geração de conteúdo e passou a estar
na integração externa com cada plataforma. No estado atual do projeto, Instagram
e Bluesky já se encontram integrados; X e LinkedIn foram analisados, mas não
implementados no MVP.

## Instagram

O Instagram foi definido como rede social principal por ser a plataforma mais
alinhada com o objetivo do MVP: gerar uma publicação visual composta por
caption, call to action, hashtags e imagem de apoio. A pesquisa inicial
identificou que a publicação automática dependia de requisitos externos da Meta,
sobretudo credenciais, conta profissional e URL público para a imagem. Com a
evolução do projeto, estes requisitos foram parcialmente resolvidos e a
publicação no Instagram passou a estar implementada tanto na interface web como
no bot Telegram.

### Pesquisa oficial da API

A Instagram Platform API permite publicar conteúdo em contas profissionais. Para
publicar uma imagem no feed, a Meta usa um fluxo de container:

1. criar um container de media no endpoint `/media`;
2. fornecer um `image_url` público e a caption;
3. receber o ID do container;
4. publicar esse container no endpoint `/media_publish` com `creation_id`;
5. receber o ID final da media publicada.

Este fluxo existe porque a API da Meta não recebe a imagem local diretamente no
pedido de publicação de imagem. A documentação explica que a Meta faz um cURL ao
URL enviado em `image_url`; por isso, a imagem tem de estar acessível num
servidor público no momento da publicação. Um ficheiro em `localhost` ou apenas
guardado no disco do projeto não é suficiente.

Para o fluxo usado pelo projeto, a documentação atual indica:

- a conta tem de ser uma conta profissional do Instagram;
- o login usado e Business Login for Instagram;
- o host usado no projeto e `graph.instagram.com`;
- é necessário um Instagram User access token;
- são necessárias permissões como `instagram_business_basic` e
  `instagram_business_content_publish`;
- a app pode usar Standard Access para contas que o programador controla ou
  Advanced Access para contas externas;
- a media precisa de estar num URL público;
- a imagem de feed deve ser JPEG;
- imagens de feed devem respeitar proporção entre 4:5 e 1.91:1;
- a caption pode ter até 2200 caracteres, 30 hashtags e 20 menções;
- o limite de publicação por API é de 100 posts num período móvel de 24 horas;
- os containers podem expirar, por isso devem ser publicados pouco depois de
  criados.

### Implementação realizada

A integração com Instagram passou a estar funcional em dois fluxos:

- interface web;
- bot Telegram.

Na interface web, o botão "Publicar no Instagram" fica disponível depois de
existir conteúdo e imagem gerada. O frontend chama o endpoint interno
`/api/publish-instagram`, enviando o `GeneratedContent` e o caminho local da
imagem. O backend resolve esse caminho dentro da pasta `outputs/`, impedindo que
seja usado um ficheiro arbitrário fora da área gerida pelo projeto.

No bot Telegram, a ação "Publicar no Instagram" usa o mesmo serviço
`InstagramPublisher`. Esta opção é relevante porque a lógica de validação,
preparação da imagem, upload público e chamada à API da Meta fica centralizada
num único ponto, em vez de estar duplicada entre a web e o bot.

O serviço `InstagramPublisher` executa o fluxo principal:

- verifica `INSTAGRAM_ACCOUNT_ID` e `INSTAGRAM_ACCESS_TOKEN`;
- recebe a configuração de URL público e o uploader de imagem;
- valida que existe imagem local antes de publicar;
- constrói a caption final;
- prepara a imagem para o formato exigido;
- cria um URL público para a imagem;
- cria o container de media no endpoint `/media`;
- publica o container no endpoint `/media_publish`;
- devolve `media_id`, `container_id`, texto publicado e `image_url`.

### Texto publicado

O Instagram usa a caption principal gerada pelo agente, não a
`caption_bluesky`. O publicador constrói o texto final juntando:

- `content.caption`;
- `content.call_to_action`;
- `content.hashtags`.

As hashtags são normalizadas antes do envio: se uma hashtag vier sem `#`, o
código acrescenta automaticamente o prefixo. O resultado final é validado contra
`INSTAGRAM_CAPTION_LIMIT = 2_200`. Se o texto ultrapassar esse limite, a
publicação é bloqueada antes de contactar a API.

Esta abordagem está alinhada com o limite oficial de caption do Instagram. A
documentação também refere limites de 30 hashtags e 20 menções. O projeto não faz uma
contagem local específica destes dois limites, mas o prompt do `ContentAgent`
pede entre 3 e 8 hashtags e não incentiva menções. Assim, para o uso normal do
MVP, o risco de ultrapassar estes limites é baixo.

### Preparação da imagem

O Instagram é mais restritivo do que o Bluesky no tratamento de imagens, porque
a API espera media acessível publicamente e com requisitos próprios de formato.
O projeto resolveu isto em duas etapas: preparar o ficheiro local e depois
disponibilizá-lo num URL público.

Na preparação local, o `InstagramPublisher`:

- confirma que o caminho da imagem existe;
- confirma que a imagem está dentro da pasta `outputs/`;
- abre o ficheiro com Pillow;
- converte imagens com transparência para RGB com fundo branco;
- valida a proporção entre 4:5 e 1.91:1;
- grava uma versão JPEG em `outputs/instagram/`;
- usa qualidade JPEG 92 com `optimize=True`.

Esta conversão é importante porque a documentação da Meta indica JPEG como o
formato suportado para imagens de feed. A validação de proporção também está
alinhada com o intervalo oficial. Como o projeto gera por omissão imagens
`1024x1280`, a proporção é 4:5, que fica no limite aceite pelo Instagram.

Depois de preparar o JPEG, o projeto precisa de transformar esse ficheiro num
URL público. A classe `InstagramPublisher` suporta duas estratégias:

- usar `SupabaseStorageUploader`, quando existem `SUPABASE_URL`,
  `SUPABASE_SERVICE_ROLE_KEY` e `SUPABASE_BUCKET`;
- construir um URL a partir de `PUBLIC_MEDIA_BASE_URL`, por exemplo com um
  tunnel público apontado para `/outputs`.

Na configuração atual da interface web e do bot Telegram, o caminho usado é o
Supabase, porque ambos instanciam o publicador com `SupabaseStorageUploader`. O
fallback por `PUBLIC_MEDIA_BASE_URL` continua disponível na classe, mas só é
usado se o publicador for criado sem uploader.

No caminho com Supabase, o ficheiro é enviado para o bucket configurado com
`Content-Type: image/jpeg`, `Cache-Control: 3600` e `x-upsert: true`. O uploader
devolve o URL público do objeto em Storage, e esse URL é enviado à Meta como
`image_url`.

### Chamada à API da Meta

Depois de ter a caption e o URL público da imagem, o projeto faz duas chamadas
HTTP em formato `application/x-www-form-urlencoded`:

1. `POST /{ig_user_id}/media`

```text
image_url=<URL_PUBLICO_DA_IMAGEM>
caption=<TEXTO_FINAL>
access_token=<INSTAGRAM_ACCESS_TOKEN>
```

Esta chamada devolve um ID de container. O código aceita tanto `id` como
`creation_id`, para ser tolerante a respostas diferentes.

2. `POST /{ig_user_id}/media_publish`

```text
creation_id=<ID_DO_CONTAINER>
access_token=<INSTAGRAM_ACCESS_TOKEN>
```

Esta segunda chamada publica efetivamente o post e devolve o `media_id`. O
endpoint `/api/publish-instagram` devolve esse ID ao frontend, que mostra a
mensagem "Publicado no Instagram".

O publicador também trata erros de forma explícita. Se a Meta devolver erro HTTP,
o código tenta extrair `message`, `code` e `error_subcode` da resposta JSON e
mostra uma mensagem útil ao utilizador. Isto ajuda a diagnosticar problemas como
token inválido, permissão em falta, URL inacessível, formato de imagem rejeitado
ou container expirado.

### Requisitos de configuração

Para publicar no Instagram, o projeto precisa das seguintes variáveis no `.env`:

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

No fluxo atual da web e do bot, as variáveis de Supabase são as mais importantes
para a publicação, porque o uploader é passado ao `InstagramPublisher`.
`PUBLIC_MEDIA_BASE_URL` fica como alternativa técnica da classe para casos em
que se queira servir diretamente a pasta `outputs/` através de um URL público.

### Limites encontrados

Os principais limites do Instagram foram parcialmente resolvidos pelo código:

- a imagem não pode ser apenas local: resolvido com Supabase Storage ou URL
  público configurado;
- a imagem tem de ser JPEG: resolvido com conversão para JPEG;
- a proporção tem de estar entre 4:5 e 1.91:1: validado antes do upload;
- a caption tem limite de 2200 caracteres: validado antes da chamada à API;
- é obrigatório existir imagem: validado na web, no bot e no publicador.

Ainda há limites que o projeto não controla totalmente:

- não verifica localmente o limite de 30 hashtags;
- não verifica localmente o limite de 20 menções;
- não consulta `/content_publishing_limit` antes de publicar;
- não faz polling de `status_code` do container;
- não implementa refresh automático do token;
- não implementa OAuth/Business Login dentro da própria aplicação;
- não envia ainda `alt_text`, apesar de o projeto gerar `image_alt_text`;
- não suporta Reels, Stories, product tags ou collaborators.

O ponto do `alt_text` é uma melhoria importante: o projeto já gera texto
alternativo para acessibilidade, e a API da Meta suporta `alt_text` para posts
de imagem. Neste momento esse campo ainda não é enviado no pedido `/media`, por
isso pode ser acrescentado como evolução direta da integração.

### Justificação da maior complexidade face ao Bluesky

Embora Instagram seja a rede principal do projeto, foi mais complexo de integrar
do que Bluesky por três motivos:

- a Meta não aceita ficheiros locais diretamente para posts de imagem;
- a publicação depende de token, permissões e tipo de conta;
- o processo exige dois passos, container e publicação.

No Bluesky, o backend consegue enviar a imagem local como blob diretamente pelo
SDK. No Instagram, foi necessário criar uma etapa intermédia: converter a imagem,
disponibilizá-la através de um URL público e só depois solicitar a publicação à
API da Meta. Por esse motivo, a integração com Instagram demonstra um nível
superior de maturidade técnica no MVP, pois resolve o obstáculo que inicialmente
impedia a publicação automática na rede principal do projeto.

### Possível adaptação para Facebook

Como Facebook e Instagram pertencem ao ecossistema da Meta, a publicação no
Facebook seria uma das adaptações mais próximas da implementação atual.

O que poderia ser reaproveitado:

- geração de caption, call to action e hashtags;
- imagem gerada localmente;
- conversão/preparação da imagem;
- upload para Supabase ou URL público;
- leitura de variáveis `.env`;
- padrão de publicador dedicado, semelhante ao `InstagramPublisher`;
- tratamento de erros HTTP da Meta.

O que teria de mudar:

- usar `https://graph.facebook.com` em vez de `https://graph.instagram.com`;
- trocar `INSTAGRAM_ACCOUNT_ID` por um `FACEBOOK_PAGE_ID`;
- trocar o Instagram User access token por um Page access token;
- pedir permissões de Pages, como `pages_manage_posts` e permissões relacionadas
  com leitura/listagem da página;
- publicar numa Page, não diretamente numa conta pessoal;
- usar endpoints de Facebook Page, por exemplo `POST /{page-id}/photos` para
  publicar uma imagem ou `POST /{page-id}/feed` para posts de texto/link.

Para uma imagem, o fluxo poderia ser mais simples do que no Instagram. Em vez de
criar um container `/media` e depois publicar em `/media_publish`, o Facebook
permite publicar fotos numa Page através do endpoint de fotos da própria Page.
Com a solução atual de Supabase, o projeto poderia enviar o URL público da imagem
como parâmetro `url`, juntamente com a caption. Outra possibilidade seria upload
multipart com o ficheiro, mas isso exigiria uma implementação diferente da atual.

Assim, Facebook seria uma evolução relativamente natural do código existente:
não exigiria uma nova arquitetura, mas exigiria um `FacebookPublisher` próprio,
novas variáveis de ambiente, Page access token, permissões de Page e testes com
uma página real. Para uso fora de contas/páginas controladas pelo programador,
também poderia ser necessária revisão de app pela Meta.

### Limitações remanescentes

A publicação no Instagram está funcional, mas ainda há melhorias possíveis:

- implementar login OAuth/Business Login para gerar tokens dentro da app;
- renovar tokens automaticamente quando aplicável;
- enviar `image_alt_text` como `alt_text`;
- consultar o limite de publicação antes de publicar;
- adicionar validação local de hashtags e menções;
- fazer preflight do URL público da imagem antes de chamar a Meta;
- adicionar testes automatizados para sucesso, erro da Meta, imagem inválida e
  caption acima do limite;
- suportar carrosséis e Reels como funcionalidades futuras.

Conclusão:

A integração com Instagram deixou de estar apenas preparada e passou a estar
implementada. O projeto já gera o conteúdo, gera a imagem, prepara JPEG,
disponibiliza a imagem publicamente, cria o container de media e publica esse
container no Instagram. A principal dependência externa continua a ser a
configuração correta de credenciais, permissões e armazenamento público, mas o
fluxo técnico essencial da publicação automática já está demonstrado no MVP.

Fontes oficiais:

- https://developers.facebook.com/docs/instagram-platform/content-publishing/
- https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/content-publishing/
- https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media/
- https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media_publish/
- https://developers.facebook.com/docs/pages-api/
- https://developers.facebook.com/docs/graph-api/reference/page/photos/
- https://developers.facebook.com/docs/graph-api/reference/page/feed/
- https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api

## Bluesky

O Bluesky foi a rede escolhida para a prova de conceito de publicação automática
porque a sua API permite publicar texto e imagem sem exigir uma conta
profissional, revisão de aplicação ou alojamento público prévio da imagem. Ao
contrário do Instagram, onde a imagem precisa de estar acessível por URL público
antes da publicação, o Bluesky permite carregar o ficheiro diretamente para o
servidor através do AT Protocol.

Do ponto de vista técnico, o Bluesky funciona sobre o AT Protocol. Um post é um
registo do tipo `app.bsky.feed.post`, com pelo menos os campos `text` e
`createdAt`. Quando existe imagem, o ficheiro não é enviado dentro do JSON do
post; primeiro é carregado como `blob` através de `com.atproto.repo.uploadBlob`
e depois esse `blob` fica referenciado no embed `app.bsky.embed.images`. Este
modelo encaixa bem no projeto, porque a imagem gerada pela OpenAI já existe
localmente em `outputs/` e pode ser lida pelo backend antes do envio.

### Implementação realizada

A integração deixou de ser apenas teórica e passou a estar funcional em dois
fluxos do MVP:

- interface web;
- bot Telegram.

Na interface web, o utilizador preenche o formulário, gera o conteúdo, gera a
imagem e só depois fica disponível a ação de publicar. O botão "Publicar no
Bluesky" chama o endpoint interno `/api/publish-bluesky`, enviando o objeto
`GeneratedContent` e o caminho da imagem gerada. Antes da publicação, o backend
valida que o caminho da imagem fica dentro da pasta de outputs do projeto, para
evitar publicar ficheiros arbitrários fora dessa área.

No bot Telegram, o fluxo é semelhante: depois de gerar o texto e a imagem, o
utilizador pode escolher "Publicar no Bluesky". O handler do bot não publica
diretamente; reutiliza o mesmo serviço `BlueskyPublisher`, garantindo que a
lógica de autenticação, validação do texto, preparação da imagem e envio é a
mesma nos dois canais.

O serviço `BlueskyPublisher` é o ponto central da integração:

- recebe `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` e `BLUESKY_SERVICE_URL`;
- cria um cliente `atproto.Client`;
- autentica no serviço configurado, por omissão `https://bsky.social`;
- constrói o texto final a partir de `content.caption_bluesky`;
- valida se a caption está vazia ou acima do limite local;
- prepara a imagem local antes de enviar;
- publica com `client.send_image(...)`;
- devolve `uri`, `cid` e texto publicado.

Este desenho evita duplicação: a web e o Telegram são interfaces diferentes,
mas a publicação real passa sempre pelo mesmo publicador.

### Texto publicado

O projeto não reutiliza diretamente a caption principal no Bluesky. Em vez
disso, o agente de conteúdo gera o campo `caption_bluesky`, uma versão escrita
de raiz para a plataforma. Esta escolha é importante porque o Bluesky tem uma
lógica de consumo mais curta e conversacional do que uma legenda típica de
Instagram.

No prompt do `ContentAgent`, o Gemini recebe regras específicas para este campo:

- escrever em português de Portugal;
- criar uma caption própria para Bluesky;
- limitar o texto a 300 caracteres;
- incluir uma chamada para ação;
- usar entre uma e três hashtags;
- manter frases completas;
- não inventar dados, estatísticas ou promessas falsas.

O modelo `GeneratedContent` também reforça este limite com
`caption_bluesky: str = Field(max_length=300)`. Isto significa que a resposta
estruturada do Gemini já deve chegar ao backend com uma caption curta. Além
disso, o frontend tem `maxlength="300"` no campo "Caption para Bluesky", e o
`BlueskyPublisher` faz uma última validação antes do envio.

### Limites encontrados

O limite oficial do registo `app.bsky.feed.post` é mais específico do que "300
caracteres": o campo `text` aceita até 300 grafemas e até 3000 bytes. Na prática,
para texto normal em português, isto corresponde ao limite que o projeto trata
como 300 caracteres. A diferença só se torna relevante em casos com emojis
compostos, combinações Unicode ou texto muito específico, porque um grafema visual
pode ocupar vários code points ou vários bytes.

Depois de analisar o código, a conclusão é que o limite de texto não está a ser
ultrapassado no fluxo normal do projeto. Pelo contrário, ele é controlado em
quatro camadas:

- prompt do Gemini: pede `caption_bluesky` com no máximo 300 caracteres;
- schema Pydantic: `GeneratedContent.caption_bluesky` tem `max_length=300`;
- interface web: o textarea tem `maxlength="300"`;
- publicador: `_build_post_text()` rejeita textos com `len(text) > 300`.

Esta validação local é conservadora. Ela protege o MVP de tentar publicar uma
caption longa, mas não implementa uma contagem perfeita de grafemas como a
definição oficial do AT Protocol. Para o uso atual, com texto curto em português
e poucas hashtags, esta simplificação é suficiente. Se o projeto evoluir para
muitos emojis, links complexos, menções ou threads, o ideal será acrescentar uma
validação de grafemas/bytes mais alinhada com o lexicon oficial.

Quanto a imagens, a documentação oficial consultada indica que um post pode ter
até quatro imagens, cada uma com alt text. A documentação também mostra que as
imagens são carregadas como blobs e depois referenciadas no post. Neste projeto,
o MVP publica apenas uma imagem por post. O código define
`BLUESKY_IMAGE_LIMIT_BYTES = 2_000_000` e usa Pillow para tentar comprimir a
imagem caso seja maior:

- abre a imagem gerada localmente;
- converte imagens com transparência para RGB com fundo branco;
- tenta manter ou reduzir o lado máximo da imagem;
- guarda como JPEG com qualidades decrescentes;
- devolve a primeira versão abaixo do limite;
- se não conseguir, bloqueia a publicação com erro claro.

Existe uma diferença a registar nas fontes oficiais: o tutorial "Creating a
post" refere 2 MB por imagem, enquanto o guia avançado "Posts" ainda refere
1,000,000 bytes. O projeto está alinhado com o valor de 2 MB e, se a API rejeitar
alguma imagem no futuro, o erro será apanhado pelo `BlueskyPublisher`.

### Requisitos de configuração

Para publicar no Bluesky, o projeto precisa de:

- conta Bluesky;
- app password criada nas definições da conta;
- variáveis no ficheiro `.env`:

```env
BLUESKY_HANDLE=exemplo.bsky.social
BLUESKY_APP_PASSWORD=...
BLUESKY_SERVICE_URL=https://bsky.social
```

### Justificação da viabilidade no MVP

O Bluesky foi mais simples de integrar do que outras redes analisadas porque:

- aceita publicação automática de posts por API;
- permite upload direto da imagem local como blob;
- não exige URL público da imagem;
- não exige conta profissional;
- não exige revisão de aplicação para uma prova de conceito local;
- permite usar uma app password em vez de implementar um fluxo OAuth completo;
- tem SDK Python disponível através da biblioteca `atproto`;
- devolve identificadores claros da publicação (`uri` e `cid`).

Isto tornou o Bluesky adequado para demonstrar o objetivo principal do projeto:
gerar texto e imagem automaticamente e publicar ambos numa rede social real a
partir da aplicação.

### Limitações remanescentes

O Bluesky deixou de estar apenas analisado e passou a estar integrado como prova
de conceito funcional, mas ainda há melhorias possíveis:

- a publicação é feita como post único; não existe criação automática de threads;
- o projeto não implementa manualmente facets para links, menções ou hashtags;
- a validação local usa contagem simples de caracteres, não uma biblioteca de
  grafemas;
- o fluxo web e Telegram exigem imagem antes de publicar, embora o publicador
  suporte também texto sem imagem;
- a compressão da imagem resolve o limite de tamanho, mas pode reduzir qualidade
  visual em imagens muito grandes;
- não há ainda testes automatizados que simulem respostas reais da API do
  Bluesky.

Conclusão:

A integração com Bluesky está funcional e constitui uma evidência concreta de
publicação automática no MVP. O código confirma que os limites de caracteres não
são ignorados: a caption curta é gerada, validada no schema, limitada na
interface e verificada antes do envio. A principal ressalva técnica é que o
limite oficial é definido por grafemas e bytes, enquanto o projeto usa uma
validação simplificada de 300 caracteres. Para o estado atual do projeto, esta
abordagem é adequada; para produção, a melhoria natural seria contar
grafemas/bytes de acordo com o lexicon `app.bsky.feed.post` e, se necessário,
criar threads automaticamente quando o texto ultrapassar o limite de um post.

Fontes oficiais:

- https://docs.bsky.app/docs/tutorials/creating-a-post
- https://docs.bsky.app/docs/advanced-guides/posts
- https://docs.bsky.app/docs/advanced-guides/api-directory
- https://docs.bsky.app/docs/advanced-guides/rate-limits
- https://atproto.com/guides/images-and-video
- https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/feed/post.json
- https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/embed/images.json

## Redes sociais analisadas sem implementação

As redes seguintes não foram implementadas no MVP. Foram analisadas para
perceber se seriam alternativas viáveis a Instagram e Bluesky, que dificuldades
técnicas poderiam surgir, que requisitos externos seriam necessários e se haveria
custos adicionais de API.

### X

O X permite publicação automática através da X API v2. O endpoint principal para
criação de publicações é `POST /2/tweets`, que recebe o texto e pode receber uma
lista de `media_ids` previamente carregados. Assim, para publicar texto e imagem,
o fluxo necessário seria:

1. autenticar o utilizador com OAuth;
2. carregar a imagem para a API de media;
3. receber um `media_id`;
4. opcionalmente associar metadata/alt text a esse media;
5. criar o post com `POST /2/tweets`, usando o texto e o `media_id`.

Do ponto de vista técnico, isto seria possível para o projeto. A imagem gerada
localmente não precisa de estar num URL público, ao contrário do Instagram,
porque o X tem endpoint próprio de upload de media. O problema principal não é a
possibilidade técnica, mas sim a autenticação, custos, limites e adaptação do
conteúdo ao formato da plataforma.

#### Requisitos técnicos

Para implementar X no projeto, seria necessário:

- criar uma conta de developer no X;
- criar um Project/App no Developer Console;
- ativar permissões de leitura e escrita;
- implementar OAuth 2.0 Authorization Code with PKCE ou OAuth 1.0a User Context;
- pedir scopes como `tweet.read`, `tweet.write`, `users.read` e, para imagens,
  `media.write`;
- guardar e renovar tokens de forma segura, usando `offline.access` se fosse
  necessário manter a sessão ativa;
- carregar a imagem via `POST /2/media/upload`;
- usar `media_category=tweet_image`;
- criar metadata em `POST /2/media/metadata` para aproveitar o
  `image_alt_text`;
- publicar com `POST /2/tweets`.

O endpoint de criação de post também tem o campo `made_with_ai`, que pode marcar
conteúdo com media gerada por IA. Como a imagem do projeto é gerada com OpenAI,
este campo teria de ser avaliado para manter transparência sobre conteúdo
gerado por IA.

#### Limites encontrados

O limite de texto no X é mais apertado do que no Instagram e até mais delicado
do que no Bluesky. A documentação indica que posts podem ter até 280 caracteres,
mas a contagem não é simplesmente `len(text)`: o X usa uma contagem ponderada,
em que emojis, CJK e alguns caracteres Unicode contam de forma diferente. A
própria documentação recomenda usar a biblioteca `twitter-text` para contar
corretamente.

Isto significa que a `caption` de Instagram seria demasiado longa e a
`caption_bluesky` também não seria ideal, porque está limitada a 300 caracteres,
enquanto X precisa de 280 caracteres ponderados. Para integrar bem, o projeto
deveria criar um novo campo, por exemplo `caption_x`, com regras próprias:

- máximo de 280 caracteres ponderados;
- uma ou duas frases curtas;
- uma chamada para ação muito curta;
- no máximo uma a três hashtags;
- compatibilidade com links encurtados e contagem especial de URLs;
- validação com `twitter-text` antes da chamada à API.

Na imagem, o X aceita imagens até 5 MB via API. Como as imagens do projeto podem
ser PNG e podem ultrapassar esse tamanho dependendo da geração, seria necessário
adicionar uma preparação semelhante à do Bluesky/Instagram: converter ou
comprimir a imagem, garantir formato aceite e bloquear o envio caso continue
acima do limite.

Também existem rate limits oficiais relevantes:

- `POST /2/tweets`: 10,000 pedidos por 24 horas por app e 100 por 15 minutos por
  utilizador;
- `POST /2/media/upload`: 50,000 pedidos por 24 horas por app e 500 por 15
  minutos por utilizador;
- `POST /2/media/metadata`: 50,000 pedidos por 24 horas por app e 500 por 15
  minutos por utilizador.

Para este MVP, estes limites seriam mais do que suficientes. O problema maior
seria custo e configuração.

#### Custos

A X API usa pricing pay-per-use com créditos comprados no Developer Console. A
documentação oficial indica que não há subscrição fixa obrigatória, mas cada
operação consome créditos. Os valores publicados incluem:

- leitura de posts: $0.005 por recurso;
- leitura de media: $0.005 por recurso;
- criação de conteúdo: $0.015 por pedido;
- criação de conteúdo com URL: $0.200 por pedido;
- metadata de media: $0.005 por pedido.

Assim, um post simples no X teria pelo menos o custo de criação de conteúdo. Se
fosse usado alt text via metadata, haveria também custo desse pedido. A
documentação também indica que diferentes endpoints podem ter custos diferentes
e que os valores atuais devem ser confirmados no Developer Console.

Comparando com Bluesky, o X seria menos apelativo para o MVP porque introduz
custo direto por uso. Comparando com Instagram, a vantagem seria não precisar de
URL público para a imagem, mas a desvantagem seria o modelo de créditos e a
necessidade de implementar OAuth mais completo.

#### Dificuldades de implementação

As principais dificuldades seriam:

- implementar OAuth e refresh de tokens;
- guardar tokens de forma segura;
- adaptar a geração de texto ao limite ponderado de 280 caracteres;
- adicionar validação com `twitter-text`;
- preparar imagens até 5 MB;
- adicionar upload de media antes do post;
- adicionar metadata/alt text;
- controlar custos por pedido;
- monitorizar rate limits e saldo de créditos;
- decidir se o campo `made_with_ai` deve ser enviado.

Conclusão:

A integração com X é tecnicamente possível, mas não foi priorizada porque o MVP
está focado em conteúdo visual para Instagram e já tem publicação funcional em
Instagram e Bluesky. X exigiria uma caption própria, upload de media, OAuth com
scopes de escrita, validação especial de caracteres e controlo de custos por
crédito. Seria uma boa terceira integração se o objetivo fosse publicar também
conteúdo curto e conversacional, mas acrescentaria custo operacional que Bluesky
não acrescenta.

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

O LinkedIn também permite publicação automática, mas a integração é diferente de
Instagram, Bluesky e X porque a plataforma separa vários produtos e permissões:
partilhas de membros, posts orgânicos, posts de organizações, posts patrocinados
e APIs de marketing. Para o projeto, o caso mais provável seria publicar uma
versão profissional do conteúdo como post orgânico, com texto e imagem, numa
conta de membro ou numa página de organização.

Existem duas vias principais na documentação:

- `Share on LinkedIn`, mais orientado para publicar em nome de um membro
  autenticado, usando `POST /v2/ugcPosts`;
- `Posts API`, mais recente, que permite criar posts orgânicos e patrocinados em
  `POST /rest/posts`.

A própria documentação indica que a Posts API substitui progressivamente APIs
mais antigas como `ugcPosts`. Para uma implementação nova, faria sentido estudar
diretamente a Posts API.

#### Requisitos técnicos

Para publicar no LinkedIn, seria necessário:

- criar uma app no LinkedIn Developer Portal;
- adicionar o produto correto à app;
- implementar OAuth 2.0;
- obter um access token do membro autenticado;
- pedir `w_member_social` para publicar em nome de um membro;
- pedir `w_organization_social` para publicar em nome de uma organização;
- garantir que o membro autenticado tem permissão adequada na página da empresa;
- usar headers obrigatórios como `Linkedin-Version` e
  `X-Restli-Protocol-Version: 2.0.0`;
- construir URNs corretamente, por exemplo `urn:li:person:{id}` ou
  `urn:li:organization:{id}`;
- enviar o post para `POST /rest/posts`.

Para publicar com imagem, seria necessário um fluxo adicional com a Images API:

1. chamar `POST /rest/images?action=initializeUpload`;
2. indicar o owner da imagem, por exemplo uma organização;
3. receber um `uploadUrl` e um `urn:li:image:{id}`;
4. enviar o ficheiro para o `uploadUrl`;
5. criar o post com `content.media.id` igual ao Image URN;
6. opcionalmente enviar `altText` no bloco de media.

Ao contrário do Instagram, o LinkedIn não exige que o projeto crie previamente um
URL público próprio para a imagem. A plataforma devolve um `uploadUrl` para onde
o ficheiro deve ser enviado. Isto reduziria a dependência de Supabase ou tunnels,
mas exigiria implementar o fluxo de upload da Images API.

#### Adaptação ao conteúdo do projeto

O conteúdo atual do projeto foi pensado sobretudo para Instagram: caption
promocional, call to action, hashtags e imagem visual. Para LinkedIn, a
publicação deveria ser adaptada para um tom mais profissional e menos
promocional. O ideal seria acrescentar um novo campo ao modelo, por exemplo
`caption_linkedin`, com regras diferentes:

- tom mais profissional e informativo;
- menos hashtags;
- foco em valor, contexto e credibilidade;
- chamada para ação mais discreta;
- possibilidade de mencionar empresa/página, se houver URN e permissão;
- texto preparado para `commentary` da Posts API.

O LinkedIn suporta texto, imagem, vídeo, documentos, artigos, multi-image e
polls em posts orgânicos. Para este MVP, a opção mais simples seria post orgânico
com uma imagem única, usando o `image_alt_text` do projeto como `altText`.

#### Limites e restrições encontrados

A documentação do LinkedIn é mais fragmentada do que a do Bluesky, porque há
vários produtos e versões de API. As restrições mais relevantes seriam:

- necessidade de OAuth 2.0 e produto correto no Developer Portal;
- necessidade de scopes específicos;
- para organizações, necessidade de papel adequado na página;
- obrigatoriedade de headers de versão;
- uso de URNs em vez de IDs simples;
- upload de imagem separado antes da criação do post;
- possível necessidade de acesso aprovado para APIs de Community Management ou
  Marketing;
- rate limits por aplicação e por membro;
- rate limits diários que não são publicados de forma fixa na documentação e
  devem ser consultados no Developer Portal;
- possível erro por campos demasiado longos, embora o limite prático dependa do
  campo e da API usada.

A Images API suporta JPG, GIF e PNG, imagens com menos de 36,152,320 pixels e
alt text. A documentação recomenda alt text com menos de 120 caracteres, embora
o máximo indicado seja 4,086 caracteres. O projeto já gera `image_alt_text`, mas
teria de garantir que esse texto ficava adequado para acessibilidade no LinkedIn.

#### Custos

Nas fontes oficiais consultadas, o LinkedIn não apresenta um modelo público de
preço por pedido equivalente ao X. A limitação principal não parece ser custo
por request, mas sim acesso, permissões, produtos aprovados e rate limits. A
documentação de rate limiting indica limites diários por aplicação e por membro,
que reiniciam a meia-noite UTC, mas também indica que os limites standard não
são publicados e devem ser consultados no Developer Portal.

Se a integração fosse apenas para publicação orgânica, o custo direto de API não
fica claro nas fontes oficiais e não parece existir uma tabela pública de
créditos por chamada. Se o projeto evoluísse para conteúdo patrocinado,
Advertising API ou campanhas, passariam a existir custos de publicidade e uma
camada adicional de acesso/tier. A documentação oficial da Advertising API
refere tiers Development e Standard, com revisão e qualificação para expandir o
uso.

#### Dificuldades de implementação

As principais dificuldades seriam:

- escolher entre Share on LinkedIn, Posts API e APIs de marketing;
- configurar produto e permissões corretas no Developer Portal;
- implementar OAuth 2.0;
- obter e guardar tokens;
- resolver o autor correto (`person` ou `organization`);
- validar se o utilizador tem papel adequado numa página;
- implementar o upload de imagem com `initializeUpload`;
- lidar com headers e versões da API;
- adaptar a caption para um tom profissional;
- monitorizar rate limits no Developer Portal;
- tratar erros de permissão, URN inválido, imagem ainda não disponível ou campo
  demasiado longo.

Conclusão:

LinkedIn seria uma rede interessante para uma versão profissional do Social Media
Autopilot, sobretudo se o projeto fosse usado por empresas B2B, marcas pessoais,
consultores ou negócios que comunicam com público profissional. No entanto, não
foi implementado no MVP porque a rede principal era Instagram e porque LinkedIn
exigiria uma adaptação editorial própria, OAuth, permissões específicas, URNs,
headers de versão e upload de imagem via Images API. Em termos de custos, parece
menos previsível que Bluesky e menos diretamente tarifado que X; a maior barreira
está no acesso e na aprovação/gestão de permissões, não num custo por post
claramente publicado.

Fontes oficiais:

- https://learn.microsoft.com/en-us/linkedin/
- https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin
- https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api
- https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api
- https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits
- https://learn.microsoft.com/en-us/linkedin/marketing/integrations/marketing-tiers
