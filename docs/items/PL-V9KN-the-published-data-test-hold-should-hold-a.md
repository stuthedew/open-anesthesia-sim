---
id: PL-V9KN
title: The published-data test hold should hold a change to a test's code and let an edit only to its comments, docstrings or failure messages merge on green, decided by comparing the parsed files
status: done
feature: review-hold
milestone: v0.6.22
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py, .claude/skills/pull-request/SKILL.md
added: 2026-11-22
closed: 2026-11-22
pr: 2252
filed-pr: 2250
tests: subprojects/docket/tests/test_arming.py::test_a_prose_only_edit_to_a_reference_test_arms, subprojects/docket/tests/test_arming.py::test_code_of_sets_aside_only_prose
---

**Problem.** `bin/docket arm` holds a branch for the owner's read when it takes away any existing line of a test under `tests/reference/`, which compares the model with published data (`PL-XSRG`, the published-data test hold). It counts lines with `git diff --numstat`, so an edit only to a comment, a docstring or an `assert` failure message holds the same as a widened tolerance. `PL-KNHK` (#2250) re-pointed 34 document mentions in five of these tests, changed no code, and still waited for the owner.

**Why it matters.** The hold exists because a loosened tolerance or a changed expected value there is where a weakened test would hide a wrong clinical value. Holding prose edits spends the owner's read where no clinical judgment is asked, and a hold that fires on wording trains the reader to approve it unread. The sources read for this, on 2026-11-22:

1. FDA, *General Principles of Software Validation; Final Guidance for Industry and FDA Staff* (11 January 2002), https://www.fda.gov/media/73141/download, read in verbatim text through § 5.2.5. § 4.9 says "Self-validation is extremely difficult" and "an independent evaluation is always better, especially for higher risk applications", which is why the hold is the owner's. § 4.8 says "Validation coverage should be based on the software's complexity and safety risk". § 5.2.5 calls the expected result "an essential element of a software test case".
2. FDA, *Computer Software Assurance for Production and Quality Management System Software* (3 February 2026), https://www.fda.gov/media/188844/download, read in verbatim text through § V.A(2). § V.A(2), p. 8, asks for assurance activities "commensurate with the medical device or process risk", and § V, p. 5, for a validation burden "no more than necessary to address the risk".
3. D. Kawrykow and M. P. Robillard, "Non-Essential Changes in Version Histories", ICSE 2011, https://www.cs.mcgill.ca/~martin/papers/icse2011.pdf, read in verbatim text through § 5.2. § 3 says whitespace and documentation-related updates are "already ignored by other change analysis tools", and § 4.1 detects the remaining non-essential changes by differencing abstract syntax trees.
4. GitHub Docs, "About code owners", https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners, read in full. Owner review applies to any change to an owned path, and the page offers no exemption by kind of change.

**Decision.** Hold a change to a published-data test's code, and let a change that leaves the parsed program identical merge on green (project owner, 2026-11-22, ratified, "Agree with recs", over keeping the line count). The parse tree already decides the same question for `PINS`: `pinned_definitions` leaves out a test's docstring, so rewording what a pinned test says about itself is not a change to what it pins.

**Done when.** `bin/docket arm` reads each published-data test that loses a line at the merge base and at the branch tip, parses both, and holds it unless the two trees match once each docstring and each `assert` statement's failure message is set aside. Comments and layout are already absent from a parse tree. A file that is deleted, is not Python, or will not parse on either side still holds. A failure message passed to a call, such as `pytest.fail`, is code and holds. `subprojects/docket/tests/test_arming.py` pins each answer, and `.claude/skills/pull-request/SKILL.md` says the same in its sentence on the hold.

**Generator check.** Not a new defect: `PL-XSRG` measured lines because git counts them directly, and the case it did not write for is a prose-only edit.

**Done, 2026-11-22.** `code_of` in `subprojects/docket/src/docket/arming.py` dumps a file's parse tree after removing each docstring and each `assert` statement's failure message. `_code_changed` reads each published-data test that loses a line at the merge base and at the tip, and sorts it three ways. Two sides that give the same program arm. Two sides that differ, including a deleted test that the tip reads as empty, go to `Verdict.references`, which holds with "it changes the code of N tests". A side that will not parse under the `python3` that runs `bin/docket`, or that git would not hand over, goes to the new `Verdict.uncompared`, which holds as if the code changed and says why, so the owner's go-ahead still releases it rather than the answer turning `unknown`. `test_code_of_sets_aside_only_prose` pins what counts as prose and what as code, and `test_a_prose_only_edit_to_a_reference_test_arms` pins the four answers: a prose-only edit arms under a `not needed` record, an unparsable side and a deleted test hold, and the owner's go-ahead releases them. Run against `arming.py` as it stood before this change, the second test failed at the prose-only edit with `assert 'hold' == 'arm'`. The full project check passed on the branch. Files checked in the documentation sweep: `arming.py`'s module header, the `REFERENCE_TESTS` comment and the `Verdict` and `_Change` docstrings; `.claude/skills/pull-request/SKILL.md`; and `docs/maintainer.md`, `docs/worker.md`, `docs/apparatus.md`, `CLAUDE.md`, `.claude/rules/` and the close-out mode, none of which states the hold.
