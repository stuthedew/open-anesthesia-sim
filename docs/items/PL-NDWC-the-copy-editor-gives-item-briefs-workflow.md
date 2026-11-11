---
id: PL-NDWC
title: The copy editor gives item briefs, workflow files, commit messages, pull request bodies and replies up to four reads and five rounds of meaning checks; the owner asked for at most two (2026-11-09)
priority: P2
effort: S
status: done
classes: session-cost
feature: copy-editor
milestone: v0.6.17
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

**Why it matters.** Each passage of an item brief or a reply that never
settles costs four copy-editor reads and up to five rounds of meaning checks.
On this branch's own close-out, 18 passages took about $5 of copy-editor and
meaning-check runs. The owner judged that the extra reads are not worth that
cost on text no clinician reads.

**The owner's rule.** At 18:26Z on 2026-11-09 the project owner asked: "Copy
edit non-core human documents like PL items etc at most twice". At 18:27Z, on
the decision card that put two readings of that request, the owner wrote: "I
want you to change repo rule". The card's option 0 was chosen: at most two
copy-editor reads and two rounds of meaning checks for those texts, with the
simulator documents unchanged. It was chosen over limiting only the copy-editor
reads and leaving the meaning checks at five rounds. The owner's request lifts
the workflow-lane pause for this change.

**Approach.** A passage's header names its readers after "For:", from the
table in `.claude/rules/plain-writing.md`. A passage whose readers are all
"A later session, or the owner reading the history" or "The project owner, an
anesthesiologist and intensive-care physician" gets at most two reads
(`LIMITED_READS = 2`) and two rounds of meaning checks
(`LIMITED_CHECK_ROUNDS = 2`). A passage with any other reader keeps the full
limits, so a request that mixes both kinds of passage still gives the simulator
text its third and fourth reads. A later read's rewrite of a limited passage is
not taken, and a loss that the second round of checks still finds keeps the
passage as it was. A test checks that the plain-writing table still names each
of those two readers, so renaming a row cannot silently give those texts the
full limits.

**Done when.** The two limits are in `tools/copy_edit.py` with tests, and
close-out step 8, `docs/prose-review/README.md` and `docs/apparatus.md` say what
the limits are.
