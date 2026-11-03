// Instala tudo de que o Studio precisa: dependências, transcrição local e as skills gratuitas.
// Uso: npm run instalar   (ou: node scripts/instalar.mjs)
// Agnóstico de agente: instala as skills no projeto para Devin, Claude Code, Codex e Cursor via `npx skills`.
// Cada passo é independente: se um falhar, os outros continuam e o resumo final diz o que resolver.
import {spawnSync} from 'node:child_process';

const win = process.platform === 'win32';
const python = win ? 'python' : 'python3';
const venvPython = win ? '.venv\\Scripts\\python.exe' : '.venv/bin/python';
const agentes = ['-a', 'devin', 'claude-code', 'codex', 'cursor', '-y'];
const nodeMajor = Number(process.versions.node.split('.')[0]);
// O extract-zip usado pelo Remotion para no meio em Node > 24 (versões não-LTS): baixa o navegador com Node 22.
const remotion = ['node_modules/@remotion/cli/remotion-cli.js', 'browser', 'ensure'];
const remotionBrowser = nodeMajor > 24 ? ['npx', '-y', '-p', 'node@22', '--', 'node', ...remotion] : ['node', ...remotion];

const passos = [
  ['Dependências do Remotion', ['npm', 'install', '--no-audit', '--no-fund']],
  ['Navegador do Remotion (Chrome Headless Shell)', remotionBrowser],
  ['Ambiente Python do projeto (.venv)', [python, '-m', 'venv', '.venv']],
  ['Transcrição e imagens (faster-whisper, Pillow, na .venv)', [venvPython, '-m', 'pip', 'install', '-r', 'requirements.txt']],
  ['Skill remotion-best-practices', ['npx', '-y', 'skills', 'add', 'remotion-dev/skills', '-s', 'remotion-best-practices', ...agentes]],
  ['Pacote HyperFrames, criação de vídeo do zero', ['npx', '-y', 'skills', 'add', 'heygen-com/hyperframes', ...agentes]],
  ['Skill overlay-graphics (playwright)', ['npm', 'ci', '--no-audit', '--no-fund', '--prefix', '.devin/skills/overlay-graphics/scripts']],
  ['Skill code-animation (shiki)', ['npm', 'ci', '--no-audit', '--no-fund', '--prefix', '.devin/skills/code-animation/scripts']],
  ['Skill soundtrack (playwright)', ['npm', 'ci', '--no-audit', '--no-fund', '--prefix', '.devin/skills/soundtrack/scripts']],
  ['Navegador headless das skills (overlay-graphics, shorts, teaser)', ['npx', '--prefix', '.devin/skills/overlay-graphics/scripts', 'playwright', 'install', 'chromium']],
  ['Navegador headless da skill soundtrack', ['npx', '--prefix', '.devin/skills/soundtrack/scripts', 'playwright', 'install', 'chromium']],
];

const falhas = [];
for (const [nome, [cmd, ...args]] of passos) {
  console.log(`\n==> ${nome}\n    ${[cmd, ...args].join(' ')}`);
  // Sem shell no Mac/Linux: argumentos chegam literais (nada de glob). No Windows o shell resolve npx.cmd.
  const r = spawnSync(cmd, args, {stdio: 'inherit', shell: win});
  if (r.status !== 0) falhas.push(nome);
}

// ponytail: a skill "assistir" (.devin/skills/) já vem no repositório — nada a instalar.
// No Claude Code, o plugin "watch" continua disponível via .claude/settings.json (opcional).

console.log('\n' + '='.repeat(60) + '\nConferindo a instalação (npm run verificar):');
const verificacao = spawnSync('node', ['scripts/verificar.mjs'], {stdio: 'inherit'});

console.log('='.repeat(60));
if (falhas.length === 0 && verificacao.status === 0) {
  console.log('Tudo instalado. Abra uma sessão NOVA do seu agente nesta pasta para as skills aparecerem.');
} else {
  if (falhas.length) {
    console.log('Passos que falharam:');
    for (const f of falhas) console.log(`  - ${f}`);
  }
  console.log('Veja guias/1-primeiros-passos.md.');
}
process.exit(falhas.length === 0 && verificacao.status === 0 ? 0 : 1);
