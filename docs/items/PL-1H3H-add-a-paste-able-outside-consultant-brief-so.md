---
id: PL-1H3H
title: Add a paste-able outside-consultant brief so big-picture review has a licensed seat outside the queue workflow
priority: P2
effort: S
status: done
classes: docs, infra
feature: planning-cadence
touches: docs/consultant-brief.md
added: 2026-09-05
closed: 2026-09-05
pr: 354
verify: python3 tools/doc_check.py check && grep -q 'apparatus-standard.md' docs/consultant-brief.md
---

**Problem.** Every session in the queue workflow is inside the frame it would
have to question. `.claude/hooks/docket-digest.sh` prints `Top:` and `Beat:`
into context before the owner's first token and its own comment notes the text
is "resent on every turn"; `bin/docket next` hands over a ranked, reserved item;
the `docket` skill's triage mode forbids widening ("Nothing else. No ranking of
what to work on, no release offer."). Each is a good throughput rule. Together
they leave no session licensed to ask whether the direction is wrong.

The project owner already works around this by opening a fresh session and
typing an outside-consultant framing by hand, and reports it reliably surfaces
architecture-level problems the queue sessions do not. The workaround has no
home in the repository, so the framing is re-improvised each time.

**Why it matters.** The failure this guards against is not a defect that a
check catches. It is a sequence of individually-correct decisions that does not
reach the goal - climbing taller trees to get to the moon, in the owner's
phrase. Nothing in the tree currently detects it, and by construction nothing
inside the queue can.

**Why more instructions would not have fixed it.** `PL-WWDT` made
`.claude/rules/expert-review.md` resident *specifically* so the specialist
standard reaches a design round, merged to `main` at 13:56 on 2026-09-05
(`afcdb3b`, #350). The owner opened an outside-consultant session anyway at
16:48 the same day. `CLAUDE.md` already carried "Challenge assumptions when
warranted. Do not preserve a weak design solely because it was proposed
earlier." The rule was present, resident, and under three hours old. The
constraint is positional rather than informational, so a further rule does not
reach it - and `make check` already reports the resident total at roughly three
times the 200-line figure Anthropic's own memory documentation gives.

**Where.** `docs/consultant-brief.md`, new. Nothing else changes; the resident
total is unchanged against `origin/main`, which `doc_check` confirms.

**Approach, and why not a skill.** A skill was the obvious carrier and is wrong
on three counts, each verified rather than argued:

- `.claude/rules/instruction-writing.md` opens by claiming precedence over "a
  project file, **a skill**, a saved preference" for the shape of every reply.
  A skill-carried review comes back in the house format. The pasted text
  arrives as a user message and does not.
- `.claude/rules/apparatus-standard.md` fires on `/.claude/**`, `/tools/**` and
  `/subprojects/docket/**` - so a consultant reviewing the apparatus loads, by
  reading the thing under review, a rule telling it that tree is not worth
  reviewing. The brief names the file and disregards it for the pass.
- `tools/doc_check.py`'s `measure_resident` walks only `RESIDENT_ROOTS` and
  `RULES_DIR`. A skill's `name` and `description` sit in every session's system
  prompt where the project's own growth instrument cannot see them. An
  anti-capture device that routes around the only capture-detecting check is
  the wrong shape.

**Alternative considered and refused.** A `.claude/agents/` definition with
`Edit`/`Write` withheld would mechanically enforce "leave no unwired artifact"
rather than asking for it in prose, which is the stronger form of that one
guard. Refused because a subagent returns a summary to a parent and cannot hold
a conversation, and half the requirement is being able to ask the reviewer
follow-up questions. Custom agents also inherit the whole `CLAUDE.md` hierarchy
(only the built-in `Explore` and `Plan` skip it), so the isolation gained is
smaller than it appears.

**Measured, on the output contract.** The brief keeps `bin/docket new` as a
secondary output because the contract demonstrably works here: the 2026-08-30
outside review filed exactly 65 items, of which 43 are `done`, 13 `ready`, 6
`dropped` and 3 `blocked`. A two-thirds completion rate is a working channel.
The one-page ranked assessment is the primary deliverable so that the review
cannot discharge itself into the queue and stop there.

**Done when.** `docs/consultant-brief.md` exists, names
`.claude/rules/apparatus-standard.md` as a rule to disregard for the pass,
orders the read so `ROADMAP.md`, `docs/items/` and `docs/WORKING_NOTES.md` come
last, and adds no resident characters of its own.

**Worked.** Brief written. Read order puts the code and the running application
first and the three framing documents last, on the ground that a reviewer who
reads them first proposes the next item in the existing sequence. Output
contract is one ranked page with "this is wrong" separated from "this could be
more", against the documented failure that a reviewer asked for gaps reports
them whether or not they exist. Executable output is permitted but may not be
left unwired - two physics checks from the retired `PL-STNV` harness are
release gates in `tests/reference/test_coupled_dynamics.py` and still run,
which is the half of that experiment that worked.

**Re-pitched before merge, on the owner's correction.** The first draft made
project direction the subject. What the owner actually valued was a deep
simulation-architecture review - the model, the numerics, the chart and the
interaction - so the spine is now the simulator, the audience and the
plausible-wrong-number asymmetry are stated up front, and the two
project-direction questions moved to an optional tail marked deletable. A
§ "Objections already answered" was added ahead of the countermands, carrying
the too-much-tooling objection and the test it must now meet; `PL-9J2W` puts
the same test in `CLAUDE.md`, where it reaches ordinary working sessions that
no pasted document can. The apparatus-ratio question was **removed** from the
brief's question list: it was the line that manufactured the objection this
pass exists to stop re-litigating.
