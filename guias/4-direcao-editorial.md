# Direção editorial

Este guia vale para todo trabalho do estúdio — edição por cima, edição com cortes e criação do zero. Ele é um **repertório**, não um regulamento: descreve o que dá para fazer e como escolher. Em cada vídeo, o plano de edição (`plano.md`) escolhe o que entra, a partir do conteúdo e das **suas orientações para aquele vídeo**. Quando você pedir outra coisa, o seu pedido manda.

Nenhum vídeo precisa usar tudo. Um pode ser quase só câmera com três inserções precisas; outro pode ser uma aula inteira em tela dividida. O que importa é cada escolha servir à fala.

---

## 1. Sensibilidade

- **Dinâmica com intenção.** O ritmo muda com a fala: respiro só com a câmera, momentos de aula densa, momentos de imersão total no conteúdo. O problema não é ter muita coisa, é ter coisa sem função.
- **Movimento suave, acabamento limpo.** Sem efeito gratuito, sem zoom rápido em excesso, sem elemento que só enfeita.
- **Regra de ouro:** cada inserção nasce de uma palavra falada, no tempo exato em que ela é dita.

## 2. Contrato do vídeo gravado

O vídeo que você coloca em `video/` é o **material-fonte** e nunca é alterado no lugar. Existem dois contratos, conforme o pedido:

- **Edição por cima (padrão, `locked-final-cut`):** o vídeo já vem cortado e finalizado; a edição é **composição visual por cima** — enquadramento, textos, animações, prints, tela dividida, B-roll. O áudio original aparece uma única vez e segue contínuo; a duração final é igual à do gravado (tolerância de 1 quadro).
- **Edição com cortes (quando você pede):** cortar, reordenar, remover silêncios e vícios, acelerar trechos, extrair clipes. O arquivo original permanece intacto — os cortes viram **arquivos novos** em `edicoes/`, e a versão cortada pode receber composição por cima normalmente.

Dois arquivos de vídeo são duas edições independentes. Eles só viram uma sequência se você pedir.

## 3. Repertório de cenas

Os nomes em `código` são os usados no plano de edição.

| Cena | O que é | Quando usar |
|---|---|---|
| `camera` | câmera cheia, limpa | gancho, opinião, tese, conexão, respiro |
| `camera-enfase` | câmera com push-in lento ou punch-in numa frase | frase-chave, pergunta retórica |
| `camera-motion` | câmera cheia com um elemento por cima (chip, número, ícone, palavra) | reforçar um termo ou dado breve |
| `camera-espaco` | câmera deslocada (escala 1,15–1,25) abrindo espaço para texto | pergunta ou frase em tipografia grande |
| `aula` | tela dividida: conteúdo à esquerda (~70%), câmera à direita (~30%) | conceito em etapas, fluxo, lista, comparação |
| `demo` | print ou interface dominante, câmera em card que muda de canto | tutorial, demonstração de ferramenta |
| `cena` | conteúdo em tela cheia, sem câmera | fluxo complexo, print que precisa ser lido, clímax da explicação |
| `broll` | vídeo ou ilustração em tela cheia, fala continua por baixo | metáfora, virada, abertura de bloco |
| `corte-dinamico` | jump cut, remoção de silêncio ou aceleração pontual (edição com cortes) | ritmo de Reels, enxugar pausas, energia |
| `transformacao` | um elemento cresce até virar tela cheia, ou a câmera encolhe até virar card | mudanças que carregam significado |

**Lado da câmera.** Nas telas divididas e no card, o padrão é **conteúdo à esquerda, câmera à direita**. Inverta só se o enquadramento do rosto, a legibilidade ou um pedido seu exigirem, e registre o motivo no plano.

### Como escolher cada trecho

