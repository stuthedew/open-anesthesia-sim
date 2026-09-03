---
id: PL-T531
title: 'Decide isoflurane''s blood:gas coefficient: 1.3 (Gas Man) or 1.4 (textbook)'
priority: P1
effort: S
status: done
classes: science
milestone: v0.3.2
touches: src/anesthesia_sim/data/agents/isoflurane.json, docs/MODEL.md, tests/reference/test_multi_agent.py
added: 2026-09-01
closed: 2026-09-03
pr: 257
verify: uv run pytest tests/unit/test_parameters.py tests/reference/test_multi_agent.py && python3 -c "import json; d=json.load(open('src/anesthesia_sim/data/agents/isoflurane.json')); assert d['blood_gas_partition_coefficient'] == 1.3; assert any('Lerman J, Gregory GA' in s['citation'] for s in d['sources'])"
---

**Problem.** `data/agents/isoflurane.json` carries
`blood_gas_partition_coefficient: 1.3`, sourced to the Gas Man parameter set
(De Wolf et al. 2012, Table 1), alongside tissue:gas coefficients 2.1 / 4.5 /
70.0 taken from the same table. Standard US textbooks give isoflurane's
blood:gas coefficient as 1.4. A resident running this simulator beside Miller
or Barash meets a number that does not match the one in front of them, and
neither the interface nor the provenance note tells them why.

**Why it matters.** $`\lambda_{b:g}`$ scales the pulmonary uptake term
$`Q\lambda_{b:g}(F_A - F_v)`$ directly, so the choice moves every displayed
alveolar, blood and tissue concentration on every isoflurane run. 1.3 against
1.4 is a 7.7% difference in the uptake coefficient — small beside
between-subject variability, and not zero.

The educational cost is the larger one. The blood:gas coefficient is the
single most-quoted number about isoflurane in teaching, and it is one a
resident already knows before they open the tool. A simulator that silently
disagrees with the textbook on exactly that number teaches that the tool is
wrong somewhere unidentified, which does more damage than 7.7% in a curve.
`CLAUDE.md` treats presentation correctness as part of safety: a correct
number whose provenance a reader cannot reconcile is a presentation failure
even when the arithmetic is sound.

**The cross-check that constrains the answer.** Yasuda, Targ & Eger 1989
(PMID 2774233), already cited in all three agent files for tissue solubility,
reports human tissue:blood partition coefficients at 37 °C. Dividing this
repository's shipped `vessel_rich` tissue:gas value by its blood:gas value
recovers the implied brain:blood ratio:

| Agent | Yasuda 1989 brain:blood | Implied here | Difference |
| --- | --- | --- | --- |
| Sevoflurane | 1.70 ± 0.09 | 1.1 / 0.65 = 1.692 | −0.5% |
| Desflurane | 1.29 ± 0.05 | 0.54 / 0.42 = 1.286 | −0.3% |
| Isoflurane | 1.57 ± 0.10 | 2.1 / 1.3 = 1.615 | +2.9% |

Sevoflurane and desflurane reproduce the primary human measurement to three
digits. Isoflurane is the loosest of the three, and inside one SD. Under
$`\lambda_{b:g} = 1.4`$ with the tissue value unchanged the implied ratio
becomes 2.1 / 1.4 = 1.500, which is −4.5% — also inside one SD, and slightly
worse.

So the cross-check does not settle which number is right. What it does settle
is that **these four numbers are a set, not four independent values.**
Changing the blood:gas coefficient alone silently changes all three implied
tissue:blood ratios, which is exactly the kind of unannounced scientific
change this project's provenance discipline exists to prevent.

**What the primary literature says about 1.4.** Lerman, Gregory, Willis &
Eger 1984 (PMID 6465597) measured blood:gas coefficients in fasting subjects
by age group and report isoflurane at **1.46** in adults aged 20–40 (children
1.28, newborns 1.19, elderly 75–85 1.29). That adult measurement is what the
textbook's rounded 1.4 rests on. Malviya & Lerman 1990 (PMID 2339795),
already cited in the file, confirms the adult value differs from neonates but
its abstract does not carry the number.

