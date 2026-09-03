---
id: PL-MHQK
title: The contrast checker prints its known-shortfall detail on every run, where the verify advisory was narrowed to what a session is about to trip over
status: needs-decision
priority: P3
effort: S
classes: session-cost, infra
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py
added: 2026-09-03
---

**Problem.** `tools/contrast_check.py` prints its `Known shortfalls (tracked,
not failing)` block unconditionally - `format_report` appends it whenever the
set is non-empty, with no gate on whether the session could act on it. Three
lines name `PL-W8DQ`, `PL-GNN1` and `PL-GVXP` on every `make check`, in every
session, whether or not anything about colour has been touched.

**Why it matters.** `CLAUDE.md`: "A check that fires every run without
changing a decision is a defect in the check - it costs attention forever and
trains a session to skim the output where a real advisory also appears."
`PL-5YK8` applied exactly that reasoning to the `verify:` advisory and
narrowed it to the items `docket next` is about to offer, so that "on a normal
day there is none at all". The contrast block never had that treatment, and
the asymmetry is the finding: two outputs in the same `make check`, one
narrowed to the moment it can change a decision and one not.

**And the mechanism does not depend on the printing.** This is what makes the
question answerable rather than a matter of taste. `.claude/rules/ui-color.md`
gives `KNOWN_SHORTFALLS` two jobs: keep a gap "visible and owned rather than
living in a comment nobody re-measures", and fail when a listed shortfall
starts *passing*, "so a fix cannot leave its excuse behind". Both are
properties of the entries existing in the table, not of the three lines being
rendered. Narrowing the output costs neither.

**Decision needed.** Whether to gate the detail block, and on what:

1. **Gate on the diff.** Print the one-line summary always -
   `18 of 21 declared pairs meet WCAG 2.2 AA, 3 known shortfalls, 0 errors` -
   and the three detail lines only when the diff touches `app/theme.py` or
   `app/simulation_view.py`. `tools/doc_check.py candidates --base <ref>` is
   the existing precedent for a diff-aware tool here, so the shape is not new.
   The summary keeps the count visible, which is the half `PL-5YK8` was
   careful to preserve when it narrowed.
2. **Leave it.** Three lines is not thirty-nine, and `CLAUDE.md`'s own gate on
   building tooling is "the benefit is unclear, the answer is no". Adding a
   `--base` to a tool that currently takes none is real work against a small
   irritation.
3. **Revisit when the set next moves.** The list only shrinks - `ui-color.md`
   forbids adding an entry to make a change go green - so the next colour item
   to land takes it to two, where the noise argument is weaker still.

Option 2 or 3 is the honest recommendation *today*: this is a real instance of
the pattern, below the threshold where mechanising pays. **What would change
that is the list growing rather than shrinking** - a fourth entry means the
suppression ledger is being used as a suppression list, which `ui-color.md`
already forbids in prose and nothing enforces.

**Where.** `tools/contrast_check.py`, `format_report`.

**Done when.** The decision is recorded. If it is option 1, the summary line
still states the count on every run, and a test covers both the gated and
ungated paths.

**Found.** 2026-09-03, by the project owner, applying `PL-5YK8`'s reasoning
about the `verify:` advisory to the contrast output in the same `make check`.
