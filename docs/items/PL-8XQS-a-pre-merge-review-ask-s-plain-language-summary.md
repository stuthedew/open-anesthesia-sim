---
id: PL-8XQS
title: A pre-merge review ask's plain-language summary is a Projects-instructions rule only, so a session outside the Project asks for a read without one
status: untriaged
added: 2026-09-27
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
