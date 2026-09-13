---
id: PL-RFLN
title: Settle what causes desflurane's five-minute washout residual, which PL-73G7 narrowed to end-tidal sampling or the published datum
priority: P1
effort: M
status: done
classes: science
feature: model-spec-accuracy
touches: docs/MODEL.md, tests/reference/test_published_wash_in_and_elimination.py
added: 2026-09-08
closed: 2026-09-13
pr: 533
verify: uv run pytest tests/reference/test_published_wash_in_and_elimination.py -q && grep -q 'def test_no_apparatus_dead_space_reaches_desflurane_s_published_elimination' tests/reference/test_published_wash_in_and_elimination.py
---

**Problem.** Settle what causes desflurane's five-minute washout residual, which PL-73G7 narrowed to end-tidal sampling or the published datum

**Where PL-73G7 left it.** With the rebreathing circuit removed as a
diagnostic, this model reproduces sevoflurane's and both isoflurane cohorts'
published five-minute `F_A/F_A0` and washes desflurane out 2.33 published SD
too fast. `docs/MODEL.md` § "Desflurane's residual, and why the parameter file
was not changed" is the authority and carries the whole account; it is not
restated here. What it rules out: desflurane's blood:gas and tissue:gas
coefficients, alveolar ventilation, cardiac output, the fast capacity this
model omits, a non-ideal lung, and residual rebreathing in the published
apparatus. Each fails the same way - it moves sevoflurane and isoflurane as
much as desflurane or more, and the published rows have no room for that, or
it moves desflurane the wrong way.

**The two candidates left, and what would separate them.** Either end-tidal
sampling in a lung with ventilation-perfusion dispersion, whose bias inflates
`F_A/F_A0` at both ends and grows as solubility falls, or the published value
itself. The first needs a weighting neither abstract gives: the flow-weighted
alveolar reading of the same calculation moves every agent the wrong way, so
the hypothesis stands entirely on which units the end-tidal sample came from.

**Route.** The methods sections of Yasuda et al. Anesthesiology
1991;74:489-98 (PMID 2001028) and Anesth Analg 1991;72:316-24 (PMID 1994760):
the breathing system, how end-tidal gas was sampled, and the alveolar
ventilation measured through the elimination. Neither is in PubMed Central and
neither is held in `docs/references/`, so this needs a copy the project owner
can supply, and it is worth deciding whether that is worth doing at all before
any work is scheduled. Failing that, a test-only multi-alveolar-compartment
diagnostic could bound the end-tidal weighting's size, which would say how
much of the residual it could possibly carry without settling that it does.

**Done when.** Either the cause is named against the methods sections, or the
question is recorded as unanswerable from what this project can reach and
`docs/MODEL.md` says so in place of the two open candidates.

**Why it matters.** `docs/MODEL.md` currently carries two open candidates for a
disagreement between this model and a published measurement, and a reader of the
specification cannot tell which. The residual is real and bounded - 2.33
published SD too fast on desflurane's five-minute washout, with sevoflurane and
both isoflurane cohorts reproduced - so the question is not whether the model is
adequate but what the specification is allowed to claim about why it misses.
Leaving two candidates standing is honest; leaving them standing indefinitely
without saying they cannot be separated is not.

**Decision needed, and it is the project owner's.** Whether to obtain the
methods sections of Yasuda et al. Anesthesiology 1991;74:489-98 (PMID 2001028)
and Anesth Analg 1991;72:316-24 (PMID 1994760). Neither is in PubMed Central nor
held in `docs/references/`, so this needs a copy the owner supplies - the
interlibrary-loan route `PL-GN8C` records is the demonstrated one, and narrowing
the request to the methods pages is what made the last such request cheap enough
to place. If the answer is no, the fallback is the test-only
multi-alveolar-compartment diagnostic, which bounds how much of the residual
end-tidal weighting could carry without settling that it does.

No work should be scheduled on this before that answer, which is why it sits at
`needs-decision` rather than `ready` despite being fully diagnosed.

## Reachability re-checked 2026-09-13: the premise holds, the decision is unchanged

Checked against the source rather than carried from this item's own text, since
the whole decision rests on it. Both papers fetched through the PubMed MCP
server: `identifiers` carries `pmid` and `doi` for each and **no `pmc` entry**,
so PubMed Central holds neither and the methods sections remain unreachable by
any route this project has. Nothing has changed that would let the question be
settled without a copy.

**What the abstracts do carry**, which is worth recording so the next session
does not re-fetch them: the five-minute `F_A/F_A0` values this comparison uses,
with their spreads - desflurane 0.14 +/- 0.02, isoflurane 0.22 +/- 0.02 and
halothane 0.25 +/- 0.02 in the *Anesthesiology* paper, sevoflurane 0.157 +/-
0.020 and isoflurane 0.223 +/- 0.024 in *Anesth Analg* - the 30-minute
administration, the inspired fractions, the 65-70% nitrous oxide both protocols
ran, and the recovery percentages `docs/MODEL.md`'s fourth caveat quotes. `F_A`
is written "alveolar (end-tidal)" in both, so this item's first candidate rests
on a sampling convention the abstract states rather than one inferred.

