---
id: PL-8ZJQ
title: Davis and Mapleson 1981 gives a published, quantified blood-pool structure, which is the source PL-3YZW's 1.0 L venous pool has never had
priority: P1
effort: M
status: done
classes: science
feature: model-spec-accuracy
milestone: v0.4.7
touches: src/anesthesia_sim/data/patients/reference_adult.json, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-07
pr: 423
not-delegable: No command can prove that a person read Davis and Mapleson 1981, and the outcome is a provenance judgment either way - adopt a volume with that lineage, or record why the 1.0 L mixing volume is kept and what it is not. A `verify:` could only check that some sentence had been written into the data file, which is exactly the thing that must not be gameable on a provenance item (the same argument PL-7HDS records).
---

**Problem.** `venous_blood_volume_l` is 1.0 in
`src/anesthesia_sim/data/patients/reference_adult.json` and has no counterpart
in the Gas Man Workbook table the file cites - the Workbook's `Blood` row reads
5.00 L, which is a blood volume rather than this model's venous mixing pool.
`PL-3YZW` carries that gap and has had no candidate source to close it with.

Lerou and Booij (Br J Anaesth 2001;86:12-28, read at full-text depth
2026-09-06) have one. Their Table 7 partitions total blood volume, taken as
0.07 x body mass, into arterial 0.2 and venous 0.8, and then splits the venous
share into four named pools "that serve to mimic circulation times in the
body" - adipose tissue 0.111, central 0.126, lean tissue 0.364 and viscera
0.399, each as a fraction of venous volume. The caption attributes the
structure to Mapleson and to **Davis NR, Mapleson WW. Structure and
quantification of a physiological model of the distribution of injected agents
and inhaled anaesthetics. Br J Anaesth 1981;53:399-405** - a journal article
with a purpose-built structure for exactly this question, and reachable where
the 1981 monograph in `PL-7HDS` is not.

**Why it matters.** The stored 1.0 L is the least defensible number in the
file: it is not the physiologic venous blood volume, it matches nothing in the
cited table, and its only role is to set a mixed-venous time constant of 12 s.
A published model that quantifies the same structure is the difference between
"a mixing volume chosen to give 12 s" and a value with a lineage.

**One arithmetic coincidence, recorded as a thing to check and not as a
finding.** At 70 kg their total blood volume is 4.9 L, of which the *arterial*
share is 0.2 x 4.9 = 0.98 L - within 2% of this file's 1.0 L *venous* pool.
Their arterial volume over their cardiac output is 0.98/5.345 = 11 s, against
this model's 1.0/5.0 = 12 s. The two compartments are not the same thing and
this model has no arterial volume at all, since it sets F_a = F_A; so this is
either coincidence or a sign that the stored pool is doing an arterial
compartment's job under a venous name. Which of those it is, is worth knowing
before any value is changed, and it is not established here.

**Where.** `src/anesthesia_sim/data/patients/reference_adult.json`
(`venous_blood_volume_l` and its `sources` entry); `docs/MODEL.md` - "Parameter
provenance" and the compartment definitions. Work it with `PL-3YZW`, which
states the gap this would close, and note `PL-024` (what the venous pool does
to early mixed-venous readings) reads on the same compartment.

**Done when.** Davis and Mapleson 1981 has been read at the source, and the
file either adopts a blood-pool volume with that provenance or records why the
1.0 L mixing volume is kept and what it is not - with the arterial/venous
question above answered rather than left open.

