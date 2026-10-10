---
id: PL-CK3F
title: tools/required_checks_check.py's _jobs walks every physical line under jobs: and takes a tab after a line's leading spaces for indentation, so a run: | body or a multi-line quoted scalar holding one - the tab-led line of a here-document that strips tabs - is refused as a tab indenting the line and the check exits 1 on a workflow YAML reads whole, where steps and triggers read the same file; latent
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: tools/required_checks_check.py, tests/unit, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
payoff: a workflow whose block or quoted scalar holds a tab-led line is read as GitHub reads it, so the required-checks check stops refusing a sound workflow and failing make check and CI
verify: grep -qF '"required checks, a tab-led line in a block scalar' tests/unit/test_doc_check.py && grep -qF '"required checks, a tab-led line in a quoted scalar' tests/unit/test_doc_check.py
---

**Problem.** tools/required_checks_check.py's _jobs walks every physical line under jobs: and takes a tab after a line's leading spaces for indentation, so a run: | body or a multi-line quoted scalar holding one - the tab-led line of a here-document that strips tabs - is refused as a tab indenting the line and the check exits 1 on a workflow YAML reads whole, where steps and triggers read the same file; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing the
larger tools. `_jobs` walks every physical line under `jobs:`, and the guard
`#1366` (`PL-848V`) added to it raises `Undecidable` wherever the character
after a line's leading spaces is a tab. That is right for a structural line,
where YAML 1.2.2 indents with spaces only, but a block scalar's content line is
`s-indent(n) nb-char+` (§ 8.1.2), so a tab past the content indentation is
content, and a double-quoted scalar's continuation line may hold a tab as a
separator after its indentation (§ 6.3, § 7.3.1). `_jobs` reads both as
structure.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against PyYAML. `TAB` marks a tab character:

```text
name: quality
on: pull_request
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - run: |
          cat <<-EOF
          TABhello
          EOF
```

`_jobs` raised `Undecidable` at line 9, a tab indenting the line;
`reporting_jobs` raised with it, so `main` printed that it cannot decide what
this tree reports and exited 1. On the same file `steps` read the `run` step and
`triggers` read `pull_request`. PyYAML read the step's `run` as `cat <<-EOF`,
a tab-led `hello` and `EOF`. A second file, an `env:` holding `GREETING:
"hello` continued on a line of spaces, a tab and `world"`, is refused the same
way; PyYAML reads `hello world`. Latent: none of the six tracked workflows holds
a tab. It fails loudly, but on a workflow GitHub reads, and the step it would
refuse is the required `checks` job's.

**Why it matters.** `required_checks_check` is what `make check` and CI ask
whether the required checks branch protection names are ones the workflows
report. Refusing a sound workflow fails both with "cannot decide", and the
step it would refuse is the required `checks` job's, so a here-document written
the conventional way, its lines led by the tabs `<<-` strips, would block every
pull request.

**Generator check.** A member of `PL-R417`: a reader takes each physical line
under `jobs:` for a structural line where a block or quoted scalar continues
across it. The guard arrived 2026-10-04, after the head was recorded, so it is
inflow; its tests pin only a column-0 tab.

**Done when.** `_jobs` passes a value over by indentation through the
`_keys` and `_passed_over` walk `steps` already uses, so only structural lines
reach the tab guard, pinned by a `required checks, ` case in `PL-R417`'s guard
for each of the two files above, failing on today's reader.