**What they do not carry** is exactly the Route section's list: the breathing
system, how the end-tidal sample was drawn, and the alveolar ventilation
measured through the elimination. The first candidate "stands entirely on which
units the end-tidal sample came from", and no abstract answers that.

**Nitrous oxide was checked and is not a missing candidate.** `docs/MODEL.md`
already carries it as the first of four caveats bounding the comparison - both
protocols ran 65-70% N2O concurrently, giving the measured curves a second-gas
effect this model cannot reproduce, "in a direction that is not obviously
conservative". Recorded here only so the next session does not raise it as new.

So **Decision needed** above stands as written and is still the owner's: obtain
the methods pages, or record the question as unanswerable and say so in
`docs/MODEL.md` in place of the two open candidates.

## Both methods sections read 2026-09-13, and the blocker is gone

The project owner supplied both papers. Neither is in PubMed Central and
neither is held in this repository; they were read and the findings recorded
here and in `docs/MODEL.md`, which is the route `PL-XJ5P` is deciding about and
the third time it has been exercised.

**What the Route section asked for, answered.** Yasuda 1991 *Anesthesiology*
(PMID 2001028) § "Materials and Methods":

- **The breathing system.** A nonrebreathing circuit. The expiratory limb is
  corrugated Teflon into a 1-l aluminium mixing chamber, whose output goes to a
  spirometer; the chamber supplies the mixed expired sample. At exactly 30 min
  administration stopped and **the circuit was exchanged for a fresh
  inspiratory and expiratory one**, so the potent agents' inspired fraction
  during elimination is zero by construction.
- **How end-tidal gas was sampled** - the fact the hypothesis "stands entirely
  on". **From a port at the tracheal tube**, with about 50 ml of corrugated
  Teflon dead space interposed between that port and the connection to the
  nonrebreathing valve, stated to protect the end-tidal sample from
  contamination with inspired gas. Inspired gas came from a port on the
  nonrebreathing valve. Mixed expired gas came from the mixing chamber and is
  reported separately as `F_M`.
- **Ventilation.** Minute ventilation was measured, not alveolar ventilation.
  The alveolar fraction of ventilation was derived from
  `F_M = f_A x F_A + f_D x F_I`, averaged over the 10-, 15- and 20-minute
  samples.

Two further protocol facts worth having recorded: all three potent agents were
given **simultaneously** from one cylinder (2.0% desflurane, 0.4% isoflurane,
0.2% halothane, balance 35% oxygen / 65% nitrous oxide), and 65% nitrous oxide
**continued through the first 150 min of elimination** - so at the five-minute
point nitrous oxide is being maintained rather than eliminated, which removes
its outpouring as a confounder there while leaving its continuing uptake.

**The *Anesth Analg* paper (PMID 1994760) does not site its ports.** It says
only that ports permitted sampling of end-tidal, mixed expired and inspired
gas. Everything else is described in near-identical terms - same nonrebreathing
circuit, same corrugated Teflon limb, same 1-l chamber, same exchange at 30
min, same 65% nitrous oxide to 150 min, seven volunteers on 1.0% sevoflurane
and 0.6% isoflurane. **The difference is one of description, not of
demonstrated equipment**, and must not be read as a cohort-specific mechanism.
It is the same group in the same year and this paper refers to the other as a
parallel study.

## What this changes, and what it does not

**Candidate 1 is unblocked, not confirmed.** `docs/MODEL.md` recorded the
obstacle as "the flow-weighted alveolar reading of that same calculation moves
every agent the wrong way, so the hypothesis rests entirely on the end-tidal
weighting, and neither abstract says how end-tidal gas was sampled". The
methods say how: a tracheal-port, last-gas sample, explicitly distinct from the
mixed expired sample the study reports as `F_M`. So the reading the fifth table
row rules out is `F_M`, not the `F_A` the published ratio is built from. What
remains is to compute the **end-tidal-weighted** bias rather than the
flow-weighted one and bound how much of 2.33 SD it could carry.

**A third mechanism is now sourced rather than assumed, and it is cheap to
test.** The sixth table row rejected rebreathing at an assumed `F_I/F_A` of
0.30. The methods give the apparatus its actual volume - about 50 ml, re-inspired
each breath - which against a normocapnic tidal volume in a paralysed 76 kg
adult is of the order of a tenth of that. So the row excluded rebreathing at a
magnitude the apparatus does not have, and says nothing yet about rebreathing
at the magnitude it does. `_eliminate_without_rebreathing()` in
`tests/reference/test_published_wash_in_and_elimination.py` already carries the
machinery.

