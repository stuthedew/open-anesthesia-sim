---
id: PL-P66B
title: bin/docket verify keeps only the last four lines of a failed make check, which after a pytest failure are its count, uv's two sync lines and make's error, so a REJECT for a failing test never names the test and the session re-runs the suite or reads .pytest_cache to learn it
status: untriaged
touches: subprojects/docket/src/docket/verify.py, docs/items/PL-087W-bin-docket-verify-unions-removed-assertions-per.md
added: 2026-10-04
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
