---
id: PL-1DZF
title: "131 of 391 red CI runs fell in the first three days of three new pull-request gates, 71 of them from the pull-request body record that was retired the next day, because a pull request's run uses main's newest workflow and tools, which a branch forked before the gate cannot see in its own make check"
status: untriaged
feature: fewer-red-runs
touches: .github/workflows/pr-title.yml, .github/workflows/quality.yml, .claude/rules/apparatus-standard.md
added: 2026-09-27
---

**Measured 2026-09-27** by `PL-JYJJ`'s census. Three new pull-request gates
account for 131 of the 391 red runs (33.5%), counted over each gate's first
three days:

| Gate | Red runs | Days | Landed |
|---|---|---|---|
| pr-title "names the items it closes" | 33 | 2026-09-03 to 09-05 | with the workflow, 2026-09-03 |
| pull-request body record | 71 | 2026-09-26 | #1068 on 09-25; retired by #1118 on 09-26 |
| pr-record | 27 | 2026-09-26 and 09-27 | #1056 on 09-25 |

The main-only whole-store verify replay behaved the same way on its first
day, 2026-09-06: 41 red pushes to `main`.

**Likely mechanism.** For `pull_request`, GitHub sets `GITHUB_REF` to
`refs/pull/N/merge`, the pull request merged into its current base (GitHub
Docs, "Events that trigger workflows", `pull_request`,
https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).
A gate merged to `main` therefore runs on every open branch at that branch's
next push. The branch's own `make check` predates the gate and cannot see it.
Each open branch then takes one red run and one fix cycle per new gate.

This has not been checked run by run. Doing so is deterministic: compare each
of the 131 runs' fork point (`git merge-base`) with its gate's merge time.

**Options.** This is a question for the project owner, because the answer
sets how every future gate lands.

1. **Grandfather.** A gate stays advisory on any branch forked before it.
   This removes the burst, but those branches then merge without the check the
   gate exists to enforce. For a record-keeping gate such as pr-record, that
   is the very gap it was built to close.
2. **Stage it.** Land the local half first (the `make check` step, and the
   command the failure message tells a session to run), and the CI half a day
   later. This helps only branches that bring `main` in during that day, and
   `CLAUDE.md` asks them not to bring it in early.
3. **Accept and count.** One red run per open branch is the price of a gate.
   When a gate's cost is in question, a one-off census inside GitHub's
   90-day window counts its first three days. `PL-JYJJ` holds the recipe; it
   was dropped, not built.

**Recommendation: 3, after the fork-point check confirms the mechanism.**
Option 1 weakens the gate it protects. Option 2 does not reach the branches
that are actually hit. The largest burst was also churn rather than mechanism:
71 red runs from a gate retired within a day. The generator pause already
targets that churn (`CLAUDE.md` § "What this project is").
