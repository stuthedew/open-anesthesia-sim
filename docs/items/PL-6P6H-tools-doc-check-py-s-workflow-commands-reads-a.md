---
id: PL-6P6H
title: tools/doc_check.py's workflow_commands reads a folded run: > block as a literal one, so a command YAML folds onto one line is read as several; no workflow uses > today
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
payoff: a CI step written as a folded YAML block is checked as the one command bash runs, instead of as fragments nobody is told were misread
verify: grep -q 'def test_workflow_commands_reads_a_folded_block' tests/unit/test_doc_check.py
---

**Problem.** tools/doc_check.py's workflow_commands reads a folded run: > block as a literal one, so a command YAML folds onto one line is read as several; no workflow uses > today

**Reproduced 2026-10-03 at triage.** `workflow_commands` on a step written
`run: >` over `python3 tools/x.py` and an indented `--flag` returns two
commands, `python3 tools/x.py` on one line and `--flag` on the next, where YAML
folds the body into one line and bash runs `python3 tools/x.py --flag`. No
workflow under `.github/workflows/` writes `run: >` today.

**Why it matters.** Latent, and silent when it lands: every check reading CI's
commands through `workflow_commands` - the path check, gate parity, the
coverage gate - would compare fragments of a folded command, so a flag that
differs between CI and the Makefile is read as a command of its own, and
nothing says a block was misread.

**Done when.** A `run: >` block is read as the one line YAML hands bash, or
refused by name as a form the reader does not take; either way a test pins the
folded case. Refusing is the cheaper answer while no workflow folds.

[superseded 2026-10-04: a member of `PL-R417`, below] **Generator check.** A
one-off: one reader missing one input form, not two spellings of a predicate
disagreeing, so not `PL-PVW2`'s or `PL-KGYT`'s fact. Filed in `PL-Q9LK`'s
closing commit as a residual that fix left on purpose, so not a re-entry of it
either.

**Generator check, 2026-10-04.** A member of `PL-R417`: YAML folds a `>`
block's lines into one before bash reads it (YAML 1.2.2 § 8.1.3), so the reader
took a physical line for a statement its format continues - the fact
`PL-JCS3` found six readers misreading. The reading above, that no second
spelling disagrees, still holds; it tested a different fact.
