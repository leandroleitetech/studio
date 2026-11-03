"""Transcrição local, gratuita, com o tempo exato de cada palavra.

Uso:
    python tools/transcrever.py "projetos/001. meu-video/video/master.mp4" "projetos/001. meu-video/transcricao" [idioma]

[idioma]: padrão pt (ou $STUDIO_LANGUAGE); "auto" detecta. Modelo: large-v3-turbo (ou $STUDIO_WHISPER_MODEL).
Gera palavras.json ({w, s, e} = palavra, início, fim em segundos) e transcript.md ([MM:SS.mmm] por frase).
Na primeira execução o faster-whisper baixa o modelo (~1,6 GB). Depois tudo roda offline.
Tenta a placa de vídeo (CUDA) e, se não houver, usa o processador sozinho.
"""

import json
import os
import sys
from pathlib import Path

# Com os._exit no fim, o resource_tracker reclamaria de semáforos "vazados" (inofensivo).
os.environ.setdefault("PYTHONWARNINGS", "ignore::UserWarning:multiprocessing.resource_tracker")

from faster_whisper import WhisperModel

MODELO = os.environ.get("STUDIO_WHISPER_MODEL", "large-v3-turbo")
DISPOSITIVOS = [("cuda", "float16"), ("cpu", "int8")]


def mmss(t):
    return f"{int(t // 60):02d}:{t % 60:06.3f}"


def transcrever(fonte, idioma):
    erros = []
    for device, compute in DISPOSITIVOS:
        try:
            m = WhisperModel(MODELO, device=device, compute_type=compute)
            segs, info = m.transcribe(str(fonte), language=idioma, word_timestamps=True, vad_filter=True)
            # o gerador só decodifica aqui; erros de CUDA/CUBLAS aparecem nesta linha
            return list(segs), info, device
        except Exception as e:
            erros.append(f"{device}: {e}")
    sys.exit("a transcrição falhou:\n" + "\n".join(erros))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    fonte, saida = Path(sys.argv[1]), Path(sys.argv[2])
    idioma = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("STUDIO_LANGUAGE", "pt")
    saida.mkdir(parents=True, exist_ok=True)
    segs, info, device = transcrever(fonte, None if idioma == "auto" else idioma)

    palavras = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in s.words]
    (saida / "palavras.json").write_text(json.dumps(palavras, ensure_ascii=False, indent=1), encoding="utf-8")

    linhas = [f"<!-- {MODELO} | {device} | {info.duration:.3f}s -->"]
    linhas += [f"[{mmss(s.start)}] {s.text.strip()}" for s in segs]
    (saida / "transcript.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"{len(palavras)} palavras, {len(segs)} frases, {device} -> {saida}")


if __name__ == "__main__":
    main()
    # O teardown do ctranslate2 pode abortar ("recursive_mutex lock failed") depois do trabalho feito.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
