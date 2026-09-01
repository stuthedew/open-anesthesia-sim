---
id: PL-K6QR
title: Record what this project is at the top of CLAUDE.md, so the workflow-versus-simulator trade-off has its reason resident
priority: P2
effort: S
status: done
classes: infra
feature: dev-tooling
touches: CLAUDE.md
added: 2026-09-01
closed: 2026-09-01
not-delegable: the deliverable is a paragraph of the project owner's own framing placed where every session reads it; there is no command that passes after the work and fails before it beyond grepping for the text, and whether the placement is right is a judgment
---

**Problem.** `CLAUDE.md` told every session how to weigh the simulator against
the workflow apparatus - "Two standards, deliberately unequal", "Where the two
compete for a session, the simulator wins", and the standing decision that
workflow work outranks product work until the workflow is settled - without
ever saying *why*. A session could read all three, apply them correctly, and
still have no idea what the project is for or what failure it is guarding
against.

That gap shows up as misplaced effort rather than as a rule violation. A
session that does not know this is a solo hobby project with no deadline reads
"streamlined" as a size target, polishes scaffolding nobody will read, or
treats a release as something with a date attached.

**Why it matters.** The rules that depend on this framing are already resident,
so their premise has to be resident too, or every session re-derives it from
the rules themselves - and derives it wrong, because a rule read without its
reason reads as arbitrary. It is also the answer to the question
`check_resident_instructions` asks of anything added here: a session makes the
workflow-versus-simulator call constantly and early, before it would have any
occasion to open a skill, a path-scoped rule or `docs/maintainer.md`.

**Where.** `CLAUDE.md`, as a new "What this project is" section between the
routing paragraph and "Working with the project owner".

**Approach.** Add the project owner's own words, unedited. This is framing
rather than a rule, so it is not a candidate for the four routing dispositions:
there is no moment it fires and no file whose reading should trigger it, which
is exactly the resident case.

**Done when.** `CLAUDE.md` carries the paragraph above "Working with the
project owner", and the routing question the growth advisory raises is answered
rather than silenced.

**Closed 2026-09-01, in the session that asked for it,** per the rule that a
behavior change takes effect in the session that asks for it. +9 resident
lines, CLAUDE.md 381 to 390.

The project owner also asked to update the length trigger so this addition
would not trip a "too long" threshold. There is no such threshold to update.
`tools/doc_check.py`'s `check_resident_instructions` is documented as
"Reported, never thresholded": it emits an advisory on *any* positive growth
against `origin/main` and `make check` does not fail on advisories, so nothing
here is red. Its docstring records why a limit is the wrong mechanism - "a
limit would be met by deleting a rule to reach a number, which is the one
outcome the routing pass must not produce" - and the advisory self-clears once
this merges, because the baseline becomes the new `main`. Left unchanged, and
put to the owner as a decision rather than acted on.
