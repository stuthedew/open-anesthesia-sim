---
id: PL-TDVJ
title: doc_check's make_targets ends a rule at a comment line, where make and _target_recipes go on reading its recipe, so a target whose first recipe line follows a comment reads as declared with no recipe and a document naming it fails as exiting 0 without running; latent
status: untriaged
feature: one-answer
added: 2026-10-05
---

**Problem.** doc_check's make_targets ends a rule at a comment line, where make and _target_recipes go on reading its recipe, so a target whose first recipe line follows a comment reads as declared with no recipe and a document naming it fails as exiting 0 without running; latent

**Found 2026-10-05 building `PL-R417`'s Makefile slice (`PL-4MLK`)**, reading
`make_targets` beside `_target_recipes`. `docket new` recorded it as a
recurrence of `PL-4MLK`, which it is not: that item is a `define` body read as
rules, and this one a comment line read as the end of a rule. The recurrence is
withdrawn naming this brief.

GNU make carries a rule on past a comment line, which it drops without ending
the rule, as an assignment, an `include` or an `export`, or another rule line
would (`record_waiting_files` in make 4.3's `src/read.c`).
`_target_recipes` reads it that way and says so ("Blank lines and comment lines
do not end a recipe, which is a rule of Make"). `make_targets` ends the rule at
any line that is neither blank nor a rule, a comment included.

**Reproduced 2026-10-05.** On `main` at `e2d43eb7`, under python3 3.11.15, a
Makefile of `.PHONY: check`, `check:`, `# run the gate`, then a tab and
`@echo CHECK-RAN` gave `make_targets` `check` declared with no recipe, while
`_target_recipes` gave `check` the `@echo CHECK-RAN` line and GNU Make 4.3 ran
it, printed `CHECK-RAN` and exited 0. `check_make_targets` told a document
naming `make check` that it "is declared but carries no recipe, so it exits 0
without running". Latent: no rule in the repository's Makefile puts a comment
line between its rule line and its first recipe line.

**Why it matters.** It fails loudly, but on a Makefile make reads correctly,
and the only way to quiet it is to move a comment that is right where it is -
the cost `PL-GZXY` records for an inline recipe. And two readers of one
Makefile disagree about where the same rule ends.

**Generator check.** A member of `PL-R417`: a reader ends a statement - here a
rule, its recipe lines included - at a line its format carries the statement
past, the fact that head's `misread:` names.
