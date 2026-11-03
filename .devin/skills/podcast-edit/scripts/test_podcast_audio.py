import json
import os
import tempfile
import unittest
from pathlib import Path

import podcast_audio as pa


class PodcastAudioTest(unittest.TestCase):
    def test_hints_ignore_case_accents_and_hyphens(self):
        self.assertTrue(pa._hit(("próximo episódio",), "OBRIGADO, ATÉ O PROXIMO-EPISODIO."))
        self.assertTrue(pa._hit(("bem-vindos",), "Bem vindos ao programa"))
        self.assertFalse(pa._hit(("bem-vindos",), "Obrigado pelo convite"))

    def test_echo_and_text_over_silence_are_suspect(self):
        segs = [
            {"start": 0.0, "end": 2.0, "text": "Bem-vindos ao podcast do estúdio hoje"},
            {"start": 2.0, "end": 4.0, "text": "Falamos de edição"},
            {"start": 6.0, "end": 8.0, "text": "bem vindos ao podcast do estudio hoje!"},
            {"start": 8.0, "end": 10.0, "text": "palavras sobre silêncio digital"},
        ]
        vals = [-20.0] * 16 + [-120.0] * 4  # 0.5 s windows: 8.0–10.0 s is digital silence
        suspects = pa.suspect_segments(segs, vals, 0.5, -40.0)
        self.assertEqual(suspects, {2: "echo of an earlier sentence", 3: "text over silence"})

    def test_silence_trim_leaves_target_pause(self):
        spans = pa.keep_spans(0.0, 20.0, [(5.0, 10.0)])
        self.assertEqual(spans, [(0.0, 5.0 + pa.TRIM_TO / 2), (10.0 - pa.TRIM_TO / 2, 20.0)])

    def test_srt_keeps_lines_that_cross_a_cut_edge(self):
        with tempfile.TemporaryDirectory() as wd:
            segs = [{"start": 8.3, "end": 11.0, "text": "Bem-vindos."},       # starts before the show start
                    {"start": 12.0, "end": 14.0, "text": "Segunda frase."}]
            Path(wd, "analysis.json").write_text(json.dumps({"segments": segs}))
            srt, txt = os.path.join(wd, "a.srt"), os.path.join(wd, "a.txt")
            cues, _ = pa.remap_transcript(wd, [(8.5, 20.0)], srt, txt)
            self.assertEqual(cues, 2)
            self.assertIn("00:00:00,000 --> 00:00:02,500\nBem-vindos.", Path(srt).read_text())


if __name__ == "__main__":
    unittest.main()
