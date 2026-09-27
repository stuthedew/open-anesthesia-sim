---
id: PL-1DW7
title: gate-status-guard.sh reads only $? as a reader of the status, so make docket 2>&1 | tail -4; echo "exit=${PIPESTATUS[0]}" is refused as losing the gate at the pipe, though PIPESTATUS[0] prints make's own status into the output - met 2026-09-26 in ordinary work, by the PL-61FT build session
priority: P3
effort: S
status: done
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-27
pr: 1151
payoff: a session that reads a gate's status out of PIPESTATUS straight after a pipe that trims it - make docket 2>&1 | tail -4; echo "exit=${PIPESTATUS[0]}" - is let through, as bash prints the gate's own status there, while a read of any other stage's status is still refused
verify: grep -q 'def test_pipestatus_read_after_the_pipeline_keeps_the_status' tests/unit/test_gate_status_guard.py
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

**Reproduced 2026-09-27** on `origin/main` at `70c38a6c`, piping the command
to the hook as its payload: refused. So is `make check > /tmp/gate.log 2>&1;
echo "exit=${PIPESTATUS[0]}"`, with no pipe at all. With the gate a stub
exiting 3, bash 5.2.21 printed `exit=3` for both.

**Why it matters.** The header's case for the guard is that it fires only
where the status is lost, so a session reads its refusals rather than routing
around them. A refusal of a command that prints the verdict costs a retry and
teaches the opposite. `PIPESTATUS` is bash's own way to read a stage's status
past a pipe that trims the output, and the one a session reaches for when it
wants `tail`'s short output and the gate's verdict in one call.

**Done when.** The gate guard admits a gate that opens its pipeline where the
command straight after that pipeline's `;` reads the first stage's status out
of `PIPESTATUS` - `${PIPESTATUS[0]}`, the bare name, or the whole array - and
still refuses each read that does not reach it: another stage's element, a
read behind `&&`, `||`, `&` or another command, one that runs only on the last
stage's answer, and one after a pipeline closed inside a subshell. The
header says so, and the tests pin each case with what bash 5.2.21 printed.

**Generator check.** The fact misread is whether a gate's status survives the
command around it, which `PL-61FT`'s `misread:` states ("What a shell command
does when run: which program it runs, on what, and whether its status
survives"). An instance of that head's fact, filed in `831493f7`, the build
that closed it. It was met in ordinary work, which that head's bound works at
its own rank; it is not a `KNOWN_GAPS` row met, which is what its reopening
number counts. No new head.
