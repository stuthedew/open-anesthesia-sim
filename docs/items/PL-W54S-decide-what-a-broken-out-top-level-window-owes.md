---
id: PL-W54S
title: Decide what a broken-out top-level window owes docs/MODEL.md's unconditional display set, which PL-WLWY named as its own real work and then closed without choosing between its three readings
priority: P2
effort: M
status: blocked
classes: safety, anticipated
feature: interface-areas
blocked-by: PL-NWTM
touches: docs/MODEL.md, ROADMAP.md
added: 2026-09-16
---

**Problem.** Decide what a broken-out top-level window owes docs/MODEL.md's unconditional display set, which PL-WLWY named as its own real work and then closed without choosing between its three readings

**Problem.** `docs/MODEL.md` guarantees the unconditional region structurally against the area system's own operations, and separately states that no required value may be covered while the application still believes it is showing it — naming a second top-level window dragged over the one carrying the region as a case it binds. It names no mechanism for that case. `PL-WLWY` (closed 2026-09-16) wrote out three candidate readings — every top-level window carries the region; the contract binds the application rather than the window; the contract binds the window that can be alone on screen — said "choosing between them is this item's real work", and then closed on the three-way tier split without choosing. `grep -nE "every (top-level )?window|each window|second window" ROADMAP.md docs/interface-provenance.md` returns nothing, so the roadmap does not carry it either, and no open item does.

**Why it matters.** Item 34 builds break-out. A broken-out window is a full window that can be dragged over the main one on a single monitor, and on a second monitor it is the strongest form of position carrying meaning — which `docs/MODEL.md` already refuses for the compare-mode readouts. Reading 2 is ruled out by `PL-WLWY`'s own argument that it is unverifiable once the window manager is involved, so the live choice is between 1 and 3, and they build differently. Recommendation: reading 3 — the main window always carries the region and cannot be closed while break-outs exist, a broken-out window naming the run it shows — because it keeps the region's cost off a small secondary view while remaining structural; reading 1 is the stricter fallback if window lifecycle turns out not to be enforceable.

**Done when.** The question is put to the project owner and the answer recorded in `docs/MODEL.md` § "Minimum displayed outputs" → "What this list requires once the layout is the reader's" and named in `ROADMAP.md` item 34; the window-creation path enforces it rather than warning about it; and a test drives break-out and asserts that every window the application can be left showing carries the unconditional set, including after the last non-broken-out window is closed.

*Basis (lens `required-values`).* ROADMAP.md:4648, item 34: "What this milestone builds is the no-overlap invariant above, plus break-out: an area may be taken into **its own top-level window**, itself a full window with its own areas." docs/MODEL.md:4851 binds the case but chooses no mechanism: the occlusion rule "binds a panel drawn over the dashboard, a second top-level window dragged over the one carrying the unconditional region, and any later floating mechanism" — while the structural guarantee at :4859 is stated only against "split, join, close or workspace switch".

**Problem.** `SimulationView.interface_strings` (`src/anesthesia_sim/app/simulation_view.py:552`) is the project's single definition of what is on screen — its own docstring says so: "Every string a reader can see on the dashboard, hidden widgets included ... so a whole-interface test holds one definition of 'on screen' rather than each walking the tree its own way." Its implementation is rooted in one widget tree and one window: `yield self.window().windowTitle()` (`:566`) and `for widget in (self, *self.findChildren(QWidget))` (`:570`). It is what the safety-facing whole-interface tests assert through — that nothing on screen says "end-tidal" without "-equivalent", that the MAC divisor and the MAC-awake band fraction are stated for every agent, that the use disclaimer is present (`tests/integration/test_simulation_view.py:2434-2600`, `:2899`, `:2921`).

**Why it matters.** The predicate answers "is this string somewhere in this widget's subtree", and today that is the same question as "can the reader see it" because the dashboard is one tree in one window with nothing closeable. Under `ROADMAP.md` planned-milestone item 34 the two come apart in both directions, and neither shows up as a failure: a value in an area the reader closed, or in a workspace that is not the active tab, is still in the tree and still counted; a value in an area broken out into its own top-level window is not a child of this widget and drops out of the walk, so an assertion that it is present starts failing for a layout that is correct, or — worse for the ones that assert absence, like the end-tidal hedge — starts passing because the string went somewhere the walk cannot reach. `CLAUDE.md`'s test for friction that compounds names the first shape exactly: a check that gives a wrong answer silently, passing while the guarantee it stands for is void.

