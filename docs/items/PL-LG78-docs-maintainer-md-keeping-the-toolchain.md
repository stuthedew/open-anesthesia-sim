---
id: PL-LG78
title: docs/maintainer.md § "Keeping the toolchain current", moved from ROADMAP.md, still carries its structure read's findings: its main point comes last in its first paragraph, two sentences repeat its lead, how each drift.yml job works and the decision history belong elsewhere, the shuffled-order check fits neither its heading nor its lead, and its heading promises upgrades it says do not happen
status: untriaged
feature: maintainer-guide-structure
added: 2026-11-07
---

**Problem.** docs/maintainer.md § "Keeping the toolchain current", moved from ROADMAP.md, still carries its structure read's findings: its main point comes last in its first paragraph, two sentences repeat its lead, how each drift.yml job works and the decision history belong elsewhere, the shuffled-order check fits neither its heading nor its lead, and its heading promises upgrades it says do not happen

**Source.** The copy editor's chapter read 43 of `ROADMAP.md` (run on the project owner's Mac on 2026-11-06), quoted whole in `PL-G6DP`'s brief. `PL-G6DP` moved the section word for word to `docs/maintainer.md` on 2026-11-07, so that a meaning review could check it as a pure move. The chapter read's findings now apply to `docs/maintainer.md`, and none was applied in the move. The read's row numbers are `ROADMAP.md` at `aff76df1`; find each passage by its words.

**What to apply, from that read.**

1. Open the first body paragraph with "The failure being guarded against ... is returning after a gap to a tree that no longer builds", and let the three version limits follow as the reason it will happen.
2. "The current pins are correct today. The point is to know when one stops being correct" repeats the lead, and has no date. "not to raise numbers on a schedule" repeats "Nothing upgrades on a schedule".
3. How each `drift.yml` job works (`uv sync --upgrade`, pytest-randomly with the date as the seed, the seed in the output, the job names as subjects) belongs in comments in `.github/workflows/drift.yml`, which already states much of the policy. The section keeps what each check tests, how often it runs, what a failure means, and that the interpreter check does not change the declared Python range.
4. The shuffled-order check is about tests that depend on each other, which fits neither the heading nor the lead. Keep a pointer that it shares the scheduled workflow. `drift.yml` also runs `doc-quotes` and `restated-constants` jobs, which the section does not mention.
5. "two questions that `quality.yml` is right not to ask" makes the reader read ahead to "Why it reports rather than gates".
6. "Automated bumps were considered and rejected, on the evidence ..." is decision history. `PL-QSWS` holds the decision; keep the decision and "Broad automation accumulates noise until people route around it".
7. The heading promises regular upgrades. The read proposed "Noticing when dependencies or Python change". Besides `PL-BYHS` and `PL-G6DP`, only closed items and `docs/pr-bodies/239.md` cite the current heading.
8. The section speaks of "the owner" in the third person, while `docs/maintainer.md` is written to the owner.

**Queries the tree answers.** "The gate" and `quality.yml` are the checks every pull request must pass before it merges, which `.github/workflows/quality.yml` runs. A failed run reaches the owner through the session-start digest, which names each `drift.yml` job whose newest result on `main` is not a pass (`tools/main_ci_status.py`, `PL-JTWV`). `PL-QSWS` holds the decision against automated bumps, and `PL-ZBJ0` is the evidence about broad automation. `PL-BYHS` is the Flet error in the same paragraph.

**Done when.** Each finding above is applied, or recorded here with the reason it was not, and no statement of the section is lost.
