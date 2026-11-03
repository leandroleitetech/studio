#!/usr/bin/env python3
"""Deterministic audio work for a podcast episode edit (raw -> publishable mp3).

Adapted from an MIT-licensed open-source podcast-editing skill (see NOTICE.md). It owns the
mechanical half of the edit so every run does it the same way. It deliberately
does NOT decide where the show starts and ends: it proposes candidates with
evidence and you confirm them. Boundaries are the only place this edit can
really go wrong, so a human (or the model) stays in that loop.

Three phases:

  analyze   extract audio, transcribe (faster-whisper via fw_whisper.py shim),
            scan for whisper repetition loops, measure the RMS distribution,
            list real silences, and propose show start/end.
            Writes report.json and prints a summary.
  verify    re-transcribe a short slice around a timestamp. Whisper hallucinates
            inside music and end-of-file silence, so every proposed boundary gets
            checked against a fresh slice before it is trusted.
  render    cut the confirmed span (minus any silence trims), normalize loudness
            two-pass, encode the mp3, and remap the transcript onto the final
            episode timeline as .srt and .txt.

Why RMS instead of ffmpeg silencedetect: on real recordings silencedetect has
reported zero silences at every threshold from -30dB to -50dB on a file that
plainly has thousands of quiet runs. Windowed RMS is reliable and gives the
speech median for free. See the skill's pitfalls log.

Usage:
  podcast_audio.py analyze --ep EP01 --src /path/to/recording.mp4
  podcast_audio.py verify  --ep EP01 --at 120.56
  podcast_audio.py render  --ep EP01 --src /path/to/recording.mp4 \
      --start 120.56 --end 3624.24 [--cut 993.96:996.27] [--out-dir DIR]

Every phase is resumable: existing artifacts in the work dir are reused, so
re-rendering with a nudged boundary costs seconds, not minutes.

Environment overrides:
  PODCAST_WORK          work dir root (default: /tmp/podcast-edit)
  PODCAST_EXPORTS       default --out-dir (default: ./edicoes)
  PODCAST_OPEN_HINTS    regexes separated by | marking the cold open
  PODCAST_SIGNOFF_HINTS regexes separated by | marking the sign-off
  STUDIO_WHISPER_MODEL  faster-whisper model (default: large-v3-turbo)
  STUDIO_LANGUAGE       transcription language (default: pt; "auto" detects)
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata

WORKROOT = os.environ.get("PODCAST_WORK", "/tmp/podcast-edit")
EXPORTS = os.environ.get("PODCAST_EXPORTS", os.path.abspath("edicoes"))
MODEL = os.environ.get("STUDIO_WHISPER_MODEL", "large-v3-turbo")
LANGUAGE = os.environ.get("STUDIO_LANGUAGE", "pt")
LUFS = -16.0      # podcast target (Apple Podcasts); override with --lufs
FW_WHISPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fw_whisper.py")


def _hints(env):
    """Optional regex hints from the environment, separated by '|'."""
    raw = os.environ.get(env, "").strip()
    return tuple(x.strip() for x in raw.split("|") if x.strip()) if raw else ()


def _norm(text):
    """Lowercase, accents stripped, hyphens as spaces: hints match whatever casing/accents whisper emits."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c)).lower().replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def _hit(hints, text):
    return any(re.search(_norm(h), _norm(text)) for h in hints)


# Shows with a formulaic cold open / sign-off can set PODCAST_OPEN_HINTS and
# PODCAST_SIGNOFF_HINTS. With none, the proposal falls back to first/last
# sustained speech — verify the boundary, always.
OPEN_HINTS = _hints("PODCAST_OPEN_HINTS")
SIGNOFF_HINTS = _hints("PODCAST_SIGNOFF_HINTS")

START_PAD = 0.5   # cut in this far before the first confirmed word
END_PAD = 1.0     # let the sign-off breathe before cutting
KEEP_UNDER = 2.0  # silences shorter than this are conversation, not dead air
TRIM_TO = 0.75    # what a trimmed silence collapses to


