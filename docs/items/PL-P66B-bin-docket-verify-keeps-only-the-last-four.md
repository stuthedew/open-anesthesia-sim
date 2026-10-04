---
id: PL-P66B
title: bin/docket verify keeps only the last four lines of a failed make check, which after a pytest failure are its count, uv's two sync lines and make's error, so a REJECT for a failing test never names the test and the session re-runs the suite or reads .pytest_cache to learn it
priority: P2
effort: S
status: ready
classes: defect, session-cost
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a REJECT from bin/docket verify names the test or finding that failed, so a red gate costs a read rather than a second three-minute make check
verify: grep -q 'def test_a_failing_project_check_s_evidence_names_the_failing_test' subprojects/docket/tests/test_verify.py
---

**Problem.** bin/docket verify keeps only the last four lines of a failed make check, which after a pytest failure are its count, uv's two sync lines and make's error, so a REJECT for a failing test never names the test and the session re-runs the suite or reads .pytest_cache to learn it

**Seen 2026-10-04 on `PL-N67T`.** `bin/docket verify --self PL-N67T` printed
`FAIL the project's own checks pass - make check` with these four lines and
nothing above them: `1 failed, 6062 passed in 196.28s`, `Resolved 26 packages
in 1ms`, `Checked 26 packages in 0.62ms`, `make: *** [Makefile:58: check]
Error 1`. The failing test, `tests/unit/test_literal_home_check.py::
test_the_real_tree_passes`, was found only by reading
`.pytest_cache/v/cache/lastfailed` and re-running it. `project_check` in
`subprojects/docket/src/docket/verify.py` slices `output.strip().splitlines()[-4:]`,
and the pytest run is followed by the `uv` sync that prints the two package lines,
so pytest's own `FAILED` summary lines fall outside the slice whenever a test fails.
The run behind it took 3 min 16 s, so the cost is a second run or a cache read per
red gate.

**Not `PL-087W`'s problem**, though filing it recorded a match there: that item
is about removed assertions being unioned across commits and never netted
against a restore. The two share `verify.py` and nothing else, so the match is
withdrawn under this item.

**Generator check.** Not a member of a head. The one `bin/docket generators`
marks still generating on 2026-10-04 is `PL-R417`, readers that take a physical
line for a statement in a format that continues across lines; this is a
fixed-size tail cut from a command's output, which parses nothing. The one other
item naming `project_check`, `PL-FVM5`, is closed and was about running the check
once per batch.

**Reproduced 2026-10-04** on `main` at `8f24fe78`:
`python3 -c "import sys, types, pathlib; sys.path.insert(0, 'subprojects/docket/src'); from docket.verify import project_check; c = types.SimpleNamespace(check_command='echo Resolved 26 packages >&2; echo Checked 26 packages >&2; echo FAILED test_x.py::test_y; echo 1 failed, 6062 passed; echo make: Error 1 >&2; exit 2'); print(project_check(pathlib.Path('.'), c).lines)"`
printed
`('1 failed, 6062 passed', 'Resolved 26 packages', 'Checked 26 packages', 'make: Error 1')`:
the `FAILED` line is cut although the two `uv` lines were written before it.
The brief's account of why is not quite right: `check` depends on `sync`, so
`uv sync` runs before pytest, and its two lines land last because `_run`
returns all of stdout followed by all of stderr. With make's error after
them, stderr fills three of the four lines, and the slice keeps exactly one
line of the failing command's own stdout: pytest's count, and by the same
arithmetic the count that closes a mypy or ruff report, never the finding
above it.

**Why it matters.** `bin/docket verify` is the close-out gate for every item,
and `verify_batch` hands the same lines to every item in a batch. A REJECT
for a failing test names only the count, so the session pays a second
`make check`, 3 min 16 s in the run the brief records, or reads
`.pytest_cache` to learn what failed, once per red gate. Not latent: every
such REJECT reads this way today.

**Done when.** A failing `project_check` carries the line naming the failing
test when the check command writes to stderr both before its stdout and after
it, as `make check` does;
`test_a_failing_project_check_s_evidence_names_the_failing_test` in
`subprojects/docket/tests/test_verify.py` pins it with such a command.
Filtering out the `uv` lines would not do it, since any stderr written before
the failure takes the same place.
