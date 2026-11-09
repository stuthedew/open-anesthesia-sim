---
id: PL-NDWC
title: The copy editor gives item briefs, workflow files, commit messages, pull request bodies and replies up to four reads and five rounds of meaning checks; the owner asked for at most two (2026-11-09)
priority: P2
effort: S
status: done
classes: workflow
feature: copy-editor
touches: tools/copy_edit.py, tests/unit/test_copy_edit.py, .claude/skills/docket/modes/close-out.md, docs/prose-review/README.md, docs/apparatus.md
added: 2026-11-09
closed: 2026-11-09
pr: 2073
payoff: an item brief or a reply costs at most two copy-editor reads and two rounds of meaning checks, while the simulator documents keep their four reads and five rounds
verify: grep -qF 'LIMITED_READS = 2' tools/copy_edit.py && grep -qF 'LIMITED_CHECK_ROUNDS = 2' tools/copy_edit.py
---

**Problem.** `tools/copy_edit.py` gives every passage up to four copy-editor
reads (`MAX_READS`) and up to five rounds of meaning checks
(`MAX_CHECK_ROUNDS`), whatever the passage is. Those limits were set on
`docs/MODEL.md`, whose readers are clinicians. An item brief, a workflow file, a
commit message, a pull request body or a reply is read by a later session or by
the owner, and each extra read costs about as much as the first.

**The owner's rule** (project owner, 2026-11-09, 18:26Z: "Copy edit non-core
human documents like PL items etc at most twice"; 18:27Z, on the decision card
that put two readings of it: "I want you to change repo rule"). The card's
option 0 was chosen: at most two copy-editor reads and two rounds of meaning
checks for those texts, with the simulator documents unchanged. It was chosen
over limiting only the copy-editor reads and leaving the meaning checks at five
rounds. This request lifts the workflow-lane pause for this change.

**Approach.** A passage's header names its readers after "For:", from the
table in `.claude/rules/plain-writing.md`. A passage whose readers are all
"A later session, or the owner reading the history" or "The project owner, an
anesthesiologist and intensive-care physician" gets `LIMITED_READS = 2` and
`LIMITED_CHECK_ROUNDS = 2`. Any passage with another reader keeps the full
limits, so a request that mixes the two still gives the simulator text its
third and fourth reads. A later read's rewrite of a limited passage is not
taken, and a loss the second check round still finds keeps the passage as it
was. A test holds each limited reader name to a row of the plain-writing table,
so a renamed row cannot silently give those texts the full limits.

**Done when.** The two limits are in `tools/copy_edit.py` with tests, and
close-out step 8, `docs/prose-review/README.md` and `docs/apparatus.md` say what
the limits are.
