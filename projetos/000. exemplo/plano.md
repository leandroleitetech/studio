# 003. jev-nao-e-hype: plano de edição

> **Exemplo real** de um plano de edição, mantido aqui como modelo. É de uma época em que o estúdio gerava B-roll num serviço pago (Higgsfield) — hoje a estrutura do plano (blocos, gatilhos por palavra, timeline, zona do rosto) continua idêntica; apenas os assets gerados saem de outras fontes ou são recriados em código.

## Fonte

`video/jev.mp4`: 739,272 s (12:19) · 1920×1080 · 29,97 fps (30000/1001) · h264 10,4 Mb/s + aac 48 kHz estéreo.
`locked-final-cut`: nada é cortado, acelerado ou reordenado. A edição é composição por cima.

## Leitura do vídeo e orientações

Vídeo de notícia sobre o Jev, da TypeSafe: um modelo que não conversa e só decide. A fala tem estes movimentos:

| bloco | tempo | conteúdo | cena dominante |
|---|---|---|---|
| 1. Gancho e promessa | 0:00–1:19 | "a IA mais interessante não sabe conversar", promessa, "não é hype", inscrição | CÂMERA |
| 2. A notícia | 1:19–1:56 | 15/set, São Francisco, dois anos em sigilo, US$ 40 mi, System One, 3 plataformas | NOTÍCIA (prints) |
| 3. O fundador | 1:56–2:24 | Diogo Almeida, ex-OpenAI, da IA que conversa para a IA que decide | CÂMERA + foto |
| 4. O problema | 2:24–3:35 | IA virou sinônimo de chat, as empresas precisam de decisão, consultor sênior | B-ROLL |
| 5. Sistema 1 × 2 | 3:35–4:44 | Kahneman, *Rápido e Devagar*, modelos de conversa = S2, Jev = S1 | AULA |
| 6. Exemplo prático | 4:44–8:07 | mensagem do curso → estado + perguntas → escolha, nota, sim/não → ação | AULA (bloco principal) |
| 7. Preço | 8:07–8:40 | cobra pelo que entra: US$ 0,04 ≈ 10 livros, resposta grátis | CENA |
| 8. Onde serve | 8:40–9:46 | atendimento, moderação, vendas, cadastro; pequeno negócio | AULA → CÂMERA |
| 9. Onde não serve | 9:46–10:46 | prompt injection e porteiro; 200×/400× contra 6–7× e 80% | B-ROLL → CENA |
| 10. Jevons e fecho | 10:46–11:59 | homenagem a Jevons, paradoxo do carvão, a aposta, "não é hype" | B-ROLL → CÂMERA |
| 11. CTA | 11:59–12:19 | like, inscrição, próximo vídeo | CÂMERA |

**Orientações recebidas:** seguir o fluxo de uma edição de notícia, só que **moderada**, com menos volume de inserções. **Zoom sem exagero.** Usar as fotos de `prints/pessoas` (Diogo, Kahneman, Jevons) e prints reais das notícias. O plano de inserções (um arquivo de referência em `prints/`) serve só de norte. A timeline segue a **transcrição**. Orçamento de **até 400–500 créditos**, com modelos moderados.

**Diferenças em relação ao plano de inserções.** Estes trechos saíram no corte e ficam fora: confiança calibrada, previsão do tempo, exemplo do banco, pulseiras da triagem, o caso de 9.081 produtos do paddo.dev, "MS Now / Morgan Stanley", a lista de X ("não escreve, não resume...") e o card de "Claude ou ChatGPT". O Kahneman aparece duas vezes na fala (3:35 e 3:53). O card dele entra só na primeira, e a AULA começa na segunda.

**Correções de nome na tela:** "Jeve/GEV" → **Jev**; "Cloud" → **Claude**; "William Stulley" → **William Stanley Jevons**; "entendimento" (8:46) → **atendimento**.

## Recursos do repertório