There are therefore three defensible values, not two: 1.3 (Gas Man,
internally consistent with the tissue set already shipped), 1.4 (the rounded
textbook number a resident expects), and 1.46 (Lerman's measured adult
value). Moving to 1.4 buys agreement with the textbook, not accuracy.

**Option A — keep 1.3, and say so in the provenance note.**

- *Work:* the `sources` note in `isoflurane.json`, and the matching paragraph
  in `docs/MODEL.md`'s "v0.2.0: isoflurane and desflurane" provenance
  subsection. No parameter change, no reference test to re-baseline.
- *Buys:* all three agents stay one internally consistent parameter set from
  one simulator whose published behavior this project can be compared
  against. Cross-agent comparison — v0.4.0's stated purpose for a
  MAC-normalized axis — stays honest, because all three agents carry the same
  source of error.
- *Costs:* the displayed isoflurane uptake stays ~7.7% faster than a curve
  computed from textbook numbers, and the note has to say that plainly, in
  words a resident will actually read rather than in a citation.

**Option B — move to 1.4 and re-derive the tissue set with it.**

- *Work:* set `blood_gas_partition_coefficient: 1.4`; re-derive each
  tissue:gas coefficient as (Yasuda 1989 tissue:blood) × 1.4 — `vessel_rich`
  becomes 1.57 × 1.4 = 2.198 → 2.20, and `muscle` and `fat` likewise from
  Yasuda's muscle:blood and fat:blood ratios. **Those two ratios are not in
  the abstract and must be read from the paper's tables.** Do not carry 4.5
  and 70.0 across: they were derived against 1.3, and keeping them would
  change every implied tissue:blood ratio without saying so. Then rewrite the
  `docs/MODEL.md` provenance subsection and re-baseline whatever in
  `tests/reference/test_multi_agent.py` pins isoflurane trajectories.
- *Buys:* agreement with the number the reader already knows.
- *Costs:* the effort above, most of it in two tissue numbers nobody has yet
  read; and isoflurane stops sharing a provenance with sevoflurane and
  desflurane, so a cross-agent comparison then mixes two sources.

**Recommendation: Option A, with the note written as a comparison rather than
a citation.** Not because 1.3 is more right than 1.4 — against Lerman's 1.46
neither is — but because the set's internal consistency is doing work that a
single closer number would not, and because the failure the review identified
is a *labeling* failure rather than a parameter failure. Fix it where it
occurs: in the provenance note, and in what the interface can be made to say
about which parameter set is running.

The eventual right answer is probably neither option: rebase all three agents
on primary human measurements (Lerman 1984 for blood:gas, Yasuda 1989 for
tissue:blood) and retire Gas Man as the parameter source. That is a
three-agent piece of work with its own reference-test consequences, it
belongs on `ROADMAP.md` rather than in this item, and it is named here only
so the decision below is not mistaken for a choice between the only two
possibilities.

