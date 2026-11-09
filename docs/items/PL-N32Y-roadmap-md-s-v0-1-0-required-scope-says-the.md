---
id: PL-N32Y
title: ROADMAP.md's v0.1.0 Required scope says the release added tissue:blood partition data, where the agent data files store tissue:gas
priority: P2
effort: S
status: done
classes: docs
feature: release-roadmap-seam
touches: ROADMAP.md
added: 2026-09-13
closed: 2026-11-09
pr: 2071
verify: grep -qF 'tissue_gas_partition_coefficients' ROADMAP.md && python3 tools/doc_check.py check
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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "Not wholly apparatus, but unable to change what a reader of the simulator sees" and "Waiting on an answer that holding v0.5.0 open would not produce".

> `PL-N32Y` is a correction to this document's account of a *past* release. v0.1.0's Required scope says that the release added tissue:blood partition data, but the agent files store tissue:gas. The scientific half is already fixed where a reader of the model meets it. `PL-212V` corrected `docs/MODEL.md`'s specification, and `PL-H46J` gave the Symbols table the Code column that maps each symbol onto `core/`. Both landed in v0.4.17. So what is left is the history, and it cannot affect a reader of the simulator. `PL-N32Y` is also `needs-decision`, on a question that only the project owner can answer. The question is whether a frozen `Required scope` line is corrected or annotated when it turns out to be wrong. Holding v0.5.0 open would not produce that answer.

> - PL-N32Y (S) ROADMAP.md's v0.1.0 Required scope says the release added tissue:blood partition data, where the agent data files store tissue:gas

**Done 2026-11-09.** v0.1.0's Required scope line keeps its wording and carries a dated note naming `tissue_gas_partition_coefficients` and the function that derives tissue:blood (`core/numerical_envelope.py`, `tissue_blood_partition_coefficient`; `TissueGroup` no longer holds it). § "Writing a milestone entry" now states the rule: a shipped release's Required scope line found wrong is annotated with a dated note, never rewritten.
