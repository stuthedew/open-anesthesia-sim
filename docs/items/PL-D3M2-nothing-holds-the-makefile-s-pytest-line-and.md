---
id: PL-D3M2
title: Nothing holds the Makefile's pytest line and quality.yml's identical, though both comments say they must stay the same
priority: P2
effort: S
status: done
classes: infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-03
closed: 2026-09-04
pr: 278
verify: uv run pytest tests/unit/test_doc_check.py && grep -rq 'def test_a_coverage_gate_that_drifted_between_them_is_an_error' tests/unit
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

**Decision needed.** Whether the rule is "the two command strings are
identical" - exact, decidable, and the kind of thing `CLAUDE.md` reserves hard
failure for - or something looser that tolerates deliberate divergence and so
has to be an advisory. The strict rule is recommended: the two lines are
deliberately identical today, `-n auto` was chosen partly to keep them so, and a
looser rule would need a judgment the tool cannot make.

**Decided and worked (project owner, 2026-09-04):** the strict rule, as
recommended. `tools/doc_check.py` gains `check_coverage_gate`, wired into
`analyze` and so into `make check` and both CI jobs.

**Exact string equality, keyed on `--cov-fail-under`.** The threshold is the
whole point of the promise, so the flag carrying it selects the lines to
compare. Deliberately narrower than "every pytest command": `drift.yml` runs a
bare `uv run pytest` on purpose, because a coverage failure there would report
as a dependency break (`PL-22Z3`), and a blanket rule would fire on it every
run - which is the advisory-fatigue failure `CLAUDE.md` names, arriving as a
hard error instead.

**Two findings, not one, because they want different sentences.** Commands that
differ is a drift; a gate present on one side and absent on the other is not a
disagreement but a missing gate, and it is the more serious of the two. The
second is checked first so it cannot be reported as the first.

| | reported as |
| --- | --- |
| both sides run the same command | nothing |
| the commands differ | "the coverage gate differs between the Makefile and CI, so the local gate and the merge gate are not asking the same question", naming both |
| one side has no gate | "the Makefile runs no `--cov-fail-under` command while .github/workflows/quality.yml:64 does, so only one of the two gates gates coverage" |
| neither side has one | nothing - this holds two statements to each other and says nothing about whether they should exist |

**Verified against the real drift rather than only a fixture.** Removing `-n
auto` from the Makefile alone produces the first error; removing the whole gate
line produces the second. Seven tests, checked against a mutated
implementation - collapsing the missing-side branch fails four.

**Why now, restated for the record.** `PL-WCZV` lengthened the string that has
to match and chose `-n auto` over a pinned width partly so the two lines could
stay identical across machines. That was a decision taken to keep a comparison
possible which nothing performed.
