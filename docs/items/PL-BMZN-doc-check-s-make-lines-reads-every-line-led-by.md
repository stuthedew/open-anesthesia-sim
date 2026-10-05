---
id: PL-BMZN
title: doc_check's _make_lines reads every line led by a tab as a recipe line, where make reads one outside any rule as an ordinary line, so a tab-indented assignment above the first rule or after a variable reaches the coverage gate and the ruff cache check as a command, and a continued one keeps the backslash-newlines make joins away; latent
status: untriaged
feature: one-answer
added: 2026-10-05
---

**Problem.** doc_check's _make_lines reads every line led by a tab as a recipe line, where make reads one outside any rule as an ordinary line, so a tab-indented assignment above the first rule or after a variable reaches the coverage gate and the ruff cache check as a command, and a continued one keeps the backslash-newlines make joins away; latent

**Found 2026-10-05 building `PL-R417`'s Makefile slice (`PL-4MLK`)**, which
declines a `define` led by a tab for the reason this item is the general case
of. `docket new` recorded it as a recurrence of `PL-4MLK`, which it is not, and
the recurrence is withdrawn naming this brief.

GNU make reads a line led by a tab as a recipe line only where a rule is open:
`eval` in make 4.3's `src/read.c` appends it to the rule's commands when a
rule's targets are pending, and otherwise reads it as any other line. An
assignment ends the rule above it (`record_waiting_files`), so a tab-led line
above the first rule or after an assignment is an assignment, a directive or a
rule, whatever leads it. `_make_lines` holds no rules, and hands every line a
tab leads back as a recipe line, its continuations kept as a recipe's are.

**Reproduced 2026-10-05.** On `main` at `e2d43eb7`, under python3 3.11.15, a
Makefile opening with a tab and `GATE := pytest --cov-fail-under=100`, then
`all:` over a tab and `@echo $(GATE)`, then `X = 1` over a tab and `Y = 2`, and
a `show:` rule echoing `$(Y)`, gave `_recipe_commands` the two assignments,
lines 1 and 5, as commands, while GNU Make 4.3 read both as assignments and
printed `pytest --cov-fail-under=100` and `Y=2`. `make_targets` and
`_target_recipes` read those lines right, since neither has a rule open there.
Latent: every line the repository's Makefile leads with a tab sits under a rule.

**Why it matters.** The coverage gate and the ruff cache check select from
`_recipe_commands` by what a command says, so an assignment holding
`--cov-fail-under` or `ruff check` is compared as a command make runs, and a
correct Makefile fails both until a line make reads right is re-indented.

**Generator check.** Not a member of `PL-R417`: each line is read whole, as
the one statement it is; what is misread is the kind of line a tab leads, which
turns on whether a rule is open there, and no other item names that fact.
Holding that state in `_make_lines` would also let it read a tab-led `define`
outside a rule as make does, which `PL-4MLK` declines by name.
