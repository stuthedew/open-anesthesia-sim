---
id: PL-JNWS
title: bin/docket next named PL-4ZK8 first among open decisions for three days after the owner answered it on 2026-09-27, because the design round left the status write to the build thread and nothing reads an Answered marker against a needs-decision front matter
priority: P2
effort: S
status: ready
classes: defect, infra
feature: brief-state-agreement
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md, .claude/skills/docket/modes/triage.md, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed as it was started, 2026-09-30
added: 2026-09-30
payoff: a decision the owner has answered stops being offered to them as still waiting, because the commit that records the answer has to move the item's status with it
verify: grep -q 'def test_an_answer_beneath_the_last_question_refuses_needs_decision' subprojects/docket/tests/test_checks.py && grep -q 'def test_a_question_posed_beneath_the_answer_keeps_needs_decision' subprojects/docket/tests/test_checks.py
---

**Problem.** bin/docket next named PL-4ZK8 first among open decisions for three days after the owner answered it on 2026-09-27, because the design round left the status write to the build thread and nothing reads an Answered marker against a needs-decision front matter

**Measured, 2026-09-30.** Replaying `main`'s first-parent history over every
commit that touched `docs/items/`, 17 items sat at `needs-decision` after an
answer had been recorded beneath their last question, from `PL-FDBK` on
2026-09-13 to `PL-4ZK8`: 16 of them for between 12 minutes and 12.5 hours,
while the work their answers called for landed, and `PL-4ZK8` for 72. Every
one of the 17 later moved off `needs-decision` - 11 closed as `done`, 1
`dropped`, 3 to `ready`, 2 to `blocked` - and none gained a new question
first, so in each the front matter was simply behind the brief. The fault reproduces on today's
checker: `analyze` on `PL-4ZK8` as `main` held it on 2026-09-28 (`8fb2012e`),
at `needs-decision` with `**Answered 2026-09-27: Q1 ratified**` beneath its
question, raises no error and no advisory about the decision. Today none of the
33 open `needs-decision` items carries an answer label, so a rule landing now
fires on nothing already in the store.

**Why it matters.** Every reader of the queue takes an item's state from the
front matter: `bin/docket next`'s "Waiting on a decision" line, `bin/docket
gate`'s debt count, and `docket verify`'s `falsifies:` fold, which reads
`needs-decision` on the base's copy as the standing statement that the answer
is still the closing session's to make. So while the brief and the front matter
disagree, the owner is asked again for an answer already given, and a build
session is told a decision is its own that the owner has already made.
`PL-8YXJ` made the brief follow the front matter; nothing makes the front
matter follow the brief, and a recorded answer is the one brief edit that
changes the item's state.

**The approach, and what it was chosen over.** `docket check` refuses the
state: an open item at `needs-decision` whose brief records an answer beneath
its last question is an error, so the commit that records the answer moves the
status with it - `ready`, `blocked`, or closed - and `docket set` refuses the
write that would put an answered item back. What a brief still asks is read
from the labels the store already prescribes, in position order: an answer is
a label opening `Answered`, `Answers`, `Decided` or `Question N is answered`
(`docs/worker.md` names all three shapes, and `.claude/skills/docket/modes/triage.md`
the first), or a heading opening `Answered` or `Answers`; a question is a
`**Decision needed.**` heading, a design round's numbered `Q1.` or its
heading, or a marked recommendation, which is a question put to the owner. A
brief whose last such label is a question is still waiting whatever came
before it, and a question still open beneath a partial answer is restated
beneath it, which is what a reader of the bottom of the brief needs anyway.
Quoted, code-span, fenced and superseded labels are not the brief's own claim
and are not read, the rule `_standing` already applies.

- *Refused: an advisory.* The design round that left `PL-4ZK8` at
  `needs-decision` did so on purpose ("The thread that builds it sets this
  item's status"), so an advisory would have printed beside a choice already
  made. It is an error because the rule is exact on the labels: 0 of the 17
  historical firings was an item still genuinely waiting, and `PL-J2TD`, the
  one answered item that did still wait - on the narrowing its own answer
  recommended - is not reached, since its last label is that recommendation.
- *Refused: have `next` read the answer.* It would patch one reader and leave
  `gate`, `list`, `show` and the `falsifies:` fold reading the stale copy,
  which is the head-per-reader altitude `PL-5MYR` names.
- *The cost, accepted:* a session recording an answer that leaves real work
  now shapes the item for `ready` in the same commit - its `verify:` run and
  seen failing, its Done-when in the decided form - where the design round
  used to hand that to the build thread. That work was owed before the close
  in any case, and `PL-4ZK8`'s re-confirm did it in one pass.

**Done when.** `bin/docket check` errors on an open `needs-decision` item whose
last decision label is an answer, quoting the label and naming the ways out,
and `docket set` therefore refuses writing `needs-decision` onto one; a
question posed beneath the answer, a recommendation standing after it, and an
answer that is quoted, in a code span, fenced or superseded all leave the item
legal; `.claude/skills/docket/modes/triage.md`'s answer-recording paragraph
says the status moves in the same commit, `subprojects/docket/README.md` states
the rule beside `**Decision needed.**`'s, and the `needs-decision` rule
`bin/docket triage` prints carries it; and the two tests `verify:` names pin
the refusal and the question-beneath-the-answer case.

**Generator check.** The fact misread is an item's current queue state, held
twice - in the front matter and narrated in the brief - where a write moved
only one copy: here the brief moved and the front matter did not. `PL-8YXJ`'s
`misread:` states that fact, and it closed on 2026-09-23 having covered only
the other direction, a status write leaving the brief's narration behind. So
this is an instance of `PL-8YXJ`'s fact filed after the head closed, recorded
in its `root-cause-of:`; one post-close instance, not three, so the head
stays `spent`, with its verdict naming both directions once this lands.
