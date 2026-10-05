---
id: PL-M2RB
title: doc_check's Makefile readers miss a recipe written on its rule's line after a semicolon (target: ; command), so make_targets reads the target as having no recipe, _target_recipes takes the command's words for prerequisites, and _recipe_commands never hands the command to the coverage gate or the ruff cache check; latent
status: dropped
feature: one-answer
added: 2026-10-05
closed: 2026-10-05
reason: Duplicate of PL-GZXY's second half (a recipe written after a semicolon on its rule's own line), which named make_targets alone. Its observation - that _target_recipes takes the recipe's words for prerequisites and _recipe_commands never yields it, reproduced on main at e2d43eb7 - is folded into PL-GZXY's brief, widening its Done when to all three readers.
---

**Problem.** doc_check's Makefile readers miss a recipe written on its rule's line after a semicolon (target: ; command), so make_targets reads the target as having no recipe, _target_recipes takes the command's words for prerequisites, and _recipe_commands never hands the command to the coverage gate or the ruff cache check; latent

**Found 2026-10-05 building `PL-R417`'s Makefile slice (`PL-4MLK`)**, and
dropped the same day as a duplicate of `PL-GZXY`'s second half, which names
`make_targets` alone; the two other readers found missing the same recipe are
folded into that brief. `docket new` recorded it as a recurrence of `PL-4MLK`,
which it is not: that item is a `define` body read as rules, and this one a
recipe on its rule's own line. The recurrence is withdrawn naming this brief.

**Reproduced 2026-10-05.** On `main` at `e2d43eb7`, under python3 3.11.15, a
Makefile of `inline: lint ; @echo RECIPE-RAN` above a `lint:` rule echoing
`lint` gave `make_targets` `inline` declared with no recipe, `_target_recipes`
`inline` with no recipe lines and `lint`, `;`, `@echo` and `RECIPE-RAN` for
prerequisites, and `_recipe_commands` only the `lint` rule's command, while GNU
Make 4.3 ran `make inline` and printed `lint`, then `RECIPE-RAN`.
