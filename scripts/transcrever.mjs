#!/usr/bin/env node
// Roda tools/transcrever.py com o Python certo:
// .venv/ do projeto quando existe (criada por `npm run instalar`),
// senão o python do sistema. Uso: npm run transcrever -- "<vídeo>" "<projeto>/transcricao"
import {existsSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const win = process.platform === 'win32';
const venvPy = win ? '.venv/Scripts/python.exe' : '.venv/bin/python';
const py = existsSync(venvPy) ? venvPy : (win ? 'python' : 'python3');

const r = spawnSync(py, ['tools/transcrever.py', ...process.argv.slice(2)], {stdio: 'inherit'});
process.exit(r.status ?? 1);
