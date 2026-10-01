---
id: PL-8XQS
title: A pre-merge review ask's plain-language summary is a Projects-instructions rule only, so a session outside the Project asks for a read without one
priority: P2
effort: S
status: done
classes: docs
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py
added: 2026-09-27
closed: 2026-10-01
pr: 1272
payoff: every pre-merge read the owner is asked for opens with a plain-language summary, whichever session asks
verify: grep -q 'def test_a_read_hold_asks_for_a_plain_language_summary' subprojects/docket/tests/test_cli.py
---

**Problem.** A pre-merge review ask's plain-language summary is a Projects-instructions rule only, so a session outside the Project asks for a read without one

**What was asked.** Stuart, 2026-09-27, in the scenario-branching thread,
after a thread explained `#1191` (`PL-SM5V`) in plain language before asking
for his read: "Make this the default behavior when asking me generically to
review a PR prior to merging. Do it automatically." The summary he meant said
in one sentence what the change does, what was wrong and what changed in terms
a clinician recognises, then numbered the specific points for him to judge (a
decision taken on his behalf, a new `docs/MODEL.md` statement, the one change a
learner would see) and what needed no review.

**Where it went, and the gap.** The Projects coordinator added it to the
Project's own instructions as a "Review asks" rule the same day, so every
Project thread carries it. Nothing in the repository does: `CLAUDE.md` and
`.claude/rules/instruction-writing.md` say nothing about a review ask's
content, so a session outside the Project that gets `bin/docket arm`'s
"waits on a read" answer asks for the read without the summary.

**Two carriers to weigh at triage.** A rule beside `instruction-writing.md`'s
decision-request rules (resident, so it pays the resident-set cost and must
name what it replaces), or one line in `bin/docket arm`'s read-hold output,
which fires at exactly the moment the ask is written and costs no resident
context but is a change to `arming.py`, itself a path that waits on his read.
If the Projects trial becomes the only way sessions run, this can be dropped.

**Why it matters.** The owner asked for it as the default on 2026-09-27, and
only Project threads carry it: a session outside the Project that gets `bin/docket
arm`'s read hold asks for the read without the summary.

**Carrier, recommended at triage.** `bin/docket arm`'s answer where a pull
request waits on a read, over a resident rule in
`.claude/rules/instruction-writing.md`: it fires at exactly the moment the ask is
written and costs no resident context, and `arming.py` waiting on the owner's
read costs one read of a change he asked for.

**Done when.** The read-hold answer tells the session to open its ask with the
summary - one sentence of what the change does, what was wrong and what changed
in terms a clinician recognises, then numbered points for him to judge, then what
needs no review - held by a test.

**Generator check.** Work the owner asked for; the request reached the
Project's instructions and not the repository.

**Built (2026-10-01, `#1272`).** `arming.READ_ASK` is printed under a `hold`
whose reasons include the read - a path outside the store, the tooling and the
records, or a change to `arming.py` - once no claim holds the branch. While a
claim holds it the pull request is a draft, which nobody is asked to read, and
the hold already says to keep it one; printed on every push during the work,
the line would be skimmed by the time it mattered. The test,
`test_a_read_hold_asks_for_a_plain_language_summary_once_no_claim_holds_the_branch`,
checks both sides of that, over a path outside the tooling and over the gate.