def run(cmd, **kw):
    """Run a command, echoing it on failure. Always -nostdin for ffmpeg."""
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}\n{p.stderr[-2000:]}")
    return p


def whisper(args_list):
    """Run the faster-whisper shim (fw_whisper.py) with the current interpreter."""
    if not os.path.exists(FW_WHISPER):
        sys.exit(f"{FW_WHISPER} missing — it ships inside this skill's scripts/")
    run([sys.executable, FW_WHISPER, *args_list])


def need(tool):
    if not shutil.which(tool):
        sys.exit(f"{tool} not found on PATH")


def workdir(ep):
    d = os.path.join(WORKROOT, ep)
    os.makedirs(d, exist_ok=True)
    return d


def duration(path):
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path])
    return float(p.stdout.strip())


def ts(t, sep=","):
    t = max(0.0, t)
    h, m, s = int(t // 3600), int((t % 3600) // 60), t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", sep)


def hms(t):
    h, m, s = int(t // 3600), int((t % 3600) // 60), int(t % 60)
    return (f"{h}h {m:02d}m {s:02d}s" if h else f"{m}m {s:02d}s")


# ---------------------------------------------------------------- analyze

def ensure_wav(src, wd):
    """16k mono analysis wav. Timestamps on it transfer 1:1 to the source."""
    wav = os.path.join(wd, "analysis.wav")
    if not os.path.exists(wav):
        run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-i", src,
             "-vn", "-ac", "1", "-ar", "16000", wav])
    return wav


def ensure_transcript(src, wd, model, language):
    js, meta = os.path.join(wd, "analysis.json"), os.path.join(wd, "analysis.meta.json")
    want = {"model": model, "language": language}
    if not os.path.exists(js) or not os.path.exists(meta) or json.load(open(meta)) != want:
        args_list = [src, "--model", model, "--language", language, "--word-timestamps", "True",
                     "--output-format", "json", "--output-dir", wd]
        whisper(args_list)
        # the shim names output after the input stem; normalize to analysis.json
        produced = os.path.join(wd, os.path.splitext(os.path.basename(src))[0] + ".json")
        if produced != js and os.path.exists(produced):
            os.replace(produced, js)
        json.dump(want, open(meta, "w"))
    return json.load(open(js))


def rms_windows(wav, wd, total):
    """Per-frame RMS in chronological order. Cached; it is the slow-ish part."""
    cache = os.path.join(wd, "rms.txt")
    if not os.path.exists(cache):
        p = subprocess.run(
            ["ffmpeg", "-nostdin", "-v", "error", "-i", wav, "-af",
             "astats=metadata=1:reset=1,ametadata=print:"
             "key=lavfi.astats.Overall.RMS_level:file=-", "-f", "null", "-"],
            capture_output=True, text=True)
        # Digital silence reports -inf: keep it as a very low level. Dropping those windows
        # would hide the silence AND shift every later timestamp (window size = total / count).
        vals = ["-120.0" if "inf" in m else m for m in re.findall(r"RMS_level=(-?inf|-?[\d.]+)", p.stdout)]
        if not vals:
            sys.exit("could not measure RMS (no astats output)")
        open(cache, "w").write("\n".join(vals) + "\n")
    vals = [float(x) for x in open(cache) if x.strip()]
    return vals, total / len(vals)


def silence_runs(vals, w, thresh, lo=None, hi=None):
    """Chronological runs below thresh, optionally restricted to [lo, hi]."""
    runs, cur = [], None
    for i, v in enumerate(vals):
        if v < thresh:
            cur = i if cur is None else cur
        elif cur is not None:
            runs.append((cur * w, i * w))
            cur = None
    if cur is not None:
        runs.append((cur * w, len(vals) * w))
    if lo is not None:
        runs = [(a, b) for a, b in runs if a > lo and b < hi]
    return runs


