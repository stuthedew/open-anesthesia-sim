---
id: PL-212V
title: MODEL.md's Symbols table has no row for the tissue:gas coefficient, which is the parameter actually stored and the one core/ names
status: untriaged
touches: docs/MODEL.md, src/anesthesia_sim/core/tissue.py
added: 2026-09-03
---

**Problem.** `docs/MODEL.md` § "Symbols" carries one tissue partition
coefficient, $`\lambda_{i:b}`$, "Tissue:blood partition coefficient for group
$`i`$". That is not the parameter the project stores. The agent data files hold
`tissue_gas_partition_coefficients` — sevoflurane vessel-rich 1.1, muscle 2.4,
fat 34.0 — and `core/tissue.py` names the field
`tissue_gas_partition_coefficient`, deriving `tissue_blood_partition_coefficient`
from it by dividing by blood:gas. The spec's symbol table therefore has no row
for the stored primitive, and the code's primary field has no symbol.

§ "Parameter provenance" is not affected: it already prints both, states the
division, and cites the stored tissue:gas key on each row. The gap is in the
symbol table alone.

**Why it matters, and why the fix is not simply "add a row".** The naming of
these ratios is unreliable *in the primary literature*, which raises the bar on
what this project's own definition has to do.

Baker and Farmery's review names the same symbol four ways in one chapter:

- "The ratio $`S_{ti}/S_b`$ is the tissue-gas partition coefficient, $`\lambda`$"
  (p. 569);
- "substituting the ratio of the tissue-gas and blood-gas solubilities,
  $`S_{ti}/S_b`$, with the tissue-blood partition coefficient, $`\lambda`$"
  (p. 570);
- Figure 2's caption: "increased tissue-gas partition coefficient";
- Table 2's title: "Blood Gas Solubilities ($`S_b`$) and Blood Tissue Partition
  Coefficients ($`\lambda`$)".

The quantity is the same throughout, and their Eq. (4) settles which name is
correct: the rate constant is $`\dot Q/(V_{ti}\lambda)`$, so $`\lambda = S_{ti}/S_b`$
is the **tissue:blood** coefficient, matching this project's
$`\tau_i = V_i\lambda_{i:b}/Q_i`$.

So a reader cannot resolve which ratio an identifier means by recalling the
convention, because the field does not hold one. That makes this a case for
`.claude/rules/core-domain.md`'s "units carried in the identifier" principle
applied to ratios: a partition-coefficient identifier must name **both phases,
in order**, and the symbol table must define each one once, unambiguously,
rather than assuming the reader supplies the convention. The project's existing
`blood_gas_partition_coefficient` and `tissue_gas_partition_coefficient` already
do name both phases, which is the right instinct; what is missing is the
definition they should resolve against.

**Where.** `docs/MODEL.md` § "Symbols" — add the stored $`\lambda_{i:g}`$ row and
state the relation $`\lambda_{i:g} = \lambda_{i:b}\lambda_{b:g}`$ so the two rows
cannot be confused. § "Tissue groups" lists what each group has and names only
the tissue:blood coefficient; it should name the stored one too.

**Done when.** Every partition coefficient the project stores or derives has a
row in § "Symbols" naming both phases in order, the relation between them is
stated, `python3 tools/doc_check.py check` passes, and no modelled value changed.

**Found.** Scoping session for planned-milestone item 29 (`core/` reads like the
domain), 2026-09-03. Reference supplied by the project owner: Baker AB, Farmery
AD. Inert gas transport in blood and tissues. Compr Physiol 2011;1(2):569-592.
https://doi.org/10.1002/cphy.c100011
