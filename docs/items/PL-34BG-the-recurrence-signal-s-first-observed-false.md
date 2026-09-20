---
id: PL-34BG
title: the recurrence signal's first observed false positive: bin/docket new matched a stale-docstring finding to PL-SHTR's LANDED_GUARD recursion on shared tokens alone, wrote recurrences: onto it, and no command can unwrite one
priority: P3
effort: S
status: ready
classes: defect, infra
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, docs/items/PL-SHTR-docket-verify-does-not-set-landed-guard-so-an.md
added: 2026-09-20
payoff: gives the one queue field a session cannot correct a correction path, and clears two entries now measured false
verify: grep -q 'def test_a_recurrence_entry_can_be_withdrawn' subprojects/docket/tests/test_cli.py
---

**Problem.** the recurrence signal's first observed false positive: bin/docket new matched a stale-docstring finding to PL-SHTR's LANDED_GUARD recursion on shared tokens alone, wrote recurrences: onto it, and no command can unwrite one

**What happened, 2026-09-20, in `PL-G21K`'s close-out.** Two unrelated findings
were filed minutes apart with `bin/docket new`. Both were matched to `PL-SHTR`
("docket verify does not set `LANDED_GUARD`, so an item whose `verify:` runs
`docket check --verify` replays the whole store one level down"), and both
wrote a `recurrences:` entry onto it. `PL-SHTR` now reads as filed again twice
since 2026-09-07, and it was filed again zero times.

| filing | subject | relation to `PL-SHTR` |
| --- | --- | --- |
| `PL-S8JT` | `tools/ignore_check.py`'s docstring cites a `SUPPRESSIONS` entry that `PL-G21K` removed | none |
| `PL-34BG` | this item | names `PL-SHTR` only to say it is not it |

**Why it matters rather than being noise.** A repeat filing is evidence that
feeds the generator tier, which ranks above every band but `P0`
(`docs/WORKING_NOTES.md`, 2026-09-20), so a false entry inflates an item toward
a tier reserved for mechanisms that cause three or more items. The signal
surfaces a cluster at three, and one more mis-match reaches it. And the field
is deliberately not writable by `docket set` - "the field's whole worth is that
each entry was written by the tool at the moment it matched a filing"
(`cli.py`, `PL-X5JR`) - so there is no command that unwrites one, and the only
correction available is hand-editing another item's front matter, which is the
thing that rule exists to prevent.

**The entry was left in place deliberately.** It is the only physical evidence
of the mechanism's first miss, and it costs one line to delete once the
question below is answered. Removing it first would destroy the specimen.

**The cause is not established, and two candidates were not separated.**
Selection needs a shared declared path and neither capture declared `touches`,
so what `near_duplicates` was given as `paths` - most likely path-shaped tokens
read out of the title - is the first thing to check. Ranking is Jaccard over
title content words, and both titles *describe* `PL-SHTR` or its vocabulary
(`docket`, `verify`, `landed`, `guard`), which is the second: a filing that
names the item it is distinguishing itself from looks like that item. Do not
write either into the brief as the cause without measuring it.

**Related, and filed before this was observed:** `PL-DGP0` holds that
`duplicates.DISPLAY_FLOOR` at 0.10 fires the near-duplicate print too readily.
This is the same floor seen from the write side rather than the print side -
the print is advisory and a session reads past it, while `recurrences:` is
written into another item's file and persists.

**Done when** a false match either cannot be written or can be withdrawn by
command, and the two candidate causes above are separated by measurement.

## Re-scoped 2026-09-20: `#794` landed during the session that filed this

`PL-DGP0` merged as `#794` - "derive the recurrence threshold from the
generator floor, and raise the similarity floor to 0.15" - between this item
being filed and its close-out. So the threshold this was evidence about has
already moved, and the question is whether either match would still be made.

**Measured against the shipped `duplicates.similarity`, not reasoned about:**

| filing | similarity to `PL-SHTR`'s title | clears the 0.15 floor? |
| --- | --- | --- |
| `PL-S8JT` | 0.1143 | no |
| `PL-34BG` (this item) | 0.1081 | no |

Both sat between the old floor (0.10) and the new one (0.15), so **neither
match would be made today** and both are evidence *for* `#794` rather than
against it - an independent, after-the-fact confirmation from a session that
had not read `PL-DGP0` when it hit the behaviour. The matching half of this
item is closed by that change and is not work.

**What is left, and it is the narrower and more durable half.** Two
`recurrences:` entries sit on `PL-SHTR` naming filings that are not repeats of
it, and they are now *known* false by the measurement above rather than merely
argued to be. The field is deliberately not writable by `docket set` - "the
field's whole worth is that each entry was written by the tool at the moment it
matched a filing" (`cli.py`, `PL-X5JR`) - and there is no command that
withdraws one. So a false entry, from any cause, is permanent, and a repeat
filing feeds the generator tier that ranks above every band but `P0`.

That is the residue: **a write with no correction path**, not a threshold.
Raising a floor reduces how often the bad write happens and gives no way to
undo one when it does, and the next cause need not be similarity at all.

**Done when** a false `recurrences:` entry can be withdrawn by command, with
the withdrawal as auditable as the write, and the two on `PL-SHTR` are gone.
Do not re-litigate the floor: `#794` decided it and the numbers above agree.

The `verify:` command greps `subprojects/docket/tests/test_cli.py` for
`test_a_recurrence_entry_can_be_withdrawn`, so the withdrawal path arrives
with a test under that name. Naming the test rather than the two `PL-SHTR`
lines is deliberate: deleting those by hand would satisfy a grep over that
file while leaving the next false entry just as permanent.
