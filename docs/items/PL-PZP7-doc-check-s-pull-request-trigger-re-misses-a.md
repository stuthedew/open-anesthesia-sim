---
id: PL-PZP7
title: doc_check's PULL_REQUEST_TRIGGER_RE misses a pull_request trigger written as a list entry, with a trailing comment or as a flow mapping, and required_checks_check keeps an on: line's trailing comment in its event name, so a pull-request workflow spelled those ways reads as gating nothing; latent
status: untriaged
feature: required-check-trigger-reading
touches: tools/doc_check.py, tools/required_checks_check.py, tests/unit
added: 2026-10-04
---

**Problem.** doc_check's PULL_REQUEST_TRIGGER_RE misses a pull_request trigger written as a list entry, with a trailing comment or as a flow mapping, and required_checks_check keeps an on: line's trailing comment in its event name, so a pull-request workflow spelled those ways reads as gating nothing; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`doc_check`'s `PULL_REQUEST_TRIGGER_RE` (5349) misses `- pull_request`, `pull_request:  # comment` and `pull_request: {...}`. `required_checks_check._triggers` reads `on: pull_request  # every PR` as the event `pull_request  # every PR`, and `on: [push, pull_request]  # both` as `push` and `pull_request]  # both`. YAML 1.2.2 § 6.6. Not a member of `PL-R417`: each spelling sits on one line. With `PL-848V` it is the second item misreading which YAML spellings name a workflow's pull-request trigger, now across two tools; `PL-C72H`, the feature's other item, misreads GitHub's branch-filter semantics rather than a spelling. With `PL-4T49`, `PL-GWQ7` and `PL-S3XS` from the same sweep, it is a member of `PL-848V`, recorded as their head the same day. Latent: every `on:` in the six workflows is a bare block mapping.
