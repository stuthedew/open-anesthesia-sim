---
id: PL-D3M2
title: Nothing holds the Makefile's pytest line and quality.yml's identical, though both comments say they must stay the same
priority: P2
effort: S
status: needs-decision
classes: infra
touches: tools/doc_check.py, tests/unit/test_doc_check.py
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

**There are now two `uv run pytest` lines in the `Makefile`, so "the Makefile's
pytest line" no longer identifies one.** `PL-FX3N` put `-n auto` on the `test`
target, which shares the flag with the `check` line and nothing else - no
`--cov`, no threshold, and no obligation to match the workflow. A checker that
finds the Makefile's pytest invocation by pattern would now find two and could
compare the wrong one, reporting drift that is deliberate. Anchor the read to
the `check` target's recipe, and treat `test` as outside the pair; the comment
above each line says which it is.

**Done when.** A drift between the two commands fails a check rather than
relying on a reader noticing. Worth deciding whether the rule is "identical
strings" - simple, exact, and the sort of thing `CLAUDE.md` reserves hard
failure for - or something looser that would need judgment and so should be an
advisory or nothing at all.

**Decision needed.** Whether the rule is "the two command strings are
identical" - exact, decidable, and the kind of thing `CLAUDE.md` reserves hard
failure for - or something looser that tolerates deliberate divergence and so
has to be an advisory. The strict rule is recommended: the two lines are
deliberately identical today, `-n auto` was chosen partly to keep them so, and a
looser rule would need a judgment the tool cannot make.
