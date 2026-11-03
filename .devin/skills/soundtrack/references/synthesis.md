# Cookbook de síntese (kit)

Todas as funções recebem `ctx` (OfflineAudioContext) e `dest` opcional (default: saída).
Notas como string `"A4"`, `"F#3"`, `"Bb2"` ou Hz direto. `spb = 60/bpm`.

## Percussão

```js
kit.kick(ctx, t, {dest, gain:0.9, base:160})        // corpo: seno 160→45Hz + click de ruído
kit.snare(ctx, t, {dest, gain:0.55})                // ruído bandpass 1800Hz + blip triangle 190Hz
kit.hat(ctx, t, {dest, gain:0.22, open:false})      // ruído highpass 7.8kHz; open=true = hat aberto
```

Padrões úteis: four-on-the-floor = kick em todo tempo; boom-bap = kick em 1 e "e" do 3;
trap = hat em 1/8 ou 1/16 com `open` ocasional.

## Harmônico/melódico

```js
kit.pad(ctx, ['A2','E3','C4'], t, dur, {dest, gain:0.15, type:'sawtooth', cutoff:1100, detune:9})
   // 2 osc desafinados por nota → LP; attack/release longos → cama harmônica
kit.bass(ctx, 'A1', t, dur, {dest, gain:0.4, type:'triangle', cutoff:700})
kit.arp(ctx, ['C4','E4','G4','B4'], {t, step:0.15, type:'square', gain:0.15, cutoff:2500})
kit.tone(ctx, {freq:'A4', type:'sine', t, dur:0.5, gain:0.4, attack:0.005, release:0.08,
               detune:0, slide:880, dest})           // slide = glissando até Hz
```

`kit.freq('C#4')` → Hz; `kit.midi('C#4')` → número midi.

## Dinâmica e transição

```js
const mus = kit.bus(ctx, 0.8, out);                 // bus = GainNode ligado a `out`
kit.pump(ctx, mus.gain, {bpm:100, beats:64, amount:0.35, release:0.28})
   // afoga `mus` a cada tempo — sidechain falso "quatro no chão"
kit.whoosh(ctx, t, {dest, dur:0.7, gain:0.3, from:300, to:6000})
   // riser de ruído com varredura de bandpass — transição/impacto
const out = kit.limit(ctx);                          // pseudo-limiter: threshold -8dB, ratio 12
```

## Utilidades

- `kit.noiseBuffer(ctx, segundos, seed)` — buffer de ruído branco determinístico.
- `kit.mulberry32(seed)` — PRNG; use para escolhas "aleatórias" reproduzíveis.
- `kit.adsr(param, t, dur, {attack, release, peak})` — envelope em qualquer AudioParam.

## Receitas rápidas

**Bed corporativo calmo** (YouTube tech): pad sawtooth LP 900Hz, acordes maiores em 4/4,
kick leve nos tempos, hat no contratempo, `pump` amount ~0.1, master ~-14dBFS RMS.

**Tensão/virada**: drone seno grave + `whoosh` 0.8s terminando exatamente no corte; depois
silêncio de 100–200ms antes do próximo bloco — o "ar" vende o impacto.

**UI beep** (notificação, pop): `tone` square 1200Hz, dur 0.06s, attack 0.001; para "sucesso",
dois tons subindo (ex.: E5→A5).

**Lo-fi**: pad com `type:'triangle'`, cutoff 700, hats abertos esparsos, kick macio
(`base:120, gain:0.3`), swing deslocando hats de +8ms.

**Trailer épico**: drones em quintas (A1+E2), `arp` ascendente ganhando densidade, `whoosh`
para cada virada, `limit` no master.

## Boas práticas

- Sempre passe o master por `kit.limit(ctx)` e mire peak ≤ −1.5dBFS.
- Mono/stereo: para espalhar, crie 2 `tone`/`osc` com `detune` ±8 e `StereoPannerNode` ±0.4.
- Crescendos: automate `param.linearRampToValueAtTime`/`exponentialRampToValueAtTime` no
  `gain` de um bus — nunca mude o código entre renders sem anotar.
- Trilha sob fala: alvo RMS da música ~−20dBFS antes do ducking; a fala manda.
