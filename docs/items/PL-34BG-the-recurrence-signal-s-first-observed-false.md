---
id: PL-34BG
title: the recurrence signal's first observed false positive: bin/docket new matched a stale-docstring finding to PL-SHTR's LANDED_GUARD recursion on shared tokens alone, wrote recurrences: onto it, and no command can unwrite one
status: untriaged
added: 2026-09-20
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
