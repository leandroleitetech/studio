---
name: teaser
description: >-
  Monta teasers/trailers de episódios: plano JSON com shots independentes, diálogo, música e
  SFX com ducking, legendas no relógio do teaser. Use para "faz um trailer", "teaser do episódio",
  "monta uma abertura chamativa". Só opera com mídia local já existente — nunca baixa assets sem
  aprovação.
---

# Teaser / Trailer

`scripts/montage.py` (só stdlib + ffmpeg) monta shots, diálogo, música e SFX num plano com
ducking automático da música sob a fala. Saída sempre nova em `edicoes/` — fontes intocadas.
Schema completo, títulos e legendas: [references/trailer-edit.md](references/trailer-edit.md).

## Estrutura de trailer

| Bloco | Duração típica | Função |
|---|---|---|
| Cold open | 3–8s | O momento mais forte, sem contexto |
| Stakes | 5–10s | Por que isso importa |
| Escalation | 10–20s | Cortes rápidos, energia crescente |
| Turn | 3–6s | A revelação/mudança |
| Promise | 3–5s | O que vem + CTA |

Música dita o ritmo: cortes nos beats, ducking sob diálogo. Sem diálogo = montagem pura.
Escolha as falas pela transcrição (as mais fortes), não por achismo.

## Plano (`teaser.json`, paths absolutos)

```json
{
  "fps": "30",
  "width": 1920,
  "height": 1080,
  "shots": [
    {"asset": "/abs/projetos/001. ep/video/ep.mp4", "source_start": 12.0, "duration": 3.0, "purpose": "gancho"},
    {"asset": "/abs/projetos/001. ep/video/ep.mp4", "source_start": 41.5, "duration": 4.0, "purpose": "virada"}
  ],
  "audio": [
    {"role": "dialogue", "asset": "/abs/projetos/001. ep/video/ep.mp4", "source_start": 12.0,
     "start": 0.0, "duration": 3.0, "transcript": "/abs/projetos/001. ep/trabalho/teaser/ep.json"},
    {"role": "dialogue", "asset": "/abs/projetos/001. ep/video/ep.mp4", "source_start": 41.5,
     "start": 3.0, "duration": 4.0},
    {"role": "music", "asset": "/abs/projetos/001. ep/trabalho/audio/tema.wav", "source_start": 0.0,
     "start": 0.0, "duration": 7.0, "gain_db": -14, "fade_out": 1.0},
    {"role": "sfx", "asset": "/abs/projetos/001. ep/trabalho/audio/whoosh.wav", "source_start": 0.0,
     "start": 2.9, "duration": 1.2, "gain_db": -6}
  ]
}
```

- `shots` em ordem de imagem; o áudio original dos shots é mudo — diálogo entra como item
  `audio` com `role: "dialogue"` e pode atravessar cortes de imagem.
- `source_start` está no relógio do arquivo-fonte; `start` do áudio, no relógio do teaser.
- Música com ducking padrão (`duck_db -12`, `duck_attack 0.18`, `duck_release 0.65`). Mix final
  normalizado para −14 LUFS / −1.5 dBTP, 48 kHz.
- Música e SFX sem samples: gere com a skill `soundtrack` (WAV local).
- `transcript` (opcional, por diálogo) = JSON whisper do arquivo-fonte, que vira legenda no relógio do
  teaser. Gere com `.venv/bin/python .devin/skills/rough-cut/scripts/fw_whisper.py "<ep.mp4>" --output-dir "projetos/<NNN. slug>/trabalho/teaser"` (grava `<nome>.json`).

## Fluxo

```bash
.venv/bin/python .devin/skills/teaser/scripts/montage.py \
  --plan "projetos/<NNN. slug>/trabalho/teaser/teaser.json" \
  --out "edicoes/<NNN. slug>/teaser.mp4"
```

Sem encoder de hardware (fora do Mac): `--encoder software`. Para uma prévia, salve um plano
menor separado. O script cacheia cada shot; revisões só remixam o áudio.

O render grava `teaser.transcript.json` (palavras no relógio do teaser) e `teaser.render.json`
(tempos reais por quadro). Legendas: agrupe as palavras em cues, renderize
`assets/captions.html` (`{"bottom": 85, "cues": [{"start", "end", "text"}]}`) como MOV com
alpha via `overlay-graphics/scripts/render.mjs` e componha com `overlay-graphics/scripts/composite.py`.
Título: `assets/title-card.html` (`kicker`, `title`, `subline`) — veja references.

## Regras

- Trabalhe em `projetos/<NNN. slug>/trabalho/teaser/`; entregue em `edicoes/<NNN. slug>/`.
- Todo arquivo do plano deve existir localmente. Nada de download silencioso — proponha a fonte
  e peça o arquivo.
- Não repita nem reordene diálogo de um jeito que mude o sentido do que foi dito.
- Assista com som e sem som antes de entregar. Testes: `.venv/bin/python -m unittest discover -s .devin/skills/teaser/scripts -p 'test_*.py'`.
