---
id: PL-RRWV
title: Fork a run from a bookmark and compare strategies side by side
status: dropped
feature: scenario-branching
added: 2026-08-25
closed: 2026-08-25
reason: aspirational rather than actionable; it is ROADMAP.md planned milestones 11 and 12, and its scope decision and measured cost context were carried into item 12
---

**Problem.** Comparing two managements of the same case — coast on low flow
versus hold 0.5 MAC, then compare time to a wake-up threshold — currently
means building the whole case twice, and the two runs then differ by every
small thing that was not reproduced identically.

**Why it matters.** This is the educational payload of the whole feature: it
isolates the variable under study. The owner's example is a three-hour case,
branched just before emergence, run two ways. It is `ROADMAP.md`'s planned
item 12, and item 13 (IV/effect-site) is sequenced behind it.

**Where.** `app/controller.py`, plus whatever holds a run as an object rather
than as the controller's own mutable state.

**Scope decision (owner, 2026-08-25).** Flat, not a tree: one trunk run with
N branches taken from points on it. Sub-forks of forks are deliberately out —
they multiply without bound and buy little over re-branching from the trunk.
Branch points are expected to be bookmarks (PL-X9R0); an arbitrary time is
the rare case and can be served by resimulating from the nearest prior
bookmark, which needs PL-WRKL.

**Measured context (2026-08-25).** Cost is not the constraint people expect.
The full dynamic state is six concentrations plus elapsed time and the
control settings — a snapshot is about the size of one history sample, so
snapshot density is nearly free. Resimulation is also cheap: `SimulationState.advance`
measured at 8.9 us per 0.1 s step, so reconstructing a 3-hour run from t=0 is
about 1 s, and 24 hours about 8 s. What is *not* cheap is the per-step
concentration history itself (see PL-011). Design the storage question around
that, not around avoiding resimulation.

**Done when.** A branch can be taken from a bookmarked point, run
independently, and plotted against its parent on a shared time axis, with
each curve unambiguously labelled as to which branch and which settings
produced it.
