---
id: PL-GT0J
title: doc_check reads a provenance or absent-path marker as nothing when its <!-- stands alone on the line before, so a prose value that disagrees with its data file and a path marked absent that exists both pass; latent
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tests/unit
added: 2026-10-04
---

**Problem.** doc_check reads a provenance or absent-path marker as nothing when its \<!-- stands alone on the line before, so a prose value that disagrees with its data file and a path marked absent that exists both pass; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 4.6 kind 2: an HTML block opened by `<!--` runs to the line holding `-->`. `PL-R417`'s first slice declined a marker split after its kind, with `provenance:` on the opening line; with `<!--` alone above "provenance: data/agents/x.json mac = 1.8 -->", `check_prose_provenance` returns no error where the one-line form reports "states mac = 1.8 but data/agents/x.json holds 2", and `_absent_paths` declares nothing where the one-line form reports "marks `tools/built.py` absent, but it is in the tree". `SPLIT_MARKER_RE`, `PROSE_MARKER_RE` and `ABSENT_MARKER_RE` are each read a line at a time. Latent: no tracked `.md` line is `<!--` alone.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
