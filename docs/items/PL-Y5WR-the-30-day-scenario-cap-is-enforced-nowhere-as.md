---
id: PL-Y5WR
title: The 30-day scenario cap is enforced nowhere as an explicit halt, and dropping PL-011 removes the only item that required it
priority: P1
effort: M
status: done
classes: safety
feature: numerical-domain
milestone: v0.4.7
touches: src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/simulation.py, tests/unit/test_supported_ranges.py, docs/MODEL.md
added: 2026-09-05
closed: 2026-09-07
pr: 421
verify: uv run pytest tests/unit/test_supported_ranges.py tests/unit/test_simulation.py tests/unit/test_exceptions.py tests/unit/test_formatting.py tests/unit/test_simulation_view.py tests/integration/test_controller.py && grep -q 'MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86_400.0' src/anesthesia_sim/core/supported_ranges.py && grep -qF '#### Supported run length' docs/MODEL.md
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

**Decision needed.** What the cap on elapsed simulated time is now that it is a
validity limit rather than a memory one, and what a run reaching it does.
Triaged to `needs-decision` on 2026-09-05; the two parts, the first of which
blocks the other:

1. **What is the number, and what is it a limit *on*?** 30 days was set as a
   memory-sizing figure for a store that no longer exists — `PL-011` is
   `dropped`, and under `PL-T691` a 30-day case is about 140 KiB. So whatever
   number is chosen now is a **validity** limit and has to be justified as one:
   the longest elapsed simulated time over which the shipped parameter set is
   claimed to hold. The slowest mode is the fat compartment at roughly 42 h
   (`PL-JDX0`), so a cap has to be many multiples of that to be worth having;
   30 days is about 17 of them.
2. **What does reaching it do?** `core/supported_ranges.py` refuses an
   out-of-range flow at the boundary, before computing. A run-time cap cannot
   refuse at entry — it is reached mid-run — so the two candidates are a halt
   that freezes the run with a stated reason, or a continue-with-a-declared
   caveat on the display. `CLAUDE.md` prefers an obvious failure to a
   plausible-looking value, which argues for the halt; the item is written that
   way and the recommendation is to keep it, but it is the owner's call because
   it is the one that a learner meets.

**`P1`/`safety` is the band, not a claim that it is urgent.** It sits with
`PL-GYH2` (bound or document the two gas volumes, which no supported range
covers) — same shape, same band: a declared domain with no boundary behind it,
where the interface will show a plausible number outside the range the model is
verified over. `docket check` pins `safety` to `P0` or `P1` and there is no `P0`
case here, so `P1` is where it lands. No `verify:` is recorded, deliberately:
the command depends on which answer part 2 gets, and a command written before
its work is how every wrong one in this store came to exist.

**Done when.** A run reaching the declared cap halts with a stated reason
rather than continuing, the cap and its provenance are declared in one place
the model and the interface both read, and `docs/MODEL.md` records the limit
alongside the other supported-input ranges. Regression test for the boundary.

**Found 2026-09-05** while reviewing the `PL-011` drop on
`origin/claude/simulation-architecture-review-qjlg4q`, which is correct about
memory and silent on this.

**Decision round 2026-09-07 — the fat time constant is the wrong yardstick.**

Part 1 above offers the fat group's roughly 42 h time constant as the scale a
cap should be "many multiples of", and reads 30 days as about 17 of them. That
inverts the relationship, and it is the sentence that would otherwise anchor the
answer near 30 days.

Many multiples of the slowest mode is the regime this document already declines
to stand behind. § "Published wash-in and elimination validation test" limitation 4 says it
outright — *"This model has no metabolism, which is why five minutes is the
limit"* — and rejects the two Yasuda papers' own multi-day elimination curves as
a comparison, because "over days the missing metabolism is no longer negligible,
and neither is the fat group's flow", which "Known limitations" records as about
twice the reachable resting measurement. So the further a run goes past the fat
time constant, the larger the share of the displayed trace that is the two
omissions rather than the model.

The fat time constant is therefore a **floor** on a useful cap — below about one
of them the fat trace stops showing what it exists to show — and not a
multiplier for one.

**What bounds it instead is the omitted metabolism.** Sevoflurane's is 2% to 5%
of the absorbed dose, and it is not a late effect: fluoride and HFIP appear in
plasma within minutes of the start of administration (Kharasch ED.
*Biotransformation of sevoflurane.* Anesth Analg 1995;81(6 Suppl):S27-38.
PMID 7486145, doi:10.1097/00000539-199512001-00005). What makes omitting it safe
over a case is the same review's finding that "metabolism of sevoflurane does not
contribute to the termination of clinical drug effect" — which holds while the
trace is dominated by ventilation and perfusion, and fails progressively once the
only thing still moving is the slow tail this model gives no sink to. That
review's dose-proportionality covers exposures of 0.35 to 9.5 MAC-hours; past
roughly ten MAC-hours even the size of the omission is unmeasured. Isoflurane and
desflurane are metabolized far less, so sevoflurane is the binding case and the
cap should be argued on it.

