---
id: PL-P7B3
title: bin/docket arm checks unreviewed prose, grown passages and the pull request body only on a branch that changes a simulator path, so text added after the copy editor's run to ROADMAP.md or another reviewed document outside those paths is not held: 46 of the last 300 merges changed such a document and no simulator path, 36 of them ROADMAP.md
status: untriaged
feature: copy-editor
added: 2026-11-11
---

**Problem.** bin/docket arm checks unreviewed prose, grown passages and the pull request body only on a branch that changes a simulator path, so text added after the copy editor's run to ROADMAP.md or another reviewed document outside those paths is not held: 46 of the last 300 merges changed such a document and no simulator path, 36 of them ROADMAP.md

**Two of the three questions below are not on `main`.** The project owner stopped `PL-HNNH` and `PL-TG6P` on 2026-11-11. The second and third questions below exist only on branch `claude/peaceful-noether-5bvpno`, in draft pull request #2115, and have not merged. If those items are dropped, this item covers the `Prose-review:` hold alone.

**Problem.** `bin/docket arm` asks its three prose questions only of a branch that changes a simulator path: `src/`, a test that imports the simulator, `docs/MODEL.md`, the parameter files and `README.md`. The questions are whether prose was added after the newest `Prose-review:` trailer (`PL-W04Z`), whether the pull request body names what each grown passage adds (`PL-HNNH`), and whether the body is the copy-edited one (`PL-TG6P`). The copy editor also reads `ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/interface-provenance.md`, `docs/machine-abstraction.md`, `docs/machine-survey.md`, `docs/references/` and `docs/consultant-brief.md`, which have rows in the reader table of `.claude/rules/plain-writing.md`. A branch that changes only those is asked nothing, so a session can skip close-out step 8 on it, or add text after the copy editor's run, and merge.

**Evidence.** Counted 2026-11-11 over the 300 newest first-parent commits on `origin/main`, from `git log --first-parent -300 --name-only`: 46 changed one of those documents and no simulator path. `ROADMAP.md` was in 36 of them, `docs/references/` in 10, and each of the others in 2 or 3.

**Why it was left out of `PL-HNNH` and `PL-TG6P`.** Widening the hold would put a copy-editor run, or its recorded trailer, on about 15% of merges, most of them `ROADMAP.md` edits such as a release cut. The owner exempted non-simulator pull requests from the body's copy edit on 2026-11-11 until `PL-BF6K` has measured what the copy editor's audit reads cost (`PL-WBT6`). The same measurement decides this. Widening also changes `test_a_change_outside_the_simulator_asks_for_no_count` in `subprojects/docket/tests/test_arming.py`, a test that pins `arm`'s answers, so the change would wait on the owner's review.

**What a fix needs.** A decision by the owner, after `PL-BF6K`, on whether a branch that changes a reviewed document and no simulator path owes the recorded review. If it does, `_read_reviews` in `subprojects/docket/src/docket/arming.py` asks the three questions wherever the change has a path outside the store, and the counts already come back zero for a file with no row in the reader table.

**Done when.** The owner has decided, and either `arm` holds such a branch or this item records why it does not.
