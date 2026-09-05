---
id: PL-Y5WR
title: The 30-day scenario cap is enforced nowhere as an explicit halt, and dropping PL-011 removes the only item that required it
status: untriaged
added: 2026-09-05
---

**Problem.** The project owner set a scenario run-time cap on 2026-08-25 — 30
days as the working figure, revisable upward. `PL-011` (bound the controller's
concentration history) recorded it and drew the consequence the owner did not
state:

> the run-time cap should be enforced as an explicit halt with a stated reason
> rather than left implicit.

Nothing enforces it. There is no ceiling on elapsed simulated time anywhere in
`core/` or `app/`: `MAXIMUM_SIMULATION_STEP_S` bounds one step's size and
`core/supported_ranges.py` bounds the four flows, but the *number* of steps a
run may take is unbounded. `PL-011` is the only item that named the gap, and
the score-architecture drop supersedes it on the **memory** argument alone.

**Why the drop does not carry it.** `PL-T691` (the run is its control-input
timeline) uses 30 days for *sizing* — "a week is 738 MB; the owner's 30-day cap
is 3.16 GB", and the closed form costs "3.6 ms over 30 days". Those are
measurements taken *at* the cap, not an enforcement of it. Making state a
closed-form function of the score removes the reason to bound the run for
**memory**, and leaves the reason to bound it for **validity** exactly where it
was. `PL-SV2R` (decide how run history is retained once fast-forward exists) is
already dropped, so nothing else covers it either.

**Why it matters.** This is a supported-domain question, not a resource one.
`docs/MODEL.md` § "Supported input ranges" refuses a flow outside its interval
rather than simulating it, and § "What a setting outside the range costs"
states the principle: a setting outside the verified domain "is not an
unverified number but a wrong one". Elapsed simulated time is the one input
with a declared limit and no refusal behind it. `CLAUDE.md`'s standard prefers
an obvious failure to a plausible-looking value where correctness cannot be
established, and a run at day 45 of a cap set at 30 is producing exactly such
values — the fat compartment, whose time constant is about 42 h, is the one
still moving out there.

The v0.4.0 playback multiplier is what makes this reachable: at 300× a 30-day
case is about 2.4 hours of wall clock, where before the multiplier it was 30
days of it.

**Where.** `src/anesthesia_sim/core/` for the limit and the refusal — beside
`supported_ranges.py`, which is the existing worked example of a declared
domain with a raising boundary — and `docs/MODEL.md` § "Supported input ranges"
or a section beside it for the declaration. The interface already has the
halt-and-say-why path from `PL-VM40`'s failure handling, so the display side
may need nothing.

**Open question this carries.** Whether 30 days is still the figure. It was
given as "the working figure, revisable upward later", and it was given before
the playback multiplier existed. Triage should put that to the owner rather
than encoding 30 days as though it were settled.

**Done when.** A run reaching the declared cap halts with a stated reason
rather than continuing, the cap and its provenance are declared in one place
the model and the interface both read, and `docs/MODEL.md` records the limit
alongside the other supported-input ranges. Regression test for the boundary.

**Found 2026-09-05** while reviewing the `PL-011` drop on
`origin/claude/simulation-architecture-review-qjlg4q`, which is correct about
memory and silent on this.