**Triaged `ready` rather than `blocked`, and `PL-3YZW` now waits on this.**
`PL-3YZW` (the venous volume's missing provenance) was triaged earlier the same
day to wait behind the 1981 monograph, on the reasoning that it was the only
untried upstream for a stored volume. `#417` established otherwise, and
this item carries the reachable candidate, so that block was re-pointed here.
The two are one branch, as the brief above says.

**Read at the source 2026-09-07, and the arterial question is answered against
the arterial reading.** The project owner supplied the paper. Its standard man
is 70 kg with a total blood volume of 5189 ml and a cardiac output of
6480 ml/min (Table I caption, Table III), and page 400 says in terms that **for
models of inhaled anaesthetics** the two venous pools may be combined, "in which
case it would be marginally more accurate to make the arterial pool 799 ml
(15.4% of the total blood volume) and the combined venous pool 1222 ml (23.6%)".

- **The arterial hypothesis does not survive the primary.** It rested on Lerou
  and Booij's arterial fraction of 0.2 - 0.98 L at their 4.9 L total, within 2%
  of the stored 1.0 L. Davis and Mapleson's own arterial pool for this model
  class is 799 ml, 15.4% rather than 20%, so the coincidence is with a secondary
  rendering rather than with anything the primary states. Their **venous** pool
  is the structurally correct comparison: one well-stirred pool carrying tissue
  return, which is exactly what `V_v` is here.
- **The time constants nearly agree, and that is the interesting number.**
  1222/6480 = 11.3 s against this model's 1.0/5.0 = 12.0 s - the closest any
  source has come to this parameter. It is a property of the time constant
  rather than of the volume, and it is not evidence of a lineage: nothing
  documents Gas Man as having taken anything from this paper.
- **Tier 2, not tier 1.** The Appendix (pages 402-404) derives the pool volumes
  from ICRP (1975) blood distribution to reproduce circulation times - 25.9% or
  1344 ml of the total is of arterial composition, of which 17.2% or 623 ml sits
  in the 3621 ml of local systemic pools, leaving 721 ml central arterial and
  847 ml central venous in the exact scheme. Derived, not measured, so
  `docs/MODEL.md` § "Source hierarchy" does not admit it as the authority for a
  stored value on its own.
- **Recorded, not adopted.** The reading is written into the data file's
  `sources` and into `docs/MODEL.md` § "Parameter provenance", which is the half
  that holds under either answer below. `PL-3YZW` is closed on it: the stored
  1.0 L is now on record as untraceable to any cited source.

**Decision needed.** Does `venous_blood_volume_l` stay at 1.0 L, or move to
1.222 L with Davis and Mapleson's provenance?

- **Keeping it** preserves comparability with the Gas Man parameter set the rest
  of this file exists to reproduce, and leaves one stored value with no lineage -
  which is now documented rather than silent.
- **Adopting 1.222 L** gives the parameter its first published provenance, and
  moves the mixed-venous time constant from 12.0 s to 14.7 s at the stored
  5.0 L/min. That changes the mixed-venous trace through the first minute of
  every simulation, so it is a displayed-value change under `CLAUDE.md`'s
  safety-critical standard and wants the project owner's call rather than a
  session's. It would also be the first parameter in this file to leave the Gas
  Man set, which is a precedent as much as a value.
- **A third option exists and is worse than either**: scaling their 23.6% onto
  the Workbook's own 5.00 L blood row gives 1.18 L, which is neither source's
  number and would have to be defended as this project's own synthesis.

Adopting would also want `PL-BD94` (the key's name reads as the physiologic
venous blood volume) decided in the same pass, since a rename and a revalue on
one key is one edit rather than two.

**Decided 2026-09-07 by the project owner: adopt.** `venous_pool_volume_l` is
1.222 L, from Davis and Mapleson's combined venous pool for inhaled-anaesthetic
models, and it is the first value in this file to carry a source other than the
Gas Man Workbook.

**What tipped it was `PL-3YZW`'s answer, not this reading.** The case for
keeping 1.0 L had rested on preserving Gas Man comparability. Tracing the value
through the repository's own history showed it was never part of the Gas Man
set: it entered at v0.1.0 under a Workbook citation belonging to its
neighbours, and all four sources ever cited for it have now been read without
finding it. So keeping it preserved nothing, and the choice was between a value
with tier-2 published provenance and a value with none.

**Measured before the change was made, not asserted after it.**

| Comparison | At 1.0 L | At 1.222 L |
| --- | --- | --- |
| Wash-in `F_A/F_I` at 30 min, four cohorts | +0.15, +0.31, +0.79, +0.38 SD | +0.16, +0.31, +0.79, +0.38 SD |
| Elimination `F_A/F_A0` at 5 min | +3.67, +4.02, +1.02 SD | +3.79, +4.15, +1.13 SD |

The wash-in comparison cannot discriminate between the two values - the pool is
long equilibrated by 30 minutes - so it is no evidence either way, and that is
worth knowing about the gate as much as about the parameter. The elimination
comparison moves 0.11 to 0.13 SD **further from** its cohort means, because a
larger pool returns more agent, which is the same direction the module already
attributes to the rebreathing circuit rather than to tissue return. That cost
is recorded in `docs/MODEL.md` and in the module rather than buried: it is a
tenth of a gap that is already 1 to 5 SD wide for apparatus reasons.

**Re-pinned, from the oracle and not from the shipped solver.** All nine
`PINNED_REFERENCE_STATES` failed, which is exactly what that pin is for, and
were re-derived through `_reference_state`; the largest movement is 8.3e-4
relative and sits in the mixed-venous state, which is where a venous-pool
change should show and nowhere else. `MODELLED_ELIMINATION_RATIOS`, the two
measured tables in `test_published_wash_in_and_elimination.py`, and a pinned 60 s circuit load
in `test_uptake_system_failure.py` were re-measured with the reason recorded
beside each.

**`not-delegable` stands as the record of what could not be proven by command.**
No command can prove a person read the paper. The adoption half *is* checkable
and is pinned by `PL-BD94`'s `verify:`, which was run against `HEAD` before the
work (exit 1) and against the finished tree (exit 0).
