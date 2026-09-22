---
id: PL-VHHB
title: Every release cut asserts that nothing computational moved, and the only evidence is tree identity - which v0.5.2 did not have, so the claim was proved by an ad-hoc AST comparison that no later cut can re-run
priority: P3
effort: M
status: ready
classes: infra
feature: release-process
touches: tools/ast_identity.py, tests/unit/test_ast_identity.py, .claude/skills/docket/modes/release.md
added: 2026-09-21
payoff: a release cut proves 'nothing computational moved' with a command a later cut can re-run, not by a reader judging each changed line of src/ to be a comment
verify: grep -q 'def test_a_docstring_only_change_reads_identical' tests/unit/test_ast_identity.py
---

**Problem.** Every release cut asserts that nothing computational moved, and the only evidence is tree identity - which v0.5.2 did not have, so the claim was proved by an ad-hoc AST comparison that no later cut can re-run

**Why it matters: tree identity stopped being enough.**

Every release since the MVP has stated "nothing computational moved" from four
tree hashes resolving to the same objects at both ends. That evidence is exact
when it holds and **absent when it does not**, and v0.5.2 is the first cut
where it did not: `src/anesthesia_sim/core/` moved `ca5a354` to `061714b` for a
docstring-only change (`PL-316G`'s citation conversion).

The fallback is reading the diff and judging each changed line to be a comment,
which is exactly the judgment the safety-critical standard says not to rest a
clinical claim on.

## What was done once, and should not have to be done again

`PL-JYTJ` proved it instead, deterministically: parse each changed file at both
revisions, walk the tree replacing every docstring `Constant` with a fixed
sentinel, and compare `ast.dump` of the results. Comments never reach an AST at
all, so an identical pair means **no executable statement moved**. Both files
came back identical.

That is a script that ran once from a scratchpad and is now gone. The
decidable half is wholly decidable - "are these two ASTs identical modulo
docstrings" has one answer - and the judgment half stays with the reader, who
still decides whether a docstring-only change is *safe*. That is the line
`CLAUDE.md` § "Prefer deterministic tooling over repeated model work" draws.

## Shape

`tools/ast_identity.py OLD_REV NEW_REV PATH...`, standard library only, exit 0
when every path's AST is unchanged and a per-path verdict on stdout either way.
Wired into `.claude/skills/docket/modes/release.md` as the step a cut runs when
a simulator tree object has moved - not into `make check`, which would fire on
every run without changing a decision.

**Gate check.** It recurs (every cut where `src/` moves at all), the answer is
deterministic, and no linter does it. What it must not become is a claim that
a docstring-only change *cannot* matter: a docstring is where a unit, a model
version or a provenance note is recorded, so `PL-JYTJ`'s own reading of the
diff stays owed alongside the script's verdict.

**Done when.** `tools/ast_identity.py OLD NEW PATH...` exists as the Shape
above describes, using the standard library only. A test in
`tests/unit/test_ast_identity.py` holds that a docstring-only change reads as
identical and a changed statement does not. `.claude/skills/docket/modes/release.md`
names it as the step a cut runs when a simulator tree object has moved, beside
the reading of the diff that it does not replace. Checked 2026-09-22 (`PL-14QR`, triage): no
such tool exists yet.
