---
name: soundtrack
description: >-
  Cria trilha sonora e SFX 100% por código, sem samples nem arquivos de áudio externos: o
  "score" é um módulo JS que agenda osciladores, ruído com seed, envelopes e drum-synths num
  OfflineAudioContext; renderiza WAV PCM16 em Chromium headless e incorpora ao MP4 com ffmpeg
  (mix simples ou ducking sidechain sob a fala). Use para "cria uma trilha", "música de fundo",
  "faz um som de transição/whoosh", "SFX", "beeps de interface", "trilha sonora por código",
  "tema de abertura". Não faz: mixar áudio já existente na composição (hyperframes-audio /
  teaser), limpar podcast (podcast-edit), voz/narração (TTS está no roadmap; media-use).
---

# Soundtrack (trilha sonora por código)

Toda a trilha é **sintetizada**: Web Audio API num `OfflineAudioContext` dentro do Chromium
headless → WAV PCM16 → ffmpeg junta ao MP4. Sem arquivos de áudio externos, sem samples, sem
rede. Reprodutível: o mesmo score gera o mesmo som (ruído usa PRNG com seed, nada de
`Math.random`/`Date.now`); entre execuções pode haver diferença de ±1 LSB por arredondamento de
ponto flutuante do Chromium — inaudível, mas o hash do WAV pode mudar.

## Conceito

- **Score** = um módulo ES que exporta `duration` (segundos) e `compose(ctx, kit, opts)`.
  Você escreve a música em código: notas (`"A4"`, `"F#3"`), ritmo, timbres, envelopes.
- **kit** = helpers de `scripts/synth.js` injetados na página: `tone`, `kick`, `snare`, `hat`,
  `pad`, `bass`, `arp`, `pump` (ducking por beat), `whoosh`, `bus`, `limit` (pseudo-limiter),
  `noiseBuffer`, `freq`, `mulberry32`, `adsr`.
- **Render** = `scripts/render-score.mjs` abre o score no Chromium, constrói
  `OfflineAudioContext` (48kHz estéreo por padrão), chama `compose`, renderiza e grava WAV.

## Fluxo

```bash
# setup: `npm run instalar` já instala as dependências e o navegador (confira com `npm run verificar`)

# 1. escreva o score em projetos/<NNN. slug>/trabalho/audio/<nome>.js (veja examples/)
# 2. renderize
node .devin/skills/soundtrack/scripts/render-score.mjs \
  --score "projetos/<NNN>/trabalho/audio/tema.js" \
  --out   "projetos/<NNN>/trabalho/audio/tema.wav"
# saída imprime duração, peak e RMS — peak deve ficar abaixo de ~-1.5dBFS (o kit.limit ajuda)
```

O renderer informa peak/RMS. Se clipar (peak ≥ 0dBFS), baixe gains e/ou roteie tudo por
`kit.limit(ctx)` como master.

## Formato do score

```js
export const duration = 20;
export const bpm = 100;

export function compose(ctx, kit) {
  const { pad, kick, hat, bus, pump, limit } = kit;
  const out = limit(ctx);                 // master
  const mus = bus(ctx, 0.8, out);         // bus da música
  pump(ctx, mus.gain, { bpm, beats: 34 }); // respiro a cada tempo
  const spb = 60 / bpm;
  pad(ctx, ['A2','E3','C4'], 0, 4*spb, { dest: mus, gain: 0.15 });
  for (let i = 0; i < 8; i++) kick(ctx, i*spb, { dest: mus, gain: 0.35 });
  for (let i = 0; i < 16; i++) hat(ctx, i*spb/2 + spb/2, { dest: mus, gain: 0.1 });
}
```

Notas: `"C4"`, `"F#3"`, `"Bb2"` ou Hz direto. Helpers aceitam `dest` (default = destination).
Receitas de timbre (drums, pads, leads, risers, ui-beeps): [references/synthesis.md](references/synthesis.md).
Exemplo completo: [examples/score-lofi.js](examples/score-lofi.js).

## Incorporar ao vídeo (ffmpeg)

**Vídeo sem fala** (trilha substitui/é o único áudio):

```bash
ffmpeg -y -i video.mp4 -i tema.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out.mp4
```

**Mix sob a fala** (nível fixo):

```bash
ffmpeg -y -i video.mp4 -i tema.wav -filter_complex \
  "[1:a]volume=0.15[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k out.mp4
```

**Ducking sidechain** (música cede quando a voz fala — mais profissional):

```bash
ffmpeg -y -i video.mp4 -i tema.wav -filter_complex \
  "[0:a]aformat=channel_layouts=stereo,asplit[voice][key];\
   [1:a]volume=0.5[mus];\
   [mus][key]sidechaincompress=threshold=0.02:ratio=8:attack=0.02:release=0.4:makeup=1[ducked];\
   [voice][ducked]amix=inputs=2:duration=first:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k out.mp4
```

`threshold` controla quando a música abaixa; `release` o tempo de volta. Em teaser/timelines
com vários shots, prefira `teaser/scripts/montage.py` — ele já tem envelopes de duck por trilha.

## Verificar antes de entregar

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 out.mp4
ffmpeg -i out.mp4 -map 0:a -af volumedetect -f null -   # max_volume < -1.5dB, sem clip
```

Confira: duração da trilha ≥ do trecho pretendido (ou loop intencional), música não engole a
fala (sidechain ou volume baixo), entrega em `edicoes/<NNN. slug>/`.

## Regras

- **Zero samples externos**: se o score carregar `fetch`/arquivo de áudio, está errado — tudo
  nasce de oscilador/ruído/filtro. Determinismo obrigatório: ruído só via `noiseBuffer(seed)` ou
  `mulberry32`.
- Score e WAV intermediários em `projetos/<NNN>/trabalho/audio/`; final em `edicoes/`.
- Trilha serve ao vídeo: pad/bed por padrão; drops e SFX pontuais em momentos de virada.
- Não é narração — para voz sintética, ver roadmap (TTS) ou `media-use`.
