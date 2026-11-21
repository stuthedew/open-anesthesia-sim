---
id: PL-RMNP
title: Check every section of docs/MODEL.md against the code and data files: fix each plain fact error, note what PL-SZ6G will change, and file what needs the owner's clinical judgment
priority: P2
effort: M
status: ready
classes: docs
feature: model-spec-accuracy
touches: docs/MODEL.md, docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md
added: 2026-11-21
payoff: a clinician or contributor reading docs/MODEL.md is not told the simulator does something it does not do
verify: grep -qE '^\*\*Sections checked\.\*\*' docs/items/PL-RMNP*.md
sweep: reads every section of docs/MODEL.md against the code and data files, and files each claim the tree contradicts that it cannot correct as a plain fact
---

**Problem.** Check every section of docs/MODEL.md against the code and data files: fix each plain fact error, note what PL-SZ6G will change, and file what needs the owner's clinical judgment

**Why it matters.** `docs/MODEL.md` is the authoritative specification of the
model as implemented, and a clinician or a contributor who trusts a wrong
sentence in it can reach a wrong conclusion from a correct number. Of the 133
findings in `docs/blind-review-findings.tsv`, 42 are coded `doc-claim-wrong`:
a document that claims something the code does not do. That is the largest
category, ahead of 35 coded `code-bug` (`PL-WKKH`, the streamlining study's
record). Those findings were each made on the diff of one item. No pass has
read the whole document against the tree.

The project owner approved this sweep on 2026-11-21 02:00Z, in the Projects
thread "Check the model spec against the code" ("Do all 3 actually").

**How.** Each section of `docs/MODEL.md` is read against the code, the data
files under `src/anesthesia_sim/data/` and the tests it names. Every checkable
claim gets one of four verdicts:

1. **Holds.** The code does what the sentence says.
2. **Plain fact error.** The sentence states a value, name, behaviour or test
   that the tree contradicts, and the code is right. It is corrected in place,
   with no value, equation or citation of the model changed.
3. **`PL-SZ6G` will change it.** The claim is about the simulation step, how
   time is held or when a control change takes effect. `PL-SZ6G` (the build of
   one exact step per whole second) is in flight and rewrites those, so the
   claim is listed here and left as it is.
4. **Needs the owner.** The document and the code disagree and which is right
   is a clinical or modelling judgment, or the code is wrong on a path the
   safety-critical standard covers. It is filed as its own item with the
   question recorded.

Within-section restructuring of `docs/MODEL.md` stays held until `PL-48MX`
(the clinician's model description replaces what is left) closes, so a fix
here changes the sentence that is wrong and nothing around it.
`docs/INTERFACE.md` is a sibling thread's sweep and is not read here.

**Done when.** Every section of `docs/MODEL.md` has a row in a table of
sections checked in this brief, with its count of claims checked and what was
found. Each plain fact error is corrected on this item's branch. Each claim
that `PL-SZ6G` will change is listed. Each finding that needs the owner is an
item of its own.

**Generator check.** Work the owner asked for, and no new mechanism. The fact
each finding misreads is whether a `docs/MODEL.md` sentence about what the
model computes matches what it computes, which `PL-B6YV` (a document sentence
about what the model computes, checked against the code) already states as a
head. This item is the sweep of that fact over the whole document, so each
item it files is counted under `sweep:` and is not a new head.
