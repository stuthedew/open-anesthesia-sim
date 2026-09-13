---
id: PL-LKGL
title: A verify: command cannot detect a stale item: it tests for the presence of the fix, not the fault, so an item whose problem was solved another way stays red forever and reads as outstanding work
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: queue-hygiene
touches: docs/items, .claude/skills/docket/SKILL.md
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

**Why it matters.** The measured scale is a third of the workflow lane - 12 dead
and 31 partly overtaken out of 134 - and the property `CLAUDE.md` names as
earning attention is present in full: the store gives a wrong answer silently.
Nothing is marked, so a stale item is ranked, offered by `bin/docket next`,
counted into the debt gate, and read past by session after session, each paying
to rediscover that it no longer reproduces. It also corrupts the lane's own
measurement, since the 0.69 self-generation rate is computed over a set a third
of which is not real.

The field that looks like it should catch this cannot, for a structural reason
rather than a fixable one: `verify:` is specified as a command that fails before
the work and passes after, so it tests for the presence of the fix and never for
the presence of the fault. `PL-K2YF` is the clean case - `grep -q '^v0.2.6 was'
ROADMAP.md` will fail forever, because the section it asks about stopped
existing and nobody will ever write the line.

**Decision needed.** What the project does about staleness, given that a churn
advisory was built, measured against the sweep's verdicts and rejected - the best
threshold tried flags 6 of 12 dead items at a 20% false-alarm rate, and `partly`
churns *less* than `yes`, so the signal is not even monotone. Three routes:

1. **Schedule the sweep.** Make the periodic audit a named beat - once per
   release train, in `ROADMAP.md`'s cadence and in the `docket` skill's release
   mode - so it recurs without anyone remembering to ask. It found 43 items in
   one pass and is the only mechanism that has worked. Cost: a session per
   release train, and it stays a judgment call rather than a check.
2. **Record a fault test beside the fix test.** A second optional field naming a
   command that passes *while the fault is present*, so an item whose problem was
   solved another way goes green and is reported. Cost: a second command per
   item, written at the same moment as the first and wrong in the same ways.
3. **Drop this item**, having recorded the negative result, and let `PL-6ZQY`'s
   sweep be the answer each time somebody notices.

The brief prefers (1): it is the only one with evidence behind it, and `CLAUDE.md`
says not to script the judgment half. Whichever is chosen, the rejected churn
advisory and its numbers stay recorded here so it is not rebuilt.

**Done when.** The route is chosen and recorded, and if it is (1) the beat is
written where a session running the release train will meet it rather than in
this brief.
