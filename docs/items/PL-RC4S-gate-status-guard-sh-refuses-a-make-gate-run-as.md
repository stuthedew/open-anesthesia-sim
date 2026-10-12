---
id: PL-RC4S
title: gate-status-guard.sh refuses a make gate run as a dry run - make --just-print check piped to tail - though --just-print runs no recipe and so has no gate status to lose; a session met it in PL-R417's link 23 sweep
priority: P3
effort: S
status: done
classes: defect
feature: bash-guard-bound
milestone: v0.5.24
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1437
payoff: a make dry run piped to tail is admitted, so auditing what a gate would run costs no retry and the refusal stops teaching a token for a command that loses nothing
verify: grep -q 'def test_a_make_dry_run_has_no_gate_status_to_lose' tests/unit/test_gate_status_guard.py
reenters: PL-61FT
---

**Problem.** gate-status-guard.sh refuses a make gate run as a dry run - make --just-print check piped to tail - though --just-print runs no recipe and so has no gate status to lose; a session met it in PL-R417's link 23 sweep

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23): an auditor's
command of the form below was refused live.

```text
make -f Makefile.copy --just-print check 2>&1 | tail
```

`--just-print` (`-n`) prints the recipes without running them, so the
pipeline loses no status a gate produced. Nothing in `docs/items/` or the
guard's `KNOWN_GAPS` covers `-n` or `--just-print`; the guard's test file says
a row becomes an item once a session is seen writing it, and this one was.

**Reproduced 2026-10-11** on `main` at `16a20a4f`, piping each command to the
hook as a Bash payload: the command above is refused as running `make check`
and throwing its status away, and so are `make -n check | tail`, `make
--dry-run check | tail` and `make --recon check | tail`. GNU make 4.3's `make
-n check` on the tracked Makefile exits 0 having run nothing. GNU make still
runs a `+`-led recipe line under `-n`, and hands `-n` on to a `$(MAKE)`
line's sub-make (manual § 5.7.1, § 9.3); the tracked Makefile has no `+` line,
and its one `$(MAKE) check`, under `prebuild`, runs dry, so the fix need not
read either today.

**Why it matters.** A dry run is how a session sees what a gate would run
without running it, which auditing a Makefile copy needs, and each refusal
costs the retry the guard's header names as the whole price of a false one.
The remedy it prints, `set -o pipefail`, would admit the command without
making it any more correct, so the refusal teaches a token rather than a fact.

**Generator check.** Not a member of `PL-R417`: one line, read whole. Read
against `bin/docket generators --misread` on 2026-10-11: the fact misread is
`PL-61FT`'s - what a shell command does when run, here that a dry run runs no
recipe and so has no gate status to lose - and this is an instance of that
head's fact filed after it closed on 2026-09-26, met in ordinary work, so
worked at its own rank under that head's ratified bound. With `PL-ZS13`,
`PL-0FGH` and `PL-6X0C` it is one of four such instances; `PL-6X0C`'s brief
records where triage's general rule and the head's bound disagree on that
count.

**Done when.** A `make` run with `-n`, `--just-print`, `--dry-run` or `--recon`
is not refused as a gate whose status is lost, with a case in
`tests/unit/test_gate_status_guard.py`.
