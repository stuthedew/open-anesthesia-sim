---
id: PL-9KP5
title: docs/ARCHITECTURE.md still describes the sample store PL-2FM6 deleted, and routes every new-code session at history_window()
priority: P2
effort: M
status: ready
classes: docs, defect
feature: documentation-standard
touches: docs/ARCHITECTURE.md
added: 2026-09-14
verify: python3 tools/doc_check.py check && ! grep -qF 'history_window()' docs/ARCHITECTURE.md
---

**Problem.** docs/ARCHITECTURE.md still describes the sample store PL-2FM6 deleted, and routes every new-code session at history_window()

**Why it matters.** `.claude/rules/where-new-code-goes.md` loads on every write
under `src/` and `tests/` and sends the session to
`docs/ARCHITECTURE.md` § "Where new code belongs" for the answer, deliberately
not restating it. That section tells a session building a panel to ask
`history_window()` for the span it draws. There is no `history_window`. The
rule's whole design rests on the document being right.

**What is stale, found 2026-09-14.** `PL-2FM6` deleted `RunHistory` and the
sample store; nothing swept the architecture document behind it.

- `docs/ARCHITECTURE.md:149-150` — "one `SimulationHistorySample` per
  simulation step, not trimmed — is answered for separately, by
  `history_window()`". Neither name exists in `src/`.
- `docs/ARCHITECTURE.md:167, 177` — `evaluate_window(start_s, stop_s, columns)`.
  `RunDefinition` has `evaluate` and `evaluate_anchored`.
- `docs/ARCHITECTURE.md:185-190` — "Both records are live in this release and
  the chart still draws from the recorded one ... PL-2FM6 is what finishes it."
  `PL-2FM6` is closed and there is one record.
- `docs/ARCHITECTURE.md:830-836` — the § "Where new code belongs" bullet above.

**What replaced them.** `SimulationController.drawn_window(start_s, stop_s,
columns)` returns a `DrawnWindow`: the states at the instants the chart plots,
per substance, with `RecordedSeries` as the address of one trace. `DrawnWindow`'s
own docstring says it "replaces `HistoryWindow`, and the difference is what
`PL-2FM6` is", so the code records the change and the map does not.

**Not a doc_check gap to close with a check.** `check_package_maps` compares
names against the tree and never the prose beside them, and that is the right
scope — whether a sentence is still *true* is the judgment `CLAUDE.md` says not
to script. This is a sweep somebody owes, not a tool.

**Verified 2026-09-14 against `fb60a00`. All four regions still read as briefed;
one line number has drifted.** `grep -n
'SimulationHistorySample\|history_window\|evaluate_window\|Both records are live'
docs/ARCHITECTURE.md` returns `149`, `150`, `167`, `177`, `185`, `919`, `923`.
The first five are where the brief says. The § "Where new code belongs" bullet
is at `docs/ARCHITECTURE.md:919-925`, not `830-836` — the heading itself is at
`:898` — and it is the same text: "read only what `SimulationSnapshot` already
carries and what a recorded sample already records — a `SimulationHistorySample`
holds its values per substance ... A panel wanting the run rather than the
instant asks `history_window()` for the span it draws".

Neither name exists in `src/`. `grep -rn 'history_window' src/` returns nothing,
and the two `SimulationHistorySample` hits under `src/` are both docstrings
naming the deleted class rather than using it (`app/controller.py:234` to say
`DrawnWindow` replaced `HistoryWindow`; `app/formatting.py:24` by mistake, which
is `PL-4K9V`). `evaluate_window` does not exist either:
`core/run_definition.py:402` and `:472` declare `evaluate` and
`evaluate_anchored`, both returning `SampledWindow`, and the controller's own
read is `SimulationController.drawn_window(start_s, stop_s, columns)` at
`app/controller.py:1096`.

**The routing half is what makes this more than a stale map.**
`.claude/rules/where-new-code-goes.md:10` sends a session to this document's
§ "Where new code belongs" and deliberately does not restate the answer, so a
session building a panel is told to call a function that was deleted. It will
find out at the first import error rather than at review, so the cost is a
session's turns and a wrong mental model of the boundary, not a wrong number —
which is why this is `docs, defect` and `P2` rather than `safety`. The
model-specification half of the same rot is `PL-27H0`, which is `safety` because
`docs/MODEL.md` misstates the provenance of a displayed point rather than the
name of a function.

**Done when.** `docs/ARCHITECTURE.md` names only symbols that exist.
`history_window`, `evaluate_window`, `SimulationHistorySample` and `RunHistory`
appear nowhere in the file; `:149-150` describes how a run's states are reached
from `RunDefinition` rather than a per-step store; `:167` and `:177` name
`evaluate` / `evaluate_anchored` and `SampledWindow`; `:185-190` no longer
claims two live records or an unfinished `PL-2FM6`; and the § "Where new code
belongs" bullet at `:919-925` tells a panel author to ask
`SimulationController.drawn_window(start_s, stop_s, columns)` for the span it
draws and names `RecordedSeries` as the address of one trace. `python3
tools/doc_check.py check` reports 0 errors.
