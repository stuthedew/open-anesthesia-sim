---
id: PL-50PZ
title: Build the View chooser and the registry's required-reachable flag, which is what makes docs/MODEL.md's accounting tier reachable from every Workspace and not removable from the application
status: blocked
feature: interface-areas
added: 2026-09-16
priority: P2
effort: M
blocked-by: PL-R1WQ, PL-WV9K
classes: safety, anticipated
touches: src/anesthesia_sim/app/, docs/MODEL.md, tests/integration
---

**Problem.** Build the View chooser and the registry's required-reachable flag, which is what makes docs/MODEL.md's accounting tier reachable from every Workspace and not removable from the application

**Why it matters.** `docs/MODEL.md` puts the agent accounting - cumulative
delivered, cumulative exhausted, total stored, and the mass-balance residual
with its absolute error - in the one required tier a Workspace may omit: "They
must stay reachable in every layout, and must not be removable from the
application." That is the one class whose guarantee cannot be structural
presence, so it has to become an invariant of the registry and of the chooser
instead. `ROADMAP.md` § "Development rules for scientific milestones" treats
mass accounting as a release gate rather than an optional diagnostic, which is
what makes this a requirement rather than a convenience.

**Done when.** "Reachable" has a written definition in `docs/MODEL.md`; the
View registry records which kinds are required-reachable and a build lacking
one fails; the chooser offers them from any Workspace; and a test asserts that
from each shipped Workspace the accounting values can be brought on screen
through the interface alone, and that a Workspace naming none of them still
leaves them reachable.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 16.
