---
name: code-animation
description: >-
  Renderiza inserts animados de código em tela cheia — diffs antes/depois em que só os tokens
  alterados se movem, trechos que se digitam sozinhos e morphs de refatoração em vários estágios —
  a partir de arquivos-fonte reais, via renderizador HyperFrames. Entrega MP4, ou overlay com
  alpha quando necessário. Use para "anima esse código", "mostra o antes e depois", "anima o diff",
  "faz o código se digitar". NÃO use para cards/lower-thirds/zooms sobre gravação
  (overlay-graphics), corte (rough-cut), legendas/verticais (shorts) ou thumbnails (thumbnail).
---

# Code Animation

Transforma uma mudança de código em insert animado de tela cheia. A câmera nunca vê um editor —
o trecho é renderizado a partir de fontes reais: quadro limpo, tipo enorme, e **só se move o que
realmente mudou**.

É irmã da `overlay-graphics`: aquela decora gravação existente; esta produz gravação que não
existia.

**Filtro de escopo.** O insert vale a pena quando a mudança é pequena e a mensagem é "olha o que
moveu". Um arquivo inteiro rolando não é animação — é screen recording; use o screen-share real
com `spotlight` (overlay-graphics). Regra prática: acima de ~14 linhas, enxugue ou não anime.

## Entradas

- **Um, dois ou três arquivos-fonte** — um por estado, em ordem. Trechos reais e compiláveis,
  aparados às linhas que importam. São fixtures, não código do repo.
- Opcional: `transcript.output.json` do rough-cut, para posicionar o insert no momento em que a
  mudança é explicada na fala.

Trabalhe em `projetos/<NNN. slug>/trabalho/code-animation/<nome>/` com `cache/` para frames
regeneráveis. Sem projeto, use `<pasta_da_fonte>/code-animation/<nome>/`. Entregue em
`edicoes/<NNN. slug>/`.

## Biblioteca de blocos

Vendorada em `assets/blocks/` do registry HeyGen HyperFrames (Apache 2.0), pinada em
`hyperframes@0.7.77`. Arquivos upstream intactos — a identidade visual é aplicada no build por
`scripts/build.mjs`, mantendo o bloco diffável. Licença e proveniência: `assets/blocks/LICENSE`
e `assets/blocks/UPSTREAM.md` (preserve-os).

| Bloco | `--seq` | Estados | Duração | O que é |
|---|---|---|---|---|
| `code-diff.html` | `diff` | 2 | 6s | antes → depois; linhas removidas colapsam em vermelho, adicionadas expandem em verde, tokens intactos deslizam |
| `code-typing.html` | `feature` | 1 | 5s | o trecho se digita com cursor e numeração |
| `code-morph.html` | `morph` | 3 | 7s | um trecho vira outro, duas vezes — refatoração em 3 estágios |

**Escolha pela intenção:** "aqui está a mudança" → `code-diff`; API nova apresentada pela
primeira vez → `code-typing`; migração em estágios → `code-morph`.

Blocos novos: `npx hyperframes@0.7.77 add <nome> --dir <tmp>`, confira o shell CSS
(`grep "width: 1380px"`), vendore, renderize um trecho real, mostre à pessoa e só então adote.

## Passo 0 — setup único por máquina

```bash
cd .devin/skills/code-animation/scripts && npm ci
```

Requer Node 22+ e ffmpeg. O renderer baixa um Chrome próprio em `~/.cache/hyperframes/chrome`
na primeira execução (~25 s). Verifique com `npx hyperframes@0.7.77 doctor` (avisos de whisper/TTS/
MusicGen são opcionais e irrelevantes aqui). Telemetria: `npx hyperframes@0.7.77 telemetry disable`.

A versão 0.7.77 é **pinada de propósito** — os blocos vendorados dependem do contrato
(`data-composition-id`, `window.__timelines`) que ainda muda no pré-1.0. Re-verifique os blocos
antes de subir a versão. O pacote completo `heygen-com/hyperframes` já está instalado neste repo
e não conflita — esta skill usa o CLI pinado e os blocos locais.

## Passo 1 — arquivos de estado

Um arquivo por estado, código real, aparado com força. Mantenha os estados **alinhados**: a
animação só impressiona quando a maioria dos tokens sobrevive à edição — não reformate, renomeie
ou re-indente entre estados a menos que isso SEJA a mudança.

Imprima os estados e o bloco pretendido; tokenize, faça build e snapshot antes de renderizar.
Guarde o projeto gerado para revisões; estado alterado invalida tokens e render.

## Passo 2 — tokenizar

Os blocos NÃO aceitam texto puro: cada token é um span com chave, e **token que mantém a chave
entre estados é o que desliza** — a atribuição de chaves É o diff. `tokenize.mjs` roda Shiki em
cada estado e encadeia um LCS entre estados consecutivos.

```bash
node .devin/skills/code-animation/scripts/tokenize.mjs \
  --seq diff --lang java --theme vitesse-dark \
  --out tokens.json before.java after.java
```

`--seq` tem que bater com o bloco. `--lang` é qualquer id do Shiki (`java`, `python`, `ts`,
`bash`, `json`…). Saída típica: `diff: 44 tokens → 53 tokens · carried (glide): 43`.

**Leia o número de carried.** Carry alto = animação legível. Carry baixo = os estados divergiram
(geralmente reformatação) e tudo vai se redigitar. Corrija os fixtures e rode de novo.

