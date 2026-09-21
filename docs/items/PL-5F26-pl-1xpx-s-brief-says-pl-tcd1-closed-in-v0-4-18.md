---
id: PL-5F26
title: PL-1XPX's brief says PL-TCD1 closed in v0.4.18, but PL-TCD1 ships in v0.4.19 (#530 merged after the v0.4.18 cut)
priority: P3
effort: S
status: dropped
classes: docs
feature: queue-hygiene
touches: docs/items
added: 2026-09-13
closed: 2026-09-21
reason: `.claude/rules/citation-drift.md`'s closed-brief clause. `PL-1XPX` is `done`, so the wrong release attribution in its brief - `PL-TCD1` closing in v0.4.18 rather than v0.4.19 - is a historical record rather than a live assertion. Checked 2026-09-21 that no live document repeats it: `ROADMAP.md` places `PL-TCD1` in the v0.4.19 row correctly, and this item was the only other file naming the pair. Re-judged in `PL-PT7M`'s pass
verify: bin/docket check && ! grep -q 'in v0.4.18' docs/items/PL-1XPX-decide-what-the-readouts-show-while-two.md
---

**Problem.** PL-1XPX's brief says PL-TCD1 closed in v0.4.18, but PL-TCD1 ships in v0.4.19 (#530 merged after the v0.4.18 cut)
**Why it matters.** Verified 2026-09-13: `PL-TCD1` carries `milestone: v0.4.19`
and closed on 2026-09-13, after the v0.4.18 cut, while `PL-1XPX`'s brief reads
"`PL-TCD1` closing in v0.4.18 is what made the snapshot able to name which run a
value belongs to". A wrong release attribution inside a brief survives, because
the next reader has no reason to check it against `docs/releases/` - and the
release notes are how this project reconstructs when a behavior arrived, which
is the question behind anything asked later about what a shipped build
displayed.

**Done when.** `PL-1XPX`'s brief names v0.4.19 as the release `PL-TCD1` shipped
in, and no line in that file still attributes it to v0.4.18.
