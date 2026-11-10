---
id: PL-XSRG
title: A pull request that edits or deletes an existing line of a published-data test under tests/reference/ merges on green when its session records that no owner's read is needed: bin/docket arm does not hold it
priority: P2
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py, .claude/skills/pull-request/SKILL.md
deferred-from: v0.7.0 - found by the 2026-11-10 audit after the freeze; apparatus, and it changes no displayed value, so the release does not wait on it
added: 2026-11-10
payoff: a widened tolerance or a changed expected value in a published-data test reaches the owner before it merges
verify: grep -q 'def test_an_edited_reference_test_holds_for_the_owner' subprojects/docket/tests/test_arming.py
reenters: PL-4W2L
---

**Problem.** A pull request that edits or deletes an existing line of a published-data test under tests/reference/ merges on green when its session records that no owner's read is needed: bin/docket arm does not hold it

**Checked 2026-11-10:** `compared` in `tools/diff_mutation.py` measures changed tests under `tests/unit/` only. For any other changed test file it appends the note "Not measured: whether N changed test files outside tests/unit/ still catch what they caught before". `.claude/skills/pull-request/SKILL.md` says of the owner's read: "Which one a change is stays your call. Record it as an `Owner-read:` trailer". `PL-G21K` and `PL-4W2L` (whether a branch's diff weakens its tests) closed on 2026-09-20 and 2026-09-23, and the check they built was later replaced by `tools/diff_mutation.py`, which runs when a session runs `bin/docket verify --self`.

**Why it matters.** `tests/reference/` compares the model with published data. A branch that widens a tolerance there, or changes an expected value, passes every check and merges on green when its session writes that no read is needed. That is the one place where a weakened test hides a wrong clinical value.

**The pause on new workflow mechanisms.** The project owner lifted it for this item on 2026-11-10.

**Done when.** `bin/docket arm` answers `hold` for a branch whose diff edits or deletes an existing line of a file under `tests/reference/`, whatever its `Owner-read:` trailer says, until the record says the owner has read it. A branch that only adds lines there is answered as before. `subprojects/docket/tests/test_arming.py` pins both answers.

**Generator check.** An instance of the fact `PL-G21K` and `PL-4W2L` state, filed after `PL-4W2L` closed on 2026-09-23: the mechanism that replaced their check does not reach `tests/reference/`.
