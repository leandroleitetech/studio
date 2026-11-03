#!/usr/bin/env python3
"""Camada de compatibilidade: CLI no estilo mlx_whisper sobre o faster-whisper.

Aceita os argumentos que os pipelines deste repo usam e escreve, por arquivo de
entrada, <stem>.json (esquema whisper: segments[].words[]={word,start,end}) e/ou
<stem>.txt em --output-dir. Rode com o Python da .venv do projeto (que tem
faster-whisper) — `npm run instalar` cuida disso.
"""
import argparse
import json
import os
import sys
from pathlib import Path

# Com os._exit no fim, o resource_tracker reclamaria de semáforos "vazados" (inofensivo).
os.environ.setdefault("PYTHONWARNINGS", "ignore::UserWarning:multiprocessing.resource_tracker")

MODEL = os.environ.get("STUDIO_WHISPER_MODEL", "large-v3-turbo")
LANGUAGE = os.environ.get("STUDIO_LANGUAGE", "pt")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("audio", nargs="+")
    p.add_argument("--model", default=MODEL)
    p.add_argument("--language", default=LANGUAGE, help="ISO (pt, en...) ou auto")
    p.add_argument("--word-timestamps", default="True")
    p.add_argument("--output-format", default="json")  # json | txt | all
    p.add_argument("--output-dir", required=True)
    p.add_argument("--verbose", default="False")
    p.add_argument("--vad-filter", default="True",
                   help="silero VAD antes de decodificar (default True). Sem ele, o turbo "
                        "decodifica música/silêncio, alucina o contexto e perde fala real.")
    p.add_argument("--condition-on-previous-text", default=None)
    args, _unknown = p.parse_known_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper não instalado — rode `npm run instalar` (cria a .venv do projeto).")

    model = WhisperModel(args.model, device="auto", compute_type="auto")
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    kw = {}
    if args.condition_on_previous_text is not None:
        kw["condition_on_previous_text"] = str(args.condition_on_previous_text).lower() == "true"
    words = str(args.word_timestamps).lower() == "true"

    for src in args.audio:
        language = None if (args.language or "auto") == "auto" else args.language
        segments, info = model.transcribe(src, language=language,
                                          word_timestamps=words,
                                          vad_filter=str(args.vad_filter).lower() == "true",
                                          **kw)
        segs = [{"id": s.id, "start": s.start, "end": s.end, "text": s.text,
                 "words": [{"word": w.word, "start": w.start, "end": w.end,
                            "probability": w.probability} for w in (s.words or [])]}
                for s in segments]
        stem = Path(src).stem
        if args.output_format in ("json", "all"):
            tmp = out_dir / (stem + ".json.partial")
            tmp.write_text(json.dumps({"text": "".join(s["text"] for s in segs),
                                       "segments": segs, "language": info.language},
                                      ensure_ascii=False))
            tmp.replace(out_dir / (stem + ".json"))
        if args.output_format in ("txt", "all"):
            (out_dir / (stem + ".txt")).write_text(
                "".join(s["text"] for s in segs).strip() + "\n")


if __name__ == "__main__":
    main()
    # O teardown do ctranslate2 pode abortar ("recursive_mutex lock failed") depois do trabalho feito.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
