# Common Ground: Neuroscience — Brain, Mind and Behaviour

A short, original course connecting brain mechanisms with attention, learning, motivation, emotion, recovery and everyday choices. Uses the authorised Common Ground player and fictional repair-café setting.

Live: https://snowch.github.io/common-ground-neuroscience/

Six chapters, 54 learner-paced pages, 24 original concept figures, 12 decisions, written transfer, retrieval and a final case. Each page, feedback choice and recall answer has its own recorded Kokoro af_heart narration. Paragraph pauses, elapsed/remaining playback time, browser offline saving and portable chapter decks follow the series format. Research stays optional and requires a connection.

## Build and verify

`python3 scripts/check_content.py` validates alignment. `python3 build.py --preview --output out/preview` supports layout review before recording. `python3 build.py --portable --output out/portable`, `python3 scripts/build_hosted.py` and `python3 scripts/check_hosted.py` prepare a release only after audio is verified. `scripts/export_pdfs.py` produces the print companions.

The manual narration workflow produces disjoint recordings and independent transcription reports; it does not publish. The course workflow publishes only reviewed content and media on main. See `production/README.md` and `docs/learning-design.md`.

## Evidence and scope

The stories, diagrams and practical applications are original teaching examples. Primary research and open textbooks support the stated distinctions; fictional cases are not study data. Neural associations, cognitive accounts, behavioural effects and personal applications remain distinct. The course offers no diagnostic instrument, treatment or brain-optimisation guarantee. Independent academic review and learner testing remain outstanding. Automated audio/transcript checks are not human listening approval.

The popular Jack Reacher article is a claim to examine, not a validated protocol. Incubation, walking and network studies are linked with their task-specific limits.

Design guidance: [Instructional Design](https://github.com/joelrkohlman/instructional-design/blob/main/SKILL.md) and [Frontend Design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md). Narration uses the pinned [record-demo workflow](https://github.com/snowch/claude-skills/tree/c9a7c521568632aa216932f4c965df386498602a/plugins/demo-video/skills/record-demo), Kokoro v1.0 ONNX, af_heart, speed 1.0. Licensed runtime and font notices are retained.
