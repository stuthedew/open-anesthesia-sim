---
id: PL-M21Q
title: A needs-decision item carries the question but not the recommendation, so a session's recommendation lives only in a reply and cannot be agreed with once that session's branch is deleted
priority: P2
effort: M
status: ready
classes: defect, docs
touches: .claude/skills/docket/SKILL.md, .claude/rules/instruction-writing.md, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-16
verify: python3 tools/doc_check.py check && grep -rqF 'record the recommendation in the item, not only in the reply' .claude/skills/docket/
---

**Problem.** A needs-decision item carries the question but not the recommendation, so a session's recommendation lives only in a reply and cannot be agreed with once that session's branch is deleted

**Found 2026-09-16**, while acting on the project owner's "agree with the
`doc_check` safety check session's recommendation for `PL-KQHN`".

**What happened.** `PL-KQHN`'s brief carried a `**Decision needed.**` naming
both answers and no recommendation. The recommendation existed only in the
`doc_check` safety-class gate advisory session's reply
(`session_01G4NBvRm2Cbq1UW5BEQjwBL`). By the time the owner agreed with it, that
session's branch `claude/doc-check-safety-gate-advisory-gmspbu` had been deleted
with `#636`'s merge, the session was in a different container, and `ListAgents`
reached no cross-session channel to it. The only surviving carrier was the
harness-written `post_turn_summary.needs_action` line - *"decide `PL-KQHN`:
withhold number + fix prose or keep mechanism"* - which names the two options
and marks neither as the recommendation.

**The answering session had to reconstruct it**, from the order of the two
options in that line, the direction `#606` had already moved the apparatus, the
item's own `Done when.` ordering, and the merits. The reconstruction was
recorded in the item so it could be corrected rather than inherited silently,
which is the mitigation and not a fix: a decision of record about the release
train rested on a reading of another model's compressed prose.

**The rule this is an instance of already exists and does not cover it.** Rule
14 of `.claude/rules/instruction-writing.md` says the closing block "is a
handover, not a store", and that "a line that could reasonably outlive this
sitting is `bin/docket new` as well". That prescribes filing a *new* item. Here
the item already existed, and what was missing was one paragraph *inside* it.
`bin/docket new` is the wrong instrument and the rule names no other.

`.claude/skills/docket/SKILL.md`'s triage mode has the same gap, one step
earlier: "put the direction half in the reply with a recommendation and leave
the item open" says the reply, and not also the brief.

**Why it matters.** `needs-decision` is the status the queue uses to route a
question to the owner, and `bin/docket gate` counts it as debt somebody can
resolve. The reply that put the question is the only place the recommendation
lives, and a reply is deleted with its session while the item persists - so the
longer an item waits, the likelier the recommendation is gone when the answer
arrives. That is backwards: waiting is what `needs-decision` is for.

**A decidable part exists.** Whether a `needs-decision` brief carries a
recommendation is answerable by reading the file, which puts it in
`CLAUDE.md`'s deterministic-tooling territory rather than in prose alone. An
advisory in `bin/docket check` - a `needs-decision` item whose brief states a
`**Decision needed.**` and names no recommendation - would fire where the gap
is, on the item, rather than where the rule is written. Whether the sentence is
a *good* recommendation is the judgment half and is not scriptable, which is
the line `CLAUDE.md` draws.

**Done when.** A `needs-decision` item's brief carries the recommending
session's recommendation, in its own words, alongside the question; the rule
that says so is written where a session acts on it - `.claude/skills/docket/`'s
triage mode, and rule 14's handover bullet, which currently routes only to
`bin/docket new`; and `bin/docket check` advises on a `needs-decision` brief
that poses a decision and recommends nothing.

**Not decided here:** whether the advisory is worth building at all is
`CLAUDE.md`'s "will it genuinely run again" gate, and the count that answers it
is how many of the store's open `needs-decision` items already carry a
recommendation. Run that count before building anything.

**Why it matters.** `needs-decision` is the status that routes a question to the
project owner, and `bin/docket gate` counts it as debt somebody can resolve. The
recommendation that would let them resolve it in one read lives only in the reply
that posed it, and a reply dies with its session while the item persists - so the
longer an item waits, the likelier the recommendation is gone when the answer
arrives. That is backwards, because waiting is what the status is for. The cost
is already on the record: `PL-KQHN`'s answer had to be reconstructed from a
harness-written summary line naming two options and marking neither, and a
decision about the release train rested on a reading of another model's
compressed prose.

**Done when** the rule is written where a session acts on it - the `docket`
skill's triage mode, and rule 14's handover bullet in
`.claude/rules/instruction-writing.md`, which today routes only to `bin/docket
new` - and a `needs-decision` brief carries the recommending session's
recommendation in its own words beside the question. Run the count the brief
asks for *first*: how many of the store's open `needs-decision` items already
carry one. The advisory in `bin/docket check` is built only if that count says it
would fire on a real population, per `CLAUDE.md`'s "where the benefit is unclear,
the answer is no"; the rule half lands either way, which is what the `verify:`
command pins.
