---
id: PL-JTHW
title: tools/main_ci_status.py passes over a cancelled main run in silence, so after PL-SMN4 a commit with no whole-store verdict is indistinguishable from one nobody asked about
priority: P3
effort: S
status: done
classes: defect, infra
feature: ci-cost
touches: tools/main_ci_status.py, tests/unit/test_main_ci_status.py, .github/workflows/quality.yml, tests/unit/test_ci_concurrency.py, .claude/hooks/docket-digest.sh, docs/ARCHITECTURE.md
added: 2026-09-16
closed: 2026-10-01
pr: 1259
verify: grep -q 'def test_a_cancelled_main_run_is_reported' tests/unit/test_main_ci_status.py && uv run pytest tests/unit/test_main_ci_status.py
---

**Problem.** tools/main_ci_status.py passes over a cancelled main run in silence, so after PL-SMN4 a commit with no whole-store verdict is indistinguishable from one nobody asked about

`VERDICTS` in `tools/main_ci_status.py` lists the conclusions that judged the
tree - `success`, `failure`, `timed_out`, `startup_failure`, `action_required` -
and `pick_run` walks past everything else to the newest run that reached one.
`cancelled` is excluded deliberately and the module docstring says why.

**That was right while a cancelled `main` run meant nothing, and `PL-SMN4`
changed what it means.** Under the shared concurrency group, a `main` run was
routinely evicted from the single pending slot by the next merge: 31 of the 257
completed `main` push runs between 2026-09-05 and 2026-09-16 - 12.1% - ended
`cancelled` having started no job. Reporting each of those would have been a
line on one session in eight about a run that was superseded seconds after it
was created, which is the advisory-nobody-reads failure `CLAUDE.md` names.

A per-commit group removed the eviction, so a `cancelled` run on `main` now
means a hand cancellation, a lost runner, or GitHub cancelling for its own
reasons. In every one of those the commit got no whole-store `bin/docket check
--verify`, and this tool still says nothing - it reports the *previous*
commit's verdict as "the most recent real answer about `main`", which is true
of that commit and silent about the one that lost its run.

**Why it was not fixed in `PL-SMN4`.** It is a behavior change with a new
output line and therefore owes a test, which closes `CLAUDE.md`'s fix-now door
on test 1. The prevention `PL-SMN4` shipped is what the item's **Done when.**
asked for; this is the reporting half it names as its second candidate shape,
scoped down to what is left once the common case is gone. `PL-SMN4` corrected
the docstring to say what now holds and to point here, so nothing in the tree
currently claims otherwise.

**Done when.** A `main` commit whose quality run was cancelled is visible to a
session - through the session-start digest or by running the tool by hand -
rather than being passed over in silence. The rule that a green `main` prints
nothing is not up for revision: whatever this reports has to be something a
reader can act on, and the rate to beat is the one above without the eviction
in it.

**Worth measuring before designing it.** How many `cancelled` `main` runs
remain once eviction is gone is not known - every instance in the window above
has that cause. If the honest answer is a handful a year, the cheapest shape
may be a line in `advisory` rather than any new state.

**Why it matters.** A commit that got no whole-store check and a commit nobody
asked about are different facts, and the tool now reports them identically: it
names the *previous* commit's verdict as "the most recent real answer about
`main`", which is true of that commit and silent about the one that lost its
run. A check reporting confidently about a question it did not answer is the
silent-wrong-answer shape `CLAUDE.md` names, and it reaches the session-start
digest, which is where a session forms its first view of whether `main` is
sound.

**Measured 2026-10-01, and the shape it chose.** GitHub's run list for
`quality.yml` filtered to `main` push runs that were cancelled,
`curl 'https://api.github.com/repos/stuthedew/open-anesthesia-sim/actions/workflows/quality.yml/runs?branch=main&event=push&status=cancelled&created=>=2026-09-16T02:24:44Z'`,
returned no run created between `PL-SMN4`'s fix merging (`#615`,
2026-09-16 02:24 UTC) and 2026-10-01 03:16 UTC, against 640 completed `main`
push runs over the same window. The same query from 2026-09-05 to that merge
returned 31, the count above, so the filter reads what it says. At zero in 640
the line cannot become one a reader learns to skim, so the brief's cheapest
shape was taken: no new state, and one line from `tools/main_ci_status.py`
when a cancelled run is newer than every verdict among the completed runs it
reads. That commit has no whole-store verdict, and the verdict reported, or
the silence of a green one, is about an older commit, so the line names both
runs and asks for a re-run.

A cancelled run older than a verdict still prints nothing, which is the
brief's own rule rather than a gap: the later run checked the whole store
again on a tree containing it, so there is nothing to act on, and printing it
would make a green `main` speak. The line says "unless a newer merge's run is
still going", because the tool reads completed runs only and cannot see one;
teaching it to would change the request every session start makes, for a case
measured at zero. `.github/workflows/quality.yml`,
`tests/unit/test_ci_concurrency.py`, `.claude/hooks/docket-digest.sh` and
`docs/ARCHITECTURE.md` each described the old silence and were corrected in the same commit, which is why
they are in `touches`. Built in `#1259` after the thread that closed
`PL-7K2C`, `PL-CR36` and `PL-NWSK` there stopped for length.
