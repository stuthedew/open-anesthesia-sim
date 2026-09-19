---
id: PL-NM7X
title: Decide whether the simulator should open at 4 L/min fresh gas flow, which is above the flow contemporary practice is moving to
status: untriaged
added: 2026-09-19
---

**Problem.** Decide whether the simulator should open at 4 L/min fresh gas flow, which is above the flow contemporary practice is moving to
 — found while writing `docs/machine-survey.md` for `PL-4DCG`.

`src/anesthesia_sim/data/machines/reference_circle_system.json` holds
`default_fresh_gas_flow_l_min: 4.0`, and that file's `provenance_gap` states it
is a project convention with no published counterpart: chosen as "a routine
mid-range clinical fresh gas flow" that puts the circuit time constant at 90 s.
`PL-4DCG` was asked to source it, and the survey's answer is that no machine
publishes a startup flow that this session could reach — but that the second
half of the rationale, "routine mid-range", no longer describes the practice the
literature reports.

**What the survey found.** Contemporary work runs and recommends much lower
flows. Candries et al. randomised flows from 0.2 to 6 L/min in patients (*J Clin
Monit Comput* 2022;36(6):1881–1890, PMID 35318567); Hoffmann et al. ran 0.3 to
6 L/min (*Anesthesiology* 2025;142(6):1038–1046, PMID 40073301); Kalmar et al.
conclude that "routine clinical practice using what historically is called 'low
flow anaesthesia' (e.g. 2 L/min FGF) should be abandoned" in favour of automated
minimal-flow delivery (*J Clin Monit Comput* 2022;36(6):1601–1610, PMID
34978655). All three read at the abstract through the PubMed MCP server on
2026-09-19.

**Why it is the project owner's decision and not a session's.** It is what a
learner meets on first contact, which `.claude/rules/instruction-writing.md`
rule 14 places on the owner's side of the line. Both answers are defensible and
they teach different things:

- **Keep 4.0.** The 90 s time constant makes the machine's own lag a visible,
  separable phase of the early rise, which is the circle system's most-taught
  point and the thing this simulator is unusually good at showing. At 0.5 L/min
  it is 12 minutes, and the lesson stops being legible inside a teaching run.
- **Lower it.** A simulator that opens at a flow the field is actively moving
  away from teaches that flow as normal, and the environmental argument is now
  part of the curriculum rather than an aside.

A third option exists and may be the best of the three: keep 4.0 as the opening
value and say on the interface, or in the documentation, that it is chosen for
legibility rather than as a recommendation.

**Where.** `src/anesthesia_sim/data/machines/reference_circle_system.json`
(`default_fresh_gas_flow_l_min` and its `provenance_gap`); `docs/MODEL.md`
§ "Parameter provenance"; `docs/machine-survey.md` § "(a2)".

**Done when.** The value is either changed or kept with a recorded decision that
says it is a teaching choice rather than a clinical convention, and the data
file's rationale no longer describes 4 L/min as mid-range practice.
