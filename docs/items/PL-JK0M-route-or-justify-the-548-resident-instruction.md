---
id: PL-JK0M
title: Route or justify the 548 resident instruction lines every session loads before reading anything
priority: P2
effort: M
status: ready
classes: session-cost, docs
feature: worker-instructions
touches: CLAUDE.md, .claude/rules
added: 2026-09-05
not-delegable: the judgment is whether each rule still fires at the moment a session needs it, which no command decides. `check_resident_instructions` reports the resident total and refuses a threshold on purpose, because a limit is met by deleting a rule to reach a number - the one outcome this item must not produce. Editing the files every session loads is also the last diff that should land unread
---

**Problem.** Two files load at launch in every session before anything has been
read: `CLAUDE.md` (408 lines) and `.claude/rules/instruction-writing.md` (140),
which carries no `paths:` frontmatter and so loads unconditionally. That is 548
resident lines. Claude Code's memory documentation targets "under 200 lines per
CLAUDE.md file", states that longer files "consume more context and reduce
adherence", and names file size as a first thing to check when instructions are
not being followed
(https://code.claude.com/docs/en/memory, "Write effective instructions"). It
also confirms the mechanism that matters here: "Rules without `paths`
frontmatter are loaded at launch with the same priority as
`.claude/CLAUDE.md`."

**Why it matters — and why this is not `PL-XXBD`/`PL-3VKZ`.** The standard here
is **adherence**, not readability. Nobody reads these files for pleasure; the
question is whether each rule fires at the moment a session needs it, at the
lowest resident cost. That makes wordiness a symptom rather than the defect,
and it makes the fix routing — moving a rule to the cheapest carrier that still
delivers it — rather than rewriting.

The distinction is load-bearing, not stylistic. `CLAUDE.md` forbids deleting a
rule for being wordy ("A rule that lands in none of the four has been lost,
which is worse than this file staying long"), and
`check_resident_instructions` in `tools/doc_check.py` refuses a line threshold
on purpose, because "a limit would be met by deleting a rule to reach a number,
which is the one outcome the routing pass must not produce." A prose-quality
standard applied here would produce precisely that. The project owner asked
explicitly (2026-09-05) that the two standards stay apart.

**What is new since this was last looked at.** `PL-JQY5` recorded 547 resident
lines on 2026-08-30 and was dropped the same day as a duplicate of `PL-H7XN`
(keep every rule resident whether or not a session needs it). `PL-H7XN` is
done — but what it delivered was the *mechanism*: the four routing
dispositions in `CLAUDE.md` and the resident-total advisory in
`tools/doc_check.py`. The pass applying that mechanism to the text that
remains was never filed. The numbers say so: 547 lines then, 548 now. Five
rules did move out of `CLAUDE.md` into `.claude/rules/`, but the one that
carries the most lines went to a file that still loads at launch, so the
resident total did not fall. `check_resident_instructions` catches growth, and
catches text trimmed to pay for an addition; it does not catch a relocation
between two resident files, which is what happened.

**Where.** `CLAUDE.md`, `.claude/rules/`.

**Approach, not yet decided.** Per rule, decide route-or-keep and record the
answer, so the question is settled rather than reopened by the next session:

- `.claude/rules/instruction-writing.md` (140 lines) is the largest single
  candidate and the hardest case. Reply shape applies to every reply, and
  `CLAUDE.md`'s own disposition list says path-scoping is "wrong for one that
  must fire before a first write, which no read precedes." It may legitimately
  have to stay resident — in which case say so in the file and stop the
  question recurring.
- The safety-critical clinical-output standard stays resident unconditionally.
  `CLAUDE.md` already states why.
- The honest expectation is that a large share of the 548 lines is
  required-resident under the project's own test. A pass that ends with a
  written justification and little movement is a successful outcome here, not a
  failed one.

Out of scope: raising a threshold in `check_resident_instructions`. That
refusal is a considered decision recorded in the code, not an oversight.

**Done when.** Every resident rule has been routed to the cheapest carrier that
still fires it, or carries a recorded reason it must stay; no rule has been
lost; and `/context` confirms what loads.
