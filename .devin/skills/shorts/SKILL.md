---
name: shorts
description: >-
  Extrai shorts/reels verticais 9:16 de episódios longos já editados. Fases: selecionar clipes
  (rubrica de hook/payoff), definir bordas por palavra, reenquadrar (crop de rosto ou layout
  empilhado para screen-share), embutir legendas karaoke com a palavra ativa em destaque,
  normalizar loudness. Use para "faz um short", "transforma em reel/TikTok", "extrai clipes
  verticais". Não faz: corte bruto (rough-cut), gráficos (overlay-graphics), thumbnails.
---

# Shorts (verticais 9:16)

Pipeline longo→vertical. Cada short sai como arquivo novo em `edicoes/<NNN. slug>/shorts/` —
a fonte nunca é tocada. Trabalho em `projetos/<NNN. slug>/trabalho/shorts/`.

## Entradas

- Episódio **final** (ex.: `_rough.mp4` aprovado) + a transcrição no **mesmo relógio**
  (`trabalho/rough-cut/transcript.output.json`, ou o JSON whisper do próprio vídeo).
- Classifique: `talking-head` (crop de rosto), `screen-share` (layout empilhado), `mixed`
  (decida por clipe).

## 1. Escolher os clipes — a parte que importa

Um bom short é autocontido: pergunta→resposta, setup→punchline, problema→solução, opinião
completa. Avalie a transcrição contra a rubrica, **proponha com timestamps e justificativa, e
aguarde aprovação** antes de extrair.

- Hook dentro dos 2 primeiros segundos; payoff no fim. Sem contexto externo necessário.
- No máximo ~3 clipes por episódio em um batch. Liste também os candidatos **descartados** e por
  quê — a pessoa pode discordar da rubrica.

## 2. Bordas e palavras do clipe

Início = onset da palavra do hook −0.15 s; fim = fim da última palavra do payoff +0.4 s. Nunca
corte no meio de palavra/frase. Depois, extraia as palavras relativas ao clipe e os parâmetros
das legendas:

```bash
S=.devin/skills/shorts; G=.devin/skills/overlay-graphics
W="$PWD/projetos/<NNN. slug>/trabalho/shorts"
.venv/bin/python $S/scripts/extract_words.py \
  --json "projetos/<NNN. slug>/trabalho/rough-cut/transcript.output.json" \
  --start 12.25 --end 41.80 --out "$W/clip1-words.json" \
  --captions-params "$W/clip1-captions.json" --style padrao
# imprime OUT_A/OUT_B = -ss/-to no vídeo
```

Estilos de legenda: `padrao`, `hormozi`, `beast`, `clean`, `mono` (`assets/captions.html`).
Fontes do sistema com fallback (Arial Black/Helvetica); para outra fonte, instale-a no sistema.

## 3. Reenquadrar (meça antes — nunca adivinhe)

Extraia quadros do trecho (skill `assistir`) e meça o centro do rosto em pixels.

- **Talking-head (1920×1080):** janela 9:16 na altura inteira = `crop=608:1080:X:0`, com
  `X = centro_do_rosto − 304`, limitado a `0…1312`. Zoom leve de 1.15–1.3×: reduza a altura
  (ex.: 1.2× → `crop=506:900:X:Y`), sempre com dimensões pares. Crop estático por clipe.
- **Screen-share:** empilhado — conteúdo no topo (zoom na região ativa), câmera embaixo:
  `[0:v]crop=CW:CH:CX:CY,scale=1080:-2[top];[0:v]crop=BW:BH:BX:BY,scale=1080:-2[cam];[top][cam]vstack,crop=1080:1920:0:0,setsar=1[v]`.
  As alturas escaladas precisam somar ≥1920: alargue uma das caixas (mantendo a proporção).
  Confirme que a câmera está na região durante o clipe inteiro.
- **Mixed:** por segmento. Um crop de rosto sobre um gráfico explicativo pode destruir o sentido.

## 4. Legendas + render + loudness (um comando)

```bash
# legendas karaoke em MOV com alpha, no tamanho vertical (--duration = OUT_B − OUT_A)
node $G/scripts/render.mjs --template $S/assets/captions.html \
  --params-file "$W/clip1-captions.json" --width 1080 --height 1920 \
  --duration 29.55 --fps 30 --out "$W/cache/clip1" --mov "$W/clip1-captions.mov"

mkdir -p "edicoes/<NNN. slug>/shorts"
ffmpeg -nostdin -y -ss 12.25 -to 41.80 -i "edicoes/<NNN. slug>/<nome>_rough.mp4" -i "$W/clip1-captions.mov" \
  -filter_complex "[0:v]crop=608:1080:946:0,scale=1080:1920,setsar=1[v];[v][1:v]overlay=0:0:eof_action=pass[out]" \
  -map "[out]" -map 0:a -af "loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart "edicoes/<NNN. slug>/shorts/short-01.mp4"
```

- `--fps` das legendas = fps do vídeo. Screen-share: troque o `crop` pelo grafo empilhado.
- O ffmpeg do Homebrew não tem `drawtext`/`subtitles`: por isso as legendas são PNG/MOV via
  navegador. MOV ProRes entra direto; **não** use `-c:v libvpx-vp9` antes dele (isso é só para WebM).
- Loudness: −14 LUFS (plataformas verticais). Confira com `ffmpeg -i short.mp4 -af ebur128 -f null -`.

## 5. Entrega e handoff

`edicoes/<NNN. slug>/shorts/short-01.mp4`… + um `notes.md` por batch (fonte, intervalos, rubrica,
o que ficou de fora). Revise um quadro no meio e no hook (legenda certa, enquadramento, nada
cortado). Sugira thumbnails (`thumbnail`) se fizer sentido.

## Regras de ouro

- Proponha→aprove→extraia. Nunca extraia sem aprovação dos clipes.
- Borda por palavra, sempre. Dimensões de crop pares.
- Saída 1080×1920, H.264, `+faststart`; fonte intocada.

Histórico de armadilhas: [references/history.md](references/history.md).