**Why `PL-41YP` does not cover it.** `PL-41YP` (assert every required displayed output reaches the rendered view, `ready`) is the item that writes the required-output test, and its brief is explicit that it works "against `app/simulation_view.py`" — the rendered view as one tree. It is the first *consumer* of a visibility predicate, not the item that supplies one. Filing this ahead of it is what stops that test being written against a predicate that will stop meaning what it says; `PL-41YP` should be re-read against whatever this settles.

**Where.** `src/anesthesia_sim/app/simulation_view.py:552-580`; `tests/integration/test_simulation_view.py:377-378` (`_interface_strings`) and its call sites.

**Done when.** There is one way to ask what a reader can currently see that spans every area and every top-level window the application owns, that distinguishes present-in-the-tree from visible-to-the-reader, and that the required-output test can be written against; and `interface_strings` either becomes that or is narrowed to the one-widget question with its callers moved.

*Basis (lens `state-ownership`).* `docs/MODEL.md` § "Minimum displayed outputs" → "What this list requires once the layout is the reader's": "The set is stated as a *test*, not as a list, and the test is: a value is unconditional when a reader could misread the run's other displayed numbers without it."

**Problem.** `ROADMAP.md` planned-milestone item 34 puts break-out in scope: an area may be taken into its own top-level window, itself a full window with its own areas. `PL-WLWY` (the minimum display under a reader-owned layout) identified the contract that follows, wrote three candidate readings of it, and called choosing between them "this item's real work":

1. every top-level window carries the unconditional region;
2. the contract binds the application rather than the window - the required values must be visible somewhere;
3. the contract binds the window that can be alone on screen, with the main window unclosable while break-outs exist and a broken-out window naming the run it shows.

It then closed on 2026-09-16 on the stepping-stone answer - the three-way split of the list, the occlusion rule, and the unconditional region sitting outside the area system - without choosing among the three. `docs/MODEL.md` names a second window exactly once, at line 4854, and only to say the occlusion rule reaches it: "That one sentence binds a panel drawn over the dashboard, a second top-level window dragged over the one carrying the unconditional region, and any later floating mechanism". So what a second window may be *dragged over* is settled and what it must itself *show* is not.

**Why it matters.** `PL-WLWY`'s own framing is that "a required value absent from the display is the same failure as a covered one", and the unconditional set is guaranteed structurally rather than by validating a saved layout - `docs/MODEL.md` put the unconditional region outside the area system, so that no split, join, close or workspace switch reached it (the sentence has since been rewritten per window, by the answer recorded below). A second top-level window is the one construct in item 34 that is outside that region's window, so the structural guarantee stops at its frame and nothing replaces it. The question is also not confined to the display: reading 1 and reading 3 imply different containers - symmetric windows each instantiating the unconditional region, against a privileged main window the container must refuse to close. Deciding it after the model is written means rewriting the model, and deciding it after break-out ships means shipping a window that presents clinical values with no context.

**Done when.** `docs/MODEL.md` § "Minimum displayed outputs" → "What this list requires once the layout is the reader's" states which of the three readings holds and what a second top-level window owes - the unconditional region, a named run, or a stated subset - and `ROADMAP.md` item 34's break-out paragraph names that answer instead of leaving it to scoping. The answer is recorded as a stepping stone the same way the rest of that section is, so that it may be revisited without the occlusion rule moving with it.

*Basis (lens `layout-ops`).* ROADMAP.md item 34 (~line 4648): "an area may be taken into **its own top-level window**, itself a full window with its own areas. The Blender Manual's § \"Areas\" documents that as *View > Duplicate Area into New Window* ... and describes the result as a fully functional window belonging to the same running instance, useful across multiple monitors." The contract that implies is stated as unanswered in docs/items/PL-WLWY-docs-model-md-s-minimum-displayed-outputs.md:91-110: "**What break-out added to the question rather than answering** (project owner, 2026-09-15 ...). An area may be broken out into its own top-level window. So there can be more than one window, and a broken-out one can be dragged over the window carrying the strip. Three candidate readings, and choosing between them is this item's real work".

