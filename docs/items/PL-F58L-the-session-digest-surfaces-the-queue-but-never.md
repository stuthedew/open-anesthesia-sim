---
id: PL-F58L
title: The session digest surfaces the queue but never the roadmap, so timeline placement has no alarm clock
priority: P2
effort: S
status: ready
classes: session-cost, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/render.py, .claude/hooks/docket-digest.sh
added: 2026-08-26
---

**Problem.** The `SessionStart` hook runs `docket digest`, which reads
`docs/items/` and nothing else. `ROADMAP.md` has no surfacing mechanism at
all: `tools/doc_check.py` opens it only to check that citations resolve, and
no command reports where the project stands on its own timeline. So the queue
nags every session and the roadmap nags never.

**Why it matters.** `CLAUDE.md`'s intent rules deliberately route a feature
that is wanted but not ready to build to `ROADMAP.md` rather than the queue,
because an unscoped item in the queue is one every session reads past and none
can work. That routing is right, but it sends the intent somewhere with no
alarm clock, and the same rules then ask a session to "close the loop back to
the roadmap" and "offer the release; do not wait to be asked" — obligations
that currently rest on a session happening to open the file.

Concretely, as of 2026-08-26: planned-milestone item 29 (make `core/` read
like the domain) is placed "after v0.3.0 and before v0.4.0", and nothing will
say so when v0.3.0 lands. The same holds for the four unscoped milestones
after it, and for the debt gate's own cadence — a gate is frozen when a
milestone is scoped, and no session is told that a milestone is due to be
scoped.

**Where.** `subprojects/docket/src/docket/render.py` builds the digest;
`.claude/hooks/docket-digest.sh` invokes it. Whatever reads `ROADMAP.md`
would be new.

**Decision needed.** How much of the roadmap is decidable enough to surface
without guessing at prose. The current version string is decidable
(`pyproject.toml`), and so is which timeline row names it, if the rows carry
their version in a parseable form. "Is this milestone's gate clear?" is
decidable from item state once the frozen list is recorded as ids — which
`PL-9CNQ` (a `docket gate` command) already proposes to compute. What is not
decidable is whether the prose around a row is still true, and a digest line
that guessed at that would be worse than none, per "Do not script the
judgment".

Recommend the narrow version: one digest line naming the current version and
the next timeline step, plus the gate's remaining count once `PL-9CNQ` lands.
That is enough to make a session ask the right question without the tool
claiming to know the answer.

**Done when.** A session is told at start where the project sits on
`ROADMAP.md`'s timeline and what the next step is, or the limitation is
recorded in `subprojects/docket/README.md` as accepted with its reason.

**Context.** Found while answering the project owner's question about what
triggers work to be scheduled (2026-08-26). The answer is that nothing does —
the digest surfaces, `docket next` ranks, and the owner decides — which is by
design for the queue and an omission for the roadmap.
