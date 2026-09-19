---
id: PL-T2LH
title: Cut v0.4.28 from the 58 finished items since v0.4.27: a patch on the v0.4.x track carrying one Gate 1 entry and v0.5.0's seventh early-shipped scope item, with v0.5.0 through v0.9.0 reserved
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-19
closed: 2026-09-19
verify: grep -q '^## Current baseline: v0.4.28' ROADMAP.md
---

**Problem.** Cut v0.4.28 from the 58 finished items since v0.4.27: a patch on the v0.4.x track carrying one Gate 1 entry and v0.5.0's seventh early-shipped scope item, with v0.5.0 through v0.9.0 reserved

**Asked for by the project owner, 2026-09-19** ("cut version"), on the offer
the session-start digest was carrying: 58 finished items stand unshipped since
`v0.4.27` (`bin/docket release --dry-run`), completing six features —
`carrier-collapse`, `decision-ownership`, `generator-heads`,
`generator-machinery-rank`, `session-start-cost` and `verify-invalidation`.

**Why this number.** `bin/docket wave` reports `Reserved 0.5.0, 0.6.0, 0.7.0,
0.8.0, 0.9.0`, every one spent by a `ROADMAP.md` milestone section, so the
`v0.4.x` patch track is the only place a cut can land — and § "Versioning
decision"'s test is the capability boundary a release crosses, which nothing
here crosses. Measured rather than read off the item titles:
`src/anesthesia_sim/data/` resolves to `d9f9c5b` at both `v0.4.27` and
`origin/main`, so no parameter moved; `tests/reference/` resolves to `fcb3eca`
at both, so every published-reference expected value is byte-identical and
still met; and the three files that change under `src/` are all under `app/`
(`chart_frame.py`, `qt_widgets.py`, `run_view.py`), so no equation, numerical
method or unit moved either. The mechanical guess agrees at `0.4.28`.

**It is not a no-op for a learner, which the last cut was.** Two of the 58
change what a learner sees, both in the interface layer. `PL-DHBX` gives the
Start, Pause and Reset buttons an explicit colour, their labels having been
illegible under the macOS Dark appearance; `PL-MN4J` makes the chart hover name
which run it is reading, so a hovered value is attributed while two runs are
drawn. Both are legibility and attribution fixes to values already displayed —
a presentation-correctness floor under `CLAUDE.md`'s safety-critical standard,
not a new capability — so the patch track is still right.

**What it carries from the gate, and why the no-interim-release rule does not
bind.** § "The debt gate" → "The cadence" says a gate takes no version and
that no interim release is cut partway through clearing one. Gate 1 stands at
**168 of 175 cleared**, with four entries still clearable here (`PL-H4N8`,
`PL-QBX0`, `PL-JVHL`, `PL-7DMJ`) and three blocked outside it (`PL-WZVZ`,
`PL-Z34C`, `PL-8PS6`), so this cut *is* partway through the clearing — unlike
`PL-TM9J`'s, which cleared the same test by carrying no gate entry at all. One
of the 58 is a frozen entry: `PL-S6WW`, added 2026-09-17 under the
unconditional safety/science exception and closed the same day, which
documents the reference temperature `docs/MODEL.md` asserted and never gave.

That does not make the cut a departure, and the practice is the record rather
than an inference. Every one of Gate 1's 175 frozen entries was checked for the
`milestone:` stamp it closed under, and cleared entries have shipped in
**twenty-one separate `v0.4.x` patches**, `v0.4.5` through `v0.4.26` — 20 in
`v0.4.15`, 16 in `v0.4.26`, 14 in `v0.4.21`, and so on down. The sentence bars
cutting a release *for* the gate, so that gate work does not scatter across
patches instead of landing in the milestone's notes; it has never been read to
bar a patch cut for its own content from carrying an entry that already merged.
`PL-T2LH` carrying one such entry out of 58 is that ordinary case.

**And a seventh Required-scope item ships early.** `PL-MN4J` is v0.5.0's own
`Required scope` entry "The chart's hover says which run it is reading"
(`ROADMAP.md:4077`), shipped in the `v0.4.x` track on the disposition timeline
row 5 already records: five in `v0.4.25` (`PL-TFX5`, `PL-J2TD`, `PL-ZMRT`,
`PL-B9PY`, `PL-5328`), `PL-8PSW` as a sixth in `v0.4.26`, and this as a
seventh. Row 5's running tally is what needs the note; the Required-scope entry
itself records what shipped and is unchanged, as `PL-8PSW`'s was.

**Why cut at all, rather than waiting for v0.5.0.** `v0.4.27` is tagged on
`origin` at `381d770`, so the refusal-on-untagged-predecessor does not bind,
and v0.5.0's implementation is still behind four open gate entries. Leaving 58
items untagged across that span means `git describe --contains` resolves
nothing over 58 items - second only to v0.4.26's 94 among the releases that
record a count — and the block includes `docs/MODEL.md` gaining 314 lines of
reference-condition specification, which is exactly the kind of change a later
reader needs to be able to date.

**What the cut carries in `ROADMAP.md`.** The version-table row, the
`current baseline` mark moved onto it, and the baseline section rewritten onto
this release — the three `bin/docket release` names — plus the timeline row 5
tally above, which it does not name. `0.4.28` reaches no milestone section, so
there is no heading to promote.

**Done when** `pyproject.toml` and `uv.lock` read `0.4.28`,
`docs/releases/v0.4.28.md` exists, `ROADMAP.md` carries the row, the moved
baseline mark and the rewritten baseline section, `make check` passes, and the
tag is pushed. The tag is the project owner's to run: a session cannot push a
tag ref here (`PL-N936`), so this item is not done on the merge alone.

**Why it matters.** Two of the 58 are reachable by a learner and both are
presentation-correctness fixes, which this project treats as part of the safety
standard rather than as polish: until `PL-DHBX`, a reader on the macOS Dark
appearance could not read the Start, Pause and Reset labels at all, and until
`PL-MN4J`, a hovered chart value named the agent and the instant but not which
of two drawn runs it came from — the correct number with the wrong patient
context. The tag is what lets a later session say which tree first had them,
and which tree first carried `docs/MODEL.md`'s reference conditions
(`PL-S6WW`); an untagged span cannot be repaired with confidence once the
history moves on.
