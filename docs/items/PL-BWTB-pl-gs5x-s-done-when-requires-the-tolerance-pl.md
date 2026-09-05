---
id: PL-BWTB
title: PL-GS5X's Done when requires the tolerance PL-X9KD sets, but PL-X9KD is blocked-by PL-GS5X, so as written neither can finish
status: done
added: 2026-09-05
closed: 2026-09-05
priority: P2
effort: S
classes: defect, docs
touches: docs/items/PL-GS5X-replace-the-operator-split-with-the-exact.md
feature: numerical-domain
verify: python3 tools/doc_check.py check && grep -qF 'Corrected 2026-09-05 (`PL-BWTB`)' docs/items/PL-GS5X-replace-the-operator-split-with-the-exact.md
---

**Problem.** `PL-GS5X` (replace the operator split with the exact matrix
exponential) closes, per its own Done when at line 114, when "the independent
oracle agrees to the tolerance `PL-X9KD` sets". `PL-X9KD` declares
`blocked-by: PL-GS5X`. As written neither can finish: the item that sets the
tolerance cannot start until the item that needs it has landed.

**Why it matters.** These are the two `P1` science items of v0.4.1 and the
first of them is the release's whole content. A worker reaching the Done when
has no defined exit, and the likely improvisation - carrying the old
`~2e-15` splitting-error figure forward - is the one thing `PL-P0BB` explicitly
refuses: "`PL-GS5X` must state the new tolerance's derivation beside it, and
must not reuse the ~2e-15 figure, which describes the old mechanism."

**The answer already exists and is not written in either item.** `PL-P0BB`
(decided 2026-09-03, closed, shipped v0.3.2) assigns the derivation to
`PL-GS5X` itself. So the tolerance for its *own* oracle comparison is
`PL-GS5X`'s to derive and record; what `PL-X9KD` re-derives afterwards is the
*published* material - MODEL.md's "Displayed precision", the supported step
bound, and the three splitting-error constants in
`tests/reference/test_coupled_dynamics.py`. Two different tolerances, one name.

**Where.** `docs/items/PL-GS5X-*.md:114` (Done when);
`docs/items/PL-X9KD-*.md` front matter.

**Done when.** `PL-GS5X`'s Done when names the tolerance it derives itself,
citing `PL-P0BB`, and no longer forward-references `PL-X9KD`; the edge runs one
way only.
