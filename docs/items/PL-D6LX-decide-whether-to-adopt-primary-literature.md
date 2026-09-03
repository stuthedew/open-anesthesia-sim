---
id: PL-D6LX
title: Decide whether to adopt primary-literature partition coefficients or label the shipped set as Gas Man's
status: untriaged
classes: science
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/agents, docs/MODEL.md, tests/reference/test_multi_agent.py, tests/reference/test_published_wash_in.py, ROADMAP.md
added: 2026-09-03
---

**Decision needed.** Whether this project builds a partition-coefficient set
from primary human measurements, and if so whether that set *replaces* the
shipped Gas Man set or *joins* it as a second selectable set. See
"Recommendation" below.

**Problem.** All twelve partition coefficients across the three agent files
are the Gas Man parameter set as published in De Wolf et al. 2012, Table 1 —
tier 3 under `docs/MODEL.md` § "Source hierarchy". The primary measurements
are cited alongside, and each stored value differs from its primary:

| Agent | Shipped $`\lambda_{b:g}`$ | Primary measurement | Difference |
| --- | ---: | --- | ---: |
| Sevoflurane | 0.65 | 0.686 ± 0.047, 37 °C, n=19 (Strum & Eger 1987, PMID 3605675) | −5.2% |
| Isoflurane | 1.3 | 1.46, adults 20–40, n=11 (Lerman et al. 1984, PMID 6465597, doi:10.1097/00000542-198408000-00005) | −11.0% |
| Desflurane | 0.42 | 0.424 ± 0.024, 37 °C, n=11 (Eger 1987, PMID 3631593) | −0.9% |

Isoflurane is the outlier and is separately open as `PL-T531` (decide
isoflurane's blood:gas coefficient, 1.3 or 1.4), which this item supersedes
in scope: `PL-T531` asks the question for one agent, this asks it for the set.

**Why this is not a swap of three numbers.** The tissue:gas coefficients are
the hard half, and the reason a "just use the primary values" instruction
cannot be executed as written.

Yasuda, Targ & Eger 1989 (PMID 2774233), the primary human tissue-solubility
study, reports tissue:blood coefficients **per organ** — brain, heart, liver,
kidney, muscle, fat. This model's `vessel_rich` group is not an organ; it is
a lumped compartment standing for brain, heart, liver, kidney, and the rest
of the richly perfused viscera. Its 6.0 L volume and 0.76 flow fraction are a
group, not a brain.

So adopting primary tissue values requires **constructing a group coefficient
from organ measurements** — a volume- or flow-weighted composite of Yasuda's
brain, heart, liver and kidney rows — and that weighting is a modeling
decision this project has never made and would have to justify. Gas Man made
some such decision, unpublished. Replacing an undocumented mapping of
theirs with an undocumented mapping of ours, and then labelling the result
"primary", would be strictly worse than the current state: a tier-3 value
honestly labelled is safer than a tier-1-flavoured value whose construction
is not recorded. `docs/MODEL.md`'s provenance checklist already requires the
tissue-group mapping to be recorded, and this is the case it was written for.

The abstract carries only the brain:blood row (desflurane 1.29 ± 0.05,
isoflurane 1.57 ± 0.10, sevoflurane 1.70 ± 0.09). **The muscle and fat rows,
and every other organ, must be read from the paper's tables.** They have not
been, in this session or any prior one — `PL-T531` records the same debt.

**What the shipped set gets right, and why that is not nothing.** Dividing
each stored tissue:gas value by its stored blood:gas value recovers an
implied brain:blood ratio that reproduces Yasuda's measurement closely:
sevoflurane 1.1 / 0.65 = 1.692 against 1.70 (−0.5%), desflurane
0.54 / 0.42 = 1.286 against 1.29 (−0.3%), isoflurane 2.1 / 1.3 = 1.615
against 1.57 (+2.9%). The set is internally coherent and was clearly built
against these measurements. That is an argument for it being a *good* tier-3
set. It is not an argument for it being tier 1, and the distinction is the
whole of this item.

**Three pieces of work, and only the last two are a decision.**

*The labeling fix is not optional and is not part of the decision.* Each
agent file's `sources` notes already state the primary value and the
substitution; what they do not state is the tier, and `docs/MODEL.md` now
requires it. That work happens whatever is decided here, and can be done
first. It closes the finding the project owner actually raised.

*Option 1 — stop there.* The shipped set stays Gas Man's, labelled tier 3,
with each difference from the primary literature stated in words a resident
comparing against a textbook can act on. Costs nothing, changes no displayed
value, re-baselines no reference test. Leaves the simulator's twelve
most-scrutinized numbers at tier 3 permanently.

*Option 2 — build a primary-literature set and replace.* Read Yasuda 1989's
organ tables, decide and document a group-weighting scheme, derive twelve
coefficients, re-baseline `tests/reference/test_multi_agent.py`, and re-check
`tests/reference/test_published_wash_in.py` — whose comparison
`docs/MODEL.md` already flags as partly circular because the shipped
parameters descend from the same lineage as the data being tested against.
That circularity weakens under this option, which is a genuine scientific
gain and the strongest argument for it. Cross-agent comparability survives,
since all three would move to one new source lineage together.

*Option 3 — build the primary set and ship both, selectable.* Option 2's work
plus a named-parameter-set concept in the data layer and the interface. The
educational payload is real and is unique to this project's purpose: "how
much does the parameter set matter?" is a question a resident cannot ask of
any commercial simulator, and answering it on one screen teaches the
provenance lesson better than any note in a JSON file will. It is a milestone,
not an item, and it needs `ROADMAP.md` scope before it needs code.

**Recommendation: do the labeling fix now, and put Option 3 on
`ROADMAP.md`'s "Planned milestones" as one line of intent.** Option 2 is
Option 3's first half, so choosing 2 now would spend the whole cost and
retire the comparison that makes it worth having. Option 1 alone under-serves
a stated project goal — the owner's direction on 2026-09-03 was that values be
supported by primary literature, and permanently tier-3 coefficients do not
satisfy that. The labeling fix is what makes waiting honest rather than
merely deferred.

**Do not change any coefficient before this is decided.** `data/` is a
protected path under `docket.toml`, and each of these twelve numbers scales
every displayed concentration on every run of its agent.

**Found.** Project owner, 2026-09-03: Gas Man was provided as a starting
point and a working example, not as a definitive citation, and is not
acceptable as a primary source. All four primary records above were verified
against PubMed in that session, including the reported values, cohorts and
reference temperatures; Yasuda's non-brain organ rows were not, and are the
sourcing this item still owes.

**Done when.** The decision is recorded here and in `docs/MODEL.md`; the
three agent files name their tier and state each difference from the primary
literature regardless of which option was chosen; `PL-T531` is closed or
folded into whatever this decides; and if a set was built, its group-weighting
scheme is documented in `docs/MODEL.md` and its reference tests re-baselined.
