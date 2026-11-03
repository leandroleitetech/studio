// Renderiza um "score" JS em WAV via OfflineAudioContext dentro do Chromium headless.
// Tudo é síntese: nenhum arquivo de áudio ou sample externo é lido.
//
//   node render-score.mjs --score trilha.js --out trilha.wav
//     [--duration 30] [--sample-rate 48000] [--channels 2]
//
// Contrato do score (módulo ES):
//   export const duration = 30;          // segundos (opcional, --duration prevalece)
//   export function compose(ctx, kit, opts) { ...agenda fontes... }
//   export default compose;              // forma alternativa
// `kit` é o conteúdo de synth.js (tone, kick, snare, hat, pad, bass, arp, pump,
// whoosh, bus, noiseBuffer, freq, mulberry32...).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const args = process.argv.slice(2);
const arg = (name, dflt) => { const i = args.indexOf(`--${name}`); return i < 0 ? dflt : args[i + 1]; };

const scorePath = arg('score', null);
const outPath = arg('out', null);
if (!scorePath || !outPath) {
  console.error('uso: node render-score.mjs --score <arquivo.js> --out <saida.wav> [--duration S] [--sample-rate HZ] [--channels N]');
  process.exit(1);
}

const here = dirname(fileURLToPath(import.meta.url));
const scoreCode = readFileSync(resolve(scorePath), 'utf8');
const synthCode = readFileSync(resolve(here, 'synth.js'), 'utf8');
const opts = {
  duration: Number(arg('duration', 0)) || 0,
  sampleRate: Number(arg('sample-rate', 48000)),
  channels: Number(arg('channels', 2)),
};

const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  await page.setContent('<html><body></body></html>');

  const result = await page.evaluate(async ({ scoreCode, synthCode, opts }) => {
    (0, eval)(synthCode); // define window.kit
    const mod = await import('data:text/javascript;charset=utf-8,' + encodeURIComponent(scoreCode));
    const compose = mod.compose || mod.default;
    if (typeof compose !== 'function') throw new Error('o score precisa exportar `compose(ctx, kit, opts)`');

    const dur = opts.duration || mod.duration;
    if (!dur) throw new Error('duração indefinida: exporte `duration` no score ou passe --duration');
    const ctx = new OfflineAudioContext(opts.channels, Math.ceil(dur * opts.sampleRate), opts.sampleRate);
    await compose(ctx, window.kit, opts);
    const buf = await ctx.startRendering();

    // WAV PCM 16-bit + estatísticas
    const ch = buf.numberOfChannels, len = buf.length, sr = buf.sampleRate;
    const bytes = new DataView(new ArrayBuffer(44 + len * ch * 2));
    const wstr = (o, s) => { for (let i = 0; i < s.length; i++) bytes.setUint8(o + i, s.charCodeAt(i)); };
    wstr(0, 'RIFF'); bytes.setUint32(4, 36 + len * ch * 2, true); wstr(8, 'WAVEfmt ');
    bytes.setUint32(16, 16, true); bytes.setUint16(20, 1, true); bytes.setUint16(22, ch, true);
    bytes.setUint32(24, sr, true); bytes.setUint32(28, sr * ch * 2, true);
    bytes.setUint16(32, ch * 2, true); bytes.setUint16(34, 16, true);
    wstr(36, 'data'); bytes.setUint32(40, len * ch * 2, true);
    let peak = 0, sumSq = 0;
    for (let i = 0, o = 44; i < len; i++) {
      for (let c = 0; c < ch; c++) {
        const s = Math.max(-1, Math.min(1, buf.getChannelData(c)[i]));
        peak = Math.max(peak, Math.abs(s)); sumSq += s * s;
        bytes.setInt16(o, s < 0 ? s * 0x8000 : s * 0x7FFF, true); o += 2;
      }
    }
    const u8 = new Uint8Array(bytes.buffer);
    let bin = '';
    for (let i = 0; i < u8.length; i += 0x8000)
      bin += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
    const rms = Math.sqrt(sumSq / (len * ch));
    const db = v => (20 * Math.log10(Math.max(v, 1e-9))).toFixed(1);
    return { wav: btoa(bin), stats: { seconds: buf.duration, sr, ch, peakDb: db(peak), rmsDb: db(rms) } };
  }, { scoreCode, synthCode, opts });

  mkdirSync(dirname(resolve(outPath)), { recursive: true });
  writeFileSync(resolve(outPath), Buffer.from(result.wav, 'base64'));
  const s = result.stats;
  console.log(`OK ${outPath} — ${s.seconds.toFixed(2)}s ${s.sr}Hz ${s.ch}ch · peak ${s.peakDb}dBFS · RMS ${s.rmsDb}dBFS`);
} finally {
  await browser.close();
}
