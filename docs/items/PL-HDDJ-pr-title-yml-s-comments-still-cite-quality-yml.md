---
id: PL-HDDJ
title: pr-title.yml's comments still cite quality.yml's floor job, which PL-D551 folded into checks
priority: P3
effort: S
status: done
classes: docs
feature: ci-cost
touches: .github/workflows/pr-title.yml
added: 2026-09-05
closed: 2026-09-06
verify: python3 tools/doc_check.py check && ! grep -qE 'quality\.yml`.s `floor`' .github/workflows/pr-title.yml
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

**Why it matters.** The first sentence is still *substantively* right — the
bare-interpreter contract is held — so nothing there misleads a reader about
behaviour. What is wrong is the name: a reader following "the `floor` job"
into `quality.yml` finds no such job and has to reconstruct where it went.
That is a small cost paid by every reader of this file, which is why it is
worth an item rather than nothing, and a small one, which is why it is not
worth widening an unrelated pull request to fix.

**The second sentence had gone stale a second way, found while fixing the
first.** Its command list — "`doc_check.py`, `bin/docket check` and
`contrast_check.py`" — named `contrast_check.py` as a floor command, and
`PL-L17Q` had already moved that script out of the floor section and under
`uv run python`, because it reads 3.14 source the 3.11 floor parser cannot
even parse (`quality.yml`, the note above `contrast_check.py`). The sentence's
conclusion survived — the floor section still never runs this script — but two
of the three commands it cited as evidence were down to one. The rewrite drops
the enumeration for "a fixed list of `tools/` scripts - `doc_check.py` and
`bin/docket check` among them", which cannot go stale the next time that list
moves.

Nothing checks this. `tools/doc_check.py` resolves cited *paths* against the
tree, and both of these cite a path that exists; the stale half is the job name
inside it, which no tool reads.

**Where.** `.github/workflows/pr-title.yml`, the two comment blocks above.
Rename to the bare-interpreter section of `checks`, matching the wording
`quality.yml` now uses for the same thing.

The `verify:` command greps for `` `quality.yml`'s `floor` `` — the possessive
specifically, not the word `floor` — because three other uses of the word in
this file are correct and must survive. Two are the ordinary noun: "not the
declared floor" and "The floor is not chosen here", both still true, because
the bare-interpreter floor is a real contract that outlived the job named
after it. The third arrived with `PL-KPP1`, which lands its
load-bearing-job-name note in this same file and cites the deleted `floor` job
by name as the incident that note exists to prevent — a backticked `` `floor`
`` that is correct precisely because it is in the past tense.

The command was originally written as `` ! grep -q '`floor`' ``, which would
have failed on that note and so would have pushed `PL-KPP1` into dropping the
one name that makes its warning concrete. Narrowed to the possessive when the
two items were worked together; the narrowed pattern matched both stale sites
on the pre-work file and matches nothing after, which is what the original was
approximating.

**Found.** During `PL-WB5K`'s doc sweep (delete README.md until a deliberate
rewrite replaces it), which touched `quality.yml` and so read its sibling.

**Done when.** No comment in `.github/workflows/` names a job that
`quality.yml` does not define.
