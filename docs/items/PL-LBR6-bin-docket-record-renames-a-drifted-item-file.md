---
id: PL-LBR6
title: bin/docket record renames a drifted item file as a side effect of writing a pr number, which conflicts against whoever else is holding that file
priority: P2
effort: S
status: done
classes: defect, infra
feature: slug-rename-on-write
milestone: v0.4.29
touches: subprojects/docket/src/docket/store.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-13
closed: 2026-09-19
pr: 708
verify: grep -q 'def test_record_keeps_a_drifted_filename' subprojects/docket/tests/test_cli.py
recurrences: 2026-09-19 PL-5QLP, 2026-09-19 PL-QMC0
---

**Problem.** bin/docket record renames a drifted item file as a side effect of writing a pr number, which conflicts against whoever else is holding that file

**Problem.** `bin/docket record` re-renders a whole item file to add `pr:`,
and the store names files from the title, so a file whose slug has drifted is
renamed by a command that was asked to write a number. The session running it
has no reason to be looking at who else holds that file.

**Observed 2026-09-08** (recorded in `PL-3833`'s brief): `record`, run to
write six owed `pr` numbers, renamed `PL-36R4` from its `thirty-eight` slug
to `forty-two` while `origin/claude/ui-overhaul-planning-avjx5r` was editing
the same file. The rename was backed out of that commit for exactly that
reason.

**Why it matters.** The rename is correct in isolation and wrong as a side
effect: it lands in a diff about something else, where no reviewer is looking
for it, and it conflicts against a concurrent edit rather than merging with
one. `CLAUDE.md` treats a command that does more than it was asked as the
hazard here, not the rename itself.

**Where.** `subprojects/docket/src/docket/store.py` — whatever `record` uses
to write an item back. The fix is presumably to write in place, keeping the
existing filename, and leave renaming to the pass that has checked (`PL-YTDN`).

**Done when.** `bin/docket record` writes a `pr` number without renaming the
file, and a test pins that against an item whose filename has drifted.

**Reproduced 2026-09-13, in the session that filed this.** `bin/docket record`
was run on `origin/main` at `de6baee` to write the fifteen `pr` numbers #505,
#506 and #507 were owed. It wrote all fifteen correctly — and renamed
`PL-DZFJ`'s file from the `roadmap-md-1816-pl-ylkr-and-pl-7h0x-say-every` slug
to `roadmap-md-s-gate-text-and-pl-ylkr-s-brief-say`, its title having been
changed on `main` while the filename was not.

So this is not a one-off that `PL-36R4` happened to hit: it fires on any
`record` run that touches a drifted file, which is now a class `docket check`
reports by name since `PL-3833`. The rename was backed out of that commit and
the `pr: 507` write kept, which is the same resolution `PL-36R4` got — and it
is a manual step a session has to know to take, every time, which is the
argument for fixing the writer rather than remembering.

**Triaged 2026-09-13.** `store.write_item` is the writer: it renders the item
and writes to `directory / filename_for(item)`, so any caller that re-renders a
drifted file renames it. `record` is the caller that should not. The `verify:`
command was run first and exits 1 - the `test_cli.py` suite passes and the test
this item owes does not yet exist.

**Fixed 2026-09-19.** `_write_pr` in `subprojects/docket/src/docket/cli.py`
now calls `store.rewrite_item` instead of `store.write_item(replace=...)`, so
the `pr:` write keeps whatever name it finds. The helper already existed:
`PL-L4YG` built it for `docket set` and its docstring names this item as the
reason, but only `set` was wired to it, which is why `record` was still
renaming six days later and why `PL-5QLP` re-discovered the same defect
independently.

`test_record_keeps_a_drifted_filename` pins it, against a real git checkout
whose item file carries a slug its title no longer generates. It failed before
the change with the file renamed out from under the assertion.

Closed with `PL-QMC0` (the same defect in `bin/docket release`), `PL-5QLP`
(the re-discovery, which also recorded the revert trap) and `PL-JF5Z` (the
recovery of `PL-5QLP` from its branch). One mechanism, one branch.
