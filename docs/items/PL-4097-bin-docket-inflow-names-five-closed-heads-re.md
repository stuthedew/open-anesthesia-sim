---
id: PL-4097
title: bin/docket inflow names five closed heads re-entered by three or more filings with no successor head - PL-61FT (7), PL-J6HP (5), PL-KGYT (5), PL-TZ7T (4), PL-GHHW (3); the four with a verdict read spent - so each is a generator whose fix did not hold under triage's three-post-close-instances rule until a session records a successor head or says why not
priority: P3
effort: M
status: done
classes: housekeeping
feature: generator-heads
milestone: v0.5.24
touches: docs/items/PL-0HLS-pl-tz7t-s-mechanism-is-producing-again-four.md, docs/items/PL-5DZ8-pl-kgyt-s-sweep-searched-what-model-vcs-and.md, docs/items/PL-8QMD-a-gate-entry-s-disposition-is-still-read-from.md, docs/items/PL-927J-pl-ghhw-s-mechanism-is-producing-again-three.md, docs/items/PL-Z64T-roadmap-md-s-v0-6-0-gate-lists-pl-5b1n-and-pl.md
added: 2026-10-12
closed: 2026-10-12
pr: 1452
verify: grep -qx 'root-cause-of: PL-6SV4, PL-9VPH, PL-SV0D, PL-TS7L' docs/items/*.md && grep -qx 'reenters: PL-KGYT' docs/items/PL-5DZ8-*.md && grep -qx 'reenters: PL-GHHW' docs/items/PL-927J-*.md && grep -qx 'reenters: PL-WD5Z, PL-J6HP' docs/items/PL-8QMD-*.md
no-successor: PL-61FT
---

**Problem.** bin/docket inflow names five closed heads re-entered by three or more filings with no successor head - PL-61FT (7), PL-J6HP (5), PL-KGYT (5), PL-TZ7T (4), PL-GHHW (3); the four with a verdict read spent - so each is a generator whose fix did not hold under triage's three-post-close-instances rule until a session records a successor head or says why not

**Recorded 2026-10-18** in this item's `no-successor:` field (`PL-C4F0`), so
`bin/docket inflow` lists `PL-61FT` apart from the open lines instead of
re-asking it.

**Answered 2026-10-12 for `PL-61FT`: no successor head** (project owner,
2026-10-12, ratified, "Agree", over reopening it live as a successor head
ranked above every band but `P0`, holding the pause on new workflow
mechanisms, with a design round for a guard redesign). It was put to him on a
decision card while `PL-6X0C` was being fixed, with keeping the bound
recommended, and he tapped "Keep the bound". `PL-61FT`'s bound works a misread
met in use as an item at its own rank, and is reopened by three `KNOWN_GAPS`
rows met within a quarter. Its seven re-entries are all done, each effort `S`,
and none was a row met: four false refusals by the gate-status guard met in
use (`PL-ZS13`, `PL-0FGH`, `PL-RC4S`, `PL-6X0C`), two ref-deleting prunes the
no-prune guard let past (`PL-VM7C`, `PL-P95F`), which the bound names as items
rather than rows, and one latent misread in `doc_check`'s make readers, found
by a sweep (`PL-GZXY`). So `PL-61FT`'s line in `bin/docket inflow` is answered
here, not a fix that did not hold, and its next re-entry is worked the same
way until three rows are met within a quarter. The question stays open for
the other four heads named above.

**Measured 2026-10-12 at 11:12 UTC:** `bin/docket inflow` also names three
closed heads the title does not, each re-entered by three or more filings:
`PL-4Q9B` (3), `PL-9HD1` (3) and `PL-WFFX` (4).

**Why it matters.** `bin/docket inflow` names these heads on every run, and the
list is how `CLAUDE.md` § "What this project is" expects something still
generating work to be found. A line nobody has answered reads as a generator
nobody is pulling, and one answered only in a reply is re-asked by the next
session to run the command. This item's own "no successor head" was that
misreading: it counted a successor by its `reenters:`, which three of these
heads' successors did not carry.

**Done when.** Every closed head `bin/docket inflow` names as re-entered by
three or more filings has its successor head named here, or the reason none is
owed, and each successor carries the `reenters:` naming the head whose fix it
says did not hold.

**Answered 2026-10-12 for the rest, by this item's design round.** Each has a
successor head, and each now carries the `reenters:` naming it, so `inflow`
lists the successor among the head's own re-entries:

- `PL-KGYT`: `PL-5DZ8` (recorded by `PL-74T0`, closed spent 2026-10-12) names
  all five re-entries as members, and the family head `PL-4S6C` (closed spent
  2026-10-12) names `PL-KGYT` itself, with `tools/fact_home_check.py` now
  refusing a second reader. `reenters: PL-KGYT` written on `PL-5DZ8`.
- `PL-J6HP`: its own verdict hands the record to `PL-WD5Z`, whose title names
  `PL-FD5Q`, and `PL-8QMD` (recorded by `PL-74T0`, closed spent 2026-10-12)
  names `PL-D388`, `PL-JV5Q` and `PL-QWF8`. `reenters: PL-WD5Z, PL-J6HP`
  written on `PL-8QMD`, which puts `PL-WD5Z` on the list too, answered by the
  same head. `PL-Z64T`'s `reenters: PL-J6HP` is removed: the backfill read its
  first generator-check line, which `PL-74T0` revised on 2026-10-11 to "Not a
  member of the gate head PL-8QMD" and to `PL-G424`'s fact - a fact owner named
  with no re-entry claimed, which the backfill's own standard leaves unwritten.
- `PL-GHHW`: `PL-927J` (closed spent 2026-09-27), titled "PL-GHHW's mechanism
  is producing again", names `PL-8BR0` and `PL-RLTK`; `reenters: PL-GHHW`
  written on it. The third, `PL-TFF9`, still open, is a deletion
  `vcs._landing_split` does not classify: a defect inside the one function every
  reader now answers from through `_Landings`, not a further reader beside it,
  so it is worked at its own rank.
- `PL-TZ7T`: none existed, and one is owed. Its four re-entries are four gaps
  in its one key, `duplicates.py` is unchanged since it closed, three are open
  with fixes that conflict over `docs/items`, and no ratified bound stands in
  the way as `PL-61FT`'s did. The count decides the record and nothing has spent
  the mechanism, so it is recorded live as `PL-0HLS`, at `P1`, which holds the
  pause on new workflow mechanisms until it closes. Its Done-when asks for a
  written bound on what no key can see, so it can close spent rather than chain.
- `PL-4Q9B`, `PL-9HD1`, `PL-WFFX` already had theirs, each carrying
  `reenters:`: `PL-MT3R`, `PL-HXJY`, `PL-979D`. `PL-MT3R`'s verdict still
  reads `live` as written when it was recorded; it closed 2026-09-26 with its
  four members done, and two filings have re-entered it since (`PL-20DL`,
  `PL-K3W5`), below three.

**Generator check.** Bookkeeping: the answers `inflow`'s list asks for, not an
instance of a head's fact. Its premise misread which later head succeeds a
closed one, because three successors carried no `reenters:`; that record is
written above, so no reader of the list is left to infer it.

**After the round, 2026-10-12.** Bringing `origin/main` in took the triage
pass merged as #1455, which put `PL-0HPV` on the list, re-entered by
`PL-RW3T`, `PL-ZXM1` and `PL-HSB3`, none of them a head. That line is
`PL-SH4H`'s question, filed rather than answered here. It also gave `PL-61FT`
an eighth re-entry, `PL-CDZ8`, which the owner's answer above covers until
three `KNOWN_GAPS` rows are met within a quarter. `PL-0WT0` asks for the list
to name a line's successor itself, so an answered line stops reading as an
open one.
