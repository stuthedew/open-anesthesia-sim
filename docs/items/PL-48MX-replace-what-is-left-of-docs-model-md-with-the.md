---
id: PL-48MX
title: Replace what is left of docs/MODEL.md with the clinician's model description the owner accepted, brought up to date and carrying its stored-value markers (stage 2 of the split PL-P3GZ decided)
priority: P1
owner-priority: P1, 2026-11-11, ratified
effort: L
status: blocked
classes: docs
feature: model-md-structure
touches: docs/MODEL.md, docs/prose-review/model-description-draft.md, docs/prose-review/README.md, tools/doc_check.py, .claude/rules/plain-writing.md, CLAUDE.md
blocked-by: PL-FWR6
added: 2026-11-11
payoff: a clinician who opens docs/MODEL.md reads the 15,500-word description of the model, its values and its limits, and nothing written for a developer
verify: ! grep -q 'model-description-draft' docs/prose-review/README.md && ! grep -q '^## How this document is held to the tree$' docs/MODEL.md
---

**Problem.** Replace what is left of docs/MODEL.md with the clinician's model description the owner accepted, brought up to date and carrying its stored-value markers (stage 2 of the split PL-P3GZ decided)

**Why it matters.** The project owner read
`docs/prose-review/model-description-draft.md` on 2026-11-11 and accepted it
as the document a clinician should get (`PL-B07T`), then decided to split
`docs/MODEL.md` by reader (`PL-P3GZ`). After the three moves of stage 1
about 24,000 words remain in `docs/MODEL.md`: the status, purpose and
intended use, the model boundary, assumptions, conventions, symbols, tissue
groups, compartment capacities, governing equations and known limitations,
and the section on how the document is checked. The draft states the same
model in about 15,500 words for a clinician. While both exist, nothing
checks the draft, and a change to the model would have to edit both.

**What to do.**

1. Bring the draft up to date. It was written from `docs/MODEL.md` at
   `50af1a2e`. Apply to it every change `docs/MODEL.md` has taken since
   (`git log 50af1a2e.. -- docs/MODEL.md`, and the three documents that
   stage 1 moved text into).
2. Put the stored-value markers back in the draft, and add its path to the
   documents that `tools/doc_check.py` checks them in. `PL-B07T` § "What
   `PL-P3GZ` takes from this" names both, and the values that the draft
   states beside a different quantity.
3. Place each fact that `PL-B07T` lists as left out in the home it names:
   one of the three developer documents, a docstring or test, the item that
   took the decision, or `ROADMAP.md`. Cut a fact only after confirming that
   its home holds it, and record each cut in this item.
4. Make the draft `docs/MODEL.md`, and delete
   `docs/prose-review/model-description-draft.md` and its entry in
   `docs/prose-review/README.md`.
5. In `.claude/rules/plain-writing.md`, leave `docs/MODEL.md` one reader, a
   clinician or educator, and remove the paragraph that keeps developer
   detail in notes opening "**For developers.**" (`PL-W8FL`), because the
   document then has no such notes. In `CLAUDE.md`, say which document is
   the home of which part of the specification.
6. Ask the owner to read only what differs from the draft they accepted,
   quoted before and after.

**What it must not do.** Change no value, unit, equation, condition or
citation except to bring it up to date with the tree. Set no word target
(`PL-J1ZM`).

**Done when.** `docs/MODEL.md` is the accepted description, up to date with
the tree and carrying its stored-value markers; the draft file is gone;
every fact of the replaced text is in `docs/MODEL.md`, in its named home, or
recorded here as cut; the owner has read the differences; and `make check`
passes.

**Generator check.** Part of the fix for the cause that `PL-P3GZ` records:
the repository named no home but `docs/MODEL.md` for a test's description,
an interface requirement or a value's source history, so each change added
them there. No new head.

**Two fact fixes landed in `docs/MODEL.md` after the draft was written, and the
draft still carries one of them (2026-11-14).** `PL-2BG1` and `PL-G0R3` merged
together, and step 1's `git log` picks both up. Neither is a restructure.

1. `PL-2BG1`: the stored MAC is a single adult value whose source, De Wolf et
   al. 2012, states no age for it. `docs/MODEL.md` no longer calls it "1 MAC
   for a 40-year-old adult" or "at age 40", and its 22% comparison is now
   against Mapleson's confidence limits only. The draft still has the old
   wording in four places: the symbol row for $`\mathrm{MAC}_\%`$ ("at age
   40"), the parameter table row "1 MAC, 40-year-old adult (percent)", the
   paragraph that opens "**MAC.** The stored MAC is 1 MAC for a 40-year-old
   adult", and "larger than either source's confidence limits". Change all
   four when the draft is brought up to date. The sentence that compares the
   stored MAC with Katoh's MAC "at age 40" is a comparison and stays.
2. `PL-G0R3`: `docs/MODEL.md` now says "simulated", "computed" or "come from
   runs on" where it reported a result of this simulator, and keeps
   "measured" for patients, tissue and equipment. The draft's own uses of
   "measured" were read on 2026-11-14 and all describe real measurements, so
   nothing in the draft changes for this one.
