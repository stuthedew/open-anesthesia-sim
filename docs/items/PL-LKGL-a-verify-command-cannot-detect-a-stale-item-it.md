---
id: PL-LKGL
title: A verify: command cannot detect a stale item: it tests for the presence of the fix, not the fault, so an item whose problem was solved another way stays red forever and reads as outstanding work
status: untriaged
added: 2026-09-12
---

**Problem.** A verify: command cannot detect a stale item: it tests for the presence of the fix, not the fault, so an item whose problem was solved another way stays red forever and reads as outstanding work

**Observed 2026-09-12**, while auditing the workflow lane under `PL-6ZQY`. A
17-agent sweep found 12 open items whose defect no longer reproduces and 31
more partly overtaken - 32% of 134 items. Nothing in the project noticed, and
the field that looks like it should cannot.

**Why `verify:` cannot.** The field is specified as "a command that fails
before the work and passes after", so it tests for the *presence of the fix*,
never for the presence of the fault. An item whose problem was solved a
different way keeps failing, and `docket check --verify` - which advises on
commands that already pass - correctly says nothing. Six of the twelve dead
items carry a `verify:`; all six still fail:

```text
PL-2QMK exit=1   PL-LM8P exit=1   PL-S5YM exit=5
PL-21GS exit=1   PL-C8MV exit=1   PL-K2YF exit=1
```

`PL-K2YF` is the clean illustration. Its command is `grep -q '^v0.2.6 was'
ROADMAP.md` - has someone written the v0.2.6 narrative paragraph. The defect
died because the "Release narrative" section stopped existing: per-release
prose now lives in the version-table row. The problem is gone, nobody will
ever write that line, and the command fails forever.

**A churn advisory was tested and does not work.** Commits touching an item's
declared `touches` since it was filed, against the sweep's verdicts:

| still_real | n | median churn |
| --- | --- | --- |
| no | 12 | 30 |
| partly | 31 | 7 |
| yes | 90 | 9 |

`partly` churns *less* than `yes`, so the signal is not monotone. The best
threshold tried, churn >= 30, flags 6 of 12 dead items and 18 of 90 live ones -
a 20% false-alarm rate to catch half. That is the shape `CLAUDE.md` calls a
defect in the check rather than coverage, so it was not built. Recorded here so
it is not rebuilt.

**What follows.** Staleness here is a judgment, and `CLAUDE.md` says not to
script the judgment half. The mechanism that did work is the periodic sweep
itself, which is cheap enough to run once per release train and found 43 items
in one pass. Any fix proposed for this item has to beat that, not merely
automate something.
