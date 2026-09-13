---
id: PL-LBR6
title: bin/docket record renames a drifted item file as a side effect of writing a pr number, which conflicts against whoever else is holding that file
status: untriaged
added: 2026-09-13
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
