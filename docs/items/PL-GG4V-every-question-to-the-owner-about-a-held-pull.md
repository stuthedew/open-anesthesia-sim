---
id: PL-GG4V
title: Every question to the owner about a held pull request lacks part of what the asking rule requires: the review form has no recommendation, no trade-off and no options, and the decision form has no context and no reason the choice is the owner's (2026-11-14): make one form that carries all of them, question and recommendation first
priority: P2
effort: S
status: done
classes: defect, ux
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py, subprojects/docket/tests/test_cli.py, tests/unit/test_owner_ask_guard.py, docs/maintainer.md, .claude/skills/docket/modes/coordinator.md
deferred-from: v0.7.0 - workflow tooling outside the schematic release, and it changes no displayed value
added: 2026-11-14
closed: 2026-11-14
pr: 2146
payoff: every question the owner is sent about a held pull request carries its options, a recommendation with the cost of the alternative, its context and why it is theirs, so they can answer it in one read
verify: grep -q 'def test_a_held_pull_request_is_asked_between_the_change_and_what_it_replaced' subprojects/docket/tests/test_arming.py
---

**Problem.** Every question to the owner about a held pull request lacks part of what the asking rule requires: the review form has no recommendation, no trade-off and no options, and the decision form has no context and no reason the choice is the owner's (2026-11-14): make one form that carries all of them, question and recommendation first

**Why it matters.** Every held pull request reaches the owner through this record, and a question without its options, recommendation and cost cannot be answered in one read. The owner has now had to correct the asks six times, one element at a time.

## What the owner said

On 2026-11-14, answering the review question for #2146 (`PL-M2JP`, one
line per part), the owner wrote: "I like the format better but you are still
asking me to make decisions without any context, recommendations, trade offs
etc which you should not do. See instructions about asking me questions."

The question they were sent was "Is this layout easier to follow than the
single paragraph you were sent on pull request 2096?", with no
recommendation, no alternative and no cost of either answer.

## Cause

Rule 10 of `.claude/rules/instruction-writing.md` requires every question,
card and read ask to carry: the question in clinical or learner terms; what
each option changes for the owner or a learner; the recommendation and its
reason; and why the choice is the owner's. The question opens the message,
with the recommendation next, and supporting detail follows.

The `Owner-ask` record grammar in `subprojects/docket/src/docket/arming.py`
enforces only part of that, and differently in each form:

- The review form (`changed | question | why | checked | reply`) has no
  options, no recommendation and no trade-off.
- The decision form (`question? | option: change | option: change |
  recommend option - why`) has no context and no reason the choice is the
  owner's.

What the grammar does not require, sessions leave out. This is the same
mechanism as `PL-9KHK`, `PL-DKBG`, `PL-KYTY`, `PL-BGN1`, `PL-77QB` and
`PL-M2JP`: each added one element of rule 10 to the record after the owner
found it missing. This item makes the grammar require every element at once.

## Design (session's choice, 2026-11-14)

One form for every question to the owner. A merge review becomes a decision
whose options are merging and holding for changes:

`<question>? | <option>: <what it changes for the owner or a learner> |
<option>: <what it changes> | recommend <option> - <why, and what the other
options cost> | context - <what changed, or what the choice is about> | why -
<why it is the owner's> | checked - <what was already checked>`

- At least two options, as now. `checked` is optional, since a choice between
  interface approaches may have nothing checked. All other fields are
  required.
- It renders question first, recommendation second, as rule 10 orders it,
  then context, the options, why it is yours and what was checked, one part
  per line as `PL-M2JP` laid out. Example:

  ```
  May this merge?
  - I recommend "Merge": the layout is the one you asked for, and holding it keeps the old paragraph in every question until it lands.
  - What changed: each part of a question to you prints on its own line, and every question now carries options, a recommendation and why it is yours.
  - Option "Merge": every later question reaches you in this layout.
  - Option "Hold for changes": questions keep the old paragraph until the change you name is made.
  - Why it is yours: it edits the tests that fix what the merge gate prints, which only you approve.
  - Already checked: the gate's and the hook's tests pass with this layout pinned.
  ```
- The `reply` field goes: the option labels say what to reply.
- A record in either current form, or in the older `risk`, `checked` and
  `look` form, is refused, and the refusal names the new form. A branch
  carrying one is affected only once it brings in `main`.
