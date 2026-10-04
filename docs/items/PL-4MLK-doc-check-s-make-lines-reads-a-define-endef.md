---
id: PL-4MLK
title: doc_check's _make_lines reads a define ... endef body as rules and recipes, so a target named only inside a multi-line variable reads as declared and a document citing make deploy passes; latent
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tests/unit
added: 2026-10-04
recurrences: 2026-10-04 PL-2JYP withdrawn 2026-10-04 PL-R417, 2026-10-04 PL-GZXY withdrawn 2026-10-04 PL-R417
---

**Problem.** doc_check's _make_lines reads a define ... endef body as rules and recipes, so a target named only inside a multi-line variable reads as declared and a document citing make deploy passes; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

GNU make manual § 6.8, "Defining Multi-Line Variables": the lines between `define` and `endef` are a variable's value. With "define DEPLOY_HELP", "deploy:", a tab and "./scripts/deploy.sh --check", "endef" above a real `check` rule, `make_targets` declares both `check` and `deploy` with recipes, `_target_recipes` and `_recipe_commands` yield the deploy line, and GNU Make 4.3 answers "No rule to make target 'deploy'". `PL-R417`'s second slice made `_make_lines` read backslash continuations whole; a `define` body is the form it did not cover. Latent: the Makefile has no `define`.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
