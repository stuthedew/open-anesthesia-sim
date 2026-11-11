---
id: PL-LG78
title: docs/maintainer.md § "Keeping the toolchain current", moved from ROADMAP.md, still carries its structure read's findings: its main point comes last in its first paragraph, two sentences repeat its lead, how each drift.yml job works and the decision history belong elsewhere, the shuffled-order check fits neither its heading nor its lead, and its heading promises upgrades it says do not happen
priority: P3
effort: S
status: done
classes: docs
feature: maintainer-guide-structure
milestone: v0.6.17
touches: docs/maintainer.md
added: 2026-11-07
closed: 2026-11-11
pr: 2097
payoff: the owner learns from the section's first lines what happens when a dependency or Python moves and what a red scheduled run means
verify: ! grep -qF 'The current pins are correct today' docs/maintainer.md
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

**Checked 2026-11-09:** § "Keeping the toolchain current" in `docs/maintainer.md` is unchanged since the move. Its first body paragraph still ends with "The failure being guarded against is not a stale pin", and the section still holds "The current pins are correct today" and "Automated bumps were considered and rejected".

**Why it matters.** The owner reads this section to learn what happens when a dependency or Python moves. Its main point comes last, and the job details push down what a red run means for him.

**Generator check.** One-off: a finding from the `ROADMAP.md` structure-read sweep (chapter read 43), carried into `docs/maintainer.md` word for word by `PL-G6DP`.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88 the section's text was in `ROADMAP.md` ("The current pins are correct today; the point is knowing ..."), with the same order and repeats that the structure read found. `PL-G6DP` moved it to `docs/maintainer.md` later without changing it, so the problem was present. The item is classed `docs` only, which is not debt, so v0.7.0's gate does not take it and it stays off the frozen list.

**Done 2026-11-11.** The section is now § "Noticing when dependencies or Python change". Each finding, in the order above:

1. Applied. The first body paragraph opens with the failure it guards against, and the version limits follow as the reason it will happen.
2. Applied. "The current pins are correct today ..." and "not to raise numbers on a schedule" are cut.
3. Applied without a change to `.github/workflows/drift.yml`, because its comments already hold the mechanics: the `dependencies` job's comment explains `uv sync --upgrade`, the `interpreter` job's step "relax the interpreter pin for this run only" explains the relaxed upper limit, and the `order` job's comment gives pytest-randomly, the date as seed and the seed in the run's header. The section keeps what each check tests, how often it runs, what a failure means, and that the interpreter check leaves the declared range unchanged.
4. Applied. `order` moved to a short list of the workflow's other report-only checks, with `doc-quotes` and `restated-constants` added, each with its cadence and what a failure means, and a pointer to the job comments in `drift.yml`.
5. Applied. The section states what `quality.yml` tests (the versions locked in `uv.lock`, on the Python `.python-version` names) instead of pointing ahead.
6. Applied. The decision-history sentence is cut, `PL-QSWS` is named as holding the decision, and the `PL-ZBJ0` sentence stays.
7. Applied, with the heading the read proposed. Only closed items and `docs/pr-bodies/239.md` cite the old heading, and those record their own time, so they are unchanged.
8. Applied. The section addresses the owner as "you".

From "Queries the tree answers", the section also says that the session-start digest names each failed `drift.yml` job (`PL-JTWV`), because that is how a red run reaches a session. No statement of the old section is lost: "monthly and on demand" became "on the first of each month, and whenever you start it by hand", and the job mechanics moved to the comments that already held them.
