---
id: PL-C1KK
title: docs/MODEL.md still names v0.2.3 as the current baseline, four releases on
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-08-30
not-delegable: docs/MODEL.md is a protected path, and whether prose names the right baseline is not decidable by a check - doc_check reads ROADMAP.md's baseline heading only, and extending it to free prose would be guessing at the judgment half
---

**Problem.** Two lines still call v0.2.3 the current released baseline, with
v0.2.7 shipped: `docs/MODEL.md:6` ("still in force in v0.2.3, the current
released baseline") and `docs/MODEL.md:1640` ("As of v0.2.3, this model does
not model").

**Narrowed 2026-08-30.** This was three lines across two documents. The third,
`docs/WORKING_NOTES.md:110` ("baseline is v0.2.3"), went with the architecture-
review thread that PL-STNV rewrote, so `docs/WORKING_NOTES.md` is clean and out
of scope. Both remaining lines are in `docs/MODEL.md`, which is why the
`not-delegable` note below still holds.

**Why it matters.** Same class as PL-N2N1 and PL-SWFM — a document naming the
wrong current version — but in two documents those items do not cover, and one
of them is `docs/MODEL.md`, which this project's own standard calls the
authoritative specification of the implemented model. A reader taking its
statement of which version's model is in force can attribute a value to the
wrong model version, which is a provenance failure rather than a tidiness one.

Both statements happen to remain *true* — no equation, parameter or numerical
method has changed since v0.2.3, which `ROADMAP.md` says explicitly; v0.2.6 and
v0.2.7 added an error bound and an applicability-domain guard around the same
equations rather than changing them — so this is a stale citation rather than a
wrong claim about the model. That is why it
is not a `P0`, and it is also why it has survived two releases: nothing reads
wrong until someone checks the version.

**Where.** `docs/MODEL.md:6` and `docs/MODEL.md:1640`.

**Worth deciding while fixing it:** whether these lines should name a version
at all. "In force since v0.1.0 and unchanged since" carries the same
information and cannot go stale, which is the shape that stops this recurring
in a third document — `doc_check`'s new baseline check covers `ROADMAP.md`
only, and extending it to free prose would be guessing at the judgment half.

**Found.** While closing PL-N2N1 (the version-table half of the same drift),
which deliberately left this out of its scope.

**Done when.** No document names a current baseline that disagrees with
`pyproject.toml`.
