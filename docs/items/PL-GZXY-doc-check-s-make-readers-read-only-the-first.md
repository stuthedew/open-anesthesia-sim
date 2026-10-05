---
id: PL-GZXY
title: doc_check's make readers read only the first clause of a fenced command line and take target: prereq ; recipe for a rule with no recipe, so cd sub && make nosuch names no target and an inline recipe reads as missing; latent
priority: P3
effort: S
status: ready
classes: defect
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a make target documented after another command in a fence, as docs/worker.md writes the gate, is caught once it stops existing, and a correct one-line rule is no longer sent for rewriting
verify: grep -q 'def test_a_make_command_chained_after_another_in_a_fence_is_read' tests/unit/test_doc_check.py && grep -q 'def test_a_rule_with_an_inline_recipe_carries_a_recipe' tests/unit/test_doc_check.py
---

**Problem.** doc_check's make readers read only the first clause of a fenced command line and take target: prereq ; recipe for a rule with no recipe, so cd sub && make nosuch names no target and an inline recipe reads as missing; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`_make_mentions` reads `clauses[0]` of each fenced line, so `cd sub && make nosuch` and `true; make nosuch` name no target. `make_targets` reads `target: prereq ; recipe` (GNU make's inline recipe) as a target with no recipe, which `check_make_targets` would report as "declared but carries no recipe". Not members of `PL-R417`. Latent: no fence holds the form and the Makefile writes no inline recipe.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`, `_make_mentions` over a bash fence holding `cd sub && make nosuch`, `true; make nosuch` and `make alone` returned only `('alone', 4)`. `make_targets` over a Makefile whose rule reads `inline: lint ; @echo RECIPE-RAN` returned `inline` as declared but not as carrying a recipe, and `check_make_targets` told a document naming `make inline` that it "is declared but carries no recipe, so it exits 0 without running", while GNU make 4.3 ran the same rule and printed `RECIPE-RAN`. One live fence does hold the chained form, which the line above missed: `docs/worker.md` teaches `set -o pipefail; make check 2>&1 | tail -45`, and `_make_mentions` reads nothing from that line. It names `check`, which the Makefile runs, so nothing is missed today, and no Makefile rule writes an inline recipe.

**Why it matters.** `check_make_targets` exists because a documented target that never ran was believed for two releases, and a fenced command chained after another one - the `set -o pipefail;` form `docs/worker.md` teaches for running the gate - is never held to the Makefile, so a target renamed or deleted under that spelling passes. The inline-recipe half fails the other way: a correct one-line rule is reported as running nothing, and the only way to quiet the error is to rewrite a Makefile that was right.

**Generator check.** Two facts. Its first half is an instance of `PL-61FT`'s fact, which program a shell line runs, filed after that head closed on 2026-09-26, the second since the close with `PL-P95F`; its second half, GNU make's inline recipe after `;`, is a one-off reading of make's rule grammar.

**Done when.** `_make_mentions` reads each simple command on a fenced line as bash runs it, so `cd sub && make nosuch` and `true; make nosuch` each name `nosuch`, while a fenced shell comment and pasted make output still name nothing; `make_targets` counts a rule whose recipe follows a `;` on the rule's own line as carrying one; and `tests/unit/test_doc_check.py` gains `test_a_make_command_chained_after_another_in_a_fence_is_read` and `test_a_rule_with_an_inline_recipe_carries_a_recipe`, pinning each.

**Widened 2026-10-05, from `PL-M2RB`, dropped as a duplicate of this item's
second half.** The inline recipe is missed by all three readers of the
Makefile's rules, not by `make_targets` alone: on `main` at `e2d43eb7`,
`_target_recipes` gave `inline: lint ; @echo RECIPE-RAN` no recipe lines and
took `;`, `@echo` and `RECIPE-RAN` for prerequisites, and `_recipe_commands`
never yielded the command, so gate parity, the coverage gate and the ruff cache
check would none of them see it. All three read `_make_lines` (`PL-R417`), so
handing the recipe back from there as the rule's recipe line answers them at
once. Done when therefore also asks that `_target_recipes` give the rule that
recipe and only `lint` for a prerequisite, and that `_recipe_commands` yield
the command.
