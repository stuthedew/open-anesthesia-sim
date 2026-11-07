---
id: PL-G6DP
title: Restructure ROADMAP.md, slice 4: move the toolchain policy to docs/maintainer.md, and the account of what the release tools read to the workflow documentation, keeping in the roadmap what each guarantees
priority: P2
effort: M
status: blocked
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
blocked-by: PL-DWGC
deferred-from: v0.7.0 - filed after the gate froze; the roadmap's arrangement and wording, with no displayed value depending on it
added: 2026-11-07
---

**Problem.** Restructure ROADMAP.md, slice 4: move the toolchain policy to docs/maintainer.md, and the account of what the release tools read to the workflow documentation, keeping in the roadmap what each guarantees

**Source.** The copy editor's structure read of `ROADMAP.md`, run on the project owner's Mac on 2026-11-06: one read per chapter, then one read of all the chapters' outlines together. Row numbers are `ROADMAP.md` at `aff76df1`, the last commit to change it before slice 1 (`PL-W0TS`), so a later slice finds each passage by the words the finding quotes. The project owner chose to file the findings as items and apply them one slice per pull request (project owner, 2026-11-07, ratified, over one pull request for the whole restructure), because the release tools read the roadmap's gate sections and a small move is easier to check against them. The raw reads are in the project's shared folder, `/mnt/project-files/v0.7.0/repo-copy-edit/mac-structure-reads/ROADMAP-md/structure/`.

**Why it matters.** These passages say what `bin/docket` and `tools/doc_check.py` read, count and refuse. They serve the sessions that run those tools, and the roadmap's reader does not know the tools' names. Kept in the roadmap, they go stale as the tools change. One already has: v0.5.0's gate section describes a `_declined_ids` reader in `tools/doc_check.py`, and no such reader exists any longer. The toolchain policy is tied to no release, while § "Project roadmap" says the file covers releases.

**The findings, as the outline read gave them** (numbered by their order in the read: 8, 9).

- Written for another reader (7455-7513): § "Keeping the toolchain current" is a standing tooling policy tied to no release, but § "Project roadmap" says the file covers releases only (7-11). It belongs in the workflow documentation; the writing rule's table lists `docs/maintainer.md` among the workflow's files. ROADMAP keeps nothing of it.
- Written for another reader (163-259, 3334-3342, 3540-3546, 4819-4827, 5807-5840, 5946-5959, 6301-6315, 7175-7182, 7584-7595, 7706-7708, 7885-7910): these passages say what `bin/docket wave`, `check` and `gate`, `tools/doc_check.py` and `check_gate_reentries` read, count and refuse. They serve the sessions that run those tools, and the reader does not know the tools' names. They belong in the workflow documentation. § "The debt gate" keeps what they guarantee: each deferral is recorded on its item, with the gate it leaves and why, and a check refuses any open debt item that the gate neither places nor defers. § "Versioning decision" keeps two guarantees: every completed version is tagged on its cut, and the tag, not the notes, records what shipped.

**Related.** `PL-BYHS` already records the outline read's query on the toolchain policy: it names Flet as a pre-1.0 dependency with an upper bound, and v0.4.26 removed Flet. The policy moves to `docs/maintainer.md` with that error, or after `PL-BYHS` fixes it, whichever lands first. The roadmap keeps what each tool passage guarantees: each deferral is recorded on its item, with the gate it leaves and why, a check refuses any open debt item that the gate neither places nor defers, every completed version is tagged when it is cut, and the tag, not the notes, records what shipped.

**The findings inside each chapter, as the chapter reads gave them.** Each chapter read also ended with an outline of one line per paragraph, which is left out here and kept in the shared folder. Each read is quoted whole, as a block, so that its quotations of the roadmap are not taken for this item's own claims.

**Chapter read 43: § "Keeping the toolchain current", rows 7455-7513.**

