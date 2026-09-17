---
id: PL-W8DQ
title: The four slider active tracks use ACCENT and miss the non-text minimum
priority: P3
effort: S
status: done
classes: defect, ux
feature: presentation-safety
milestone: v0.4.26
touches: src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/simulation_view.py, tools/contrast_check.py
added: 2026-09-02
closed: 2026-09-16
pr: 621
verify: python3 tools/contrast_check.py && ! grep -q '("ACCENT", "PANEL"): ' tools/contrast_check.py
---

> **This fix rides the Qt port, not Flet.** `ROADMAP.md` § "Completed: v0.4.26 -
> the interface moves to Qt" names this item under "Fixes this port carries":
> the defect lives in code that milestone rewrites from scratch, so fixing it
> on Flet means writing the same lines twice. Project owner, 2026-09-10.

**Problem.** All four parameter sliders - fresh gas flow, delivered
concentration, alveolar ventilation and cardiac output - draw their active
track and thumb in `ACCENT` (`app/simulation_view.py:320`, `:336`, `:346`,
`:356`). Against the panel they sit on, `ACCENT` measures **2.93:1**, below
WCAG 2.2 SC 1.4.11's 3:1 for user-interface components. It misses by 0.07,
which is small enough that it would never be spotted by eye and large enough
that the criterion says it is not met.

**Why it matters.** The active track is how each slider shows where its value
sits in its range - the only continuous cue for a control whose numeric readout
is a separate element beside it. These four are the entire input surface of the
simulator: every value the model is run with is dialled here. A reader who
cannot see the filled portion against the unfilled has to fall back on the
readout, which turns a direct-manipulation control into a number they have to
read twice.

Found while doing `PL-30P6`, which took `ACCENT`'s other failing role - text -
and gave it a token of its own. This is the remaining half, and it is the reason
that split was worth making: one constant was carrying a text role at 4.5:1, a
trace role at 3:1 and a control role at 3:1, and no single value satisfies all
three.

**Approach: candidate 1, and it is no longer conditional.** `PL-GVXP` closed on
2026-09-07 and answered the question this item was waiting on. The alveolar
trace now carries its own `ALVEOLAR_COLOR` in `app/simulation_view.py`, so
`ACCENT` is not a chart colour any more: darkening it moves the four slider
tracks and nothing else.

The reason the two split is worth carrying into the fix. A chart trace has to
clear 3:1 against the panel under simulated dichromacy as well as as displayed,
and has to stay separable from five sibling traces; a slider track has neither
constraint - it is one graphical object against the panel behind it. So the
value here is bounded by exactly one requirement, and picking it is a
one-dimensional problem.

So: darken `ACCENT` until it clears 3:1 on `PANEL`, keeping hue and saturation
as `ACCENT_TEXT` did (that constant is the same hue at 5.00:1, so the target
sits between the two). The rejected alternative was a fourth colour constant
for the sliders, which is now pointless - `ACCENT` *is* the sliders' constant.
The `KNOWN_SHORTFALLS` entry for `("ACCENT", "PANEL")` goes in the same change;
the checker errors on a shortfall that starts passing.

**Where.** `app/theme.py` (`ACCENT`); `app/simulation_view.py:320`, `:336`,
`:346`, `:356`; `tools/contrast_check.py`'s `KNOWN_SHORTFALLS`.

**Done when.** The slider active track meets 3:1 against the panel, the
shortfall entry is gone, and whichever route was taken is recorded so the next
reader knows whether `ACCENT` is still shared with the chart.

**Depends on.** Nothing. It sequenced after `PL-GVXP` (separate the six chart
traces by more than colour) to avoid picking a value that item would replace;
that item closed on 2026-09-07 and this one is unblocked.

**Deferred to the Qt port, 2026-09-13 (`PL-D143`, project owner).** `status:
blocked`, `blocked-by: PL-L9RD` - the Qt re-expression of app/theme.py, where ACCENT is defined. `bin/docket next` therefore stops
offering work that cannot be done until that port lands. The owner's 2026-09-10
note above is the decision; this only makes the queue agree with it.

It is blocked on the **item** rather than on the port's version because the two mean
different things in this store: `blocked-by: <version>` says an item is waiting
for a milestone to be *scoped*, and `docket check` promotes it back to `ready`
the moment that section carries its four subsections - which the port's already
does, so the version form raised "ready to promote" on every run. The port item
is the edge that is actually true.

## Closed 2026-09-16: `ACCENT` is `#17A192`, and the shortfall ledger is empty

**Unblocked by `PL-L9RD` closing**, which is what the deferral was waiting for.
The route taken is the one this item already chose - candidate 1, darken
`ACCENT` - and nothing about it changed, because the Qt port turned out not to
have redecided the palette at all.

**The value.** `#18A999` → `#17A192`, giving **3.21:1** against `PANEL` where it
measured 2.93:1. Chosen the same way the six traces were re-picked: the
*lightest* shade clearing **3.2:1** rather than 3.0:1, so the shipped value is
not itself the boundary case the next edit trips over, with hue and saturation
held - 173.4 deg and 0.858 become 173.5 and 0.857, which is 8-bit rounding
rather than a change. The accent family still reads as one colour, and
`ACCENT_TEXT`'s description of itself as a uniform darkening of `ACCENT` stays
true.

**Bounded by exactly one requirement, which is why this was a
one-dimensional pick.** `PL-GVXP` had already given the alveolar trace its own
`ALVEOLAR_COLOR`, so `ACCENT` is no longer a chart colour: it had neither the
simulated-dichromacy floor nor the six-way separation constraint to satisfy.
Against the `GRIDLINE` groove the filled track sits in, darkening only
increases the separation, so the one adjacency the declared pair does not name
moves the right way too.

**The ledger is now empty and the mechanism stays.** `KNOWN_SHORTFALLS` held
this as its last entry; `tools/contrast_check.py` reports **24 of 24 declared
requirements meeting WCAG 2.2 AA, 0 known shortfalls, 0 errors**. The comment
above the dict says explicitly that an empty dict is not a reason to delete it -
a shortfall that is found, owned and visible is what it replaced a
comment-nobody-checks with, and the next one needs somewhere to go that is not
a silent failure.

**Docs swept**, and the distinction worth recording is which `#18A999` mentions
are live and which are history. `app/theme.py:10` quoted 2.93:1 as a live fact
about why the accent is not legible as text and is now 3.21:1 - the argument is
unchanged, since SC 1.4.3 asks 4.5:1 and neither value meets it.
`docs/MODEL.md` § the six compartment traces and `tools/contrast_check.py:250`
both say the *alveolar trace was* `#18A999`, which is past tense and still
true. `docs/MODEL.md:5706` describes `ACCENT`'s role rather than its value and
needed nothing. `tests/unit/test_contrast_check.py:138` uses the string in an
identity assertion where any colour would do.
