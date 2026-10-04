---
id: PL-PZP7
title: doc_check's PULL_REQUEST_TRIGGER_RE misses a pull_request trigger written as a list entry, with a trailing comment or as a flow mapping, and required_checks_check keeps an on: line's trailing comment in its event name, so a pull-request workflow spelled those ways reads as gating nothing; latent
priority: P3
effort: S
status: ready
classes: defect
feature: required-check-trigger-reading
touches: tools/doc_check.py, tools/required_checks_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a pull-request workflow whose trigger carries a comment, a list dash or an inline mapping still counts as reporting on pull requests, so neither check passes or fails for not having seen it
verify: grep -q 'def test_each_spelling_of_a_pull_request_trigger_is_the_merge_gate' tests/unit/test_doc_check.py && grep -q 'def test_a_trailing_comment_is_no_part_of_an_event_name' tests/unit/test_required_checks_check.py
---

**Problem.** doc_check's PULL_REQUEST_TRIGGER_RE misses a pull_request trigger written as a list entry, with a trailing comment or as a flow mapping, and required_checks_check keeps an on: line's trailing comment in its event name, so a pull-request workflow spelled those ways reads as gating nothing; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`doc_check`'s `PULL_REQUEST_TRIGGER_RE` misses `- pull_request`, `pull_request:  # comment` and `pull_request: {...}`. `required_checks_check._triggers` reads `on: pull_request  # every PR` as the event `pull_request  # every PR`, and `on: [push, pull_request]  # both` as `push` and `pull_request]  # both`. YAML 1.2.2 § 6.6. Not a member of `PL-R417`: each spelling sits on one line. With `PL-848V` it is the second item misreading which YAML spellings name a workflow's pull-request trigger, now across two tools; `PL-C72H`, the feature's other item, misreads GitHub's branch-filter semantics rather than a spelling. With `PL-4T49`, `PL-GWQ7` and `PL-S3XS` from the same sweep, it is a member of `PL-848V`, recorded as their head the same day. Latent: every `on:` in the six workflows is a bare block mapping.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`, `doc_check._gates_pull_requests` returned `False` for an `on:` block whose member is written `- pull_request`, `pull_request:  # every PR` or `pull_request: {branches: [main]}`, and `True` for the bare `pull_request:` control. `required_checks_check._triggers` read `on: pull_request  # every PR` as the one event `pull_request  # every PR`, and `on: [push, pull_request]  # both` as `push` and `pull_request]  # both`; `reporting_jobs` over a directory whose one workflow opens `on: pull_request  # every PR` returned no job. Latent, as the line above says: every `on:` under `.github/workflows` is a block mapping, and neither of its two `pull_request` keys carries a comment or a value on its own line.

**Why it matters.** A pull-request workflow read as triggering nothing drops out of both checks. `required_checks_check` leaves its jobs out of the reconciliation, so a job reporting on pull requests without being required passes unreported - the `PL-H8YD` failure that let `#654` merge on a failed `pr-title` - and a required one reads as orphaned, an error that points at the settings rather than at the reader. `doc_check`'s `check_gate_parity` reads every script only that workflow runs as missing from the merge gate. Each spelling is ordinary YAML that a workflow edit can introduce, and neither tool says it could not read it.

**Generator check.** A member of `PL-848V`, recorded there by `PL-R417`'s sweep: which YAML spellings name a workflow's pull-request trigger.

**Done when.** `PL-848V`'s one reader of a workflow's `on:`, which `required_checks_check._triggers` and `doc_check`'s `_gates_pull_requests` both call, names `pull_request` for a member written `- pull_request`, `pull_request:  # every PR` or `pull_request: {branches: [main]}`, and leaves a trailing comment out of an inline `on:`'s event names, so `on: [push, pull_request]  # both` names `push` and `pull_request`; `tests/unit/test_doc_check.py` gains `test_each_spelling_of_a_pull_request_trigger_is_the_merge_gate` and `tests/unit/test_required_checks_check.py` gains `test_a_trailing_comment_is_no_part_of_an_event_name`. The head's fix covers every case here, so this closes with `PL-848V`.