```text
- Rows 7460-7467 make two points, and the main one comes last. That point is at 7464-7467: "The failure being guarded against … is returning after a gap to a tree that no longer builds." Open the paragraph with it. The three version limits (Python 3.14 and 3.15, Flet below 1.0, dev tools with lower bounds only) can then follow as the reason it will happen.
- The point that the version limits go out of date is made twice. It appears at 7460-7461 ("every version constraint in `pyproject.toml` will be wrong eventually"), with the lead's "a scheduled run notices" (7457). It appears again at 7498-7499 ("The current pins are correct today. The point is to know when one stops being correct"). It belongs at 7457 and 7460-7461, and 7498-7499 keeps nothing. The 7498 sentence has no date, so it would read as true whenever someone reads it.
- "not to raise numbers on a schedule" (7499) repeats the lead's "Nothing upgrades on a schedule" (7458). The lead keeps it. Rows 7497-7503 keep the decision (no automated dependency pull requests and no version-bump campaign) and its reason.
- How the breakage happened at 7469-7473 (`prefer_fwd_module=`, `typing._eval_type`, 3.14.0rc2) is for a developer. It belongs in `pyproject.toml`, which 7469 says already records this case. The roadmap keeps one sentence: pydantic 2.12.4 and the final CPython 3.14.0 release together stopped parameter loading, from one patch release and one interpreter build. The pointer to `pyproject.toml` stays.
- How each check works (7479-7490) is for a developer and belongs in comments in `.github/workflows/drift.yml`. This covers "It resolves them with `uv sync --upgrade`" (7480), "It uses pytest-randomly, with the date as the seed" and "The run's output names the seed that reproduces the failure" (7488-7490), and the job names `dependencies`, `interpreter` and `order` as the subjects of the bullets. For each check, the roadmap keeps what it tests, how often it runs and what a failure means. From 7483-7484 it keeps the promise that the interpreter check does not change the project's declared Python range.
- The shuffled-order check (7487-7490) is about tests that depend on each other. It is not about a dependency or the interpreter changing, so it fits neither the heading nor the lead (7457). It belongs where the roadmap covers the test suite, and this section keeps only a pointer saying it shares the scheduled workflow. This chapter cannot show whether such a section exists, so the outline read should place it.
- "two questions that `quality.yml` is right not to ask" (7476) makes the reader read ahead, because the reason only comes at 7505-7508 ("Why it reports rather than gates"). At 7476, state only the fact that the checks every change must pass do not ask these questions. Leave the reason at 7505-7508.
- "Automated bumps were considered and rejected, on the evidence this project already cites about narrow versus broad automation" (7500-7501) is decision history and belongs in the item that holds the decision. The roadmap keeps the decision (7497-7498) and its reason: "Broad automation accumulates noise until people route around it" (7501-7502).
- The heading at 7455, "Keeping the toolchain current", promises regular upgrades. The section says nothing upgrades on a schedule (7458) and describes noticing a change and leaving the upgrade to the owner. A heading that fits is "Noticing when dependencies or Python change". Other files may cite the section by its heading, so a rename must update them.
- The section is 549 words, and its bold labels ("What notices", "What does not happen", "Why it reports rather than gates") already let the reader find their way. It needs no subheadings.
- Query: the reader needs to know what "the gate" (7464) and `quality.yml` (7476) are, and the chapter does not say.
- Query: the lead says "the owner decides" (7457), but the chapter does not say how a failed run or the report of versions beyond the bounds (7492-7495) reaches the owner. It could be a notification, a new item or issue, or only the run's log.
- Query: the chapter does not say which item holds the decision against automated bumps. It also does not say which source "the evidence this project already cites about narrow versus broad automation" (7500-7501) is. The chapter names `PL-ZBJ0` only as the record of how broad automation fails.
```

**How to apply.** Move and deduplicate only. No sentence is reworded, except a pointer that replaces a restatement, a word such as "above" or "below" that a move made wrong, and a heading. The line edit of what this slice changes follows in `PL-YRY3`, once the copy editor no longer drops requirements (`PL-F0Q2`). Each finding is applied, or recorded here with the reason it was not. A query that the tree answers is answered in the pull request, and one that needs the author is filed as its own item under `roadmap-structure`. Whether a finding that moves decision history out of the roadmap and into an item is applied is decided by the project owner's answer in `PL-LVN8`. Before the pull request is marked ready, two reviewers compare the old and new text passage by passage for any change of meaning. The move-only restructures of the machine documents and of `docs/interface-provenance.md` each changed 10 or 11 meanings that only such a comparison found.

**Done when.** Each finding below is applied, or recorded here with the reason it was not. No statement is lost: every sentence that leaves its place is kept at its one home, or replaced by a pointer that names that home. `bin/docket wave`, `bin/docket gate` and `bin/docket check` give the same answers before and after the slice, and `make check` passes.

**Generator check.** The repeats came from accretion. Each change that touched a topic stated its own record in the section it was working in, instead of pointing to the section that already held it. The structure read found the same shape in every document it read (`PL-BSMF`, `PL-SVGH`, `PL-T8RL`, `PL-39ZK`, `PL-3MTS`), so these are one sweep's findings. No check can decide whether two sentences state one fact. The structure read, which the project owner put ahead of every line edit on 2026-11-07, is the procedure that catches the shape. Not recorded as a generator.

**Left for this slice by `PL-DWGC` (2026-11-07).** Slice 3 reordered
`ROADMAP.md` § "Release tags and release notes" under four subheadings and
left these to this slice, because each leads into a sentence about the tools:

- "This section deliberately does not restate which versions those are ...
  which it twice was not" is decision history and moves to an item. It leads
  into "Instead, `tools/doc_check.py` checks ...", so the two move together.
- The v0.5.3 incident ("`v0.5.3` was pushed before its release merged ...",
  `PL-YKSD`) goes to `PL-YKSD`. It leads into "So `tools/doc_check.py` also
  reads the `pyproject.toml` ...".
- "Failing on the window would turn `make check` red ... (PL-R7C0)" goes to
  `PL-8HJ2` and `PL-R7C0`.
- "The claim this section makes is about navigation only. It stops being true
  the moment either mechanism behind it changes ..." goes. The first sentence
  describes the text, and the two mechanisms go with the tool text.
- The rule for writers ("A version that has genuinely gone out untagged is
  named in a bold sentence here ...") goes with the check's documentation.
  `tools/doc_check.py` reads both bold claims, the untagged count and "**One
  version shipped with a stale version file**", only between "**Tags.**" and
  the next heading, so they must stay in the first subsection or the check
  must change with them.

Keep in the roadmap the exemption that a release's own cut pull request is
inside its own span. Slice 3 cut the other copy of that convention as a
repeat. `PL-V82M` corrects what the exemption says the next release does.