**Decision needed.** Option A or Option B. If B, whether the target is 1.4
(the textbook round number) or 1.46 (Lerman's measured adult value), since
the re-derivation of the tissue coefficients differs accordingly.

**Do not change the data file before the decision is made.** The edit is one
character and looks harmless, which is exactly why it needs the decision
first — `data/` is a protected path under `docket.toml` and a change to it
alters a displayed clinical value on every isoflurane run.

**Found.** Outside review, relayed by the project owner on 2026-09-01 in a
capture-only session. The Yasuda 1989 brain:blood values and the Lerman 1984
adult blood:gas value above were verified against the PubMed abstracts of
PMID 2774233 (DOI unavailable) and PMID 6465597
(https://doi.org/10.1097/00000542-198408000-00005) during that session; the
muscle:blood and fat:blood ratios Option B needs were not, and are the one
piece of sourcing this item still owes.

**Appended 2026-09-03 — the recommendation above rests on a premise the
project owner has since demoted; not re-decided here.**

Option A's case is that "the set's internal consistency is doing work that a
single closer number would not" — that is, that keeping 1.3 keeps all three
agents inside one coherent Gas Man parameter set. On 2026-09-03 the project
owner stated that Gas Man was supplied as a starting point and a working
example, never as a definitive citation, and is not acceptable as a primary
source. `docs/MODEL.md` § "Source hierarchy" now records that as the standard:
a reference implementation is tier 3, and a peer-reviewed paper reprinting its
parameter table — which De Wolf et al. 2012 is — does not promote the values
in it.

That does not make Option A wrong. Internal consistency across three agents is
still a real property, and it is still the property a cross-agent comparison
needs. It does mean the case for A can no longer be made as "stay with the
authoritative set", only as "stay with one coherent tier-3 set and say so",
which is a weaker and more honest claim than the one written above.

It also confirms this item's own closing observation — that the eventual right
answer is to rebase on primary measurements — as the owner's stated direction
rather than a session's aside. That work is now scoped as `PL-D6LX` (decide
whether to adopt primary-literature partition coefficients or label the
shipped set as Gas Man's), which asks this question for all three agents and
records why "just use the primary values" is not executable as written: this
model's `vessel_rich` group is a lumped compartment and Yasuda 1989 reports
per-organ coefficients, so a group-weighting scheme has to be constructed and
justified before any tissue value can be called primary.

**Recommend deciding this item as part of `PL-D6LX` rather than separately.**
Deciding isoflurane alone now would set a precedent for the other two agents
without the analysis that covers them, and `PL-D6LX` carries the verified
primary values for all three (sevoflurane 0.686, isoflurane 1.46, desflurane
0.424) alongside what adopting them would cost. Nothing here is changed.

**Done when.** The decision is recorded in `isoflurane.json`'s `sources` note
and in `docs/MODEL.md`'s parameter-provenance section, in terms that tell a
reader comparing against a textbook why the number differs and by how much;
and, if B was chosen, the tissue coefficients were re-derived from Yasuda
1989's tissue:blood ratios against the new blood:gas value rather than
carried across, with the reference tests re-baselined and the provenance
table updated.


## Answered 2026-09-03, as part of `PL-D6LX`

The project owner decided the broader question this item is a slice of: keep
the shipped Gas Man set, label it honestly, and route the move to primary
values through `ROADMAP.md`'s planned-milestone item 31 (ship a
primary-literature set alongside the Gas Man set, selectable) rather than
through one agent at a time.

**Effectively Option A, for a different reason than the one argued above.**
Not "stay with the authoritative set" — the 2026-09-03 appendix records why
that argument no longer stands — but "stay with one coherent tier-3 set,
labelled as one, until a primary set can be built for all three agents
together". Moving isoflurane alone would have split the three agents across two
provenances to buy agreement with a rounded textbook number that is itself not
the measurement (1.4 against Lerman's 1.46).

**What landed.** `isoflurane.json` now cites Lerman et al. 1984 directly — it
previously cited only Malviya & Lerman 1990, whose abstract carries no adult
value, so 1.46 was named nowhere in the tree — and records that the stored 1.3
is the Gas Man figure, 11.0% below the measured adult value and the widest such
gap in the project. `docs/MODEL.md` § "Source hierarchy" carries the same
number and names item 31 as the route. **No coefficient changed.**

**The debt this item owed is unchanged and moves to item 31:** Yasuda 1989's
muscle and fat rows have still not been read, and `PL-D6LX` records the further
obstacle — `vessel_rich` is a lumped compartment while Yasuda reports per-organ
coefficients, so a group-weighting scheme must be built and justified before
any tissue value may be called primary.
