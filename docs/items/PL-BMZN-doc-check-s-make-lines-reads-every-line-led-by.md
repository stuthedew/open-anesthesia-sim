---
id: PL-BMZN
title: doc_check's _make_lines reads every line led by a tab as a recipe line, where make reads one outside any rule as an ordinary line, so a tab-indented assignment above the first rule or after a variable reaches the coverage gate and the ruff cache check as a command, and a continued one keeps the backslash-newlines make joins away; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-05
payoff: a tab-indented assignment outside any rule is no longer compared as a command make runs, so the coverage gate and the ruff cache check stop failing a Makefile make reads correctly
verify: grep -qF 'recipe commands, a tab-led assignment above the first rule is no command' tests/unit/test_doc_check.py && grep -qF 'recipe commands, a tab-led assignment after a variable is no command' tests/unit/test_doc_check.py
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
Re-run at triage on `main` at `b67dace8`, whose `PL-4MLK` taught `_make_lines`
to read a `define`: the same Makefile gives the same four commands, the two
assignments among them, and GNU Make 4.3 the same two lines, so it still holds.

**Why it matters.** The coverage gate and the ruff cache check select from
`_recipe_commands` by what a command says, so an assignment holding
`--cov-fail-under` or `ruff check` is compared as a command make runs, and a
correct Makefile fails both until a line make reads right is re-indented.

**Generator check.** A member of `PL-R417`: where one statement ends, the
statement here a Makefile rule with its recipe lines. Revised at triage,
2026-10-05, from the capture's one-off, which `PL-R417`'s link 15 also
recorded: read against that head's `misread:`, whether a rule is open at a
tab-led line is whether the rule above has ended, and an assignment ends it
(`record_waiting_files`). That is the fact `PL-TDVJ` misreads the other way,
ending a rule at a comment line, and that head already holds `PL-TDVJ` to it.
The continued case is the head's fact outright: make joins a non-recipe line's
backslash-newlines and keeps a recipe line's for the shell. `_target_recipes`
already reads where a rule ends, so one reading of it shared by the three
Makefile readers is the likely fix, and `PL-TDVJ` the item to build it beside.
Recorded in `PL-R417`'s `root-cause-of:` by its link 16. Holding
that state in `_make_lines` would also let it read a tab-led `define` outside a
rule as make does, which `PL-4MLK` declines by name.

**Done when.** A line led by a tab is a recipe line only while a rule is open,
as make 4.3's `eval` reads it: above the first rule, and after an assignment or
a directive that ends the rule above, it is read as the line its words make it,
its backslash-newlines joined as make joins a line that is not a recipe's.
`_recipe_commands`, `make_targets` and `_target_recipes` agree about which
lines are recipe lines, and `PL-R417`'s guard gains a case for a tab-led
assignment above the first rule and one after an assignment, each failing on
today's reader.
