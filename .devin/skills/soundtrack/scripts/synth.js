/* kit de síntese — injetado na página antes do score; roda em OfflineAudioContext.
   Tudo determinístico: ruído sai de PRNG com seed, nada de Math.random/Date. */
(function () {
  const NOTES = { C:0,'C#':1,Db:1,D:2,'D#':3,Eb:3,E:4,F:5,'F#':6,Gb:6,G:7,'G#':8,Ab:8,A:9,'A#':10,Bb:10,B:11 };

  function midi(n) {
    if (typeof n === 'number') return n;
    const m = /^([A-Ga-g])([#b]?)(-?\d)$/.exec(String(n).trim());
    if (!m) throw new Error('nota inválida: ' + n);
    return NOTES[m[1].toUpperCase() + m[2]] + 12 * (Number(m[3]) + 1);
  }
  const freq = n => 440 * Math.pow(2, (midi(n) - 69) / 12);

  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  function noiseBuffer(ctx, dur = 1, seed = 1) {
    const len = Math.ceil(dur * ctx.sampleRate);
    const buf = ctx.createBuffer(1, len, ctx.sampleRate);
    const d = buf.getChannelData(0), rnd = mulberry32(seed);
    for (let i = 0; i < len; i++) d[i] = rnd() * 2 - 1;
    return buf;
  }

  /* ADSR enxuto: sobe em `attack`, cai exponencial até o fim de `dur`,
     e solta em `release` segundos depois do fim. */
  function adsr(param, t, dur, { attack = 0.005, release = 0.08, peak = 1, curve = 4 } = {}) {
    const end = t + dur;
    param.setValueAtTime(0.0001, t);
    param.exponentialRampToValueAtTime(Math.max(peak, 0.0001), t + attack);
    param.setTargetAtTime(0.0001, end - Math.min(dur * 0.5, 0.05), (dur * 0.5) / curve);
    param.setTargetAtTime(0.0001, end, Math.max(release, 0.01) / curve);
    return param;
  }

  function bus(ctx, gain = 1, dest = ctx.destination) {
    const g = ctx.createGain(); g.gain.value = gain; g.connect(dest); return g;
  }

  /* Oscilador com envelope. freq pode ser nota ("A4", "F#3") ou Hz. */
  function tone(ctx, o = {}) {
    const { note, type = 'sine', t = 0, dur = 0.5, gain = 0.5, attack = 0.005,
            release = 0.08, dest = ctx.destination, detune = 0, slide } = o;
    const f0 = o.freq != null ? o.freq : freq(note != null ? note : 440);
    const osc = ctx.createOscillator(); osc.type = type; osc.frequency.setValueAtTime(f0, t);
    if (slide) osc.frequency.exponentialRampToValueAtTime(slide, t + dur);
    if (detune) osc.detune.value = detune;
    const g = ctx.createGain(); adsr(g.gain, t, dur, { attack, release, peak: gain });
    osc.connect(g); g.connect(dest);
    osc.start(t); osc.stop(t + dur + release + 0.1);
    return osc;
  }

  function kick(ctx, t, { dest = ctx.destination, gain = 0.9, base = 160, seed = 3 } = {}) {
    tone(ctx, { type: 'sine', freq: base, slide: 45, t, dur: 0.14, gain, attack: 0.002, release: 0.05, dest });
    const n = ctx.createBufferSource(); n.buffer = noiseBuffer(ctx, 0.03, seed);
    const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 4000;
    const g = ctx.createGain(); adsr(g.gain, t, 0.02, { attack: 0.001, release: 0.015, peak: gain * 0.4 });
    n.connect(hp); hp.connect(g); g.connect(dest); n.start(t); n.stop(t + 0.05);
  }

  function snare(ctx, t, { dest = ctx.destination, gain = 0.55, seed = 5 } = {}) {
    const n = ctx.createBufferSource(); n.buffer = noiseBuffer(ctx, 0.2, seed);
    const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 1800; bp.Q.value = 0.8;
    const g = ctx.createGain(); adsr(g.gain, t, 0.16, { attack: 0.001, release: 0.06, peak: gain });
    n.connect(bp); bp.connect(g); g.connect(dest); n.start(t); n.stop(t + 0.25);
    tone(ctx, { type: 'triangle', freq: 190, t, dur: 0.09, gain: gain * 0.5, attack: 0.001, dest });
  }

  function hat(ctx, t, { dest = ctx.destination, gain = 0.22, open = false, seed = 7 } = {}) {
    const dur = open ? 0.25 : 0.045;
    const n = ctx.createBufferSource(); n.buffer = noiseBuffer(ctx, dur + 0.05, seed);
    const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 7800;
    const g = ctx.createGain(); adsr(g.gain, t, dur, { attack: 0.001, release: dur, peak: gain });
    n.connect(hp); hp.connect(g); g.connect(dest); n.start(t); n.stop(t + dur + 0.05);
  }

  /* Pad: 2 osciladores desafinados por nota, através de um low-pass comum. */
  function pad(ctx, notes, t, dur, { dest = ctx.destination, gain = 0.2, type = 'sawtooth',
                                      cutoff = 1100, detune = 9, attack = 0.4, release = 0.5 } = {}) {
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = cutoff; lp.Q.value = 0.5;
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(gain, t + attack);
    g.gain.setValueAtTime(gain, t + dur);
    g.gain.linearRampToValueAtTime(0.0001, t + dur + release);
    lp.connect(g); g.connect(dest);
    for (const note of notes) {
      for (const d of [-detune, detune]) {
        const osc = ctx.createOscillator(); osc.type = type;
        osc.frequency.value = freq(note); osc.detune.value = d;
        osc.connect(lp); osc.start(t); osc.stop(t + dur + release + 0.1);
      }
    }
  }

  function bass(ctx, note, t, dur, { dest = ctx.destination, gain = 0.4, type = 'triangle', cutoff = 700 } = {}) {
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = cutoff;
    lp.connect(dest);
    tone(ctx, { type, freq: freq(note), t, dur, gain, attack: 0.004, release: 0.06, dest: lp });
  }

  /* Arpejo: toca `notes` em sequência a partir de t, passo `step` segundos. */
  function arp(ctx, notes, { t = 0, dur = notes.length, step, type = 'square', gain = 0.15,
                             noteDur, dest = ctx.destination, cutoff = 2500 } = {}) {
    step = step || dur / notes.length;
    noteDur = noteDur || Math.min(step * 0.9, 0.4);
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = cutoff;
    lp.connect(dest);
    notes.forEach((n, i) => tone(ctx, { type, freq: freq(n), t: t + i * step, dur: noteDur,
                                        gain, attack: 0.003, release: 0.05, dest: lp }));
  }

  /* "Pump" de sidechain falso: afoga o gain a cada tempo do compasso.
     Uso: const mus = kit.bus(ctx, 0.5); kit.pump(ctx, mus.gain, {bpm:100, start:0, beats:64}) */
  function pump(ctx, param, { bpm = 100, start = 0, beats = 64, amount = 0.35, release = 0.28 } = {}) {
    const spb = 60 / bpm, base = param.value;
    for (let i = 0; i <= beats; i++) {
      const t = start + i * spb;
      param.setValueAtTime(base, t);
      param.linearRampToValueAtTime(base * (1 - amount), t + 0.02);
      param.linearRampToValueAtTime(base, t + release);
    }
  }

  /* Whoosh/riser de SFX: ruído com filtro varrendo para cima. */
  function whoosh(ctx, t, { dest = ctx.destination, dur = 0.7, gain = 0.3, seed = 11,
                            from = 300, to = 6000 } = {}) {
    const n = ctx.createBufferSource(); n.buffer = noiseBuffer(ctx, dur + 0.1, seed);
    const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.Q.value = 1.2;
    bp.frequency.setValueAtTime(from, t);
    bp.frequency.exponentialRampToValueAtTime(to, t + dur);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(gain, t + dur * 0.8);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    n.connect(bp); bp.connect(g); g.connect(dest); n.start(t); n.stop(t + dur + 0.1);
  }

  /* Pseudo-limiter no master: compressor rápido que segura picos sem achatar.
     Uso: const out = kit.limit(ctx); // tudo toca para `out` */
  function limit(ctx, { threshold = -8, ratio = 12, attack = 0.003, release = 0.25 } = {}) {
    const c = ctx.createDynamicsCompressor();
    c.threshold.value = threshold; c.ratio.value = ratio;
    c.attack.value = attack; c.release.value = release; c.knee.value = 3;
    c.connect(ctx.destination);
    return c;
  }

  window.kit = { midi, freq, mulberry32, noiseBuffer, adsr, bus, tone, kick, snare, hat, pad, bass, arp, pump, whoosh, limit };
})();