**Usados:**
- **CÂMERA** limpa na maior parte do tempo, com push-in lento de 1,00 → 1,03. Esta edição respira mais.
- **CÂMERA + ênfase** com punch-in **no máximo 1,08** (orientação: sem zoom exagerado), só em "não é hype", "decisão e não conversa", "onde isso entra?" e "passa longe de ser hype".
- **CÂMERA + motion**: fotos das pessoas em card de papel girado, lower-third com nome, chips e pílulas à esquerda do rosto.
- **NOTÍCIA / DEMO**: prints reais (Yahoo/Business Wire, blog TypeSafe, Vercel, OpenRouter, docs), com zoom lento de 1,00 → 1,05 e marca-texto no trecho citado. A câmera vira card no canto livre.
- **AULA 70/30**: Sistema 1 × 2, o exemplo prático e os casos de uso. O layout fica fixo dentro de cada bloco.
- **CENA**: comparação de preço e gráfico de números.
- **B-ROLL** papel recortado: sete clipes, cada um num momento de metáfora.

**Fora:** cena realista (Veo), porque a fala é expositiva e o custo não se paga; carimbo, só um no máximo; e tela final e animação de like, que não existem no canal como asset.

**Dialeto:** preset papel recortado com intensidade **sutil a equilibrada**. Folhas creme `#F0EEE6`, tinta `#141413`, e **terracota `#D97757` só para números e para o nome "Jev"**, que é a cor de destaque do vídeo. Os estados positivo e negativo usam sálvia e vermelho. Tipografia: Newsreader nos títulos e números, Inter em chips e rótulos, JetBrains Mono no "< 0,5 s" e no "US$ 0,04".

**Curva de energia:** gancho seco com câmera → pico curto de notícia (1:19–1:56) → respiro com o fundador → B-rolls do problema → aula longa e densa (3:53–8:07) com um respiro em câmera no meio (6:55–7:22) → preço → casos de uso → respiro no pequeno negócio → B-roll e números nas limitações → Jevons (B-roll) → fecho em câmera limpa.

**Zona do rosto a preservar** (frames da watch, plano único e estável): **x 700–1250, y 0–760**. O microfone ocupa x 820–1080, y 700–1080. Elementos sobre a câmera cheia ficam em **x < 660**. Na AULA, a câmera vai para a direita (x 1368, w 504), recortada no rosto.

## Timeline

Tempos em segundos do master. Os gatilhos vêm do `palavras.json` e serão refinados palavra a palavra no `edit.jsx`.

