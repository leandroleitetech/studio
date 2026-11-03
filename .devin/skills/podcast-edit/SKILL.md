---
name: podcast-edit
description: >-
  Transforma gravação crua de podcast/programa de áudio em MP3 publicável: extrai áudio, detecta
  silêncios por RMS (não silencedetect), propõe abertura/encerramento com evidência, verifica
  bordas re-transcrevendo fatias frescas, corta, normaliza loudness em duas passadas e remapeia a
  transcrição para SRT/TXT. Detecta alucinações do Whisper (loops de repetição, palavras em
  silêncio, eco de frases). Use para "edita meu podcast", "limpa esse áudio", "tira os silêncios do
  episódio". Não faz: vídeo (rough-cut), show notes, publicação. Nunca sobrescreve saída já
  publicada.
---

# Podcast Edit (áudio longo → publicável)

`scripts/podcast_audio.py` (stdlib + ffmpeg + `fw_whisper.py`) cuida da parte mecânica. Você decide
as bordas — o script **propõe com evidência, você confirma**. Três fases, todas resumíveis.

Destinos: trabalho em `$PODCAST_WORK/<ep>/` (default `/tmp/podcast-edit`) ou
`projetos/<NNN>/trabalho/podcast/`; entrega em `edicoes/<NNN. slug>/<ep>.mp3` + `.srt` + `.txt`.
**Nunca sobrescreva um episódio já publicado** — verifique se o arquivo de saída existe e
confirme antes.

## Fase 1 — analyze

```bash
.venv/bin/python .devin/skills/podcast-edit/scripts/podcast_audio.py analyze \
  --ep EP01 --src "/abs/gravacao.mp4"
```

- Extrai `analysis.wav` mono, transcreve com tempo por palavra (faster-whisper `large-v3-turbo`
  via `fw_whisper.py`; idioma padrão `pt`, `--language en`/`auto` para outros), mede RMS por
  janela (silêncio digital incluso), lista silêncios reais e propõe início/fim do programa.
  Trabalho em `$PODCAST_WORK/<ep>/` (padrão `/tmp/podcast-edit`) — exporte
  `PODCAST_WORK="$PWD/projetos/<NNN. slug>/trabalho/podcast"` para mantê-lo no projeto.
- **RMS, não `silencedetect`**: em gravações reais o silencedetect já reportou zero silêncios em
  todos os thresholds de −30 a −50dB num arquivo com milhares de pausas. O RMS por janela dá os
  silêncios E a mediana de fala de graça.
- O relatório separa: candidatos a abertura (cold open), sign-off, silêncios >2s (ar morto),
  e **suspeitas de alucinação do Whisper** — loops de repetição, frases que ecoam uma anterior
  (o modelo relendo a abertura em cima da música) e texto sobre áudio abaixo do limiar de
  silêncio. Suspeitas ficam fora da proposta de bordas. Alucinação em cima de **música** só a
  `verify` revela — por isso ela é obrigatória.
- Abertura/encerramento formulaicos: exporte `PODCAST_OPEN_HINTS`/`PODCAST_SIGNOFF_HINTS`
  (regexes separadas por `|`; comparação ignora maiúsculas, acentos e hífens). Sem hints, a proposta cai para primeiro/último bloco de fala
  sustentada — verifique sempre.

## Fase 2 — verify (obrigatória para cada borda)

Whisper alucina dentro de música e no silêncio de fim de arquivo. Toda borda proposta é checada
contra uma fatia fresca antes de ser confiada:

```bash
.venv/bin/python .devin/skills/podcast-edit/scripts/podcast_audio.py verify --ep EP01 --at 120.56
```

Re-transcreve uma janela curta em volta do timestamp e imprime o texto. Fatia que volta vazia =
o candidato era detrito (música, silêncio), não fala. Repita para início e fim, e para qualquer
corte interno que removeria conteúdo.

## Fase 3 — render

```bash
.venv/bin/python .devin/skills/podcast-edit/scripts/podcast_audio.py render \
  --ep EP01 --src "/abs/gravacao.mp4" \
  --start 120.56 --end 3624.24 \
  [--cut 993.96:996.27 ...] --out-dir "edicoes/<NNN. slug>"
```

- Corta com `atrim` + `concat` — **nunca `aselect`/`select`**: filtros de seleção são frágeis em
  timestamps longos e já corromperam saída; `atrim`+`concat` é exato e auditável.
- Silêncios internos ≥2s colapsam para ~0.75s (configurável) — conversa natural preservada.
- Loudness em duas passadas: mede (`loudnorm=print_format=json`), aplica com os valores medidos.
  Alvo de podcast: `I=-16:TP=-1.5:LRA=11` (fala estéreo; `--lufs -14` para outro alvo). **Atenção ao true peak**: se a medição
  pedir gain que estouraria o teto, o script reporta — prefira limiter a clipagem.
- Remapeia a transcrição inteira para o relógio do episódio final → `.srt` + `.txt` ao lado do MP3.
- Cache: re-render com borda ajustada custa segundos (áudio extraído e transcrição são reusados).

## Armadilhas conhecidas (por que o script é assim)

- **Loops de repetição do Whisper**: o modelo às vezes trava e repete a mesma frase por minutos.
  O analyze marca os trechos; trate como não-transcrito e verifique por fatia.
- **Palavras em música/silêncio**: timestamps "perfeitos" em trecho sem fala são inventados.
  Nunca corte borda sem `verify`.
- **True peak vs loudness**: normalizar para −16 LUFS pode pedir mais gain do que o teto −1.5dBTP
  permite — o loudnorm passa a limitar (modo dinâmico) e o script avisa em vez de clipar.
- **`silencedetect` mente** em áudio de fala com noise floor — use o RMS do analyze.

## Regras

- Proposta → verificação → corte. Borda sem `verify` não entra no render.
- Fonte intocada; saída é arquivo novo em `edicoes/`.
- Reporte: duração original vs final, silêncios colapsados, LUFS antes/depois, alucinações
  encontradas, o que ficou para revisão humana.
