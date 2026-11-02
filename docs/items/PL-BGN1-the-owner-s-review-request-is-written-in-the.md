---
id: PL-BGN1
title: The owner's review request is written in the repository's shorthand ("a pinned test of the owner-ask guard changes, so a relayed ask could be refused"), because the plain-writing rule names replies but not review requests or the Risk to review / Checked template bin/docket arm prints
priority: P2
effort: S
status: done
classes: infra
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_arming.py, tests/unit/test_owner_ask_guard.py, .claude/rules/plain-writing.md, .claude/skills/docket/modes/coordinator.md, docs/maintainer.md
added: 2026-11-02
closed: 2026-11-02
pr: 1946
payoff: a review request tells the owner in plain words what changed, asks one question they can decide, and says what to reply, so they can answer it without decoding the repository's vocabulary
verify: grep -q 'def test_arm_ask_is_written_in_plain_words_for_the_owner' subprojects/docket/tests/test_cli.py && ! grep -q 'Risk to review: {risk}' subprojects/docket/src/docket/arming.py
---

**Problem.** Twice on 2026-11-02 the owner could not tell what a review
request asked of them. Both used the risk form that `bin/docket arm` prints:
"Risk to review: ... Checked: ... Please look at: ...".

On `#1946` the ask read: "Risk to review: a pinned test of the owner-ask guard
changes, so a relayed ask in the new form could be refused or a bare ask let
through." On `#1947` it read: "Checked: tools/model_rewrite.py lost accounts
for every figure that left the section, doc_check holds every marker to its
stored value, ... and verify --self ACCEPTs." It then asked the owner to look
at reworded paragraphs and judge whether they kept their meaning.

**The owner's words** (project owner, 2026-11-02):

> Can all text follow these? Even like interaction with me. Like what does
> this mean? (19:34Z, with a screenshot of the `#1946` ask)

> I am having a hard time understanding what this is asking from me? is there
> any suggestion for instructions to make something like this clearer?
> (19:39Z, quoting the `#1947` ask)

> How am I supposed to judge that? (on `#1947`, relayed by the coordinator)

**Why it matters.** Every pull request held for the owner's read reaches them
through this ask, and the project's guard makes a session copy the recorded
line word for word. Whatever vocabulary the record holds therefore reaches the
owner. An ask they cannot decode stalls the merge, and an ask that has them
re-check a rewording asks for a judgment the tests and reviews already made.

**Cause.** Three gaps:

1. The plain-writing rule listed replies but not review requests, and nothing
   said that each field of the `arm` line is prose the owner reads.
2. The risk form's labels and fields invited a session to describe its own
   checks ("what was checked to rule it out") in the repository's terms.
3. Nothing limited the question to one the owner can decide. The `look` field
   handed them a re-check of work the reviews had done.

**Fix.** The coordinator proposed a five-part shape for every review request:
what changed, one yes-or-no question, the text before and after, what was
already checked, and what to reply. The owner approved it for every session:
"Tell all active sessions to use this format" (project owner, 2026-11-02,
19:51Z, ratified, over the three-part risk form). This builds it:

1. The review form becomes `changed - <one plain sentence> | question - <one
   yes-or-no question>? | checked - <what was already checked> | reply -
   <what to reply>`. `arm` renders it as "What changed: ... Question for you:
   ...? Already checked: ... What to reply: ...".
2. The question is one the owner can decide as the owner or as a clinician.
   It never asks for a re-check of what the tests or reviews covered. Where
   no such question exists, the question says so and recommends merging.
3. `arm` refuses a record in the old `risk`, `checked` and `look` form, so a
   branch that still carries one asks the owner nothing until it records the
   new form.
4. `arm` refuses a record that names a tool, file, command-line flag,
   snake_case name or item id (`ASK_JARGON`). Whether the rest of a sentence
   is plain stays judgment, which the printed instructions ask for.
5. The plain-writing rule names review requests and each field of the `arm`
   line. The maintainer guide and the coordinator mode describe the new form.

The guard reads the rendered form from the same templates in `arming.py`, so
it recognizes the new line with no change of its own.

**Done when.** `arm` prints the new review form, refuses the old one and any
record naming a tool or file, and the plain-writing rule covers review
requests. A test pins each of these.
