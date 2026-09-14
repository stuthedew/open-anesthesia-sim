---
id: PL-9KP5
title: docs/ARCHITECTURE.md still describes the sample store PL-2FM6 deleted, and routes every new-code session at history_window()
status: untriaged
added: 2026-09-14
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
