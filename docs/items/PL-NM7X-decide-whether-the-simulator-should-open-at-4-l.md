---
id: PL-NM7X
title: Decide whether the simulator should open at 4 L/min fresh gas flow, which is above the flow contemporary practice is moving to
priority: P1
effort: S
status: done
classes: science
feature: anesthesia-machine
touches: src/anesthesia_sim/data/machines/reference_circle_system.json, docs/MODEL.md, docs/machine-survey.md
added: 2026-09-19
closed: 2026-09-20
payoff: stops the simulator's opening fresh gas flow teaching 4 L/min as routine practice when its own survey found the field has moved below it
verify: grep -q 'teaching default, not a clinical recommendation' src/anesthesia_sim/data/machines/reference_circle_system.json
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

**Why it matters.** The opening fresh gas flow is the first clinical number a
learner meets, and a default carries an implicit recommendation whether or not
anyone intends one. The file's own rationale calls 4 L/min "a routine mid-range
clinical fresh gas flow", which the survey's sources contradict, so the
simulator currently teaches a practice norm on the authority of a sentence that
is no longer true. Under `CLAUDE.md`'s safety-critical standard a correct number
with a wrong provenance is still a presentation failure.

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

**Decision (project owner, 2026-09-20, ratified, over lowering the default to
match contemporary low-flow practice).** Keep `default_fresh_gas_flow_l_min` at
4.0, and rewrite the rationale so it reads as a teaching choice rather than as a
description of practice.

The case that was put and accepted: an unlabelled default teaches a norm
whatever number it holds, so moving to 0.5 L/min relocates the problem instead
of removing it — and 0.5 would carry the same unsourced provenance gap this item
objects to, since no machine publishes a startup flow either. What 4.0 buys is a
circuit time constant near 90 s, which makes the machine's own lag a separable
phase ahead of patient uptake inside a run a learner will sit through; at
0.5 L/min that is roughly 12 minutes and the demonstration no longer completes.
What is actually wrong today is the sentence, not the number.

The third option in the section above — also surfacing the caveat on the
interface — was **not** taken in this round. It is a separate change to
learner-facing display and is not part of this item's scope.

**Done when.** `src/anesthesia_sim/data/machines/reference_circle_system.json`
no longer describes 4 L/min as "a routine mid-range clinical fresh gas flow",
and its `provenance_gap` instead records the value as a **teaching default, not
a clinical recommendation** — that exact phrase, so the claim is greppable —
with the time-constant legibility reason and this decision's date. `docs/MODEL.md`
§ "Parameter provenance" and `docs/machine-survey.md` § "(a2)" are corrected to
match, since both restate the superseded rationale.

**Sources behind the supersession**, gathered by `PL-4DCG`'s survey session at
abstract level through the PubMed server on 2026-09-19 and **not yet confirmed
against full text** — the implementing session confirms them before the
citations land in `docs/MODEL.md`: Candries et al., *J Clin Monit Comput*
2022;36(6):1881–1890 (PMID 35318567); Hoffmann et al., *Anesthesiology*
2025;142(6):1038–1046 (PMID 40073301); Kalmar et al., *J Clin Monit Comput*
2022;36(6):1601–1610 (PMID 34978655).

**Confirmation done 2026-09-20, and one of the three does not support the claim
it was cited for.** Route and depth for each, per
`.claude/rules/citing-sources.md`:

- **Kalmar et al.** (PMID 34978655) — **read at full text** from PubMed Central
  (PMC9637609). The quoted sentence is verbatim and is the abstract's closing
  one; the body's Conclusion restates it without the parenthesised 2 L/min. It
  holds, with its design stated: a single-centre retrospective, 25 cases per
  group, Flow-i workstations only, so it is a *recommendation about what
  practice should be* rather than a measurement of what it is. What it does
  establish about practice is its own comparator — a fixed 2 L/min group it
  calls conventional low flow, already below this project's 4.0.
- **Candries et al.** (PMID 35318567) — abstract confirmed against the PubMed
  record; no PubMed Central full text, and not in the private reference corpus
  (checked 2026-09-20). Its 0.2–6 L/min is the *protocol* of a Gas Man
  validation study, chosen to span a wide envelope, and is not a report of
  practice.
- **Hoffmann et al.** (PMID 40073301) — abstract confirmed against the PubMed
  record; no PubMed Central full text, and not in the private reference corpus
  (checked 2026-09-20). It is an **in vitro** bench study into a 2 L test lung,
  and its 0.3–6 L/min range *contains* 4, 5 and 6 L/min, settings the paper
  describes as reflecting clinical conditions. **It does not support "the field
  has moved below 4 L/min"; if anything it reads the other way.**

Neither of the two unreachable full texts is needed: every claim made from them
is about a protocol flow range, and both ranges are stated in full in the
abstracts.

**This does not reopen the decision — it strengthens it.** The ratified answer
was to keep 4.0 and fix the sentence. A weaker supersession makes that more
clearly right, not less, and makes the relabelling *more* necessary rather than
less: the data file should now make no claim about clinical practice in either
direction, which is what it does. What changed is the supporting text, which
says what each source establishes instead of reading three flow ranges as one
finding.

**Not changed, deliberately.** `ROADMAP.md`'s v0.5.0 gate entry quotes the old
"routine mid-range clinical fresh gas flow" wording as the defect this entry was
frozen against. A frozen gate entry is a record of the finding at freeze time,
and the entries for closed items are left as written, so it stays.