## Passo 3 — build e render

`build.mjs` aplica as trocas de identidade, dimensiona o card ao trecho e emenda os tokens.

```bash
node .devin/skills/code-animation/scripts/build.mjs \
  --block .devin/skills/code-animation/assets/blocks/code-diff.html \
  --tokens tokens.json --out proj/index.html --filename UserController.java

printf '{"name":"%s","width":1920,"height":1080,"fps":30}\n' "$NOME" > proj/hyperframes.json
```

O renderer exige `index.html` na **raiz do projeto** + `hyperframes.json`. Snapshot o início, a
mudança e o estado final e inspecione antes de codificar. MP4 por padrão; o comando alpha (WebM)
só quando a edição precisar de overlay:

```bash
(cd proj && npx -y hyperframes@0.7.77 render . \
  --output renders/$NOME.mp4 --fps 30 --quality high --gpu)

# overlay transparente OPCIONAL (rode da raiz do repo, como o build acima)
node .devin/skills/code-animation/scripts/build.mjs \
  --block .devin/skills/code-animation/assets/blocks/code-diff.html \
  --tokens tokens.json --out alpha/index.html --filename UserController.java --transparent
cp proj/hyperframes.json alpha/
(cd alpha && npx -y hyperframes@0.7.77 render . \
  --output renders/$NOME-overlay.webm --format webm --fps 30 --quality high)
```

`proj/`, `alpha/` e `tokens.json` ficam em `projetos/<NNN. slug>/trabalho/code-animation/<nome>/`
(use esses paths completos no lugar dos curtos acima).

`--fps` igual ao do vídeo (`ffprobe … r_frame_rate`). Para 4K: `--resolution landscape-4k`.
Se `build.mjs` avisar que swaps de marca não bateram, o CSS upstream mudou — corrija a lista de
swaps, nunca edite o bloco vendorado.

## Passo 4 — verificar e entregar

- `npx hyperframes@0.7.77 snapshot . --at <t1>,<t2> --no-end --output snaps` e **olhe a folha**:
  nada cortado na borda direita, estado final é o código certo, card não virou tirinha.
- Componha uma prévia com a narração em volta (plano de overlay-graphics + `composite.py`).
  O **change**, não o início da animação, deve alinhar com a explicação falada.
- `code-diff` termina ~3.6s dos 6s — a cauda é hold estático (bom handle de edição).
- Entregue MP4 em `edicoes/<NNN. slug>/`; alpha master em `projetos/<NNN>/trabalho/gfx/overlays/`.
  Reporte: bloco, estados, carry count, destino dos arquivos.

## Composição do overlay (armadilha do alpha VP9)

O WebM carrega alpha VP9, mas o ffmpeg usa o decoder **nativo** de vp9 por padrão — e ele
descarta o alpha em silêncio (caixa preta opaca, sem aviso). Force libvpx **antes** do input:

```bash
ffmpeg -y -i footage.mp4 -c:v libvpx-vp9 -i overlay.webm \
  -filter_complex "[1:v]setpts=PTS-STARTPTS+12.0/TB[o];[0:v][o]overlay=eof_action=pass[v]" \
  -map "[v]" -map 0:a -c:v libx264 -preset fast -crf 19 -pix_fmt yuv420p -c:a copy out.mp4
```

`-c:v` é sensível à posição: vale para o input seguinte. Prove antes de entregar — composite
sobre magenta e leia o pixel do canto (`fd00fc` = alpha ok, `000000` = falhou):

```bash
ffmpeg -v error -y -f lavfi -i color=c=magenta:s=1920x1080 -c:v libvpx-vp9 -i overlay.webm \
  -filter_complex "[0:v][1:v]overlay=shortest=1" -ss 3.6 -frames:v 1 /tmp/proof.png
ffmpeg -v error -i /tmp/proof.png -vf "crop=8:8:0:0,scale=1:1" -f rawvideo -pix_fmt rgb24 - | xxd -p
```

## Diário de armadilhas (lições do upstream)

- Blocos são **pré-tokenizados**: `window.__TOKENS` é embutido no HTML e precisa ser reescrito —
  é por isso que `tokenize.mjs` existe.
- **Chaves de token são o diff.** Chaves iguais deslizam; chaves novas leem como adicionado.
- Os blocos fixam editor **1380×800** independente do conteúdo — `build.mjs` dimensiona pelo
  número de linhas e linha mais longa. Orce o chrome do diff (22px sinal + 14px indent) além do
  gutter de 104px e padding de 44px, ou a linha mais longa clipa na direita.
- VP9 alpha: ffprobe reporta `pix_fmt=yuv420p`; só a tag `ALPHA_MODE: 1` denuncia. Sempre rode a
  prova do magenta.
- `code-morph` em **linha única longa** renderiza uma tira 1380×174 quebrada. Morph quer estados
  multi-linha; para one-liner use `code-diff`.
- `snapshot` recebe DIR de projeto, não `--composition <arquivo>` (o flag listado na doc não
  existe em 0.7.77). Confie no `--help`, não no site.
- Upstream manda comentário `<!-- hyperframes-registry-item -->` **antes** do doctype, que dispara
  o próprio StaticGuard. `build.mjs` remove.
- Blocos puxam GSAP de CDN jsDelivr no render — pipeline "local" precisa de rede. Vendorize o
  GSAP se virar problema.