def repetition_scan(segs):
    """Whisper can fall into a repeat loop and shred a whole region (S5E19)."""
    texts = [s["text"].strip() for s in segs]
    counts = {}
    for t in texts:
        counts[t] = counts.get(t, 0) + 1
    repeats = sorted(((n, t) for t, n in counts.items() if n >= 4 and len(t) > 8),
                     reverse=True)
    longest, run = 1, 1
    at = None
    for i in range(1, len(texts)):
        run = run + 1 if texts[i] == texts[i - 1] else 1
        if run > longest:
            longest, at = run, segs[i]["start"]
    return {"repeated_texts": [{"count": n, "text": t[:80]} for n, t in repeats[:5]],
            "longest_consecutive_run": longest,
            "longest_run_at": at,
            "suspect": bool(repeats) or longest >= 4}


def suspect_segments(segs, vals, w, thresh):
    """Hallucination candidates: a sentence that echoes an earlier one (whisper re-reading the
    opening over music) or text sitting on audio that is mostly below the silence threshold."""
    seen, out = set(), {}
    for i, s in enumerate(segs):
        key = _norm(re.sub(r"[^\w\s-]", "", s["text"]))
        if len(key.split()) >= 4 and key in seen:
            out[i] = "echo of an earlier sentence"
        seen.add(key)
        lo, hi = int(s["start"] / w), max(int(s["start"] / w) + 1, int(s["end"] / w))
        win = vals[lo:hi]
        if win and sum(v < thresh for v in win) / len(win) > 0.8:
            out.setdefault(i, "text over silence")
    return out


def propose_start(segs, limit=360):
    """First sustained, sentence-shaped speech. Expect it near 2:00."""
    hinted, first = [], None
    for s in segs:
        if s["start"] > limit:
            break
        txt = s["text"].strip()
        if len(txt.split()) < 4:
            continue
        if first is None:
            first = s
        if _hit(OPEN_HINTS, txt):
            hinted.append(s)
    pick = hinted[0] if hinted else first
    return ({"at": pick["start"], "text": pick["text"].strip()[:120],
             "matched_formula": bool(hinted)} if pick else None)


def propose_end(segs, tail=420):
    """Sign-off phrase if present, else the last sustained speech run."""
    total = segs[-1]["end"] if segs else 0
    window = [s for s in segs if s["end"] >= total - tail]
    hinted = [s for s in window
              if _hit(SIGNOFF_HINTS, s["text"])]
    if hinted:
        pick = hinted[-1]
        # keep any full-sentence reply that follows the sign-off
        after = [s for s in segs if s["start"] >= pick["end"]
                 and len(s["text"].split()) >= 4]
        pick = after[-1] if after else pick
        return {"at": pick["end"], "text": pick["text"].strip()[:120],
                "matched_formula": True}
    subst = [s for s in window if len(s["text"].split()) >= 3]
    pick = subst[-1] if subst else (segs[-1] if segs else None)
    return ({"at": pick["end"], "text": pick["text"].strip()[:120],
             "matched_formula": False} if pick else None)


