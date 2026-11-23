---
id: PL-B0JG
title: docs/MODEL.md and app/playback.py give PL-SQJ1's measured playback rate as 99.0 to 99.9% of every rung's setting, but the item's own table measured 20x at 98.9%
priority: P3
effort: S
status: done
classes: docs
feature: presentation-safety
milestone: v0.6.22
touches: docs/MODEL.md, src/anesthesia_sim/app/playback.py, docs/INTERFACE.md
added: 2026-09-27
closed: 2026-11-22
pr: 2260
payoff: the authoritative spec states the playback measurement it cites, not a floor a tenth of a point above it
verify: ! grep -qF '99.0 to 99.9' docs/INTERFACE.md
---

**Problem.** `docs/MODEL.md`'s passage under **What the rate label is a
statement about, and what was measured** (§ "Interface boundary") and
`src/anesthesia_sim/app/playback.py`'s module docstring both say that, measured
on 2026-09-27 on the Qt loop, every rung from 1x to 300x delivered "99.0 to
99.9%" of its setting. `PL-SQJ1`'s measurement table, which both passages
report, has the 20x rung at 98.9% (19.8x delivered over 8 s), and its own prose
puts what is left of the shortfall at 0.1-1.3%. The floor both documents state
is a tenth of a point above the lowest rung measured.

**Why it matters.** It changes no decision and no displayed value: `PL-2NYN`'s
guard is drawn at 95% of ticks, and the ratified answer to leave the label as
it is rests on the loop keeping its rate, which 98.9% still shows. But
`docs/MODEL.md` is the authoritative specification, and it states the figure as
a measurement, so it should be the measured one. Found while cutting v0.5.15
(`PL-ZZTF`), whose release notes give the table's 98.9 to 99.9%.

**Done when.** Both passages give the range the table measured, and neither
states 99.0 as its floor: `! grep -rnE '99\.0 to 99\.9' docs/MODEL.md src/`.

**Reproduced 2026-09-28.** Both passages read "99.0 to 99.9%", and
`PL-SQJ1`'s table row for 20x reads 98.9%.

**Checked 2026-11-22** against `d4e8200`: still applies. `docs/INTERFACE.md` and the module docstring of `app/playback.py` both still say every rung "delivered 99.0 to 99.9%" of its setting, against `PL-SQJ1`'s measured 98.9% at 20x.

**Closed 2026-11-22.** Documentation checked for statements this change made false: `docs/INTERFACE.md` (§§ "Minimum displayed outputs", "Values that must stay reachable", "The code and tests behind the layout requirements", "Minimum contrast for text and graphics", "Color as a cue: agent colors and the alert color", "The code and tests behind the color requirements", "The agent-accounting panel", "What the reader chooses: traces, window and playback rate"), `docs/MODEL.md`, `docs/VERIFICATION.md`, `README.md`, `.claude/rules/ui-color.md`, `.claude/skills/run-the-app/SKILL.md`, and the docstrings of `app/dashboard_frame.py`, `app/formatting.py`, `app/playback.py` and `tests/integration/test_qt_rendering.py`.