**Recommended answer to part 1: 24 hours**, declared as a supported-domain limit
on elapsed simulated time and argued as the clinical envelope checked against the
omission — not as a multiple of any time constant. Four supports:

- it clears every anesthetic this simulator exists to teach by a wide margin;
- it is about 0.6 of the fat time constant, so the fat compartment is still
  visibly loading and the slow-compartment teaching point survives intact, which
  a cap of a few hours would truncate;
- it sits inside the regime the primary source calls clinically negligible for
  metabolism, and near the outer edge of the exposure range over which that
  omission's size has been measured at all;
- it reads as a designed boundary in the interface, where "30 days" reads as a
  resource cap — which is what it was.

Like the four flow intervals, this is a declared envelope rather than a
discovered cliff: § "What a setting outside the range costs" already records that
the error did not explode at the boundary, and the same is true here.

**Recommended answer to part 2: halt, with three specifics the brief does not
yet state.**

1. **Compare step counts, not accumulated seconds.** § "Simulated time is a count
   of steps, not a running total" is what the reproducibility guarantee rests on;
   a float comparison would put the halt at a different step on different
   platforms and break deterministic replay at exactly the boundary a regression
   test pins.
2. **The halt must not present as a failure.** `PL-VM40`'s failure path exists
   and reusing it would tell a learner the simulator broke when it did the right
   thing. Reaching a declared limit is the model declining to extrapolate — the
   same act as `core/supported_ranges.py` refusing a cardiac output of
   1000 L/min — and it must read that way.
3. **Frozen, not terminated.** State stays inspectable and the chart stays
   readable; reset is the way out. A learner who has just watched a 24-hour
   washout has to be able to read the trace at the moment it stopped.

**Why not continue-with-a-caveat.** A flow refusal has a moment where the user
chose to leave the domain and can be told so. A run-time cap has none — nobody
opts in to hour 25 — so a caveat would sit beside a curve the learner is already
reading, which is the "polished graphics implying more certainty than the model
supports" failure rather than a guard against it.

**Out of scope, and named so it is not mistaken for a reason to raise the
number.** Volatile sedation in intensive care runs for days through an
anesthetic-conserving device (Al Aseri Z, et al. *The advantages of inhalational
sedation using an anesthetic-conserving device versus intravenous sedatives in an
intensive care unit setting: a systematic review.* Ann Thorac Med
2023;18(4):182-9. PMID 38058786, doi:10.4103/atm.atm_89_23). That is a real
teaching target and it is precisely the regime this model is wrong in. Reaching
it is a model extension — metabolism first — and belongs on `ROADMAP.md`, not in
this cap.

**Resolved 2026-09-07. Both parts answered by the project owner, who agreed
with the recommendations above.**

**The cap is 24 hours of elapsed simulated time**, declared as
`MAXIMUM_ELAPSED_SIMULATION_TIME_S` in `core/supported_ranges.py` beside the
three flow intervals, and argued there and in `docs/MODEL.md`
§ "Supported run length" against what the model omits rather than as a
multiple of the fat time constant. The citation is marked tier 2 in both
places: 24 hours is not computed from a metabolic rate, and saying so is what
keeps a review from reading as the authority for a stored value.

**Reaching it halts the run**, on an integer step-count comparison derived
once per step size, so the boundary falls at the same step on every machine
and deterministic replay still holds at it. The interval is closed like the
other four: at the shipped 0.1 s step a run completes exactly 864 000 steps
and lands on 86 400.0 s, and the 864 001st is refused before anything
advances.

**A new exception type carries the distinction the interface needs.**
`SimulationDomainLimitError` subclasses `SimulationExecutionError`, so a
caller that knows only the base classes stops the run - the safe default -
while one that catches it specifically knows nothing failed. `app/` reads it:
the status line says "Stopped - supported run length reached" rather than
"simulation error", the notice says which limit was reached and why it is
where it is instead of describing a rollback that did not happen, the colour
is not the failure's WARNING, and Start is disabled because the controller
would refuse it. `SimulationSnapshot.supported_limit_reason` is the field
that carries it, separate from `failure_reason` for the same reason.

**Regression cover.** The boundary is pinned from both sides in
`tests/unit/test_supported_ranges.py` and `tests/unit/test_simulation.py`,
including that a refused step leaves compartment state and the clock exactly
where they were; the exception's place in the hierarchy in
`tests/unit/test_exceptions.py`; the three stopped states in
`tests/integration/test_controller.py`; and the presentation in
`tests/unit/test_simulation_view.py`, which asserts the notice does *not* say
"error", "failed" or "rolled back".
