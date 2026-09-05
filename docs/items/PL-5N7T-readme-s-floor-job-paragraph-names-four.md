---
id: PL-5N7T
title: Nothing checks a prose enumeration of quality.yml's bare-interpreter commands against the workflow, so it has drifted silently twice in one day
status: ready
priority: P3
effort: S
classes: docs
feature: project-introduction
touches: docs/ARCHITECTURE.md, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-05
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_marked_enumeration_missing_a_run_step_fails' tests/unit/test_doc_check.py
---

**Problem.** Two documents hand-enumerate what `.github/workflows/quality.yml`'s
`floor` job runs:

- `README.md:194-196` — "executes `python3 tools/doc_check.py check`, `python3
  tools/branch_id_check.py`, `bin/docket check` and `python3
  tools/contrast_check.py` under it".
- `docs/ARCHITECTURE.md:461` — the same list, in the same order.

`PL-LLWN` added a fifth command, `python3 tools/rules_paths_check.py`. The
`ARCHITECTURE.md` copy was corrected in that branch. **The `README.md` copy was
not, because `README.md` is frozen** (`.claude/rules/readme-hold.md`), and the
freeze is explicit that a doc sweep does not override it: record and move on.
So the README statement is wrong as of 2026-09-05 and stays wrong until the
freeze lifts.

**Why it matters.** Two halves, and the second is the one worth building for.

The stale sentence itself is minor: a reader learns of four checks where there
are five, and nothing they do on that basis is unsafe. The README copy is moot
in any case - see the restatement below, which is the current scope of this
item.

The drift is not minor. `tools/doc_check.py` already resolves the *paths* these
lines cite, which is why the addition did not fail `make check` — a path that
exists is not an enumeration that is complete. So the check that exists gives a
green answer to a question next to the one that matters, and a second document
went stale on the first addition after it was written. That is the shape
`CLAUDE.md` calls a silent wrong answer, at low stakes here only by luck.

**Where.** `README.md:194-196` (frozen); `docs/ARCHITECTURE.md:461` (already
correct); `tools/doc_check.py` for the check.

**Approach.** The decidable part: parse `floor`'s `- run:` steps out of
`.github/workflows/quality.yml`, and hold any prose block that enumerates them
to the same set. Finding the prose is the hard half and should not be guessed
at — a heuristic hunting for command-like spans across all documentation would
fire on every example and be routed around within a week. Prefer an explicit
marker naming the block to check, the way the package-map trees are already
delimited rather than discovered, so the tool is told where to look and the
question stays decidable.

## Restated 2026-09-05, under `PL-WB5K` — unblocked, and stronger

`PL-WB5K` deleted `README.md`, which removes the *stale sentence* half of this
item outright: there is no frozen copy to correct and nothing waiting on
`PL-N092`. This item is `ready` rather than `blocked`, and its scope is now
`docs/ARCHITECTURE.md` alone.

**The drift half survived and immediately recurred, which is the argument for
building the check rather than the argument for dropping it.** `PL-WB5K` added
a sixth command, `python3 tools/readme_hold_check.py`, to the same section.
`docs/ARCHITECTURE.md`'s enumeration went stale the moment that landed and
`make check` stayed green, exactly as this item predicted — the path it cites
still resolves, and the count is what changed. It was caught by a session
reading this item's own text during the same change, which is luck rather than
a mechanism, and is precisely the "silent wrong answer" test in `CLAUDE.md`.
Two additions, two silent drifts, in one day.

Note the sixth command is the shortest-lived: `PL-N092` deletes
`readme_hold_check.py` when it writes the deliberate README, so the
enumeration will change again in the other direction. A check would catch that
removal too; a reader would not.

**Where, now.** `docs/ARCHITECTURE.md` (the paragraph beginning "The floor
section of `.github/workflows/quality.yml`'s `checks` job performs the run they
stand in for"), corrected under `PL-WB5K` but still unheld by anything;
`tools/doc_check.py` for the check; `tests/unit/test_doc_check.py`.

One naming correction the deletion forces: `PL-D551` folded the `floor` job
into `checks`, so what is being enumerated is the **bare-interpreter section
of `checks`**, not a job. The marker and the failure message should say so, or
the check ships describing a job that does not exist.

**Done when.** `make check` fails when the marked prose enumeration in
`docs/ARCHITECTURE.md` disagrees with the run steps of `quality.yml`'s
bare-interpreter section, and the two agree.

**A third drift, in the other direction, the same day.** `PL-L17Q` *removed*
`python3 tools/contrast_check.py` from that section - it parses `app/` source
targeting 3.14 and cannot run under the 3.11 floor - so the section runs five
commands, not the six the paragraph above counts: `doc_check.py check`,
`branch_id_check.py`, `rules_paths_check.py`, `readme_hold_check.py` and
`bin/docket check`. `docs/ARCHITECTURE.md` was corrected in that branch, by
hand again, and `make check` stayed green again.

So the enumeration has now drifted three times in one day - two additions and
one removal - and been repaired three times by a session that happened to be
reading it. The removal case is the one that argues hardest for the check: an
addition at least leaves the prose *incomplete*, while a removal leaves it
naming a command that is no longer run, which reads as authoritative and is
false.
