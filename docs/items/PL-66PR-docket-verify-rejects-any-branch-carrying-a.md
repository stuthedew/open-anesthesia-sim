---
id: PL-66PR
title: docket verify REJECTs any branch carrying a capture, because item_commits matches the leading id CLAUDE.md requires on every commit subject and only the item's own file is exempt from the touches audit; a new untriaged item file is mechanically distinguishable and could be exempted the same way
priority: P2
effort: S
status: done
classes: defect, infra
feature: delegation
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-07
closed: 2026-09-12
verify: uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_a_capture_committed_on_the_branch_is_not_outside_touches' subprojects/docket/tests/test_verify.py
---

**Problem.** docket verify REJECTs any branch carrying a capture, because item_commits matches the leading id CLAUDE.md requires on every commit subject and only the item's own file is exempt from the touches audit; a new untriaged item file is mechanically distinguishable and could be exempted the same way

**Why it matters.** `CLAUDE.md` requires every commit subject to lead with the
current item's id, and it requires a finding not fixed in the session to be
captured before the session ends. Following both puts a capture commit on the
branch whose subject carries the item's id, so `item_commits` attributes the new
item file to the item being verified, and the `touches` audit reports it as
outside the commission. The result is `REJECT` on a branch that did exactly what
the instructions asked.

It is the same shape as `PL-ZYQC` and lands on the same audit: a check that
fires on correct work, cannot distinguish it from the thing it exists to catch,
and so trains a reader to skim a `REJECT` - which `CLAUDE.md` names as the
failure mode a check must not have. The two differ only in which sanctioned edit
they refuse, and the fix for one should be shaped so it covers the other.

**Done when.** A branch carrying a capture - a new item file at `status:
untriaged`, added by a commit whose subject leads with the item being verified -
passes the `touches` audit, while an edit to an existing item the branch does
not own still fails it, with a test for each.
