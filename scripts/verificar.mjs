// Confere, sem instalar nada, se o Studio está pronto para uso. Uso: npm run verificar
// Sai com código 1 se faltar algo obrigatório; cada linha diz como resolver.
import {existsSync, readdirSync, statSync} from 'node:fs';
import {join, resolve} from 'node:path';
import {spawnSync} from 'node:child_process';

const win = process.platform === 'win32';
const venvPython = win ? '.venv\\Scripts\\python.exe' : '.venv/bin/python';
let faltando = 0;
const ok = (msg) => console.log(`  ✓ ${msg}`);
const aviso = (msg) => console.log(`  ! ${msg}`);
const falta = (msg, como) => { faltando++; console.log(`  ✗ ${msg}\n      → ${como}`); };
const roda = (cmd, args) => spawnSync(cmd, args, {encoding: 'utf8', shell: win});

const procura = (dir, nome) => {
  if (!existsSync(dir)) return false;
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    if (e === nome) return true;
    if (statSync(p).isDirectory() && procura(p, nome)) return true;
  }
  return false;
};

const major = Number(process.versions.node.split('.')[0]);
if (major < 18) falta(`Node ${process.versions.node} é antigo demais`, 'instale o Node.js LTS (22 ou 24)');
else if (major > 24) aviso(`Node ${process.versions.node} não é LTS — funciona, mas prefira o Node 22 ou 24 LTS`);
else ok(`Node ${process.versions.node}`);

for (const programa of ['ffmpeg', 'ffprobe']) {
  roda(programa, ['-version']).status === 0 ? ok(programa) : falta(`${programa} não encontrado`, 'instale pelo guia 1 (winget/brew)');
}

existsSync('node_modules/remotion') ? ok('dependências do Remotion') : falta('dependências do Remotion ausentes', 'npm run instalar');
procura('node_modules/.remotion/chrome-headless-shell', win ? 'chrome-headless-shell.exe' : 'chrome-headless-shell')
  ? ok('navegador do Remotion')
  : falta('navegador do Remotion ausente ou extraído pela metade', 'npm run instalar');

if (!existsSync(venvPython)) {
  falta('ambiente Python do projeto (.venv) ausente', 'npm run instalar');
} else {
  const py = roda(venvPython, ['-c', 'import faster_whisper, PIL, av; assert int(av.__version__.split(".")[0]) < 19, "av " + av.__version__']);
  py.status === 0 ? ok('.venv com faster-whisper, Pillow e av compatível') : falta('.venv incompleta', `npm run instalar  (${py.stderr.trim().split('\n').pop()})`);
}

for (const skill of ['hyperframes', 'remotion-best-practices']) {
  existsSync(`.devin/skills/${skill}/SKILL.md`) ? ok(`skill ${skill}`) : falta(`skill ${skill} ausente`, 'npm run instalar (depois abra uma sessão nova do agente)');
}

for (const skill of ['overlay-graphics', 'code-animation', 'soundtrack']) {
  const dir = `.devin/skills/${skill}/scripts`;
  if (!existsSync(`${dir}/node_modules`)) { falta(`dependências da skill ${skill} ausentes`, 'npm run instalar'); continue; }
  if (skill === 'code-animation') { ok(`skill ${skill}`); continue; }
  const pw = roda('node', ['-e', `console.log(require(${JSON.stringify(resolve(dir, 'node_modules/playwright'))}).chromium.executablePath())`]);
  const exe = pw.stdout.trim();
  exe && existsSync(exe) ? ok(`skill ${skill} (navegador headless)`) : falta(`navegador headless da skill ${skill} ausente`, `npx --prefix ${dir} playwright install chromium`);
}

if (process.platform === 'darwin') {
  roda('swift', ['--version']).status === 0 ? ok('swift (recorte de sujeito da skill thumbnail)') : aviso('swift ausente: só o recorte automático de thumbnail fica indisponível (xcode-select --install)');
}

console.log(faltando ? `\n${faltando} item(ns) faltando.` : '\nTudo pronto.');
process.exit(faltando ? 1 : 0);
