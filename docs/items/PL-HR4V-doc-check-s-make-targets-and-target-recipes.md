---
id: PL-HR4V
title: doc_check's make_targets and _target_recipes take a rule line's targets and prerequisites by their own patterns, where _make_lines reads the line as make does, so a trailing comment's words become .PHONY names and prerequisites, and a target-specific variable or a ::= assignment declares a target make has no rule for; latent
priority: P3
effort: S
status: ready
classes: defect
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed at triage 2026-10-06
added: 2026-10-06
payoff: a word in a Makefile comment, or a target-specific variable, no longer counts as a target, and a rule naming two targets declares both, so a document naming a make target is told the failure make would give
verify: grep -q 'def test_a_rule_line_comment_declares_no_target_or_prerequisite' tests/unit/test_doc_check.py && grep -q 'def test_a_target_specific_variable_declares_no_target' tests/unit/test_doc_check.py && grep -q 'def test_a_double_colon_assignment_declares_no_target' tests/unit/test_doc_check.py && grep -q 'def test_every_target_a_rule_line_names_is_declared' tests/unit/test_doc_check.py
---

**Problem.** doc_check's make_targets and _target_recipes take a rule line's targets and prerequisites by their own patterns, where _make_lines reads the line as make does, so a trailing comment's words become .PHONY names and prerequisites, and a target-specific variable or a ::= assignment declares a target make has no rule for; latent

**Found 2026-10-06 building `PL-TDVJ` and `PL-BMZN`** (`#1384`), which gave
`_make_lines` make 4.3's reading of a rule line to decide which rule a tab-led
line belongs to: `_rule_opened` cuts the line at an unquoted `;` or `#`, finds
the targets' colon outside a variable reference, and reads an assignment after
it as a target-specific variable. `make_targets` and `_target_recipes` still
take the targets and prerequisites from the statement's text by
`MAKE_TARGET_RE`, `PHONY_RE` and a split on blanks.

**Reproduced 2026-10-06** on that branch, under python3 3.11.15, against GNU
Make 4.3. Over `.PHONY: check # the gate` and a `check:` rule, `make_targets`
declares `#`, `the` and `gate` beside `check`, where make reads a comment. A
Makefile of `a: X = 1` alone has `make_targets` declare `a` with no recipe,
where `make a` answers "No rule to make target 'a'", and `a ::= 1` alone does
the same, since the `(?!=)` in `MAKE_TARGET_RE` passes a second colon.
`_target_recipes` reads `check: lint # and test` as the prerequisites `lint`,
`#`, `and` and `test`.

**Re-run at triage, 2026-10-06**, on `main` at `2ea40f3e` against GNU Make 4.3:
all four still hold, and a fifth form of the same misread turned up. A rule
naming two targets, `a b: ; @echo ran-$@`, has `make_targets` declare neither,
since `MAKE_TARGET_RE` wants the colon straight after one name, where make runs
`make a` and `make b` alike. Make also runs an order-only prerequisite after
`|`, and reads a static pattern rule's prerequisites after its second colon,
neither of which a split on blanks reads.

**Why it matters.** `check_make_targets` tells a document naming `make a` that
the target is declared but carries no recipe, so it exits 0 without running,
where make refuses it as having no rule: the answer names the wrong failure.
A word in a `.PHONY` comment becomes a target a document can name unwarned.
Latent: no rule or `.PHONY` line in the Makefile carries a comment, a
target-specific variable or `::=`.

**Generator check.** The fact the second half of `PL-GZXY` misreads, a rule
line's grammar past its targets, there an inline recipe after `;`, so the
recurrence `docket new` recorded on that item stands. Not a member of
`PL-R417`: nothing here continues across lines. Built beside `PL-GZXY`, the
likely fix is one reading of a rule line, the one `_rule_opened` already
makes, handed to both readers in place of their own patterns.

**Done when.** `make_targets` and `_target_recipes` take a rule line's
targets, prerequisites and `.PHONY` names as make 4.3 reads them: a comment
cut off, an assignment after the colon read as a target-specific variable that
gives no target a rule, `::=` read as an assignment, and every target a rule
line names declared. Each is pinned by a
test that fails on today's reader.
