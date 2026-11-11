---
id: PL-1VXY
title: Apply the 2026-11-05 chapter reads' within-section findings to docs/MODEL.md: PL-BSMF applied only the outline read, and the 30 chapter reads in /mnt/project-files/v0.7.0/repo-copy-edit/runs/docs-MODEL-md/structure/chapter-NN.txt also move paragraphs within a section and fix headings; their row numbers are from cfb15a4a, before the restructure
priority: P2
effort: L
status: blocked
classes: docs
feature: model-md-structure
touches: docs/MODEL.md
blocked-by: PL-48MX
added: 2026-11-07
payoff: each section of MODEL.md reads in the order its reader needs, so a qualifying paragraph comes before the value it qualifies, and the line edit can start
verify: ! grep -qF 'milestone (v0.1.0) must demonstrate' docs/MODEL.md
---

**Problem.** PL-BSMF applied only the outline read's 77 findings to docs/MODEL.md (order, repeated facts, misplaced passages, two headings). This item applies the within-section findings of the 30 chapter reads of 2026-11-05, which move paragraphs within a section and fix headings. The reads are in /mnt/project-files/v0.7.0/repo-copy-edit/runs/docs-MODEL-md/structure/chapter-NN.txt.

**Found 2026-11-07 at the close of `PL-BSMF`.** The chapter reads contain
several hundred findings inside single sections, such as paragraphs in the
wrong order, a heading that no longer covers its section, and release history
inside § "Purpose". Their queries were filed separately, as `PL-HR4T` and the
twelve others that `PL-BSMF` names. The reads' row numbers are from cfb15a4a,
before the restructure, so each structural finding has to be found again in
the restructured text.

Apply the findings before the line edit, because the owner ruled on 2026-11-07
that no document is line edited ahead of its restructure. Audit the old text
against the new as `PL-BSMF` did, with two reviewers and in both directions.

**Checked 2026-11-09:** The chapter reads are not in this checkout or this
container. `ls /mnt/project-files` finds no such directory, so the reads can be
opened only where the project's files are mounted, as in a Projects thread.
One within-section finding of the kind this item names is still present:
`grep -n 'must demonstrate' docs/MODEL.md` finds § "Purpose" opening with
release history, "The “Sevo works” milestone (v0.1.0) must demonstrate:"
(line 52), and ending with what v0.2.0 added (lines 65 to 67). `PL-BSMF`'s
`verify:` tested for "The milestone must demonstrate", which the restructure
reworded, so it passes while the release history stays.

**Why it matters.** The restructure put the chapters in order, but inside many
sections a reader still meets a paragraph before the one it depends on, a
heading that no longer covers what is under it, or release history where they
look for what the model does. A clinician reading a section to decide whether
to trust a value can reach the paragraph that qualifies it late, or miss it.
The next line edit of `docs/MODEL.md` waits on this item, because the owner
ruled on 2026-11-07 that no document is line edited before its restructure.

**Done when.** Each within-section finding of the 30 chapter reads has been
found again in the restructured text, and either applied or recorded as no
longer applying, with the reason. The old and new text have been audited in
both directions by two reviewers, as `PL-BSMF` did, so that no statement was
lost. The queries the reads raised stay with their own items (`PL-HR4T` and
the twelve others that `PL-BSMF` names).

**Size, and a recommended split (2026-11-09).** This is effort L and too large
for one session. `PL-BSMF` applied the outline read's 77 findings as one L
item. This item holds several hundred findings across 30 chapter reads, each
to be found again by hand in a 12,763-line document, and each change owes the
two-reviewer audit. Split it before starting into about six slices of five
chapter reads each, in the restructured chapter order, each with its own pull
request and audit. The first slice covers § "Status" through § "Conventions",
which holds the § "Purpose" finding above. Give each slice a `verify:` that
removes one passage its reads name, as this item's does. The work needs the
reads mounted, so it suits a Projects thread.

**Generator check.** One-off: this item applies the `docs/MODEL.md`
structure-read sweep of 2026-11-05. It is not a defect with a cause of its own.

**Waits on the split, 2026-11-11.** The project owner decided on 2026-11-11
to split `docs/MODEL.md` by reader (`PL-P3GZ`). The text this item edits
moves to three new documents (`PL-CTXZ`, `PL-6PPZ`, `PL-FWR6`), and what is
left is replaced by the description the owner accepted (`PL-48MX`). So this
item waits on `PL-48MX`. The three items that then sort each document
(`PL-SY7G`, `PL-4H8Q`, `PL-N83Z`) apply this item's findings for the
sections they hold, and the session that applies the last of them closes
this item.
