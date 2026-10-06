---
id: PL-HR4V
title: doc_check's make_targets and _target_recipes take a rule line's targets and prerequisites by their own patterns, where _make_lines reads the line as make does, so a trailing comment's words become .PHONY names and prerequisites, and a target-specific variable or a ::= assignment declares a target make has no rule for; latent
status: untriaged
added: 2026-10-06
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
gives no target a rule, and `::=` read as an assignment. Each is pinned by a
test that fails on today's reader.
