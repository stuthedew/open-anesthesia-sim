---
id: PL-8DDG
title: Add CITATION.cff so the simulator is citable, and decide whether CONTRIBUTING.md is warranted yet
status: untriaged
feature: project-introduction
touches: CITATION.cff, README.md
added: 2026-09-05
---

**Problem.** The repository root has `LICENSE` and nothing else of the
community set: no `CITATION.cff`, no `CONTRIBUTING.md`. Found while deciding
`PL-RM83` (what `README.md` is for), against the documentation standards
recorded in that item.

**Why it matters.** `CITATION.cff` is the clear half. GitHub parses a root
`CITATION.cff` into APA and BibTeX snippets behind a "Cite this repository"
control, so the cost is one small file and the return is that anyone writing
about the simulator cites it correctly and consistently. Lee 2018 makes it
rule 10 of ten — "tell people how to cite your software" — and recommends
exactly this file plus a DOI and a written reference. It matters more here than
for most hobby projects: the project owner writes resident curriculum material
and journal articles, so a citable simulator is likely to be cited in their own
work first, and an uncitable one gets referenced as a bare URL that rots.

A DOI is the natural companion — Zenodo mints one per GitHub release, and JOSS
is the other route — but that is a decision with a publication dimension, not a
file to add, so it is named here and not assumed.

**Where.** `CITATION.cff` at the repository root; a citation line in
`README.md`, which is frozen until `PL-N092` (rewrite README as a
human-readable introduction) runs, so the two should land together or the
README line should wait.

**Open question for the project owner.** Is `CONTRIBUTING.md` warranted yet?
JOSS requires community guidelines covering how to contribute, report issues
and seek support, and `PL-RM83` decided that audience A — a contributor
interested in both anesthesiology and code — is one of the two readers the
README is written for, which argues yes. Against it: this is a solo project
with an unusual contribution model, and a `CONTRIBUTING.md` that describes the
`bin/docket` queue and the agent-session workflow would be documenting
scaffolding to an audience that does not exist yet. A holding position that
costs nothing is a "Contributing" section in the rewritten README pointing at
issues, and a real `CONTRIBUTING.md` only when someone actually asks.

**Done when.** `CITATION.cff` exists at the root, validates, and names the
project, the owner and the license; GitHub's "Cite this repository" control
renders from it; and the `CONTRIBUTING.md` question is answered either way in
this item.
