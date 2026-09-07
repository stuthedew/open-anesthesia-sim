---
id: PL-LLDB
title: PL-T691's verify command requires class RunHistory to be gone from src/, which the item's own Out of scope assigns to PL-2FM6, so PL-T691 can never satisfy it
priority: P2
effort: S
status: dropped
classes: defect, infra
feature: dev-tooling
touches: docs/items
added: 2026-09-07
closed: 2026-09-07
reason: PL-T691 closed 2026-09-07 (pr 430) already carrying the paired-shape command this item asked for - a grep for `def test_evaluate_matches_a_stepped_run` in tests/unit/test_run_score.py, which names a test PL-T691 itself adds and does not depend on PL-2FM6's deletion of RunHistory (PL-2FM6 is still open and the class is live at controller.py line 260). The Done when is met, and a closed item's verify is a record docket check refuses to rewrite.
---

**Problem.** `PL-T691` (hold the run as a score plus keyframes) carries

    verify: uv run pytest -q tests/unit tests/integration && ! grep -rq 'class RunHistory' src/anesthesia_sim/

while its own **Out of scope** says "Deleting `RunHistory` and re-pointing the
chart is `PL-2FM6`." The command therefore proves `PL-2FM6`'s work rather
than `PL-T691`'s, and the queue orders that deletion after this item — so the
command cannot pass at the moment `PL-T691` is finished, and a session working
it to the item's own definition of done will find its `verify:` red.

This item is a repair to `PL-T691`'s `verify:` field and can be made at any
time; nothing here waits on either of them.

**Why it matters.** It is the failure mode the `docket` skill's `verify:`
section describes — a command written away from the work it is meant to prove —
reached from the other direction. The skill's existing guards do not catch this
one: `docket check --verify` raises an advisory for a command that *passes* on a
tree without the work, and this one correctly fails; nothing checks that it
fails for the item's *own* reason. The consequence is that whichever session
finishes `PL-T691` either widens the item into `PL-2FM6` to make its gate go
green, or edits the command at the moment of closing, which is exactly when the
skill says a command is least trustworthy.

**Where.** `docs/items/PL-T691-the-run-is-its-control-input-timeline.md`, the
`verify:` field. The repair is the paired shape the skill prescribes: the suite
that must stay green, and a `grep` for the entry point `PL-T691` actually adds —
its "public `evaluate`-shaped entry point" — rather than for the absence of a
class another item deletes.

**Done when.** `PL-T691`'s `verify:` names something `PL-T691` itself delivers,
was run before the work and observed to fail for that reason, and passes on the
finished branch without any of `PL-2FM6`'s deletions.
