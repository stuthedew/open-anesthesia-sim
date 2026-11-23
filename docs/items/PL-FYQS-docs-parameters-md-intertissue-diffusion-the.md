---
id: PL-FYQS
title: docs/PARAMETERS.md § 'Intertissue diffusion: the missing fourth compartment' gives Yasuda 1991 and Hendrickx and De Wolf in full with reading records, while docs/VERIFICATION.md now points to their entries in docs/references/README.md; give each source one full citation
priority: P3
effort: S
status: ready
classes: defect, docs
feature: documentation-standard
touches: docs/PARAMETERS.md, docs/references/README.md
deferred-from: v0.7.0 - captured after the freeze; a repeated citation of sources that are the authority for no stored value, not safety or science
added: 2026-11-22
payoff: each of these three sources has one full citation, so a reader checking a limitation against its source never compares two copies to find the complete one
---

**Problem.** docs/PARAMETERS.md § 'Intertissue diffusion: the missing fourth compartment' gives Yasuda 1991 and Hendrickx and De Wolf in full with reading records, while docs/VERIFICATION.md now points to their entries in docs/references/README.md; give each source one full citation

**Where.** `docs/PARAMETERS.md` § "Intertissue diffusion: the missing fourth
compartment" lists Yasuda et al. 1991 (both papers) and Hendrickx and De Wolf
2008 with their full citations and reading records. `PL-R3J6` gave each
source one full citation in `docs/VERIFICATION.md`, which now points to the
entries in `docs/references/README.md`.

**Fix.** Keep one full citation for each source, in `docs/references/README.md`
or in this section, and point to it from the other. Keep each reading record
(route, pages and depth), because `.claude/rules/citing-sources.md` requires
it beside the claim it supports.

**Found by** the worker building `PL-R3J6`, 2026-11-22.

**Why it matters.** Two full copies of one citation can drift apart, and a
reader checking a value against its source then has to compare them to learn
which is complete. `PL-R3J6` found the same pattern in `docs/MODEL.md`, where
one copy had already lost its reading record.

**Done when.** `docs/references/README.md` is the only place in
`docs/PARAMETERS.md` and `docs/references/README.md` that gives the two Yasuda
et al. 1991 papers and Hendrickx and De Wolf 2008 in full. The source list in
`docs/PARAMETERS.md` § "Intertissue diffusion: the missing fourth compartment"
names each by authors, journal and year, points to its entry, and keeps every
page it read, the route and the depth.

**Generator check.** One-off: the copy was left behind when `PL-48MX` and
`PL-N83Z` moved the evidence for the known limitations out of `docs/MODEL.md`,
and `PL-R3J6` cleared the other copies. No head's `misread:` states this fact.

**Approach, researched 2026-11-23.** A reference list gives each source once,
and every other mention points to that entry: the ICMJE Recommendations,
"Preparing a Manuscript for Submission to a Medical Journal", § References,
number references "consecutively in the order in which they are first
mentioned" and identify them in text by number (icmje.org, page read in full
2026-11-23). The repository already follows this: `docs/references/README.md`
records "each source's full citation" (`docs/PARAMETERS.md` § "Source
hierarchy"), `PL-R3J6` pointed `docs/VERIFICATION.md` there, and the Workbook
entry in `docs/PARAMETERS.md` § "Agent amount" names what was read and
points to its README entry. So the README keeps the full citations, and the
source list here keeps its own reading record beside a pointer.