def cmd_analyze(a):
    need("ffmpeg"); need("ffprobe")
    wd = workdir(a.ep)
    if not os.path.exists(a.src):
        sys.exit(f"source not found: {a.src}")
    total = duration(a.src)
    wav = ensure_wav(a.src, wd)
    # Transcribe the SOURCE, not the 16k analysis.wav: the ffmpeg mono downsample drops
    # speech the decoder would otherwise find (quieter co-hosts vanish from VAD/detection).
    tr = ensure_transcript(a.src, wd, a.model, a.language)
    segs = [s for s in tr["segments"] if s["text"].strip()]
    if not segs:
        sys.exit("transcript has no segments")

    vals, w = rms_windows(wav, wd, total)
    speech = [v for v in vals if v > -40]
    speech_median = sorted(speech)[len(speech) // 2] if speech else -20.0
    thresh = a.silence_thresh if a.silence_thresh is not None else round(speech_median - 15, 1)

    rep = repetition_scan(segs)
    suspects = suspect_segments(segs, vals, w, thresh)
    trusted = [s for i, s in enumerate(segs) if i not in suspects]
    start, end = propose_start(trusted), propose_end(trusted)
    if not start or not end:
        sys.exit("could not propose boundaries; inspect analysis.json by hand")

    runs = silence_runs(vals, w, thresh, start["at"], end["at"])
    trims = [{"start": round(s, 2), "end": round(e, 2), "dur": round(e - s, 2)}
             for s, e in runs if e - s >= KEEP_UNDER]

    report = {
        "episode": a.ep, "source": a.src, "source_duration": round(total, 2),
        "workdir": wd,
        "rms": {"window_ms": round(w * 1000, 1), "speech_median_db": round(speech_median, 1),
                "silence_threshold_db": thresh, "quiet_runs": len(runs)},
        "repetition": rep,
        "suspect_segments": [{"start": round(segs[i]["start"], 2), "end": round(segs[i]["end"], 2),
                              "why": why, "text": segs[i]["text"].strip()[:80]}
                             for i, why in sorted(suspects.items())],
        "proposed_start": start, "proposed_end": end,
        "trim_candidates": trims,
        "proposed_cut_start": round(start["at"] - START_PAD, 2),
        "proposed_cut_end": round(end["at"] + END_PAD, 2),
    }
    json.dump(report, open(os.path.join(wd, "report.json"), "w"), indent=2)

    print(f"EPISODE {a.ep}   source {hms(total)}   workdir {wd}")
    print(f"  speech median {speech_median:.1f}dB -> silence threshold {thresh}dB "
          f"({len(runs)} quiet runs in show region)")
    if rep["suspect"]:
        print("  !! WHISPER REPETITION SUSPECTED — re-transcribe the affected region as a")
        print(f"     slice before trusting boundaries. longest run {rep['longest_consecutive_run']}"
              + (f" at {rep['longest_run_at']:.1f}s" if rep["longest_run_at"] else ""))
        for r in rep["repeated_texts"]:
            print(f"     x{r['count']}  {r['text']!r}")
    else:
        print("  repetition scan clean")
    if suspects:
        print(f"  !! {len(suspects)} suspect segment(s) left out of the boundary proposal (verify them):")
        for i, why in sorted(suspects.items()):
            print(f"     {segs[i]['start']:7.2f}s  {why}: {segs[i]['text'].strip()[:70]!r}")
    print()
    print(f"  START  {start['at']:.2f}s ({hms(start['at'])})"
          + ("  [matched cold-open formula]" if start["matched_formula"] else "  [NO formula match]"))
    print(f"         {start['text']!r}")
    print(f"  END    {end['at']:.2f}s ({hms(end['at'])})"
          + ("  [matched sign-off formula]" if end["matched_formula"]
             else "  [NO sign-off formula — using last sustained speech; confirm this]"))
    print(f"         {end['text']!r}")
    print()
    if trims:
        print(f"  {len(trims)} silence(s) >= {KEEP_UNDER}s inside the show:")
        for t in trims:
            print(f"     {t['start'] / 60:6.2f}min  {t['dur']:.2f}s  "
                  f"--cut {t['start']}:{t['end']}")
        print("     (judgement call: a pause after a punchline is content, not dead air)")
    else:
        print(f"  no silences >= {KEEP_UNDER}s inside the show (normal for this show)")
    print()
    print("  NEXT: verify both boundaries, then render:")
    print(f"    podcast_audio.py verify --ep {a.ep} --at {start['at']:.2f}")
    print(f"    podcast_audio.py verify --ep {a.ep} --at {end['at']:.2f}")
    print(f"    podcast_audio.py render --ep {a.ep} --src {a.src!r} "
          f"--start {start['at']:.2f} --end {end['at']:.2f}")


# ---------------------------------------------------------------- verify

def cmd_verify(a):
    wd = workdir(a.ep)
    report_path = os.path.join(wd, "report.json")
    if not os.path.exists(report_path):
        sys.exit(f"{report_path} missing — run analyze first")
    src = json.load(open(report_path))["source"]
    lo = max(0.0, a.at - a.window / 2)
    slice_wav = os.path.join(wd, f"slice_{int(a.at)}.wav")
    # Slice the SOURCE (native rate): a 16k slice of analysis.wav loses quiet speech to VAD.
    run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-ss", f"{lo}",
         "-t", f"{a.window}", "-i", src, "-vn", "-ac", "1", slice_wav])
    whisper([slice_wav, "--model", a.model, "--language", a.language,
             "--output-format", "txt", "--output-dir", wd])
    txt = open(os.path.join(wd, f"slice_{int(a.at)}.txt")).read().strip()
    print(f"SLICE {lo:.2f}s -> {lo + a.window:.2f}s (around {a.at:.2f}s)")
    print(txt if txt else "  (silence — nothing transcribed; the candidate was debris)")
    print()
    print("  Agrees with the full-file transcript? Boundary is real. If it disagrees or comes")
    print("  back empty, that candidate was a hallucination — pick the next run.")


