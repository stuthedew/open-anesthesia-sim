---
id: PL-V9S0
title: docs/MODEL.md's paragraph 'The fresh gas flow control offers the intersection, read from the circuit' does not say that a machine profile opening the run off the slider's 0.1 L/min grid is refused, which PL-1KQ9 built; held back because docs/MODEL.md was declared by PL-HQF5's open pull request (found building PL-1KQ9)
priority: P3
effort: S
status: done
classes: docs
feature: anesthesia-machine
touches: docs/MODEL.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-10-18
closed: 2026-10-18
pr: 1578
payoff: a profile author who meets the off-grid refusal finds the rule in the paragraph it cites
verify: grep -q "test_an_opening_fresh_gas_flow_off_the_slider_grid_is_refused" docs/MODEL.md
---

**Problem.** docs/MODEL.md's paragraph 'The fresh gas flow control offers the intersection, read from the circuit' does not say that a machine profile opening the run off the slider's 0.1 L/min grid is refused, which PL-1KQ9 built; held back because docs/MODEL.md was declared by PL-HQF5's open pull request (found building PL-1KQ9)

The paragraph in `docs/MODEL.md` § "The model's envelope and a machine's
deliverable range are two claims" says how the fresh gas flow slider's range
is offered. `PL-1KQ9` added a second rule beside it: a machine profile whose
opening flow is not one of the slider's 0.1 L/min steps inside that range is
refused when the dashboard builds its controls, and the refusal cites this
paragraph. The paragraph does not say so yet. `PL-1KQ9` left it alone because
`PL-HQF5`'s open pull request declared `docs/MODEL.md`.

**Why it matters.** `docs/MODEL.md` is the specification of the model and its
interface contract, and the refusal points a reader at a paragraph that does
not mention it. A profile author who meets the refusal at launch should find
the rule where the message sends them.

**Done when.** The paragraph says that a profile's opening flow must be one
of the offered steps, and why: a slider position is a printed value
(`PL-25KS`, decision D4). It names
`test_an_opening_fresh_gas_flow_off_the_slider_grid_is_refused` among the
tests that hold it. Start it after `PL-HQF5`'s pull request has merged.

**Written 2026-10-18.** The paragraph now says that a machine profile whose
opening flow is not one of the offered steps is refused when the dashboard
builds its controls, gives the reason from `PL-25KS` decision D4, and names
`test_an_opening_fresh_gas_flow_off_the_slider_grid_is_refused`.
