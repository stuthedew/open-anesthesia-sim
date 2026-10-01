---
id: PL-848V
title: required_checks_check.py reads a block-sequence on: (on: followed by - pull_request lines) and a flow-mapping on: ({pull_request: ...}) as no events, so a pull-request workflow spelled either way drops out of the reconciliation and the check passes; its docstring calls the three spellings it reads the three the YAML spec allows
priority: P3
effort: S
status: ready
classes: defect
feature: required-check-trigger-reading
touches: tools/required_checks_check.py, tests/unit/test_required_checks_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: a pull-request workflow spelled as a YAML list or flow mapping is counted, so the reconciliation cannot pass by not seeing it
verify: grep -q 'def test_a_block_sequence_on_names_its_events' tests/unit/test_required_checks_check.py && grep -q 'def test_a_flow_mapping_on_names_its_events' tests/unit/test_required_checks_check.py
---

**Problem.** required_checks_check.py reads a block-sequence on: (on: followed by - pull_request lines) and a flow-mapping on: ({pull_request: ...}) as no events, so a pull-request workflow spelled either way drops out of the reconciliation and the check passes; its docstring calls the three spellings it reads the three the YAML spec allows

**Why it matters.** `required_checks_check` exists to fail when no workflow reports a required check on a pull request, and a workflow it cannot read drops out of the reconciliation and the check passes - a check passing while its guarantee is void. Latent: every `on:` under `.github/workflows` is a block mapping (read 2026-10-01). The docstring's claim that the three spellings it reads are the three YAML allows is false now.

**Done when.** `_triggers` reads a block-sequence `on:` and a flow-mapping `on:` as the events they name, a test pins each, and the docstring no longer claims the spec allows only three spellings.

**Reproduced 2026-10-01.** `_triggers` returns an empty set for a block-sequence `on:` naming `pull_request` and `push`, and for a flow mapping returns one event named for the whole mapping text.

**Generator check.** The fact is which workflow triggers make a required check report on a pull request, an external behaviour (YAML syntax and GitHub's trigger rules) the tool models by hand. `PL-C72H` is a second reading of it in the same function and no third is filed, so it is below a head's three; both carry `feature: required-check-trigger-reading` so a third is seen.
