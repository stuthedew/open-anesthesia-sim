---
id: PL-KYTY
title: Make every question or read ask put to the owner obvious on first reading, with annotated screenshots of each option for an interface choice
priority: P2
effort: S
status: done
classes: docs
feature: owner-attention
touches: .claude/rules/instruction-writing.md, .claude/skills/run-the-app/SKILL.md, docs/maintainer.md, docs/resident-instructions.md, subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py
added: 2026-10-19
closed: 2026-10-19
pr: 1654
payoff: the owner sees on first reading what each question asks them to judge, and sees each interface option side by side, so no ask needs a second round
verify: grep -q 'what they are judging' .claude/rules/instruction-writing.md && grep -q 'Compare interface approaches for the owner' .claude/skills/run-the-app/SKILL.md && grep -q 'def test_arm_read_ask_asks_in_learner_terms_with_screenshots' subprojects/docket/tests/test_cli.py
---

**Problem.** Make every question or read ask put to the owner obvious on first reading, with annotated screenshots of each option for an interface choice

**Why it matters.** On 2026-10-19 the owner had to ask twice what they were
being asked to judge on `#1650` (`PL-L59K`, the chart time-window notes). The
first ask named the change in the code's terms: notes now describe "their own
chart's window". It did not say what a learner would see under each answer.
What worked in the end was one concrete run (8% sevoflurane for 10 minutes,
then 0% for 25), one screenshot per option, and the question in one sentence.
Every unclear ask costs the owner a round trip and holds a pull request while
it waits.

The project owner's rule, 2026-10-19, in their words: "I don't want to have to
ask for clarification every time. Can it make it obvious in the future? And
any time it's a UI question about different approaches, I want screenshots
(annotated if possible) for comparison."

The owner added a second rule the same day, after a workflow thread asked them
directly what to work on next: "It shouldn't be asking me directly. It should
be asking you and if you have questions then ask me." A session running under
a coordinator sends such a question to the coordinator. The coordinator
decides it, or brings the owner only a real decision.

**Done when.** The rule is written where sessions write their asks, and the
tooling's own ask text agrees with it:

- `.claude/rules/instruction-writing.md` rule 10 says that a question or read
  ask put to the owner makes plain on first reading what they are judging. It
  is worded in clinical or learner terms, says what a learner sees under each
  option, gives a recommendation, and says why the choice is the owner's. An
  ask about different approaches to the interface carries one screenshot per
  option, annotated where the options differ.
- The same rule says that a session running under a coordinator sends a
  question the coordinator can answer to the coordinator, never to the owner.
- `.claude/skills/run-the-app/SKILL.md` has a tested procedure for rendering
  those captures from the branch and annotating them.
- The `READ_ASK` text that `bin/docket arm` prints asks for the same things,
  and a new arm test pins the added parts.

**Generator check.** Work the owner asked for. It is related to `PL-9KHK` and
`PL-DKBG`, which made the read ask name something to judge at all. This item
is about how plainly the ask says it, so it is not a re-entry of either.
