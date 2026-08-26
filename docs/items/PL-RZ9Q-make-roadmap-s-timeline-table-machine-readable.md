---
id: PL-RZ9Q
title: Make ROADMAP's timeline table machine-readable and enforce the row shape in doc_check
priority: P2
effort: M
status: ready
classes: infra
feature: planning-cadence
touches: ROADMAP.md, tools/doc_check.py, tests/test_doc_check.py
added: 2026-08-26
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