# ---------------------------------------------------------------- render

def parse_cuts(raw):
    cuts = []
    for c in raw or []:
        try:
            a_, b_ = c.split(":")
            cuts.append((float(a_), float(b_)))
        except ValueError:
            sys.exit(f"bad --cut {c!r}, expected START:END in seconds")
    return sorted(cuts)


def keep_spans(start, end, cuts):
    """Show span minus trimmed silences.

    A silence [a, b] collapses to TRIM_TO by keeping TRIM_TO/2 of it on each
    side of the join: keep up to a + TRIM_TO/2, resume at b - TRIM_TO/2. That
    leaves exactly TRIM_TO of pause and keeps real audio well clear of the cut.

    Do NOT centre the removal on the gap's midpoint, and do not pad outward
    across the join. Both shrink the removal: on a 2.31s pause with TRIM_TO
    0.75 that combination removed 0.45s and left 1.86s, a trim that does
    nothing. There is no whisper timing error to pad against here either, since
    these boundaries come from RMS measurement, not from word timestamps.
    """
    spans, cursor = [], start
    for a_, b_ in sorted(cuts):
        if b_ <= start or a_ >= end:
            continue
        left, right = a_ + TRIM_TO / 2, b_ - TRIM_TO / 2
        if right <= left or left <= cursor:
            continue  # shorter than the target, or overlaps the previous cut
        spans.append((cursor, left))
        cursor = right
    spans.append((cursor, end))
    return [(max(0.0, s), e) for s, e in spans if e > s]


