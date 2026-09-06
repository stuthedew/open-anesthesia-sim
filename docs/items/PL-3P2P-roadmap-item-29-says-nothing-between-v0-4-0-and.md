---
id: PL-3P2P
title: ROADMAP item 29 says nothing between v0.4.0 and v0.7.0 touches core/, but v0.5.0's score architecture does, so the exact step is pinned ahead of v0.5.0 rather than free in that span
status: untriaged
added: 2026-09-06
---

**Problem.** Planned-milestone item 29's *Placement* paragraph justifies putting
the exact matrix exponential immediately after v0.4.0 partly on this sentence:

> Nothing between v0.4.0 and v0.7.0 touches `core/` either - v0.5.0 and v0.6.0
> are interface releases on an unchanged model - so the step is free anywhere in
> that span, and it now sits immediately after v0.4.0 as the `v0.4.x` row of
> "The timeline", which keeps the benefit as early as the constraint allows.

That was written 2026-09-02. The score-architecture design round of 2026-09-05
placed `PL-T691` and `PL-P1Z3` in v0.5.0, and both declare
`src/anesthesia_sim/core` in their `touches` - `PL-T691` also
`app/controller.py`, `docs/MODEL.md` and `docs/ARCHITECTURE.md`; `PL-P1Z3` also
`tests/reference`. So v0.5.0 is not an interface release on an unchanged model,
and the step is **not** free anywhere in that span.

**Why it matters.** The sentence understates the exact step's own priority in
the one document that decides priority. Read as written, `PL-GS5X` is a
readability pass that could slip anywhere before v0.7.0 without cost. In fact
`bin/docket concurrent PL-GS5X` named `PL-T691`, `PL-X9KD` and `PL-2HTF` as
waiting on it, and the score architecture's remaining four items - `PL-2FM6`,
`PL-P1Z3`, `PL-8LXM`, `PL-49R8` - chain from `PL-T691` in turn, so the exact
step was the head of v0.5.0's whole dependency chain and therefore of the MVP's
critical path. (`PL-GS5X` closed 2026-09-06 in pull request 376, which is what
makes that chain startable; the sentence in item 29 is unchanged and still
wrong.) Timeline row 5 records the chaining
("chained behind `PL-GS5X`"); item 29 does not record being chained *to*, and
the two paragraphs are read at different moments by different sessions.

This is also the second time this pair of paragraphs has disagreed: v0.4.1
closed the case where `bin/docket wave` read the `v0.4.1` row as a milestone
because item 29 already called it the `v0.4.x` row. The store can decide the
`touches` half of this one, which is why the check below is worth having.

**Where.** `ROADMAP.md`, planned-milestone item 29, the *Placement (project
owner, 2026-08-26; revised 2026-09-02)* paragraph - the sentence beginning
"Nothing between v0.4.0 and v0.7.0 touches `core/` either". Timeline row 5 and
the v0.5.0 milestone section carry the correct statement and need no change.

**Done when.** The sentence says what is now true: v0.5.0's score architecture
does touch `core/`, so the exact step is pinned immediately ahead of v0.5.0
rather than free across the span, and the readability benefit and the
critical-path position are stated as the two separate reasons they are. Consider
whether `tools/doc_check.py` can decide the mechanical half - a prose claim that
a release touches no `core/` path, held against the `touches` of the items that
release's section names - or record why it cannot.
