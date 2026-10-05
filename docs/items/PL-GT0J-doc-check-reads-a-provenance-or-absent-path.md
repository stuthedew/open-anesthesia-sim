---
id: PL-GT0J
title: doc_check reads a provenance or absent-path marker as nothing when its <!-- stands alone on the line before, so a prose value that disagrees with its data file and a path marked absent that exists both pass; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-05
pr: 1358
payoff: a provenance or absent marker written across lines is refused by name, so no restated value or denied path goes unchecked for its layout
verify: grep -qF '"markers, a marker whose comment opens on the line above' tests/unit/test_doc_check.py
---

**Problem.** doc_check reads a provenance or absent-path marker as nothing when its \<!-- stands alone on the line before, so a prose value that disagrees with its data file and a path marked absent that exists both pass; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 4.6 kind 2: an HTML block opened by `<!--` runs to the line holding `-->`. `PL-R417`'s first slice declined a marker split after its kind, with `provenance:` on the opening line; with `<!--` alone above "provenance: data/agents/x.json mac = 1.8 -->", `check_prose_provenance` returns no error where the one-line form reports "states mac = 1.8 but data/agents/x.json holds 2", and `_absent_paths` declares nothing where the one-line form reports "marks `tools/built.py` absent, but it is in the tree". `SPLIT_MARKER_RE`, `PROSE_MARKER_RE` and `ABSENT_MARKER_RE` are each read a line at a time. Latent: no tracked `.md` line is `<!--` alone.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `SPLIT_MARKER_RE` does not match `<!--` standing alone on its line, and neither `PROSE_MARKER_RE` nor `ABSENT_MARKER_RE` matches the `provenance: ... -->` or `absent: ... -->` line under it, so `check_prose_provenance` and `_absent_paths` read the marker as nothing.

**Why it matters.** A provenance marker is what holds a value restated in prose to its data file, and an absent marker what holds a denied path to its absence, so with its `<!--` on the line above, a restated value that has drifted from `src/anesthesia_sim/data/` and a path marked absent that is in the tree both pass `make check`.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** A marker whose comment opens on the line above it is refused by name with the error a marker split after its kind already gets, read from the comment's HTML block rather than a line at a time; a `markers, ...` case in `CONTINUED_STATEMENTS` pins it.
