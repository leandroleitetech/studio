// Exemplo: pad lo-fi + kick/hat suaves, 16s @ 84 bpm. Rende com:
//   node ../scripts/render-score.mjs --score score-lofi.js --out lofi.wav
export const duration = 16;
export const bpm = 84;

export function compose(ctx, kit) {
  const { pad, bass, kick, hat, bus, pump, limit } = kit;
  const spb = 60 / bpm;                       // segundos por tempo
  const beats = Math.round(duration / spb);   // ~22 tempos

  // master com pseudo-limiter: segura picos sem clipar
  const out = limit(ctx);
  // música passa por um bus com "pump" sutil (respiro no beat)
  const mus = bus(ctx, 0.8, out);
  pump(ctx, mus.gain, { bpm, beats, amount: 0.12, release: spb * 0.5 });

  // progressão Am – F – C – G, um acorde por compasso de 4 tempos
  const chords = [['A2','E3','C4'], ['F2','C3','A3'], ['C3','G3','E4'], ['G2','D3','B3']];
  const bar = 4 * spb;
  chords.forEach((c, i) => pad(ctx, c, i * bar, bar, { dest: mus, gain: 0.13, cutoff: 900 }));

  // baixo na tônica, um por tempo
  for (let i = 0; i < beats; i++)
    bass(ctx, chords[Math.floor(i / 4) % 4][0], i * spb, spb * 0.85, { dest: mus, gain: 0.24 });

  // kick nos tempos, hat no contratempo
  for (let i = 0; i < beats; i++) {
    kick(ctx, i * spb, { dest: mus, gain: 0.38 });
    hat(ctx, i * spb + spb / 2, { dest: mus, gain: 0.1, open: i % 4 === 3 });
  }
}
