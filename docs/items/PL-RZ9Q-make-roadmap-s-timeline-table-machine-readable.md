---
id: PL-RZ9Q
title: Make ROADMAP's timeline table machine-readable and enforce the row shape in doc_check
priority: P2
effort: M
status: done
classes: infra
feature: planning-cadence
touches: ROADMAP.md, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-08-26
closed: 2026-08-26
commit: 11fc560
---

**Problem.** `ROADMAP.md`'s timeline under "The plan" is the project's
authoritative statement of where it is and what comes next, and nothing can
read it. The rows are prose in a markdown table, written in whatever shape
each edit left them: some carry a version (`**v0.3.0 — the foundation**`),
some carry a gate with no version (`**Gate 1**`), and one carries a patch
placeholder (`**v0.3.x — core/ reads like the domain**`). A parser guessing at
that would be guessing at the project's plan.

**Why it matters.** This is the enabling dependency for the whole
`planning-cadence` feature: `PL-6G8C` (a `docket wave` command) cannot report
which timeline step the project is on without a reliable answer to "which row
names the current version, and which row is next". It is also the reason a
duplicate of this table is dangerous — a copy of the release train written in
a closed external proposal (PRs #59/#60) was accurate when written at 20:58 on
2026-08-25 and stale by 21:50 the same evening, when the merge of #58 added
the `v0.3.x` row. Nothing detected that, because a chain of version strings
cites no path that `doc_check` can find dangling.

**Approach.** Keep the table exactly as it reads today; make its row *shape* a
checked contract rather than a convention. `tools/doc_check.py` already holds
`docs/ARCHITECTURE.md`'s package trees and `docs/MODEL.md`'s provenance table
to the files on disk, in both directions; this is the same move applied to the
timeline. Chosen over a separate structured data block (which adds a format to
keep in sync with its own prose) and over regexing the prose as-is (which
fails silently on a formatting change, and silent failure in the mechanism
that reports the plan is the failure mode least likely to be noticed).

**Scope.** Fix the row grammar for the step column — a version row, a gate
row, and a non-milestone row each get one form, with the version in a
parseable position. Rewrite the existing rows to match, changing no meaning.
Add a `doc_check` rule that fails when a row in that table does not match, and
that the version rows' order is monotonic. Expose the parse as a function the
`docket wave` command can import or reimplement against the same grammar.

Out of scope: deciding whether the prose in a row is still *true*, which is
judgment and stays with the reader per "Do not script the judgment"; and
anything that writes to `ROADMAP.md`, which is `PL-N2N1`'s half of the problem.

**Done when.** `doc_check` fails on a malformed timeline row, passes on the
table as rewritten, and a caller can obtain the ordered list of steps with
their versions from `ROADMAP.md` without heuristics. Regression tests cover a
malformed row, a gate row with no version, and the `v0.3.x` patch row, since
those three are what an over-simple grammar gets wrong.

**Context.** Design round with the project owner, 2026-08-26, adopting
rolling-wave planning as an evolution of the existing roadmap rather than a
new process document. Strategy chosen by the owner from three options.

**Worked.** The table as written already satisfied a clean grammar, so no row
was rewritten and no meaning changed — the work was to state the grammar and
enforce it. `parse_timeline` reads all eleven rows of `ROADMAP.md`'s timeline
into `TimelineStep` records; `check_timeline` reports breaches through the
existing `Report`, so they fail `make check` alongside the other three checks.
`_table_rows` gained a heading `level`, which is what lets a `###` table be
read with the code the `##` provenance table already used.

Two decisions worth recording. The em dash separator is spelled out in the
grammar rather than matched loosely: a hyphen typed in its place would
otherwise leave the row matching neither version form and falling through to
"marker", silently reclassifying a release as a boundary. And a row that opens
`v<digit>` but matches neither version form is a distinct error rather than a
marker, which is what makes `v0.4` and `v0.4.0 - name` fail loudly.

An absent `ROADMAP.md` is skipped; a present one with no readable timeline is
an error, since a renamed heading would otherwise disable the check without
saying so.
