---
id: PL-D3M2
title: Nothing holds the Makefile's pytest line and quality.yml's identical, though both comments say they must stay the same
status: untriaged
feature: dev-tooling
added: 2026-09-03
---

**Problem.** The `Makefile`'s coverage line and `.github/workflows/quality.yml`'s
`checks` step run the same pytest invocation, and both carry a comment saying
they have to. Nothing checks it. `tools/doc_check.py` validates that a workflow
step's *paths* resolve and that a cited `make` target exists, but it does not
compare the two commands.

**Why it matters.** The invocation carries `--cov=anesthesia_sim.core
--cov-branch --cov-fail-under=100`, which is what holds `core/` at 100%. If the
two drift, the local gate and the merge gate stop asking the same question and
the difference is silent - a session sees green locally and CI sees something
else, or worse, both stay green while one of them has stopped enforcing the
threshold.

**Why now.** `PL-WCZV` added `-n auto` to both lines, so the string that must
match is now longer and has one more thing to get wrong. It also chose `auto`
partly *because* a pinned width would have made the two lines legitimately
different and so uncheckable - a decision taken to keep a comparison possible
that nothing performs.

**Where.** `tools/doc_check.py`, which already parses both files: `workflow_commands`
yields every `run:` line and `Makefile` target parsing is beside it.

**Done when.** A drift between the two commands fails a check rather than
relying on a reader noticing. Worth deciding whether the rule is "identical
strings" - simple, exact, and the sort of thing `CLAUDE.md` reserves hard
failure for - or something looser that would need judgment and so should be an
advisory or nothing at all.
