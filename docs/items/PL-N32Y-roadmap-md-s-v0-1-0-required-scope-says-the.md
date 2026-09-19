---
id: PL-N32Y
title: ROADMAP.md's v0.1.0 Required scope says the release added tissue:blood partition data, where the agent data files store tissue:gas
priority: P2
effort: S
status: ready
classes: docs
feature: release-roadmap-seam
touches: ROADMAP.md
added: 2026-09-13
verify: python3 tools/doc_check.py check && grep -qF 'tissue_gas_partition_coefficients' ROADMAP.md
---

**Problem.** ROADMAP.md's v0.1.0 Required scope says the release added tissue:blood partition data, where the agent data files store tissue:gas

`ROADMAP.md` v0.1.0 § "Required scope" reads "Add sevoflurane blood:gas and
tissue:blood partition data with source provenance and validation". The blood:gas
half is right. The tissue half is not what shipped: the agent data files store
`tissue_gas_partition_coefficients`, and `TissueGroup.tissue_blood_partition_coefficient`
derives the blood-referenced form from it by dividing by blood:gas.

**Why it matters.** This is the exact confusion `PL-212V` was filed on — the
two ratios differ by a factor of $`\lambda_{b:g}`$, which is 0.65 for
sevoflurane and 0.42 for desflurane, so a reader who takes the stored numbers
for tissue:blood values reads every tissue capacity wrong by that factor. The
primary literature does not hold a convention that would catch it: Baker and
Farmery name the same quantity three ways in one chapter. `PL-212V` fixed the
specification; this is the same statement in the release history.

**The judgment this needs, and why it is not a typo fix.** A Required scope
list is a frozen record of what a release was scoped to do, so correcting one
edits history rather than a current claim. Either the line is corrected with a
note that the stored form is tissue:gas, or it is left as written and the
history is read as history. That is the project owner's call about how
`ROADMAP.md` records past releases, not a session's.

**Where.** `ROADMAP.md`, v0.1.0 § "Required scope".

**Found.** Doc sweep for `PL-H46J` and `PL-212V`, 2026-09-13.

**Decision needed.** Whether a `Required scope` line is corrected once it is
found to be wrong about what shipped, or left standing as the record of what
the release was *scoped* to do and annotated instead. Both are defensible, and
the choice is about what `ROADMAP.md`'s release history is for rather than
about this sentence: it sets the precedent for every later correction, so it is
worth answering once instead of per line. The one reading to rule out is
leaving it unmarked, because the confusion it carries is the exact one
`PL-212V` was filed on and the literature offers no convention that would catch
it.

**Done when.** The v0.1.0 `Required scope` line no longer lets a reader take
the stored coefficients for tissue:blood values - by correction or by
annotation, on the answer above - and whichever route is chosen is stated in
`ROADMAP.md`'s own development rules, so the next such line is not reargued
from scratch.

**Decided 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
The decision is made and it is clause 4: **annotate with a dated note, never
rewrite the scope line.** A `Required scope` list asserts what a release was
scoped to do, which is a record; editing it to carry a later fact is the one
thing clause 4 forbids. The note names the stored form -
`tissue_gas_partition_coefficients` - so the confusion `PL-212V` was filed on
cannot survive the annotation. Promoted from `needs-decision` to `ready`, with
a `verify:` command run on 2026-09-19 and watched to fail (exit 1: `doc_check`
is green, `ROADMAP.md` names the stored form nowhere).
