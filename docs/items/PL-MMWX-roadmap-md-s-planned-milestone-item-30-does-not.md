---
id: PL-MMWX
title: ROADMAP.md's planned-milestone item 30 does not say that cardiac-output scaling is one of its obligations, or that weight scaling is only safe as a coupled package
priority: P1
effort: S
status: ready
classes: safety, docs, planning
feature: release-roadmap-seam
touches: ROADMAP.md
added: 2026-09-08
verify: python3 tools/doc_check.py check && grep -q 'coupled package' ROADMAP.md
---

**Problem.** ROADMAP.md's planned-milestone item 30 does not say that cardiac-output scaling is one of its obligations, or that weight scaling is only safe as a coupled package (`PL-YKSM`, 2026-09-08).

Item 30, "Add patient factors - age, sex and weight as inputs", carries the
project owner's decisions on body composition and on the MAC basis, and it
names the reference adult as a placeholder for it. It says nothing about
cardiac output, and nothing about the coupling constraint `PL-YKSM` closed on.

**The constraint.** A time constant is $`V_i \lambda_{i:b} / Q_i`$, so a
weight-scaling rule applied to the flows alone - with compartment volumes left
as the fixed litres this project stores - makes $`\tau \propto M^{-3/4}`$: a
heavier patient equilibrates faster, a lighter one more slowly. Worked at 20 kg
against the shipped sevoflurane coefficients, that gives a child **2.64 times**
the adult's time constants where the paediatric direction is faster, against
**0.76 times** when volumes scale with the flows and **1.00** when nothing
scales at all. So the half-measure is further from the truth than the status
quo, and the rule has to move volumes, alveolar volume, alveolar ventilation
and the perfusion fractions together with the flows, or move none of them.

**Why it needs to be in item 30 rather than only where it was written.** It is
recorded in `docs/MODEL.md` "Known limitations" and in
`reference_adult.json`'s Cattermole entry, which is where a reader of the
*stored value* meets it - but a session scoping item 30 reads item 30. The
failure this guards against is that session scoping weight scaling as "cardiac
output becomes a function of weight", which is exactly the change `PL-YKSM`
examined and refused, and which would ship a paediatric patient whose kinetics
are wrong in the most-taught direction. A `safety`-classed omission in a
milestone's scope is cheaper to fix now, in one paragraph, than after it has
been built.

**Approach.** One paragraph in item 30's entry in `ROADMAP.md`, in the shape
its existing owner-decision paragraphs use: cardiac output is one of the
quantities the milestone must scale; the scaling is a coupled package; and
`PL-YKSM` is where the arithmetic and the refused alternative are recorded.
Add the suggestion that weight-banded measured normal ranges (Cattermole et al.
2017, already cited in `reference_adult.json`, 2218 subjects aged 0.5-89) are
likely a better basis for a *default* than an allometric formula, since the
learner sees the default rather than the law.

**Not this item's job**: scoping the milestone, choosing the scaling law, or
deciding between total body weight and fat-free mass. This records a
constraint on a milestone that has not been scoped yet.


**Why it matters.** The failure this guards against is a session scoping item 30
as "cardiac output becomes a function of weight", which is exactly the change
`PL-YKSM` examined and refused. Applied to the flows alone, with compartment
volumes left as the fixed litres this project stores, a weight-scaling rule
makes tau proportional to M^-3/4: worked at 20 kg against the shipped
sevoflurane coefficients, a child gets **2.64x** the adult's time constants
where the paediatric direction is faster, against **0.76x** when volumes scale
with the flows and **1.00** when nothing scales. The half-measure is further
from the truth than the status quo, and it would ship a paediatric patient whose
kinetics are wrong in the most-taught direction.

The constraint is recorded in `docs/MODEL.md` "Known limitations" and in
`reference_adult.json`'s Cattermole entry, which is where a reader of the stored
*value* meets it - but a session scoping item 30 reads item 30. A safety-classed
omission in a milestone's scope is one paragraph now against a rebuild later.

**Done when.** `ROADMAP.md` item 30 states that cardiac output is one of the
quantities the milestone must scale, that the scaling is a coupled package -
volumes, alveolar volume, alveolar ventilation and the perfusion fractions move
with the flows or nothing does - and cites `PL-YKSM` for the arithmetic and the
refused alternative. It also carries the suggestion that weight-banded measured
normal ranges (Cattermole et al. 2017, already cited in `reference_adult.json`)
are likely a better basis for a default than an allometric formula, since the
learner sees the default rather than the law.

**Not this item's job**: scoping the milestone, choosing the scaling law, or
deciding between total body weight and fat-free mass.
