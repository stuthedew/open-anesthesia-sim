---
id: PL-V8QG
title: docs/maintainer.md recommends Claude Code's opusplan mode as the default split for strong-model work, which names the wrong family if the strongest model is not an Opus
priority: P2
effort: S
status: done
classes: docs, defect
feature: model-capability-routing
touches: docs/maintainer.md
added: 2026-09-19
closed: 2026-09-19
verify: grep -q 'code.claude.com/docs/en/model-config' docs/maintainer.md && ! grep -qF 'opusplan` mode is a reasonable default' docs/maintainer.md
---

**Problem.** docs/maintainer.md recommends Claude Code's opusplan mode as the default split for strong-model work, which names the wrong family if the strongest model is not an Opus

**Why it matters.** It is the only *concrete* model recommendation the
repository makes. § "Match model capability to the work" says `opusplan` "is a
reasonable default for that split", and states two caveats about it — neither of
which is that it may name the wrong family. If the strongest available model is
not an Opus, an owner following the file's one actionable sentence puts
reasoning-heavy work on a weaker model than the file's own rule asks for, and
the two caveats make the recommendation read as considered rather than stale.

Confirmed by the project owner on 2026-09-19 that Fable is stronger than Opus,
which is what makes this live rather than hypothetical.

**Why this is separate from `PL-13PB`.** `PL-13PB` names the current strongest
model, which is a fact to record. This decides what the *mode* recommendation
should become, which needs knowing what Claude Code currently offers for the
strong/cheap split — whether an equivalent of `opusplan` exists for a
non-Opus strong model, or whether the recommendation should be replaced by the
plain instruction to switch deliberately and group runs to avoid a cold cache.
That is why it is `blocked-by: PL-13PB` rather than folded into it: the fact
comes first, and this needs a source consulted rather than recalled.

**Do not answer this from memory.** `CLAUDE.md` requires current standards and
tooling be checked against the source rather than recalled, and Claude Code's
mode lineup is exactly the kind of fact that moves. Read the current
documentation before rewriting the paragraph.

**Done when.** § "Match model capability to the work" makes no recommendation
that presumes an Opus-family strong model, and whatever replaces it is either
verified against current Claude Code documentation or stated as a plain
switch-deliberately instruction with no mode named.
