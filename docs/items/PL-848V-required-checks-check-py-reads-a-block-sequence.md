---
id: PL-848V
title: required_checks_check.py reads a block-sequence on: (on: followed by - pull_request lines) and a flow-mapping on: ({pull_request: ...}) as no events, so a pull-request workflow spelled either way drops out of the reconciliation and the check passes; its docstring calls the three spellings it reads the three the YAML spec allows
priority: P1
effort: M
status: done
classes: defect
feature: required-check-trigger-reading
touches: tools/required_checks_check.py, tools/doc_check.py, tests/unit, docs/items/PL-S3XS-doc-check-s-workflow-readers-take-any-line.md, docs/items/PL-R417-readers-take-a-physical-line-for-the-statement.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-05
pr: 1366
payoff: a pull-request workflow spelled as a YAML list or flow mapping is counted, so the reconciliation cannot pass by not seeing it
verify: grep -q 'def test_a_block_sequence_on_names_its_events' tests/unit/test_required_checks_check.py && grep -q 'def test_a_flow_mapping_on_names_its_events' tests/unit/test_required_checks_check.py && grep -q '^generator: spent' docs/items/PL-848V-required-checks-check-py-reads-a-block-sequence.md
root-cause-of: PL-C72H, PL-PZP7, PL-4T49, PL-GWQ7, PL-S3XS
generator: spent - both tools read a workflow's triggers through one reader, required_checks_check.triggers and reports_on, which names the events of every form GitHub's workflow schema gives on: and reads or refuses each pull-request filter by name and line; no other reader of on: is left in tools/, docket or .claude/hooks/ (searched 2026-10-05), so a spelling a workflow can write meets that reader's refusal rather than a second reader's silence
misread: Which events a workflow's on: names, and so whether its checks report on a pull request
recurrences: 2026-10-04 PL-4T49, 2026-10-04 PL-PZP7
---

**Problem.** required_checks_check.py reads a block-sequence on: (on: followed by - pull_request lines) and a flow-mapping on: ({pull_request: ...}) as no events, so a pull-request workflow spelled either way drops out of the reconciliation and the check passes; its docstring calls the three spellings it reads the three the YAML spec allows

**Why it matters.** `required_checks_check` exists to fail when no workflow reports a required check on a pull request, and a workflow it cannot read drops out of the reconciliation and the check passes - a check passing while its guarantee is void. Latent: every `on:` under `.github/workflows` is a block mapping (read 2026-10-01). The docstring's claim that the three spellings it reads are the three YAML allows is false now.

**Done when.** `required_checks_check` and `doc_check` read a workflow's triggers through one reader, which names the events of a block-sequence and a flow-mapping `on:` and of each member's spelling, or declines a spelling by name, so none reads as no trigger or as reporting; a test pins each; `_triggers`' docstring no longer claims the spec allows only three spellings; and `generator:` is rewritten `spent` with the reason.

**Reproduced 2026-10-01.** `_triggers` returns an empty set for a block-sequence `on:` naming `pull_request` and `push`, and for a flow mapping returns one event named for the whole mapping text.

**A head, from 2026-10-04 (`#1353`).** `PL-R417`'s last-slice sweep filed four
more readings of this item's fact in one pass: `PL-PZP7` (`doc_check`'s
`PULL_REQUEST_TRIGGER_RE` misses this item's two spellings and a trailing
comment, and `_triggers` keeps a comment in an event's name), `PL-4T49`
(`_triggers` reads a value opening on the line after `on:`, a block-scalar
header and an explicit `?` key as no trigger), `PL-GWQ7` (a four-space indent
under `on:` or `jobs:` is skipped) and `PL-S3XS` (`doc_check` reads an `on:`
carrying a comment or an anchor as triggered by nothing). `docket new` matched
the first two here, and those matches stand. With `PL-C72H` that is five items
from one mechanism: two hand readers of a workflow's `on:`,
`required_checks_check._triggers` and `doc_check`'s pull-request trigger
reading, each taking a few of the spellings YAML and GitHub's workflow syntax
allow and reading the rest as no trigger, or a branch filter as reporting. The
fix is one reader of a workflow's triggers that both tools call, naming the
events of each spelling it reads and declining the rest by name - one fact read
once (`.claude/rules/apparatus-standard.md` § "Read the fact from its record;
where none exists, write one"). `PL-4T49` and `PL-S3XS` are also `PL-R417`'s
members, for their continued statements; whichever head's work reaches them
first closes them.

**Next steps (recorded 2026-10-04).** A thread of its own, since the head
ranks above every band but P0: build the one reader of a workflow's `on:` that
`required_checks_check._triggers` and `doc_check`'s pull-request trigger
reading both call, naming the events of each spelling GitHub's workflow syntax
documents and declining the rest by name; read `PL-C72H`'s branch filter or
decline it; pin each member's case; and rewrite `generator:` `spent` when no
spelling a workflow can write reads as no trigger. `PL-R417`'s YAML slice
already refuses a flow collection carried past `on:`'s line, which the reader
keeps.

**As built (`#1366`, 2026-10-05).** `required_checks_check.triggers` is the
one reader of a workflow's `on:`, and `reports_on` the one answer to whether a
workflow runs on every pull request onto a branch; `reporting_jobs` and
`doc_check._gates_pull_requests` both ask it, the second of `pull_request`
alone, since `pull_request_target` runs the base's workflow rather than the
branch's. It reads the forms GitHub's workflow schema gives `on:` - a string, a
sequence or a mapping, in block or flow form, on the key's line or the next,
with a comment or an anchor after the key or the key quoted, at any indent of
spaces - and refuses by name
and line each form it does not read: a block scalar, an alias, a tag, an
explicit key, a flow collection carried past its line, a scalar continued onto
the next line, a tab in the indentation, and a second `on:`. Each pull-request
filter is read or refused. `branches` and `branches-ignore` are matched against
the default branch with the cheat sheet's patterns, in order, so a filter
leaving it out reports nothing (`PL-C72H`), and a pattern the cheat sheet does
not document, or a filter with no default branch to match, is refused. `paths`
and `paths-ignore` are refused, since whether one skips a pull request turns on
its diff and a skipped workflow's checks stay Pending. A `types:` list leaving
out `opened`, `synchronize` or `reopened` is refused, since a pull request
reaching the one left out would not run it. `_jobs` and `_job_name` read a job
at the indent its workflow uses (`PL-GWQ7`). Sources: GitHub's workflow schema
(`workflow-v1.0.json` in `actions/languageservices`), and *Workflow syntax for
GitHub Actions* and *Events that trigger workflows* on docs.github.com, all
read 2026-10-05.

**Generator check.** The head: the fact is which events a workflow's `on:` names, and so whether its checks report on a pull request, an external behaviour (YAML syntax and GitHub's trigger rules) the tools model by hand. Recorded on 2026-10-04 at six readings of the fact, this item the first and `PL-C72H` the second, as the 2026-10-01 triage note asked when it put both under `feature: required-check-trigger-reading` so a third would be seen.
