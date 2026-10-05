---
id: PL-4MLK
title: doc_check's _make_lines reads a define ... endef body as rules and recipes, so a target named only inside a multi-line variable reads as declared and a document citing make deploy passes; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-R417's Makefile slice, 2026-10-05
added: 2026-10-04
payoff: a target or a command written only inside a define ... endef value is no longer read as one the Makefile runs, so a document naming it fails the make-targets check and the gate checks compare only what make runs
verify: grep -q 'make targets, a define body is the variable' tests/unit/test_doc_check.py
recurrences: 2026-10-04 PL-2JYP withdrawn 2026-10-04 PL-R417, 2026-10-04 PL-GZXY withdrawn 2026-10-04 PL-R417
---

**Problem.** doc_check's _make_lines reads a define ... endef body as rules and recipes, so a target named only inside a multi-line variable reads as declared and a document citing make deploy passes; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

GNU make manual § 6.8, "Defining Multi-Line Variables": the lines between `define` and `endef` are a variable's value. With "define DEPLOY_HELP", "deploy:", a tab and "./scripts/deploy.sh --check", "endef" above a real `check` rule, `make_targets` declares both `check` and `deploy` with recipes, `_target_recipes` and `_recipe_commands` yield the deploy line, and GNU Make 4.3 answers "No rule to make target 'deploy'". `PL-R417`'s second slice made `_make_lines` read backslash continuations whole; a `define` body is the form it did not cover. Latent: the Makefile has no `define`.

**Why it matters.** The make-targets check exists so that no document tells a
session to run a target that does not run (`PL-ZRFC`). Read as rules, a
`define` body declares targets make never has, so a document naming
`make deploy` passes while make answers "No rule to make target". Read as
recipe lines, the same body puts its commands into what the coverage gate,
gate parity and the ruff cache check compare, so a coverage run or a script
that is only a variable's value counts as one `make check` runs. Each is the
silent half: a check passing on a target or a command the Makefile never runs.

**Reproduced 2026-10-05, at triage.** On `main` at `f4a96014`, under python3
3.11.15, the Makefile this brief describes - `define DEPLOY_HELP`, `deploy:`, a
tab and `./scripts/deploy.sh --check`, `endef`, then `.PHONY: check` and a
`check:` rule - gave `make_targets` `deploy` declared with a recipe,
`_target_recipes` a `deploy` target and `_recipe_commands` the deploy line on
line 3, while GNU Make 4.3 answered "No rule to make target 'deploy'" and
exited 2. The repository's Makefile holds no `define`.

**Done when.** `_make_lines` reads a `define` directive through the `endef`
that closes it as one statement, as GNU make 4.3 reads one: the word `define`
after any modifier make allows ahead of it (`override`, `export`, `unexport`,
`private`), not followed by an assignment operator, which would make `define`
a variable's name; a body in logical lines, where a line led by a tab is the
body's, a bare `define` nests, and an `endef` standing alone or before a blank
closes. So `make_targets`, `_target_recipes` and `_recipe_commands` take
nothing in a body for a rule or a recipe line, and the four checks reading
them read the Makefile as make does. A `define` no `endef` closes, one naming
no variable, both of which make refuses, and one led by a tab, which make
reads as a directive outside a rule and as a recipe line inside one, are
declined by name, each check saying what went unchecked. `PL-R417`'s guard
gains a case per reader and form.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
