---
id: PL-9T8T
title: The primary partition-coefficient citation names an author who is not on the paper
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/agents, docs/MODEL.md, tests/unit/test_parameters.py, tests/reference/test_multi_agent.py, docs/items
added: 2026-09-01
verify: uv run pytest tests/unit/test_parameters.py tests/reference/test_multi_agent.py && ! grep -rq Stadler src/anesthesia_sim/data docs/MODEL.md tests/
---

**Problem.** Every partition coefficient in this project — all twelve, across
three agents — is sourced to one table, cited throughout as "Stadler M, et
al." There is no Stadler among that paper's authors. The correct citation is:

> De Wolf AM, Van Zundert TC, De Cooman S, Hendrickx JF. Theoretical effect of
> hyperventilation on speed of recovery and risk of rehypnotization following
> recovery - a Gas Man simulation. BMC Anesthesiol. 2012;12:22.
> PMID 22989260. PMC3502091. doi:10.1186/1471-2253-12-22

Journal, year, volume, article number, title and the PMC URL recorded in the
data files are all correct. Only the author name is wrong, and it is wrong in
ten places across six files:

| File | Lines |
| --- | --- |
| `src/anesthesia_sim/data/agents/sevoflurane.json` | 2 |
| `src/anesthesia_sim/data/agents/isoflurane.json` | 3 |
| `src/anesthesia_sim/data/agents/desflurane.json` | 2 |
| `docs/MODEL.md` | 738 |
| `tests/unit/test_parameters.py` | 154 |
| `tests/reference/test_multi_agent.py` | 98 |

**The correct attribution already exists in the tree, exactly once.**
`docs/items/PL-4YY1-record-provenance-for-the-circuit-volume-and.md:48` names
De Wolf, Van Zundert, De Cooman and Hendrickx correctly in its **Approach**
section. So the right answer was recorded in one place and the wrong one in
ten, with nothing reconciling them — which is the shape of the defect as much
as the misspelled name is.

That same line mistitles the paper: it gives "risk of rehyperventilation"
where the paper says "risk of rehypnotization following recovery".
Rehypnotization — the anesthetic partial pressure in the vessel-rich group
climbing back above MAC-awake when hypoventilation follows emergence — is the
paper's actual finding, so the mistitle inverts its subject. Its author
initials are also slightly off ("Van Zundert TCRV", "Hendrickx JFA"). Fix all
of that here; it is the same citation.

**Why it matters.** This is the sole primary source for all twelve partition
coefficients — the parameters that scale every uptake and distribution term in
the model, and therefore every displayed concentration on every run. A reader
checking a coefficient the way readers actually check coefficients, by author
search, finds nothing and cannot complete the verification. `CLAUDE.md`
requires provenance to be versioned and recorded for scientific constants and
requires a displayed value to be traceable to the parameters that produced it;
a citation that does not resolve breaks that chain at its only link.

It is also self-inflicted rather than inherited: the paper is open access, the
data files already carry its correct PMC URL, and one item in the queue
already has the authors right.

**The values themselves are correct and must not change.** Table 1 of the
paper, read from PMC3502091 while writing this brief, gives for
desflurane / sevoflurane / isoflurane:

| Row | Table 1 | Data files |
| --- | --- | --- |
| Blood | 0.42 / 0.65 / 1.3 | identical |
| VRG | 0.54 / 1.1 / 2.1 | identical |
| Muscle | 0.97 / 2.4 / 4.5 | identical |
| Fat | 13 / 34 / 70 | identical |

**This item is attribution only. It must change no modelled number.** A diff
that alters a coefficient is out of its scope, and the data files are a
protected path under `docket.toml`.

**Where.** The six files in the table above. `docs/MODEL.md:738` sits inside
the "v0.2.0: isoflurane and desflurane" provenance subsection, which is the
paragraph asserting that all three agents draw from one source table — the
claim this citation exists to support.

**Approach.** Replace the author string in all ten places with the full author
list above, and correct `PL-4YY1`'s title and initials in the same pass so the
tree carries one form of the citation rather than three. Prefer the full
four-author form over "De Wolf AM, et al." in the data files, since these are
the provenance records a reader will search from. Check whether the two test
files assert on the citation string, in which case the assertions move with
it — that is what makes `tests/` a legitimate target for an attribution-only
change.

Consider, but do not assume: `tools/doc_check.py` already decides the
provenance-table and dangling-citation questions. Whether an author string
appearing in a data file's `sources` block can be checked against anything
deterministic is a genuine question, and probably answers no — nothing in the
tree knows the paper's author list. If so, say so rather than building a
check that pattern-matches one name.

**Found.** External multi-domain review, relayed by the project owner
2026-09-01. Author list, title, and Table 1 values were confirmed in this
session against the PubMed Central full text (PMC3502091,
https://doi.org/10.1186/1471-2253-12-22).

**One occurrence added since.** `docs/items/PL-T531-*.md`, written earlier in
this same session, repeated "Stadler et al. 2012, Table 1" before this finding
arrived. It was corrected on this branch rather than left to this item,
because knowingly leaving a false citation in a science-classed provenance
brief is the defect this item describes. The count of ten above is the tree as
it now stands.

**Done when.** No occurrence of "Stadler" remains under
`src/anesthesia_sim/data`, in `docs/MODEL.md`, or under `tests/` — the scope
the `verify:` command checks, which deliberately excludes this brief and any
other `docs/items/` file that has to name the wrong string in order to
describe it; every one of the ten sites names the four authors above; `PL-4YY1`'s
citation carries the correct title and initials; `python3 tools/doc_check.py
check` and the full test suite pass; and no partition coefficient, patient
parameter or other modelled value differs from before the change.
