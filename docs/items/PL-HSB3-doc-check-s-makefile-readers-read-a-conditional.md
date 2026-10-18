---
id: PL-HSB3
title: doc_check's Makefile readers read a conditional's branches in turn, so make_targets and the gate parity check count a recipe line only one configuration runs, where until PL-TDVJ they dropped every recipe line inside a conditional; latent
priority: P3
effort: M
status: done
classes: defect
touches: tools/doc_check.py, tests/unit/test_doc_check.py, tests/unit/test_makefile_reference.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-06
closed: 2026-10-18
pr: 1580
payoff: gate parity and the make-target check count a recipe line only where every configuration runs it, so neither passes a script make check may skip
verify: grep -q 'def test_a_recipe_line_inside_a_conditional_runs_only_in_its_branch' tests/unit/test_doc_check.py
reenters: PL-0HPV
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

[superseded 2026-10-12: answered below, a re-entry of `PL-0HPV`] **Generator question, open at the 2026-10-11 triage pass; left untriaged for it.**
This item's own brief calls it the Makefile side of `PL-ZXM1`'s fact, and
`PL-ZXM1` records itself as the second post-close instance of `PL-0HPV`'s fact
(the checks the local gate and the merge gate each run, and where the two sets
differ), after `PL-RW3T`, "one short of the three that would record PL-0HPV's
fix as not holding". This would be the third (filed 2026-10-06), `PL-5M36`'s
first bullet a fourth (2026-10-10), and `PL-GSJ6` possibly a fifth. Unlike the
`PL-KR6M` and `PL-JTCQ` questions, the instances keep arriving from ordinary work
rather than a sweep, so the reading is **`live`**, which is `P1` by rule and
restarts `CLAUDE.md`'s pause on new workflow mechanisms. **Leaning: record a live
head**, after re-reading `PL-0HPV`'s and `PL-ZXM1`'s briefs; settle it before
triaging this item.

**Answered at the 2026-10-12 triage pass: a re-entry of `PL-0HPV`, recorded as
`reenters: PL-0HPV`.** It is the third filing to carry the field, after
`PL-RW3T` and `PL-ZXM1`, so `bin/docket inflow` names `PL-0HPV` as a head whose
fix did not hold, and whether it takes a successor head is answered under
`PL-4097` with the other heads that report names. A `live` reading restarts
`CLAUDE.md`'s pause on new workflow mechanisms, which is why `PL-61FT`'s went to
the owner; this item is worked at its own band meanwhile.

**Fixed 2026-10-18 under `PL-ZQ3R`, by declining.** `_make_lines` takes
`every_branch`. `make_targets` and `_target_recipes` pass it false, so a
recipe line inside a conditional raises `UnreadStatement` naming the
conditional's line. `check_make_targets` and `check_gate_parity` then decline
the Makefile by name instead of counting a command make runs in one branch.
`_recipe_commands`, which the coverage gate and ruff cache checks read, still
holds every branch. Reading each branch's commands per configuration would
need make's variables evaluated, and the Makefile's one conditional holds no
recipe line, so declining is the cheaper ending and costs nothing today.
`tests/unit/test_makefile_reference.py` drops its `PL-HSB3` known departure
and now draws conditionals. `test_a_recipe_line_inside_a_conditional_runs_only_in_its_branch`
fails on the code before the fix.