| O que está sendo falado | Primeira opção |
|---|---|
| opinião, experiência, conclusão | `camera` |
| dado ou termo breve | `camera-motion` |
| contraste, relação, fluxo | `aula` ou `cena` |
| passo a passo de software | `demo` |
| lista, framework, aula longa | `aula` |
| conceito abstrato de alto impacto | `broll` ou `cena` |
| notícia, pesquisa, documento | `demo` com o print e marca-texto |

Perguntas úteis:

- Aqui a atenção deve estar **em mim**, **no conteúdo** ou **dividida**?
- A ideia se entende melhor **vendo uma metáfora**, **acompanhando um fluxo** ou **olhando a ferramenta**?
- A última mudança foi há quanto tempo? Um corte ou uma troca de cena renova a atenção?
- Isso ajuda a entender ou só enfeita?

## 4. Movimento e transições

**Câmera**

- Base suave: push-in de 1,00 → 1,04 ao longo de um trecho, ou pull-out de 1,06 → 1,00 ao voltar de uma inserção.
- Ênfase: punch-in até ~1,12 em 2–3 s.
- Limite do pan: `|deslocamento| ≤ largura × (escala − 1) / 2`, senão aparece borda preta.

**Mudança de layout** (entrar numa `aula`, card da `demo` trocando de canto): **0,9–1,2 s**, curva suave sem "quique" (`Easing.inOut(Easing.cubic)` no Remotion; em HyperFrames, GSAP com ease equivalente). Câmera e painel se movem **juntos**, com a mesma curva e a mesma janela de tempo. Pode começar alguns quadros antes da palavra para estar pronto nela, mas o conteúdo nunca aparece antes de ser dito.

**Vozes de transição** (misture para não ficar previsível):

- **Corte seco:** mudança de assunto, frase de impacto, ritmo de lista.
- **Fade curto (10–14 quadros):** entre cenas de mesma atmosfera, ou numa volta elegante.
- **Transformação animada:** reserve para mudanças com significado.

Nunca deixe tela vazia ou preta entre cenas.

**Elementos em cena:** painéis e cards sobem com mola suave; texto entra palavra por palavra; B-roll e destaques entram com wipe. Na `aula` e na `cena`, os elementos entram **acompanhando a explicação**: um passo do fluxo por vez, a seta aparece quando a relação é dita, o destaque muda de item conforme a fala avança.

## 5. Traduções úteis (fala → visual)

Ideias de partida, não obrigações:

- **Ferramenta citada** → `demo` com o print real que você salvou em `prints/`.
- **Notícia ou pesquisa** → print íntegro com zoom lento e marca-texto exatamente sobre a frase citada.
- **Processo ou etapas** → `aula` com um fluxo que se monta passo a passo.
- **Conceito abstrato** → `broll` metafórico ou ilustração que se transforma.
- **Número central** → contador, barra ou comparação.
- **Pergunta retórica** → tipografia grande sobre a câmera deslocada.
- **Comparação** → `aula` com dois lados que se revelam.
- **"Já gravei um vídeo sobre…"** → card com a miniatura real, levemente girado.

## 6. Prints e marca-texto

Prints são a matéria-prima mais valiosa da edição: o resultado fica muito melhor quando você **tira print do que quer ver animado e salva direto em `prints/`**.

- O print preserva inteira a região que comprova a fala: título, frase, número. Corte acidental reprova o quadro.
- Recorte deliberado é permitido quando melhora a leitura, desde que a evidência continue visível.
- O marca-texto é semântico: cobre **exatamente** a frase citada, entra na palavra-gatilho, e acompanha o zoom do print (os dois ficam no mesmo contêiner).
- Antes do render final, confira um quadro com o print assentado e outro com cada marca-texto completo.

## 7. Formatos

| Formato | Tamanho | Uso | Cuidados |
|---|---|---|---|
| Horizontal 16:9 | 1920×1080 | YouTube, aulas | padrão; herda fps do vídeo gravado |
| Vertical 9:16 | 1080×1920 | Reels, TikTok, Shorts | deixe livres ~250 px no topo e ~420 px embaixo (interface do app); legenda grande abaixo do queixo; tela dividida vira **em cima / embaixo** |
| Quadrado ou 4:5 | 1080×1080, 1080×1350 | feed | textos maiores, menos elementos por vez |

