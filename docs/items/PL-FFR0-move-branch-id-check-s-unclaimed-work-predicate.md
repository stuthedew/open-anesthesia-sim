---
id: PL-FFR0
title: Move branch_id_check's unclaimed-work predicate into claims.py once PL-N162's unclaimed: row lands, so the CI refusal and flight's row read one definition of a work branch that claims nothing
status: done
feature: claim-record
milestone: v0.5.11
touches: subprojects/docket/src/docket/claims.py, tools/branch_id_check.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py
added: 2026-09-24
closed: 2026-09-24
pr: 1002
verify: grep -qF 'def claims_nothing' subprojects/docket/src/docket/claims.py && grep -qF 'claims_nothing,' tools/branch_id_check.py && ! grep -qE '^def (in_queue|_work_under_record|claims_here)\b' tools/branch_id_check.py && grep -qF 'unclaimed(inv.root' subprojects/docket/src/docket/cli.py
---

**Problem.** Move branch_id_check's unclaimed-work predicate into claims.py once PL-N162's unclaimed: row lands, so the CI refusal and flight's row read one definition of a work branch that claims nothing

**Why.** `PL-J9S0` (#991) built the refusal of a work branch that claims nothing inside `tools/branch_id_check.py` - `claims_here`, `in_queue` and `_work_under_record` - because `claims.py` was being reshaped by `PL-N162` at the same hour. `PL-N162` adds `flight`'s `unclaimed:` row, which asks the same question. Two spellings of one question are two answers waiting to disagree, and the design round's pre-registered 1-in-20 threshold is counted from that row, while CI refuses on the tool's copy.

**The definition both must share**, recorded in `PL-J9S0`: a `claude/` branch with a non-merge commit whose own tree carries `CUTOVER_MARKER` and which changes a path outside the queue (the items, `roadmap_file` and `notes_file`), and no non-legacy claim bound to it in any state, and no item id in its name.

**Done when.** One function in `claims.py` answers it, `branch_id_check` imports it, and `flight`'s `unclaimed:` row reads the same function.
