---
id: PL-4DK2
title: Item field predicates are respelt beside model and checks - a pr: number by isdigit in vcs and pr_body_check, a milestone's leading v four ways, a typed id in claiming._keys and cli, the top band in trend, the anticipated exemption, startable statuses and list splitting - and pr: 07, milestone: 0.4.1, k7qx and an untriaged P0 each read two ways
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/store.py, subprojects/docket/src/docket/trend.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_claiming.py, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_store.py, subprojects/docket/tests/test_trend.py, tools/doc_check.py, tools/pr_body_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-18
pr: 1582
payoff: an item's fields mean one thing to every command and check that reads them
verify: grep -q 'def test_a_lower_case_id_is_claimed_as_find_item_reads_it' subprojects/docket/tests/test_claiming.py
---

**Problem.** Item field predicates are respelt beside model and checks - a pr: number by isdigit in vcs and pr_body_check, a milestone's leading v four ways, a typed id in claiming._keys and cli, the top band in trend, the anticipated exemption, startable statuses and list splitting - and pr: 07, milestone: 0.4.1, k7qx and an untriaged P0 each read two ways

- A `pr:` number: `checks.PR_RE` (`^[1-9][0-9]*$`) beside `item.pr.isdigit()` in `vcs.closures_on_base` and `pr_body_check`. On `pr: 07` checks errors and the other two record `#7`; on `pr: ²` `isdigit` is true and the `int()` after it raises. `PL-FYV7` (ready) holds `verify.PR_VALUE_RE`, `RECURRENCE_ENTRY` and `RECORD_NAME_RE`.
- A milestone's leading `v`: `checks._check_cut_window` and `release.notes_name` strip it, `checks._check_release_notes` and `release.unreleased` do not. On `milestone: 0.4.1`, which `SEMVER_RE` accepts, the first two read `v0.4.1` and the release-notes check errors.
- A typed item reference: `store.find_item` and `cli._as_identifier` read `k7qx` as `PL-K7QX`; `claiming._keys` refuses it as no item id, and `cli._say_held_elsewhere` keys on `K7QX`.
- The top band: `checks._top_band` leaves untriaged items out; `trend.analyze` counts them and falls back to `P1`. An untriaged `P0` beside ready `P1` items gives `P1` and `P0`.
- Agreeing copies: the anticipated-and-blocked exemption (`checks._check_item`, `doc_check`'s `ANTICIPATED_CLASS` and `BLOCKED_STATUS`, whose comment says it reads from checks), startable statuses (`cli.cmd_show`, `plan._unseated_by`) and list splitting (`cli._comma_separated`, `model._split_list`).

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** Each predicate lives once in `docket.model`, `store` or `checks`, the others call it, and a test pins each parting input.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.

**Closed 2026-10-18.** Each predicate now has one home, and the old sites call it: `model.pr_number` (checks, `vcs.closures_on_base`, `tools/pr_body_check.py`), `release.tag_name` for a milestone (`checks._check_cut_window`, `checks._check_release_notes`, `release.unreleased`, `release.unrecorded_milestones`), `store.as_identifier` (`find_item`, `claiming._keys`, `cli._say_held_elsewhere`, `cmd_withdraw`), `model.top_band` (`checks`, `trend.analyze`), `Item.waits_anticipated` (checks, `tools/doc_check.py`), `Item.is_startable` (`cli.cmd_show`, `plan._unseated_by`) and `model.split_list` (model, cli, verify). The sweep also found a fifth milestone reading: the cut-window advisory looked the notes up by the bare version while `notes_by_version` keys them `v0.3.8`, so it never found the cut's own notes. It now asks by tag name, and the tests' helper keys the notes as `notes_by_version` does.