| # | início–fim | cena | entrada | gatilho (palavra @ tempo) | visual | asset |
|---|---|---|---|---|---|---|
| 1 | 0,0–12,8 | CÂMERA | — | abertura | push-in 1,00 → 1,03 | — |
| 2 | 12,8–16,0 | CÂMERA + motion | palavra | "Jev" @ 12,8 | "Jev" Newsreader 150 px terracota à esquerda + chip "TypeSafe AI" | recriado |
| 3 | 30,8–40,2 | CÂMERA + motion | mola | "o que é" @ ~31,6 · "funciona" @ ~33,5 · "não consegue" @ ~37,8 | três chips numerados à esquerda: "O que é", "Como funciona", "O que faz bem e o que não faz" | recriado |
| 4 | 40,4–45,9 | CÂMERA + ênfase | punch-in 1,06 | "hype" @ ~44,6 | pílula terracota "não é hype" | recriado |
| 5 | 45,9–58,4 | B-ROLL | wipe | "saturado" @ 45,9 | avalanche de cartões de notícia de papel empilhando na mesa; chips "GPT-5 · 5.1 · Astra" @ 49,8 | **B1** |
| 6 | 58,4–79,0 | CÂMERA | fade | respiro | pull-out 1,04 → 1,00; chip discreto "inscreva-se" @ ~70,2 | — |
| 7 | 79,0–90,6 | DEMO | corte seco | "15 de setembro" @ 79,5 | print Yahoo/Business Wire dominante, câmera em card à direita; chips "15 set · São Francisco" @ 83,4 e "TypeSafe" @ 86,2 | `prints/yahoo.png` |
| 8 | 90,6–97,0 | B-ROLL | wipe | "sigilo" @ 90,6 | laboratório de papel atrás de uma cortina que se abre para a luz | **B2** |
| 9 | 97,0–103,5 | DEMO | corte seco | "40 milhões" @ 97,0 | volta ao print com marca-texto em "$40M"; número "US$ 40 mi" conta ao lado | `prints/yahoo.png` |
| 10 | 103,5–108,5 | CENA | fade | "System One" @ 103,5 | print do blog "Introducing System One Models & Jev" em tela cheia, zoom lento até o título; destaque em "Jev" @ 106,5 | `prints/blog.png` |
| 11 | 108,5–115,7 | CENA | corte seco | "três" @ 108,5 | os prints da Vercel e do OpenRouter entram como folhas giradas; chips "Vercel · OpenRouter · Cloudflare" e rótulo "em menos de 1 semana" | `prints/vercel.png`, `prints/openrouter.png` |
| 12 | 115,7–120,6 | CÂMERA | fade | respiro | — | — |
| 13 | 120,6–130,4 | CÂMERA + motion | mola | "Diogo" @ 120,7 · "OpenAI" @ 123,6 | card girado com a foto do Diogo (recortada sem a legenda original) + lower-third "Diogo Almeida · fundador da TypeSafe" + chip "ex-OpenAI · pesquisa por trás do ChatGPT" | `prints/pessoas/diogo.png` |
| 14 | 130,4–144,0 | CENA | transformação | "conversação" @ ~132 · "não tem esse mesmo modelo de chat" @ ~134,4 | balão de chat com reticências ("IA que conversa") → seta → interruptor ("IA que decide") | recriado |
| 15 | 144,0–158,3 | CÂMERA + motion | mola | "Claude" @ ~153,5 | chips "ChatGPT · Claude · Gemini" à esquerda | recriado |
| 16 | 158,3–169,9 | CÂMERA + ênfase | punch-in 1,06 | "decisão" @ ~164,0 | pílula "decisão, não conversa" | recriado |
| 17 | 169,9–185,8 | B-ROLL | wipe | "mensagem" @ ~170,5 | esteira de papel: envelopes caindo em três bandejas; contador "milhares por dia" @ ~181,5 | **B4** (herói) |
| 18 | 185,8–191,0 | CÂMERA | fade | respiro | — | — |
| 19 | 191,0–204,9 | B-ROLL | corte seco | "consultor" @ 191,6 | consultor de terno em papel separando cartas, com relógio grande; chips "hora cheia" @ 194,2 e "demora mais, custa mais" @ 202,0 | **B5** |
| 20 | 204,9–215,0 | CÂMERA | fade | respiro | — | — |
| 21 | 215,0–229,0 | CÂMERA + motion | mola | "Kahneman" @ 215,0 · "Nobel" @ ~218,5 · "Rápido e Devagar" @ 219,7 | card girado com a foto de Kahneman + "Daniel Kahneman · Nobel de Economia, 2002" + chip do livro | `prints/pessoas/daniel.png` |
| 22 | 229,0–242,7 | CÂMERA | fade | repetição falada do Kahneman | câmera limpa | — |
| 23 | 242,7–284,3 | AULA 70/30 | transformação 1,0 s | "Dois jeitos" @ 242,7 · "Sistema 1" @ 245,2 · "tom de voz" @ 248,4 · "Sistema 2" @ 255,9 · "imposto" @ 259,7 · "modelos de conversa" @ 264,7 · "Sistema 1" @ 275,5 | duas colunas: "Sistema 1 · rápido" (raio, "tom de voz bravo") e "Sistema 2 · devagar" (engrenagem, "imposto de renda"). Chips ChatGPT/Claude/Gemini deslizam para S2; "Jev" em terracota entra sozinho em S1 | recriado |
| 24 | 284,3–287,7 | CÂMERA | transformação reversa | "exemplo prático" | pull-out | — |
| 25 | 287,7–311,4 | AULA 70/30 | transformação 1,0 s | "Imagina" @ 287,7 · "Comprei" @ 293,1 · "acesso negado" @ ~295,6 · "Não quero" @ 306,5 | cartão de mensagem de suporte à esquerda com o texto entrando enquanto é lido; marca-texto em "acesso negado" e "Não quero meu dinheiro de volta" | recriado |
| 26 | 311,4–332,0 | AULA | fade de conteúdo | "Estado" @ 318,3 · "perguntas" @ 319,5 · "escolhe" @ 327,0 | cartão ganha o rótulo ESTADO; coluna PERGUNTAS vazia; caixa "Jev" com setas ESTADO + PERGUNTAS → Jev; nota "escolhe entre as opções que você deu" | recriado |
| 27 | 332,0–376,2 | AULA | mola | "escolha" @ 332,7 · "técnico … pedagógico" @ 348,4 · "devolve" @ 356,3 | "1 · ESCOLHA: qual setor?"; barras Suporte técnico ~95% / Financeiro ~3% / Pedagógico ~2%, e a vencedora acende | recriado |
| 28 | 376,2–414,7 | AULA | mola | "nota" @ 377,3 · "irritado" @ 392,5 · "tranquilo" @ 397,5 · "agressivo" @ 403,3 · "1,8" @ ~412,8 | "2 · NOTA: quão irritado?"; régua com 4 níveis e marcador deslizando até 1,8, perto de "muito frustrado" | recriado |
| 29 | 414,7–442,2 | CÂMERA + motion | transformação reversa | "intervalares" @ ~423,4 | respiro durante a digressão estatística; chip "entre 1 e 2 = mais precisão" | recriado |
| 30 | 442,2–459,7 | AULA | transformação | "terceiro" @ 442,2 · "sim ou não" @ ~449,4 · "reembolso" @ 457,7 | o mesmo quadro volta; "3 · SIM/NÃO: pede reembolso?"; medidor 0–1 com ponteiro caindo até 0,03, "quase certeza de que não" | recriado |
| 31 | 459,7–487,3 | AULA | pulso | "ao mesmo tempo" @ 464,4 · "meio segundo" @ 465,5 · "técnico" @ 473,5 · "prioridade" @ 474,7 · "reembolso" @ 476,5 · "se" @ 481,9 | as três respostas piscam juntas; cronômetro "< 0,5 s"; três ações; o quadro limpa e fica "SE ... → ENTÃO ..." | recriado |
| 32 | 487,3–519,6 | CENA | corte seco | "preço" @ 488,0 · "output" @ 495,4 · "cálculo" @ 497,3 · "quatro centavos" @ 508,0 · "dez livros" @ 513,3 · "de graça" @ 516,6 | dois lados: balão de chat escrevendo com moeda caindo a cada palavra × Jev acendendo as opções de uma vez; depois "US$ 0,04 ≈ 10 livros" e "resposta: grátis" | recriado |
| 33 | 519,6–526,4 | CÂMERA + ênfase | punch-in 1,06 | "onde isso entra?" @ 520,0 | tipografia "Onde isso entra?" à esquerda | recriado |
| 34 | 526,4–568,9 | AULA 70/30 | transformação | "atendimento" @ 526,4 · "moderação" @ 535,2 · "vendas" @ 542,3 · "cadastro" @ 549,9 · "cai" @ ~566,0 | quatro cartões com ícone entrando um por fala (balão, escudo, funil, caixa) e acendendo quando citados; chip "custo cai" | recriado |
| 35 | 568,9–586,5 | CÂMERA | transformação reversa | "pequeno negócio" | fala direta, câmera limpa | — |
| 36 | 586,5–591,4 | CÂMERA + motion | mola | "não serve" @ ~588,7 | rótulo "ONDE NÃO SERVE" | recriado |
| 37 | 591,4–605,4 | B-ROLL | wipe | "desconfia" @ 591,4 · "prompt injection" @ ~604,2 | carta de papel com uma tira vermelha escondida passando por um portão sem guarda; chip "prompt injection" | **B8** |
| 38 | 605,4–613,3 | CÂMERA + motion | fade | "porteiro" @ 609,6 | pílula "não use como porteiro de dado sensível" | recriado |
| 39 | 613,3–641,1 | CENA | corte seco | "200" @ 616,9 · "400" @ 620,1 · "própria" @ ~621,6 · "independente" @ 626,2 · "6 a 7" @ ~631,6 · "80%" @ 635,4 | gráfico de barras: "anúncio: 200× mais rápido / 400× mais barato" (rótulo "teste da própria empresa") ao lado de "teste independente: 6–7× mais rápido / 80% mais barato" | recriado |
| 40 | 641,1–646,0 | CÂMERA + motion | fade | "menores" @ ~644,2 | chip "menor que o anunciado, ainda relevante" | recriado |
| 41 | 646,0–655,5 | CÂMERA + motion | mola | "homenagem" @ 646,9 · "economista" @ ~652,9 | card girado com o retrato de Jevons + "William Stanley Jevons · economista inglês, séc. XIX" | `prints/pessoas/william.png` |
| 42 | 655,5–668,8 | B-ROLL | wipe | "máquina a vapor" @ 656,4 · "aumentou" @ ~663,6 | máquina a vapor com pilha de carvão → várias máquinas surgindo (start → end); chip "menos carvão por máquina → mais carvão no total" | **B9** (2 imagens) |
| 43 | 668,8–682,9 | B-ROLL | fade | "aposta" @ 668,8 · "quase nada" @ ~673,4 | mapa de cidade em papel com pequenas luzes terracota acendendo (loja, banco, atendimento); chip "custo por decisão ↓" | **B10** |
| 44 | 682,9–719,4 | CÂMERA + ênfase | fade + punch-in 1,06 | "hype" @ ~684,8 · "80%" @ ~705,4 · "7 vezes" @ ~707,4 | pílula "não é hype" (callback do #4); depois chips "80% mais barato · até 7× mais rápido"; pull-out em 1,00 | recriado |
| 45 | 719,4–739,3 | CÂMERA | — | "like" @ ~724,2 | câmera limpa; chip discreto "deixe seu like · inscreva-se" 724–730 | recriado |

Resumo de volume: 7 B-rolls, 6 cenas de print/notícia, 3 fotos de pessoas, 4 blocos de AULA e cerca de 45% do tempo em câmera limpa ou com um único chip.

## Assets a gerar (histórico — serviço de IA pago da época)

Exemplo de como a seção de assets gerados era registrada. Hoje, esses B-rolls sairiam de outras fontes: imagens/vídeos gerados por outro provedor, banco de mídia ou — mais comum — cenas reconstruídas em código (Remotion/HyperFrames), que são gratuitas e revisáveis. Os nomes de modelo abaixo são do serviço antigo e só fazem sentido como referência de formato.

Todos em papel recortado, sem texto. Imagens com `nano_banana_pro` 2k 16:9 (2 cr). Vídeos com `kling3_0` mode `pro`, sound `off` (~1,75 cr/s), exceto o herói.

| asset | cena | imagem | vídeo | custo |
|---|---|---|---|---|
| B1 | avalanche de cartões de notícia sobre a mesa | 1 img | kling pro 8 s | 2 + 14 |
| B2 | laboratório atrás de uma cortina que se abre | 1 img | kling pro 6 s | 2 + 11 |
| B4 | esteira: envelopes caem em três bandejas (**herói**) | 1 img | `seedance_2_0` 1080p 8 s | 2 + 72 |
| B5 | consultor de terno separando cartas, relógio grande | 1 img | kling pro 10 s | 2 + 18 |
| B8 | carta com tira vermelha passando por portão sem guarda | 1 img | kling pro 8 s | 2 + 14 |
| B9 | máquina a vapor + carvão → várias máquinas (start/end) | 2 img | kling pro 10 s | 4 + 18 |
| B10 | mapa de cidade com luzes terracota acendendo | 1 img | kling pro 10 s | 2 + 18 |
| **subtotal** | | **18 cr** | **165 cr** | **183 cr** |
| margem de refação | ~4 imagens + 2 vídeos kling | 8 | ~30 | 38 |
| **total estimado** | | | | **~220 cr (teto 260)** |

Fica bem abaixo do limite de 400–500, como pede uma edição moderada. Se quiser gastar mais, as melhores trocas são B9 em Seedance (+~55 cr) ou mais dois B-rolls: #14 (conversa → decisão) e #32 (preço), com +~30 cr cada. Nesse caso, eles deixam de ser recriados na montagem.

Tudo o que é texto, chip, AULA, gráfico, print e foto é montado no Higgsedit, com 0 crédito.

## Saída

`edicoes/003. jev-nao-e-hype/jev-nao-e-hype_final.mp4`

## Resultado

- Render em 5 blocos no sandbox (`--range`, 3 workers; com 7 faltou memória), unidos localmente com o áudio do master copiado bit a bit.
- Validação: 1920×1080, 29,97 fps, h264 + aac, duração 739,285 s contra 739,272 s do master (0,4 quadro), uma trilha de áudio, volume igual (média de −22,3 dB, pico de −0,6 dB).
- Ajustes do QC: o card da câmera mostrava a planta (a mídia tinha geometria fixa); layout da resposta 2 da AULA; "≈" e "→" sem glifo nas fontes; exemplo prático contínuo em AULA (242,7–487,3 s), sem voltar para a câmera na digressão.
- Créditos: 144 (8 imagens `nano_banana_pro` + 6 Kling pro + 1 Seedance).