- Order: `PL-BGN1` (2026-11-02) led the review form with what changed. Rule
  10 puts the question and the recommendation first, and the owner pointed
  at the asking rules. The question is one clause and context follows on the
  next line, so it is read in context. Placeholder: reversible in one
  template if the owner prefers context first.

## Work

- `arming.py`: one grammar and renderer for `OWNER_ASK`, `READ_ASK`
  rewritten as one form, `ASK_LINE` unchanged in substance.
- Tests: `subprojects/docket/tests/test_arming.py`,
  `subprojects/docket/tests/test_cli.py` (the parse table and the pinned
  `test_arm_*` texts), `tests/unit/test_owner_ask_guard.py`.
- Docs: `docs/maintainer.md` § on how a hold comes to the owner,
  `.claude/skills/docket/modes/coordinator.md` ("in its decision or review
  form").
- Lands on the same pull request as `PL-M2JP`, #2146, because it changes the
  same template and the same pinned tests, and #2146 already waits on the
  owner's read.

## Second round (2026-11-14)

Shown the built form, the owner agreed to the order, recommendation first
("Agree with recommended first"), and found the next gap: "it doens't really
explain trade offs? Just why one is good and one is bad. So why wouod I ever
choose the bad". Each option said only what it did, and the recommendation
said only what the others cost, so nothing asked what the recommended option
gives up or what the alternative gains. Every option now carries
`<what it gets>; cost: <what it gives up>`, and the recommendation says why
its gain is worth its cost. An option without a cost is refused. Whether a
cost is honest, rather than a straw man, stays judgment, which the printed
instructions ask for.

## Third round (2026-11-14): a merge approval is not a choice

Shown the merge question with a cost on each option, the owner wrote: "I
still don't understand the pro of the non-recommended option. I'm assuming
that if you're asking then their is a trade off, but no pro is mentioned for
other option". They were right. "Hold for changes" has no gain of its own
unless the owner already has a change in mind, so a form that requires two
options with a gain each makes a session invent one for every merge approval.
That is the straw man the second round tried to rule out.

**Proposed (session's, 2026-11-14), and refused.** A separate approval form
for a held pull request: no options, and a line saying what the owner accepts
by approving.

## Fourth round (2026-11-14): every question is a choice

The owner refused the approval form: "I don't like that distinction An
approval is a choice with trade offs otherwise you wouldn't be asking me to
decide. [...] I don't find "approval" questions useful. because it seems like
you are asking me for a rubber stamp. So either you shouldn't be asking me in
the first place because it's not a real question, or you need to tell me what
I need to make an informed decision." Their examples of a real trade-off were
a session recommending a deviation from what they asked for, and a requested
feature that needs a large refactor.

**Decision (project owner, 2026-11-14).** No approval form. Every question
is a choice, and each option has a gain the owner can name. For a held pull
request, the options are the change and what it was chosen over: what the
owner asked for, the behavior it replaces, a smaller version, or the larger
rework it would need. Merging against holding for changes is never offered. A
session that cannot say what the option it does not recommend gains does not
ask. For a change to a test that pins the gate's answers, the options are the
gate as changed and the gate as it was.

What was built: the printed instructions, the refusal of an old review form,
`docs/maintainer.md` and the coordinator mode say this, and the examples in
the tests offer real alternatives in place of merging and holding. The record
form from the second round is unchanged. One case is left: a change to the
merge gate that has nothing to weigh still waits on the owner. Whether that
hold stays is filed as `PL-TQHT`, with options and a recommendation.

**Generator check.** The mechanism is that the `Owner-ask` grammar enforces only part of rule 10, so each missing element is left out until the owner notices it. It caused `PL-9KHK`, `PL-DKBG`, `PL-KYTY`, `PL-BGN1`, `PL-77QB` and `PL-M2JP`, all closed. This item removes the mechanism by making the grammar require every element rule 10 names, and no open item remains under it.

**Done when.** `bin/docket arm` refuses an `Owner-ask` record that lacks
options, a recommendation, context or the reason the choice is the owner's,
and prints an accepted one question first and recommendation second, each
part on its own line, pinned by a test.
