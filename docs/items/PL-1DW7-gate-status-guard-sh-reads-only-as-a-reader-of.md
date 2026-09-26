---
id: PL-1DW7
title: gate-status-guard.sh reads only $? as a reader of the status, so make docket 2>&1 | tail -4; echo "exit=${PIPESTATUS[0]}" is refused as losing the gate at the pipe, though PIPESTATUS[0] prints make's own status into the output - met 2026-09-26 in ordinary work, by the PL-61FT build session
status: untriaged
feature: bash-guard-bound
added: 2026-09-26
---

**Problem.** gate-status-guard.sh reads only $? as a reader of the status, so make docket 2>&1 | tail -4; echo "exit=${PIPESTATUS[0]}" is refused as losing the gate at the pipe, though PIPESTATUS[0] prints make's own status into the output - met 2026-09-26 in ordinary work, by the PL-61FT build session

**Met 2026-09-26 in ordinary work.** The `PL-61FT` build session ran `make
docket 2>&1 | tail -4; echo "exit=${PIPESTATUS[0]}"` to validate the store
after an item edit, and the gate guard refused it: "This command runs `make
docket` and then throws its exit status away. A pipeline reports its LAST
stage ...". The walk in `.claude/hooks/gate-status-guard.sh` loses the gate at
the `|`, because the segment after it (`tail -4`) holds no `$?`, and it never
reaches the `echo`: the one reader it knows is a `$?` in the segment straight
after a separator. `PIPESTATUS` holds "a list of exit status values from the
processes in the most-recently-executed foreground pipeline" (Bash Reference
Manual § 5.2 "Bash Variables"), so the `echo` prints `make`'s own status into
the output - the guarantee the `$?` exemption accepts - whatever `tail` did.
The session re-ran it as `set -o pipefail; make docket 2>&1 | tail -4; echo
"exit=$?"`, which the guard admits.

A false refusal met rather than probed, so under `PL-61FT`'s bound it is
worked at its own rank rather than recorded as a known gap. Not probed
further: which other spellings of the array (`${PIPESTATUS[@]}`, a copy taken
into a variable) the fix reads is the fix's to settle.
