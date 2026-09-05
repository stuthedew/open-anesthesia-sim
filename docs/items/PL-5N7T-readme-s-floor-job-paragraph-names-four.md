---
id: PL-5N7T
title: README's floor-job paragraph names four commands and quality.yml now runs five, and nothing checks that enumeration against the workflow
status: blocked
priority: P3
effort: S
classes: docs
feature: project-introduction
touches: README.md, tools/doc_check.py, tests/unit/test_doc_check.py
blocked-by: PL-N092
added: 2026-09-05
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
are five, and nothing they do on that basis is unsafe. It waits for `PL-N092`
(rewrite README as a human-readable introduction), which rewrites the paragraph
anyway.

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

Do this once the freeze lifts, not before: a check that fails on a file nobody
is allowed to edit is a gate with no move behind it.

**Done when.** `make check` fails when a marked prose enumeration of the
`floor` job's commands disagrees with the workflow, and both copies agree with
it.
