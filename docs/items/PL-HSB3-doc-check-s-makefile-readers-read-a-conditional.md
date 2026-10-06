---
id: PL-HSB3
title: doc_check's Makefile readers read a conditional's branches in turn, so make_targets and the gate parity check count a recipe line only one configuration runs, where until PL-TDVJ they dropped every recipe line inside a conditional; latent
status: untriaged
touches: docs/items/PL-GZXY-doc-check-s-make-readers-read-only-the-first.md
added: 2026-10-06
---

**Problem.** doc_check's Makefile readers read a conditional's branches in turn, so make_targets and the gate parity check count a recipe line only one configuration runs, where until PL-TDVJ they dropped every recipe line inside a conditional; latent

**Found 2026-10-06 building `PL-TDVJ` and `PL-BMZN`** (`#1384`). `_make_lines`
now holds which rule is open and reads a conditional's directives as GNU make
4.3 does, ending no rule. Which branch make takes turns on variables it does not
evaluate, so it reads every branch in turn, declining a tab-led line only where
a branch changed which rule is open, and yields a recipe line in either branch
under the rule above it. Until then `make_targets` and `_target_recipes` ended
the rule at the `ifdef` and dropped every recipe line from there to the next
rule line, while `_recipe_commands` read them all.

**Reproduced 2026-10-06** under python3 3.11.15: `check:` over `ifdef X`, a
tab and `@echo x`, `else`, a tab and `@echo y`, and `endif` gives
`_target_recipes` both commands under `check`, and `make_targets` `check` as
carrying a recipe. GNU Make 4.3 runs `@echo y` alone without `X` and `@echo x`
alone with it. With a recipe line in the `ifdef` branch only, make runs nothing
for `make check` without `X`, and the reader still gives `check` a recipe.

**Why it matters.** `check_gate_parity` compares the scripts `make check` runs
with the merge gate's, so a script `make check` runs in one configuration
counts as run in every one, and `check_make_targets` passes a target whose only
recipe sits in a branch make may not take. The coverage gate and ruff cache
checks hold every command make might run, which is right for them. Latent: the
Makefile's one conditional, around `UV_NATIVE_TLS`, holds an assignment and a
directive and no recipe line.

**Generator check.** The Makefile side of the fact `PL-ZXM1` misreads on the
workflow side, a command gate parity counts whatever condition it runs under,
there a step's `if:`. Not a member of `PL-R417`, since nothing here continues
across lines. `docket new` matched it to `PL-GZXY` by a shared path, which is
not the same fact, so that recurrence is withdrawn naming this brief.

**Done when.** `make_targets` and `check_gate_parity` read a recipe line inside
a conditional as running only in its branch, so a target carries a recipe only
where every branch gives it one and a script counts as run by `make check` only
where no branch leaves it out, or decline by name a target whose recipe a
conditional splits; a test pins each.
