---
id: PL-HD96
title: tools/doc_check.py's MAKE_TARGET_RE reads a rule line naming two or more targets (fix lint: sync) as no target, so their recipes go unread by gate parity and a documented make fix is reported as undefined; a target list a backslash continues now joins into that shape
status: untriaged
added: 2026-10-04
---

**Problem.** tools/doc_check.py's MAKE_TARGET_RE reads a rule line naming two or more targets (fix lint: sync) as no target, so their recipes go unread by gate parity and a documented make fix is reported as undefined; a target list a backslash continues now joins into that shape

**Found 2026-10-04 building `PL-R417`'s Makefile slice (`#1338`).**
`MAKE_TARGET_RE` takes one name before the colon, so `fix lint: sync` matches
nothing: `_target_recipes` and `make_targets` read it as no rule, its recipe
lines belong to no target, and `check_make_targets` reports a documented
`make fix` as a target the Makefile does not define. Latent: this repository's
`Makefile` names one target per rule. `_make_lines` joins `a \` over `b: c`
into `a b: c` as make does, so a continued target list now meets the same gap
where it used to lose only its first line. GNU make manual, "Rule Syntax":
`targets : prerequisites`, the targets being file names separated by spaces.
