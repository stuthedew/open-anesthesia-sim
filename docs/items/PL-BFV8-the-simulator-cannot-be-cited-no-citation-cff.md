---
id: PL-BFV8
title: The simulator cannot be cited: no CITATION.cff, no DOI, and nothing in the repository says how to reference it
status: untriaged
feature: documentation-standard
touches: CITATION.cff, README.md
added: 2026-09-05
---

**Problem.** Lee 2018 rule 10 asks that software say how to cite it. This
repository has no `CITATION.cff`, no DOI, and no citation section anywhere;
`grep -riE 'citation|zenodo|joss|DOI' README.md ROADMAP.md docs/*.md`
(2026-09-05) returns only the model's own source citations. The project is
educational software written by an academic who publishes curriculum and
journal articles, so an uncitable release is a real gap rather than a
completeness one.

**Why it matters.** The cost is asymmetric and rises with time: a DOI minted
now covers every later release, while one minted after the software has been
used in teaching cannot be applied backwards to the version somebody actually
ran. It is also the half of provenance this repository does not yet do — it
holds every stored constant to a traceable source and offers no way to trace a
result back to the simulator that produced it.

**Where.** A `CITATION.cff` at the repository root, which GitHub renders as a
"Cite this repository" control. The README half is blocked by the freeze
(`.claude/rules/readme-hold.md`) and belongs to `PL-N092`, the README rewrite.

**Note on verification.** The mechanics below were not confirmed against
current documentation: egress to `github.com`, `docs.github.com` and
`zenodo.org` is refused from this environment (measured 2026-09-05, `CONNECT
tunnel failed, response 403`), and the Citation File Format is not indexed by
the PubMed route `.claude/rules/citing-sources.md` names. Confirm the current
CFF schema version and the Zenodo release hook before implementing, rather
than taking them from this item.

**Done when.** A `CITATION.cff` at the root validates against the current
schema and names the software, its authors, the license, the version, and the
release date; whether to mint a DOI, and through which service, is the project
owner's decision and is recorded here when they make it.