def loudnorm_measure(src, spans, wd, lufs):
    """Pass 1. Also tells us WHY we may not hit the target: if the source peaks
    above the true-peak ceiling, loudnorm falls back to dynamic and no number of
    passes will land exactly on the target.

    Via a script file, not -filter_complex: an episode with many trims builds a
    chain long enough to run into argument limits."""
    path = os.path.join(wd, "filter_measure.txt")
    open(path, "w").write(
        build_chain(spans, tail=f"loudnorm=I={lufs}:TP=-1.5:LRA=11:print_format=json"))
    p = subprocess.run(["ffmpeg", "-nostdin", "-i", src, "-vn",
                        "-/filter_complex", path, "-map", "[outa]",
                        "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr, re.S)
    if not m:
        sys.exit("loudnorm measurement pass produced no JSON")
    return json.loads(m.group(0))


def build_chain(spans, tail):
    parts, labels = [], []
    for i, (s, e) in enumerate(spans):
        parts.append(f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{i}]")
        labels.append(f"[a{i}]")
    if len(spans) > 1:
        parts.append("".join(labels) + f"concat=n={len(spans)}:v=0:a=1[cat]")
        head = "[cat]"
    else:
        head = labels[0]
    parts.append(f"{head}{tail}[outa]")
    return ";".join(parts)


def remap_transcript(wd, spans, out_srt, out_txt):
    tr = json.load(open(os.path.join(wd, "analysis.json")))
    segs = [s for s in tr["segments"] if s["text"].strip()]

    offsets, cum = [], 0.0
    for s, e in spans:
        offsets.append((s, e, cum - s))
        cum += e - s

    def to_out(t, side):
        """Output time of t; a time inside a removed region snaps to the nearest kept edge
        (start -> next kept span, end -> previous one), so boundary-crossing lines survive."""
        for s, e, sh in offsets:
            if s <= t <= e:
                return t + sh
        if side == "start":
            nxt = [s + sh for s, e, sh in offsets if s > t]
            return nxt[0] if nxt else None
        prv = [e + sh for s, e, sh in offsets if e < t]
        return prv[-1] if prv else None

    cues, plain, prev = [], [], None
    para = []
    for s in segs:
        a_, b_ = to_out(s["start"], "start"), to_out(s["end"], "end")
        if a_ is None or b_ is None or b_ <= a_:
            continue
        txt = s["text"].strip()
        cues.append(f"{len(cues) + 1}\n{ts(a_)} --> {ts(b_)}\n{txt}\n")
        if prev is not None and a_ - prev > 1.2 and len(" ".join(para)) > 400:
            plain.append(" ".join(para)); para = []
        para.append(txt); prev = b_
    if para:
        plain.append(" ".join(para))

    open(out_srt, "w").write("\n".join(cues))
    open(out_txt, "w").write("\n\n".join(plain) + "\n")
    return len(cues), sum(len(p.split()) for p in plain)


def measure_output(path):
    p = subprocess.run(["ffmpeg", "-nostdin", "-i", path, "-af",
                        "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    def grab(pat):
        m = re.search(pat, p.stderr)
        return float(m.group(1)) if m else None
    return {"i": grab(r"I:\s*(-?[\d.]+)\s*LUFS"),
            "lra": grab(r"LRA:\s*(-?[\d.]+)\s*LU"),
            "tp": grab(r"Peak:\s*(-?[\d.]+)\s*dBFS")}


def cmd_render(a):
    need("ffmpeg")
    wd = workdir(a.ep)
    if not os.path.exists(a.src):
        sys.exit(f"source not found: {a.src}")
    if not os.path.exists(os.path.join(wd, "analysis.json")):
        sys.exit(f"no analysis.json in {wd} — run analyze first")
    if a.end <= a.start:
        sys.exit(f"end ({a.end:.2f}) must be after start ({a.start:.2f})")
    cuts = parse_cuts(a.cut)
    spans = keep_spans(a.start, a.end, cuts)
    kept = sum(e - s for s, e in spans)
    src_dur = duration(a.src)

    stats = loudnorm_measure(a.src, spans, wd, a.lufs)
    dynamic = stats.get("normalization_type") == "dynamic"
    tail = (f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11"
            f":measured_I={stats['input_i']}:measured_TP={stats['input_tp']}"
            f":measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}"
            f":offset={stats['target_offset']}:linear=true")

    out_dir = a.out_dir or EXPORTS
    os.makedirs(out_dir, exist_ok=True)
    mp3 = os.path.join(wd, f"{a.ep}.mp3")
    chain_file = os.path.join(wd, "filter.txt")
    open(chain_file, "w").write(build_chain(spans, tail))
    run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-i", a.src, "-vn",
         "-/filter_complex", chain_file, "-map", "[outa]",
         "-ac", "2", "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", mp3])

    srt, txt = os.path.join(wd, f"{a.ep}.srt"), os.path.join(wd, f"{a.ep}.txt")
    n_cues, n_words = remap_transcript(wd, spans, srt, txt)
    meas = measure_output(mp3)

    # Never clobber a published episode. The transcripts follow the mp3's name:
    # a .srt describing a different cut than the .mp3 beside it is worse than
    # an extra file.
    stem = a.ep
    renamed = os.path.exists(os.path.join(out_dir, f"{a.ep}.mp3"))
    if renamed:
        stem = f"{a.ep}-new"
    final = os.path.join(out_dir, f"{stem}.mp3")
    shutil.copy(mp3, final)
    shutil.copy(srt, os.path.join(out_dir, f"{stem}.srt"))
    shutil.copy(txt, os.path.join(out_dir, f"{stem}.txt"))

    print(f"Original: {hms(src_dur)}  ->  Episode: {hms(kept)}")
    print(f"Show starts {ts(a.start, '.')}  ends {ts(a.end, '.')}")
    print(f"Bumper cut: {hms(a.start)} · End clipped: {src_dur - a.end:.0f}s · "
          f"Silences trimmed: {len(cuts)}")
    print(f"Loudness: {meas['i']} LUFS, {meas['tp']} dBTP, LRA {meas['lra']}")
    if dynamic:
        print(f"  (loudnorm ran dynamic: the gain to reach {a.lufs} LUFS would push the source true peak")
        print(f"   ({stats['input_tp']} dBTP) past the -1.5 ceiling, so it limits instead. Expected, not a defect.)")
    print(f"Transcript: {n_cues} cues, {n_words} words")
    print(f"Delivered:  {final}")
    print(f"            {os.path.join(out_dir, stem)}.srt / .txt")
    if renamed:
        print(f"  !! {a.ep}.mp3 already exists in {out_dir} and was NOT overwritten;")
        print(f"     this render went to {stem}.* instead. That existing file is a published")
        print("     episode, so check which one you actually want before uploading.")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    an = sub.add_parser("analyze", help="extract, transcribe, measure, propose boundaries")
    an.add_argument("--ep", required=True, help="episode token, e.g. S5E20")
    an.add_argument("--src", required=True, help="raw recording (audio or video)")
    an.add_argument("--model", default=MODEL)
    an.add_argument("--language", default=LANGUAGE, help="ISO (pt, en...) or auto; default pt or $STUDIO_LANGUAGE")
    an.add_argument("--silence-thresh", type=float, default=None,
                    help="override the computed dB threshold")
    an.set_defaults(func=cmd_analyze)

    ve = sub.add_parser("verify", help="re-transcribe a slice around a timestamp")
    ve.add_argument("--ep", required=True)
    ve.add_argument("--at", type=float, required=True, help="timestamp to check (s)")
    ve.add_argument("--window", type=float, default=10.0)
    ve.add_argument("--model", default=MODEL)
    ve.add_argument("--language", default=LANGUAGE)
    ve.set_defaults(func=cmd_verify)

    re_ = sub.add_parser("render", help="cut, normalize, encode, remap transcript")
    re_.add_argument("--ep", required=True)
    re_.add_argument("--src", required=True)
    re_.add_argument("--start", type=float, required=True, help="confirmed first word (s)")
    re_.add_argument("--end", type=float, required=True, help="confirmed last word (s)")
    re_.add_argument("--cut", action="append",
                     help="silence to trim, START:END in seconds (repeatable)")
    re_.add_argument("--out-dir", default=None)
    re_.add_argument("--lufs", type=float, default=LUFS, help="integrated loudness target (default -16)")
    re_.set_defaults(func=cmd_render)

    a = p.parse_args()
    # start/end arrive as the confirmed WORD boundaries; apply the show pads here
    if a.cmd == "render":
        a.start = max(0.0, a.start - START_PAD)
        a.end = a.end + END_PAD
    a.func(a)


if __name__ == "__main__":
    main()
