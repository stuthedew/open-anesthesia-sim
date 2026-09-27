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

---

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it. None of
these is a learner-visible fork; they are taken under the delegated call
unless the owner objects.

**Q1. The written definition of *reachable* for `docs/MODEL.md`.**
**Recommendation:** *A View kind is reachable in a Workspace when a reader
can bring it on screen from that Workspace through the interface alone, in a
bounded number of steps, without a drag or a file edit.* Two mechanisms make
it true for every kind at once: every Area's chooser lists every registered
kind, unfiltered, and `set_view` places the chosen one; and a menu and
keyboard route exists beside the pointer one (`PL-M352`). The tree is never
empty by construction (closing the last Area leaves one empty Area), so there
is always somewhere to place a View.

**Q2. The registry flag and what fails a build.** `required_reachable` on
the registry entry (`PL-R1WQ`), and a module-level
`REQUIRED_REACHABLE = ("agent_accounting",)` that tests read: the tag is
registered, its entry carries the flag and a factory, the chooser built from
each shipped Workspace lists it, `set_view` places it, and the values appear
by `PL-904Y`'s predicate. A build lacking any of those fails in CI, which is
what "not removable from the application" means here: the registry is code.

**Q3. "From any Workspace", including one naming none of them.** The
chooser reads the registry, not the Workspace, so a Workspace whose file
names no accounting Area still offers it. The test loads a fixture Workspace
of two charts, opens the chooser in one Area, chooses the accounting kind,
and asserts the values. Since the shipped defaults omit the accounting View
(`PL-KXTL`, project owner 2026-09-16), the chooser is its only route in the
shipped set, and this test is what guards the guarantee.

**Q4. Where the chooser sits.** In the container-owned Area header
(`PL-TH35` Q11), one control per Area, listing kinds by registry title;
Blender's editor-type menu occupies the same position. Its appearance is
entry 20's.

## Answers 2026-09-27

**Every recommendation above: ratified** (project owner, 2026-09-27,
ratified, over the alternative each names). The one decision the owner
specified otherwise is `PL-WV9K` Q4: layouts are saved by an explicit "Save
as default" action in the layout menu, not automatically; `PL-WV9K`
§ "Answers 2026-09-27" carries that design.
