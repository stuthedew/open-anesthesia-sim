---
id: PL-M2JP
title: The question a session sends the owner about a held pull request prints as one unbroken paragraph of four labelled parts, and the owner found it dense and hard to follow (2026-11-10): print each part on its own line, and keep the question to one clause
priority: P2
effort: S
status: done
classes: defect, ux
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py, subprojects/docket/tests/test_cli.py, .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py, docs/maintainer.md
deferred-from: v0.7.0 - workflow tooling outside the schematic release, and it changes no displayed value
added: 2026-11-11
closed: 2026-11-14
pr: 2146
payoff: the owner reads a held pull request's question once and can answer it
verify: grep -q 'def test_a_review_question_prints_each_part_on_its_own_line' subprojects/docket/tests/test_arming.py
---

**Problem.** The question a session sends the owner about a held pull request prints as one unbroken paragraph of four labelled parts, and the owner found it dense and hard to follow (2026-11-10): print each part on its own line, and keep the question to one clause

## What the owner saw

On 2026-11-10 the owner was sent this as the one line of a reply's closing
block, on pull request 2096, and asked "Is this a new prompt style from you?
It's a little dense and hard to follow":

> What changed: after a pull request merges, a session is now told to push
> plainly and never to force the push, and a pull request that waits on you is
> released only once a session has written the date and your words into the
> branch. Question for you: both parts follow the design you agreed to before
> it was built, so nothing new needs deciding, and it is yours because it
> changes the rule that decides what merges without you: merge it? Already
> checked: the full test suite and the close-out audit pass, and each new test
> failed before its fix. What to reply: Merge it, or say what to change.

Two causes, and both are in `subprojects/docket/src/docket/arming.py`:

1. `ASK_REVIEW_SHOWN` joins the four parts into one paragraph, and the
   printed instructions tell the session to repeat the line word for word.
   `ASK_DECISION_SHOWN` joins a decision's options the same way.
2. The printed instructions ask the question field to carry three things: the
   yes-or-no question, why it is the owner's, and, where nothing needs
   deciding, a statement that nothing does. The session wrote all three into
   one sentence.

A fix would print each part on its own line, and move "why it is yours" and
"nothing new needs deciding" out of the question into a part of their own or
drop them. The stored trailer can stay one line.

**Why it matters.** This question is how a held pull request reaches the owner, and every held pull request sends one. A question the owner has to read twice slows each merge decision, and `.claude/rules/plain-writing.md` asks that the owner understand each sentence the first time.

**Done when.** `bin/docket arm` prints a held pull request's question with each labelled part on its own line, the question part asks one yes-or-no question in one clause, and a test in `subprojects/docket/tests/test_arming.py` pins that layout.

**Generator check.** A one-off: one template constant joins the parts. No head's `misread:` states how a question to the owner is laid out.
