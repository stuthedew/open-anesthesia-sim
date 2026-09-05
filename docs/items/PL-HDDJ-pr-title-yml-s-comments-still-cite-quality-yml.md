---
id: PL-HDDJ
title: pr-title.yml's comments still cite quality.yml's floor job, which PL-D551 folded into checks
touches: .github/workflows/pr-title.yml
added: 2026-09-05
status: untriaged
---

**Problem.** `PL-D551` folded the separate `floor` job into `checks`, ahead of
the `uv` install, and `.github/workflows/quality.yml` was updated to say so.
`.github/workflows/pr-title.yml` was not, and names the removed job twice:

- Line 17: "`tools/` runs under a bare `python3` by contract, which
  `tests/unit/test_tools_portability.py` and `quality.yml`'s `floor` job hold
  it to."
- Line 61: "not the declared floor, because `quality.yml`'s `floor` job runs
  `doc_check.py`, `bin/docket check` and `contrast_check.py` and never this
  one."

**Why it matters.** Both sentences are still *substantively* right — the
bare-interpreter contract is held, and those three commands still do not
include this script — so nothing is failing and nothing misleads a reader
about behaviour. What is wrong is the name: a reader following "the `floor`
job" into `quality.yml` finds no such job and has to reconstruct where it
went. That is a small cost paid by every reader of this file, which is why it
is worth an item rather than nothing, and a small one, which is why it is not
worth widening an unrelated pull request to fix.

Nothing checks this. `tools/doc_check.py` resolves cited *paths* against the
tree, and both of these cite a path that exists; the stale half is the job name
inside it, which no tool reads.

**Where.** `.github/workflows/pr-title.yml`, the two comment blocks above.
Rename to the bare-interpreter section of `checks`, matching the wording
`quality.yml` now uses for the same thing.

**Found.** During `PL-WB5K`'s doc sweep (delete README.md until a deliberate
rewrite replaces it), which touched `quality.yml` and so read its sibling.

**Done when.** No comment in `.github/workflows/` names a job that
`quality.yml` does not define.
