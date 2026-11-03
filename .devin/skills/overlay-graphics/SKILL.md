---
name: overlay-graphics
description: >-
  Compõe elementos gráficos pré-construídos (lower-third, título de seção, callout, spotlight,
  nudge de inscrição) sobre vídeo já editado, sincronizados à fala. Use quando falarem
  "adiciona lower-thirds", "mostra texto na tela", "chamada para inscrever", "destaca esse
  trecho". Não trata de: corte (rough-cut), legendas (shorts ou Remotion), thumbnails
  (thumbnail), vídeo do zero (hyperframes).
---

# Overlay Graphics (gráficos sobre o vídeo)

Renderiza cards HTML em PNG+alpha / MOV ProRes 4444 (`scripts/render.mjs`, Chromium headless,
determinístico) e os compõe sobre o vídeo base com um plano `graphics.json`
(`scripts/composite.py`). O vídeo base nunca é tocado: a saída é um arquivo novo `_gfx.mp4`.

Contrato completo (parâmetros, cache, schema do plano, alpha): [references/rendering.md](references/rendering.md).
Movimentos de câmera (punch/push): [references/camera-moves.md](references/camera-moves.md), só se planejados.

## Relógio: sempre o do vídeo base

Todos os tempos do plano estão no relógio do vídeo que recebe os gráficos.

- Depois de um `rough-cut`, use `transcript.output.json` (já está no relógio do `_rough.mp4`) —
  não mapeie de novo.
- Âncora no relógio da **fonte** bruta: converta com
  `.venv/bin/python .devin/skills/rough-cut/scripts/pipeline.py map --manifest edit.json --clip <id> --time <s>`.
  Trecho cortado não tem mapa: escolha outro momento. Só encaixe uma borda (até 0.3 s) depois de
  ouvir e confirmar que a palavra sobreviveu ao corte.
- Mudança de velocidade é decisão do `rough-cut` (antes dos gráficos): refaça o manifesto e
  reancore. Se o corte mudar, o `manifest_id` do plano fica inválido.

Extraia quadros reais de cada intervalo planejado (`assistir`/ffmpeg): câmera, painéis e
terminais mudam dentro do mesmo clipe.

## Escolha o gráfico pela função

| Template (`assets/templates/`) | Uso e padrões | Parâmetros |
|---|---|---|
| `lower-third.html` | Apresentar nome/função; ~6 s, uma vez, na autoapresentação | `name`, `role` |
| `section-title.html` | Troca real de capítulo; ~4 s, canto inferior esquerdo (ou direito se livre) | `num`, `title`, `kicker`, `side` |
| `callout.html` | Repo, URL, versão ou número útil; ~5 s | `label`, `value`, `side` |
| `subscribe-nudge.html` | Uma vez, num respiro a ~60–75% do vídeo, sem cobrir explicação; ~6 s | `channel`, `side` |
| `spotlight.html` | Escurece em volta de um retângulo medido (código/resultado); 4–5 s | `x`, `y`, `w`, `h` (frações), `label`, `dim` |

`side: "right"` só quando o quadro real comporta. Textos longos estouram: encurte a cópia.

## Sincronizar o REVEAL com a fala

O momento que importa é a revelação, não o primeiro quadro da animação. Calcule você mesmo:

`start = tempo_da_palavra - offset_de_reveal`

| Template | Offset aproximado |
|---|---|
| lower-third | 1.8 s (nome); 2.15 s (função) |
| callout | 0.42 s + min(1.1 s, caracteres do `value` × 0.045 s) |
| section-title | 0.78 s |
| subscribe-nudge | 1.9 s |
| spotlight | 0.4 s (caixa); 0.5 s (rótulo) |

Se `start` der negativo, encurte a entrada ou mude para a próxima batida com sentido — nunca
corte uma revelação calada. Reconfira os offsets com `seek()` se o template mudar.

## Fluxo (pôster → prévia → final)

Trabalhe em `projetos/<NNN. slug>/trabalho/gfx/`; paths absolutos no plano.

```bash
S=.devin/skills/overlay-graphics
G="$PWD/projetos/<NNN. slug>/trabalho/gfx"
mkdir -p "$G/overlays" "$G/cache"

# 1. pôster de 1 quadro para revisar texto, contraste e posição contra um quadro real
echo '{"name":"Ana Souza","role":"Engenheira"}' > "$G/lower-third.json"
node $S/scripts/render.mjs --template $S/assets/templates/lower-third.html \
  --params-file "$G/lower-third.json" --duration 6 --fps 30 --poster "$G/poster-lt.png" --at 2.2

# 2. render com alpha (MOV ProRes 4444) — --fps igual ao do vídeo base (ffprobe r_frame_rate)
node $S/scripts/render.mjs --template $S/assets/templates/lower-third.html \
  --params-file "$G/lower-third.json" --duration 6 --fps 30 \
  --out "$G/cache/lower-third" --mov "$G/overlays/lower-third.mov"
```

3. Escreva `$G/graphics.json` (schema em rendering.md): `video` (o `_rough.mp4` ou master),
   `video_identity` (`size` e `mtime_ns` de `Path(video).stat()`), `edit_manifest` +
   `manifest_id` (do `edit.json`, se veio do rough-cut) e `clips[]` com `asset`, `start`,
   `duration`, `anchor` (a fala) e `purpose`.

```bash
# 4. prévia curta, em resolução menor, com a narração em volta — confira entrada, reveal e saída
.venv/bin/python $S/scripts/composite.py --plan "$G/graphics.json" \
  --start 0 --duration 10 --width 960 --out "$G/preview.mp4"

# 5. final em resolução nativa (arquivo novo, ao lado do _rough.mp4)
.venv/bin/python $S/scripts/composite.py --plan "$G/graphics.json" \
  --out "edicoes/<NNN. slug>/<nome>_gfx.mp4"
```

Sem hardware H.264 (fora do Mac), acrescente `--encoder software` ao `composite.py`. Um quadro
parado não prova sincronia: assista a prévia com áudio. Corrija só o asset/posição afetado.

## Logo depois de um rough-cut

Quando o `rough-cut` encadeia esta skill, o entregável é o `<nome>_gfx.mp4` ao lado do
`<nome>_rough.mp4` intocado. Faça pôster e prévia, use só templates aceitos e termine com um
relatório único dos dois arquivos. Direção visual nova = descreva a ideia, não improvise.

## Regras

- Pôster antes de render; prévia com áudio antes do final.
- Nunca cubra olhos, boca ou contorno do rosto — confira em quadros reais. Em screen-share
  claro, use painel escuro atrás do texto.
- Nada de texto dentro de imagem gerada por IA.
- Templates novos: HTML 1920×1080 autocontido com `window.setParams(obj)` e `window.seek(t)`;
  animação função pura de `t` (sem transições CSS nem timers).
- Testes: `node --test $S/scripts/render-options.test.mjs` e `.venv/bin/python $S/scripts/test_media.py`.

Falhas históricas: [references/history.md](references/history.md).