**Done when** (replacing the version above, which assumed the papers were
unreachable). The rebreathing row is re-run at the apparatus's sourced dead
space and `docs/MODEL.md` records the result; on that result, either the cause
is named or the end-tidal-weighted bound is what is still missing and the
specification says so in place of the open candidates.

**Order, and it matters.** Run the cheap diagnostic first. It is a re-run of
machinery that exists, at a number now taken from the primary source, and if it
closes the gap the multi-alveolar-compartment work is unnecessary. Building
that bound first would spend an `M` of effort on a result the item's own brief
says "would say how much of the residual it could possibly carry without
settling that it does".


## Settled 2026-09-13: the apparatus's dead space is not the cause, and the framing it was asked under was wrong

**The diagnostic the brief ordered first, run.** The result is a close, and the
cause is *not* named — which the "Done when" above allows for, and the
specification now says so in place of the two open candidates.

**The framing had to change before the sourced number could be used, and that
is the finding.** The sixth candidate row rejected "residual rebreathing in the
published apparatus" at an assumed `F_I/F_A` of 0.30, and this item's brief
proposed re-running it at the apparatus's sourced 50 ml — of the order of a
tenth of that ratio. That re-run would have been meaningless. The 50 ml of
corrugated Teflon holds alveolar gas at end-expiration and fresh gas at
end-inspiration, which makes it a **series dead space**, and in a model with
one perfectly mixed alveolar compartment a series dead space is not a non-zero
inspired fraction at all:

    alveoli receive V_T carrying V_D * F_A,  expel V_T carrying V_T * F_A
    net = -(V_T - V_D) * F_A  ==  V_A_dot * (F_I - F_A)  at F_I = 0

provided `V_A_dot` is the true alveolar ventilation `(V_T - V_D) * f`. So the
apparatus's dead space is an alveolar-ventilation decrement of `V_D * f` and
nothing else. Treating it as an `F_I` describes this model's circuit, not
Yasuda's apparatus.

**Measured, it fails as a common-mode mechanism.** Run at 50 ml across the
conventional respiratory rates for a paralysed normocapnic adult, against the
-2.33 SD desflurane sits at with no dead space:

| f (/min) | V_A | Desflurane | Isoflurane n=8 | Worst wash-in |
| --- | --- | --- | --- | --- |
| 6 | 3.70 | -1.89 SD | +1.59 SD | -0.42 SD |
| 8 | 3.60 | -1.73 SD | +1.82 SD | -0.63 SD |
| 10 | 3.50 | -1.56 SD | +2.05 SD | -0.85 SD |
| 12 | 3.40 | -1.38 SD | +2.30 SD | -1.08 SD |

It carries 0.44 to 0.95 SD of the 2.33 — a quarter to two fifths — and buys
that by pushing the isoflurane cohort that was inside its spread at +0.94 SD
out to between +1.59 and +2.30. The wash-in comparison sets its own ceiling at
11 breaths per minute, and at that largest admissible decrement desflurane is
still 1.48 SD short with both isoflurane cohorts outside their spreads. It is
the second candidate row — alveolar ventilation — at a sourced magnitude rather
than a fitted one, and it fails the same way.

**Whether any decrement is owed at all is undetermined, and that is now the
live question.** Yasuda derived the alveolar fraction of ventilation from
`F_M = f_A x F_A + f_D x F_I`, and the 1-l mixing chamber supplying `F_M` sits
beyond the nonrebreathing valve — so the 50 ml that is re-inspired never
reaches it, and their derived `f_A` is `(V_T - V_D_anat - V_D_app)/V_T`,
already netting the apparatus out. A comparison run at their alveolar
ventilation must not subtract it again. This model runs at 4.0 L/min, which
`data/patients/reference_adult.json` records as a program default with no
primary source, and which is neither quantity. `PL-ZDWL` reads the study's own
figure.

**What is left, recorded in `docs/MODEL.md` in place of the two open
candidates.** One reachable candidate and one that is not: `PL-03ZG` bounds
candidate 1's end-tidal-weighted bias, which the methods unblocked and nothing
has demonstrated; candidate 2, the published value itself, no measurement this
project can run will settle.

**`verify:` was changed, and deliberately.** It named
`test_rebreathing_at_the_published_apparatus_dead_space`, which would have
baked the mischaracterisation above into a test name. The tests added are
`test_no_apparatus_dead_space_reaches_desflurane_s_published_elimination`
(parametrised over the four rates) and
`test_the_apparatus_dead_space_moves_every_cohort_together` (the common-mode
half). Both were mutation-checked: raising `APPARATUS_DEAD_SPACE_L` to 150 ml
fails all five cases.

**`touches` was widened** from `docs/MODEL.md` alone to include
`tests/reference/test_published_wash_in_and_elimination.py`, which the item's
own `verify:` command had always implied.
