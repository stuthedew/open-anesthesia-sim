---
id: PL-HD96
title: tools/doc_check.py's MAKE_TARGET_RE reads a rule line naming two or more targets (fix lint: sync) as no target, so their recipes go unread by gate parity and a documented make fix is reported as undefined; a target list a backslash continues now joins into that shape
priority: P3
effort: S
status: ready
classes: defect
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: an alias rule or a backslash-continued target list neither turns make check red on correct documentation nor drops its recipe from the gate-parity comparison
verify: grep -q 'def test_every_target_a_rule_names_carries_its_recipe' tests/unit/test_doc_check.py
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

**Reproduced 2026-10-04** on `main` at `8f24fe78`:
`python3 -c "import sys; sys.path.insert(0, 'tools'); import doc_check as d; mk = '.PHONY: fix lint\nfix lint: sync\n\truff check --fix .\n'; print(*map(sorted, d.make_targets(mk)), d._target_recipes(mk))"`
printed `['fix', 'lint'] [] ({}, {})`: both names are declared through
`.PHONY`, neither carries a recipe, and `_target_recipes` holds no recipe or
prerequisites for either. Through `check_make_targets`, a document naming
`make fix` is then reported as declared with no recipe, so exiting 0 without
running, and without the `.PHONY` line as a target the Makefile does not
define. With a `fix lint:` rule running a tool and `check: lint`,
`_target_commands` reads `make check` without that tool's line, which is what
gate parity compares. `_make_lines` joins `fix \` over `lint: sync` into one
line reading `fix lint: sync`, as the brief says.

**Why it matters.** Latent: this repository's `Makefile` names one target per
rule, and `make_targets` reads all ten of its targets. The first rule naming
two, an alias pair or a target list continued by a backslash, turns
`make check` red on every document that names one of them, a hard failure on
correct documentation that a session is tempted to clear by rewording the
document. If such a rule is a prerequisite of `check`, gate parity reads
`make check` short as well: a gate its recipe runs that CI also runs is
reported as CI-only, and one CI does not run passes unreported, an answer
given from a partial read.

**Done when.** Every name before a rule's colon is a target: `make_targets`
and `_target_recipes` give each name the rule's recipe and prerequisites, so a
documented `make fix` under `fix lint: sync` is quiet and gate parity counts
that recipe under each name; `test_every_target_a_rule_names_carries_its_recipe`
in `tests/unit/test_doc_check.py` pins it.

**Generator check.** One-off. The fact misread is a rule line's target list:
GNU make's `targets : prerequisites`, the targets being names separated by
spaces. It is not `PL-R417`'s fact, where one statement ends, since the rule
`fix lint: sync` is misread on one physical line, and `_make_lines` only
brought a continued list to that shape. Both readers already take a rule's
targets from one pattern, so the record exists and states the grammar short;
correcting it corrects every reader. `PL-0HPV`'s fact, which checks each gate
runs, is where one consequence lands, not what is misread. Not a re-entry:
`MAKE_TARGET_RE` is unchanged since `PL-ZRFC` (closed 2026-08-30), and no item
closed since 2026-09-04 named it; `PL-G2FY` (closed 2026-10-04) was a
continued recipe line.
