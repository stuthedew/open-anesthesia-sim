---
id: PL-X9HM
title: README's status section understates the solver disagreement as 1.2e-2 percentage points where MODEL.md gives 2.3e-2 for the same domain
priority: P1
effort: S
status: done
classes: science, docs
milestone: v0.4.2
touches: README.md
added: 2026-09-05
closed: 2026-09-05
verify: python3 tools/doc_check.py check && grep -q '2.3e-2 percentage points across the settings' README.md
---

**Problem.** `README.md`'s status section justifies the two-decimal readout with
a measured bound, and quotes the wrong row of the table it is drawn from:

> the shipped operator split disagrees with an independent solution by up to
> 1.2e-2 percentage points across the settings the interface exposes

`docs/MODEL.md` § "Displayed precision" gives $`1.2\times10^{-2}`$ for *maximum
flows at the agent's maximum dial* — one row of six — and
$`2.3\times10^{-2}`$ for "the worst reachable trajectory", which that section
then states is "the worst the four sliders can reach". The sliders are the
settings the interface exposes, so the README's own qualifying clause names the
domain whose bound is 2.3e-2. It understates it by a factor of about 1.9.

**Why it matters.** It is a number about how far this model's output can be
from the right answer, in the one document most readers will open, and it is
the sentence carrying the project's justification for its displayed precision.
The direction of the error is the bad one: it claims the model is nearly twice
as close to the reference solution as the measurement supports.

It is also a live instance of the coupling `docs/MODEL.md` warns about in that
section — "The two are coupled and must be revised together". `PL-74TX`
re-affirmed the resolution on 2026-08-30 against a widened measurement that
moved the extreme from about one count to about two, `docs/MODEL.md` was
updated, and this sentence was not.

**Where.** `README.md` § "Current status", the paragraph beginning
"Concentrations are displayed to 0.01 percentage points". The authority is
`docs/MODEL.md` § "Displayed precision", whose table and the sentence beneath it
carry both figures.

**Blocked by the README freeze.** `.claude/rules/readme-hold.md` holds
`README.md` until the project owner lifts it, and that rule says explicitly that
a doc sweep does not override it. Found and left alone while sweeping
`docs/MODEL.md` for `PL-RCTQ`.

**Decision needed.** The freeze holds this correction, and the freeze now
waits on `PL-XYRN` (decide when the repository goes public) rather than on
anything undecided about the README itself. `PL-XYRN` is `L` and P2, so on the
current plan a wrong error bound — wrong in the direction that claims more
accuracy than was measured — stands in the document most readers open until a
public-readiness pass that has no date. So: does the project owner lift the
freeze for this one sentence, or accept the stated bound until `PL-N092`
(rewrite README as a human-readable introduction) runs?

**Answered, 2026-09-05: the project owner lifted the freeze for this one
sentence.** `blocked-by: PL-XYRN` was dropped with the answer.

**Resolved by correction, not by narrowing or deletion.** The `Done when` below
offered three routes; the figure was corrected to `2.3e-2`, leaving the
sentence's own domain clause ("across the settings the interface exposes")
intact, because that clause is accurate — `docs/MODEL.md` states of the
2.3e-2 row that it "is the worst the four sliders can reach", and the sliders
are what the interface exposes. Narrowing the sentence to the domain 1.2e-2
covers would have been the larger edit and would have left the README quoting
a bound for a corner of the envelope while implying it covered the whole of
it.

`.claude/rules/readme-hold.md` records the exception rather than being deleted:
the hold still stands for every other line of the file, and `PL-T67Y` (README
covers neither the playback rate nor the chart time base) was deliberately not
included in it.

**Not the same item as `PL-N092`** (rewrite README as a human-readable
introduction), though they touch the same paragraph. `PL-N092` cites this very
sentence as an example of detail that belongs in `docs/MODEL.md` or nowhere, so
the rewrite may well delete it — but `PL-N092` is itself blocked behind
`PL-XYRN` (decide when the repository goes public), so a wrong measured bound
would sit in the README until a public-readiness decision lands. Whichever
happens first: if the rewrite reaches this paragraph, deleting the sentence
closes this too; if the freeze lifts first, correct the figure without waiting
for the rewrite.

**Done when.** The README no longer states a solver-error bound that disagrees
with `docs/MODEL.md` § "Displayed precision" — either corrected to
$`2.3\times10^{-2}`$ percentage points for the domain it names, narrowed to the
domain 1.2e-2 actually covers, or removed with the rewrite. `make doc-check`
passes.
