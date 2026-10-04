---
id: PL-GMR6
title: docket picks drops the plan walker's unread entries, so a gate entry the walker declines by name is left out of the pick list at exit 0, where docket wave names it and exits 1; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/picks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: the pick list says when a gate entry went unread, so it is never taken for the whole of what is left
verify: grep -q 'def test_picks_names_a_gate_entry_the_plan_walker_declines' subprojects/docket/tests/test_picks.py
---

**Problem.** docket picks drops the plan walker's unread entries, so a gate entry the walker declines by name is left out of the pick list at exit 0, where docket wave names it and exits 1; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`Wave.unread` carries the list walker's decline (`PL-MFVV`, `#1343`); `picks` (`#1345`, after it) builds a `Picks` with no field for it, and `cmd_picks` exits 0. With a gate entry whose bold lead wraps onto a lazy line, `plan.unread` names the line and the pick list simply lacks the entry. The decline reached `check`, `wave` and the digest and stopped there. Latent: `wave(ROADMAP.md).unread` is empty, and `doc_check` fails each such line in `make check`.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, with a gate entry of docket's `test_picks` fixture carried on from the margin, `wave` returns the line in `plan.unread`, and `picks` returns a `Picks` with no field for it, so `format_picks` says nothing of it.

**Why it matters.** `docket picks` is the what's-left list a report is built from, so a gate entry the plan walker declines is missing from it at exit 0, and the list reads as complete where `wave`, `check` and the digest each say a count may be short.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** `Picks` carries the plan's unread entries, `format_picks` names them as `format_wave` does, and `docket picks` exits 1 where any went unread; a test in `subprojects/docket/tests/test_picks.py` pins it.