A galeria em [estilos/](../estilos/README.md) mostra exemplos de cada formato.

## 8. Identidade visual

Separe três decisões:

1. **Identidade permanente:** clareza, sincronia com a fala, legibilidade no celular, acabamento humano, assets reais.
2. **Dialeto do vídeo:** paleta, fontes, textura, iconografia, densidade. Escolha um estilo da [galeria](../estilos/README.md) ou traga o seu (prints de referência em `prints/` funcionam muito bem). Intensidade: `sutil`, `equilibrada` ou `dominante`.
3. **Direção da cena:** o layout (seção 3) e a metáfora usada naquele trecho.

Quando várias marcas aparecem no mesmo vídeo, prefira uma base neutra com acentos por marca. Não recrie logos ou interfaces sem ter o asset real.

## 9. Cuidados fixos

Valem em todo vídeo, em qualquer estilo, porque são qualidade:

1. **Tempo por palavra.** Todo gatilho usa o início exato da palavra no `palavras.json`.
2. **Rosto livre.** Texto e elementos não cobrem olhos, boca ou contorno do rosto. A posição do rosto vem dos quadros reais do vídeo, nunca de um palpite.
3. **Legibilidade.** Todo texto precisa ser lido na tela de um celular.
4. **Sem texto dentro de imagens geradas por IA.** Todo texto entra na montagem.
5. **Números como foram falados**, sem "correção" na tela.
6. **Prints íntegros** (seção 6).

## 10. Regras da edição com cortes

Quando o pedido é cortar (skill `rough-cut`), as decisões seguem esta doutrina — detalhada em `.devin/skills/rough-cut/references/editing-rules.md`:

- **Silêncio tem contexto.** Talking-head: pausas >~1,5–2 s são candidatas a corte. Screen-share: pausa curta com tela ativa (digitação, scroll, cursor) fica — faz parte da demonstração. Silêncio sem atividade nenhuma é candidato forte.
- **Digitação/cola sem fala é cortada** quando o resultado aterrissa logo depois; quem assiste não quer ver código aparecendo letra a letra. **O resultado nunca é cortado** — build rodando, teste passando, app respondendo ficam no vídeo.
- **Narração por cima protege tudo.** Se há fala sobre o trecho, o trecho fica, mesmo com tela "parada".
- **Retakes:** mantenha a última take completa e genuína. O corte entra no intervalo entre takes, nunca no meio de palavra. Narração repetida de demo não é retake (é ênfase).
- **Na dúvida, mantenha e sinalize.** Corte errado destrói conteúdo; corte não feito só deixa gordura.
- **Borda de corte nunca dentro de palavra.** Encaixe no onset/offset da palavra vizinha, com respiro (~0,1–0,2 s). Palavra que cruza a borda vai para revisão, nunca é fatiada no automático.
- **Fillers ("ééé", "tipo", "né") e tosses:** corte só confirmado, e só quando não carrega ritmo nem autenticidade. Uma pausa de pensamento é humana; dez segundos é ar morto.

## 11. Embalagem: a regra da congruência

Thumbnail, título e abertura são um contrato único com quem clica:

1. **A thumbnail promete** — uma ideia, uma tensão, uma pergunta.
2. **O título confirma** — mesma promessa em palavras, sem repetir o texto da imagem.
3. **Os primeiros 30 segundos entregam** — o vídeo prova imediatamente que a promessa era real. Nada de enrolação ("throat-clearing"), apresentação longa ou logo animada antes do conteúdo.

Congruência quebrada = clique traído = retenção morta. Quando fizer thumbnail (skill `thumbnail`) ou cortar a abertura, verifique o trio junto.