**Problem.** `docs/MODEL.md` § "Minimum displayed outputs" opens "The interface must show:" (`docs/MODEL.md:4731`) and answers the layout question with a single region: "The unconditional region sits outside the area system, so no split, join, close or workspace switch reaches it" (`docs/MODEL.md:4859-4861`). `ROADMAP.md` planned-milestone item 34 builds break-out - "an area may be taken into **its own top-level window**, itself a full window with its own areas" (`ROADMAP.md:4648`) - and the specification says nothing about what a second window owes. The one sentence that names a second window covers a different failure: the occlusion rule binds "a second top-level window dragged over the one carrying the unconditional region" (`docs/MODEL.md:4854`), which is about covering, not about a window read on its own.

**Why it matters.** A chart broken out onto a second monitor, with the main window on another screen or behind it, draws compartment traces with no simulated time, no playback rate, no run state, no halt reason and no agent name - the whole of the invariant tier that section defines, whose own test is that "a value is unconditional when a reader could misread the run's other displayed numbers without it". § "Reasonably foreseeable misuse, and the hazards the presentation carries" rests a hazard control on the same assumption - "the agent name is always visible" (`docs/MODEL.md:175`) - and break-out is what makes that sentence false without any code disagreeing with it. This is the correct-number-wrong-context failure `CLAUDE.md` classes as a safety failure, and break-out is inside item 34's own scope rather than a later mechanism, so the answer is owed by the milestone that builds it. `PL-WLWY` (the minimum-display division, closed) built the three-way split for one window; `PL-T86Q` (the item that corrected item 34's floating paragraph, closed) settled occlusion. Neither reaches this, and no open item names break-out.

**Done when.** `docs/MODEL.md` § "Minimum displayed outputs" states what the unconditional region owes in a top-level window other than the one carrying it - replicated per window, or break-out restricted to views that carry their own context, or another answer with its reason recorded - the hazard table's "always visible" row is qualified to match, and the occlusion paragraph distinguishes a second window that covers the region from one read alone.

*Basis (lens `docs-routing`).* ROADMAP.md item 34, on what this milestone builds: "What this milestone builds is the no-overlap invariant above, plus break-out: an area may be taken into **its own top-level window**, itself a full window with its own areas." (ROADMAP.md:4646-4649)

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Filed 2026-09-16 by the area-model queue audit (`PL-BNYF`), which swept 49 open and untriaged items and seven gap lenses against `ROADMAP.md` item 34, `docs/interface-provenance.md` and `.claude/rules/ui-areas.md`. Each candidate was checked against the store before it was filed, so a gap an existing item already covers is not here.

---

## Answered 2026-09-16: the tier split, and what is left of this item

**The decision is taken** (project owner, 2026-09-16, scoping item 34). Neither
of the two live readings was adopted. The answer splits the obligation the way
`docs/MODEL.md` had already split the list: **every top-level window carries
the invariant tier** - simulated time, the rate it is advancing at, run state,
why a run halted, and what is being administered - **plus the name of the run
it shows**; the **per-substance tier lives once, in a main window that cannot
be closed while any other top-level window is open**. The accounting tier is
unchanged.

The reasoning, the two refused readings, and the limit on what occlusion an
application can observe are in `docs/MODEL.md` § "Minimum displayed outputs" ->
"What this list requires once the layout is the reader's"; `ROADMAP.md` item 34
names the answer. Reading 1 (every window carries the whole region) was refused
because forcing the per-substance tier into a small break-out window either
dominates it or is squeezed, which is the never-hidden divergence's own failure.
Reading 3 (main window carries everything, break-out names only its run) was
refused because it rests the guarantee on a window the reader may not be able to
see, which is the property `PL-WLWY` used to rule out reading 2.

**What is left of this item is v0.6.0's half**: building the unconditional
region in that per-window shape, with the main window's identity and the
per-substance tier's single home, so that v0.7.0 adds a window rather than
rebuilding the region. The second window's own application of the rule - the
window lifetime, and the test that drives break-out - is `PL-Y04W`. The
whole-interface visibility predicate this item also carried was split out to
`PL-904Y` on the same day, because it breaks at Area close and join rather than
at break-out.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 7, beside `PL-NWTM`.
