---
name: assistir
description: Assiste um vídeo local do Studio — extrai quadros com ffmpeg para a pasta frames/ do projeto, lê as imagens e mapeia enquadramento, posição do rosto, fundo e luz. Use sempre que precisar entender o conteúdo visual de um vídeo em projetos/, antes de planejar a edição.
allowed-tools:
  - exec
  - read
  - grep
  - glob
---

# Assistir: entender um vídeo sem tocá-lo

Esta skill substitui o plugin `watch` (Claude-only) com ferramentas que todo agente tem: `ffmpeg`/`ffprobe` + leitura de imagens. O vídeo gravado é **material-fonte: leitura apenas** — nunca sobrescreva o original. Se a edição pedir cortes, eles saem como arquivos novos em `edicoes/`.

## 1. Metadados

```bash
ffprobe -v error -show_entries format=duration,bit_rate -show_entries stream=codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels -of default=noprint_wrappers=1 "<video>"
```

Registre duração, resolução, fps e codecs no topo do `plano.md`.

## 2. Quadros de visão geral (mapa do vídeo)

Extraia amostras baratas primeiro — mosaicos de visão geral:

```bash
mkdir -p "<projeto>/frames"
ffmpeg -hide_banner -loglevel error -i "<video>" -vf "fps=1/15,scale=320:-1,tile=8x5" -q:v 4 "<projeto>/frames/mosaico_%02d.jpg"
```

Cada `mosaico_XX.jpg` é uma grade de até 40 quadros (1 a cada 15 s), ou seja, cobre ~10 min
de vídeo; o último sai parcial. Para vídeos curtos (< 3 min), use `fps=1/3` para ter quadros suficientes. Leia os mosaicos para achar mudanças de cena, cartelas e trechos em que o enquadramento muda.

## 3. Quadros de leitura fina

Para mapear rosto, luz e fundo com precisão, extraia quadros maiores — 1 a cada 2–5 s nos trechos relevantes (ou o vídeo todo se for curto):

```bash
ffmpeg -hide_banner -loglevel error -i "<video>" -vf "fps=1/2,scale=1280:-1" -q:v 3 "<projeto>/frames/f%04d.jpg"
```

Para medir a **zona do rosto** em pixels reais, extraia alguns quadros na resolução nativa:

```bash
ffmpeg -hide_banner -loglevel error -ss <segundos> -i "<video>" -frames:v 1 -q:v 2 "<projeto>/frames/nativo_<segundos>.jpg"
```

Leia as imagens em lotes (o tool `read` renderiza JPG/PNG). Mapeie e anote no plano:

- **Zona do rosto:** retângulo x/y em pixels do quadro nativo; confira em pelo menos 3 momentos (início, meio, fim) e em cada mudança de enquadramento.
- **Enquadramento:** plano único? câmera se mexe? há elementos fixos (microfone, monitor)?
- **Fundo e luz:** cor dominante, direção da luz — o B-roll e os painéis devem parecer do mesmo mundo.
- **Mudanças de cena:** cortes internos do master (apresentador some, muda roupa/cenário).

## 4. Áudio e fala

A transcrição com tempo por palavra é outro passo — `npm run transcrever -- "<video>" "<projeto>/transcricao"`
(faster-whisper na `.venv`, local e gratuito; idioma padrão `pt`, `auto` detecta). Esta skill é só para a parte visual. Para checar volume/trechos mudos:

```bash
ffmpeg -i "<video>" -af volumedetect -f null -
ffmpeg -i "<video>" -af silencedetect=noise=-35dB:d=0.5 -f null - 2>&1 | grep silence
```

## 5. Resumo ao usuário

Termine com: duração, resolução, fps, zona do rosto, 2–3 observações de enquadramento/luz e quantos quadros foram extraídos. Se o vídeo for longo, prefira mais mosaicos e menos quadros finos.
