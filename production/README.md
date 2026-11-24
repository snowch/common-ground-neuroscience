# Narration production

Canonical captions and speech forms are in `af-heart/scenes.json`. Use pinned Kokoro v1.0 ONNX, af_heart, speed 1.0 throughout, with 0.65-second paragraph pauses. The separately obtained record-demo scripts and pinned model assets are hash-verified by `render_part.py`.

The manual Actions workflow renders four disjoint parts with four workers each, independently transcribes every clip with tiny.en and additionally checks flags and chapter samples with small.en, then verifies and assembles all 96 clips. Review discrepancies and phonemes before release. `encode_audio.py` produces AAC clips and six continuous chapter tracks at 48 kHz, 160 kbps, -16 LUFS with a -1.5 dB true-peak target.

Raw WAVs and production tools are local build products. Final screening reports and media hashes are retained under qa/. Automated transcript and waveform checks are not human listening approval; no independent academic review is claimed.
