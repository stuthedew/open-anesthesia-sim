---
id: PL-51T3
title: Scope v0.2.8 - the workflow works - and freeze its gate
priority: P2
effort: M
status: ready
classes: planning
feature: planning-cadence
touches: ROADMAP.md
added: 2026-08-30
verify: python3 tools/doc_check.py check && bin/docket wave
---

**Problem.** The project owner has approved a workflow-hardening release ahead
of v0.3.0 and approved its contents, but the list exists only in a session
transcript. Nothing in the tree carries it, so a fresh session cannot see the
plan, cannot report progress against it, and will propose Gate 0's product
work instead. Writing the section is what turns the approved list into
something every session reads at startup.

**Why it matters.** This is the release that makes the development loop cheap
enough to run at speed; until it is recorded, each session re-derives the
ordering from conversation, which is the cost the whole release exists to
remove.

**The mechanism is verified and needs no code change.** `wave()` picks
`recorded[0]` from the unreleased milestone sections sorted by version, so a
v0.2.8 section carrying a `### Debt gate` subsection becomes the nearest gate
and the beat follows it. Checked across the lifecycle against a patched
`ROADMAP.md` on 2026-08-30:

| State | Beat |
| --- | --- |
| Nothing closed | `clear the gate - 17 entries of 17 still open`, step v0.2.8 (1 of 10) |
| Six closed | `clear the gate - 11 entries of 17 still open` |
| All closed | `implement v0.2.8 ... - its gate is clear` (see `PL-NSN9`) |
| v0.2.8 released | `clear the gate - 8 entries of 20 still open`, step back to v0.3.0 |

Gate 0 is untouched throughout: still recorded under v0.4.0, still binding it,
and the nearest gate again the moment v0.2.8 ships.

**The approved contents - 17 entries.**

*The loop is visibly broken without these:*

- PL-J786 - require a green `checks` run before any merge into main
- PL-64LS - detect items stranded on an unmerged branch
- PL-8HJ2 - `make release` stops mid-way on the ROADMAP table it does not write
- PL-M5FK - ROADMAP's tag statements go stale on every release, unchecked
- PL-1TPM - `docket next` ranks work the current milestone excludes
- PL-019F - the "what next" rule answers below the roadmap step that decides it
- PL-5YK8 - the `verify:` advisory can never reach zero
- PL-H7XN - `CLAUDE.md` is 572 lines against a documented 200-line target
- PL-NSN9 - a self-gating milestone reports `implement` where `release` is due

*Stops new debt being introduced:*

- PL-S4M2 - switch main to squash-merge
- PL-ZQ9C - record an item's pull request, so provenance survives squash-merge
- PL-F5HB - the project runs a Python 3.14 release candidate, not 3.14 final
- PL-020 - bring tests and `tools/` under the type-check gate
- PL-W5LG - hold CI config to the same path checks as the documentation
- PL-ZN0N - enable ruff RUF100 so inert `noqa` directives fail the build
- PL-69J3 - clear the inert `noqa` directives RUF100 will catch
- PL-STNV - retire the review-verification harness and capture its last finding

`PL-J3ZK` and `PL-20ZR` were on the approved list and closed before it was
written; they are not entries.

**Where, and the part that needs care.** `ROADMAP.md`. Four things:

1. A `## Next milestone: v0.2.8 - the workflow works` section carrying all
   four subsections `REQUIRED_SUBSECTIONS` names - goal, required scope,
   definition of done, explicitly out of scope - plus `### Debt gate: the
   frozen list` holding the 17 entries. v0.3.0's section is the closest
   template: it is also a release whose content is a frozen list.
2. A timeline row for it, which **renumbers steps 1 to 9 into 2 to 10**.
3. The prose under the timeline that refers to rows by number - "Only row 1 is
   a release of gate work", "rows 3, 5 and 7 carry no version", "Rows 4 to 8
   are the intended order", "Row 4's internal ordering". These are the reason
   this item is `M` rather than `S`: each sentence explains *why* a row is what
   it is, so renumbering them is reading rather than substitution.
4. The editorial heading prefixes: v0.2.8 becomes "Next milestone", and
   v0.3.0's and v0.4.0's prefixes shift with it. The parser treats the prefix
   as editorial - the version is the identity - so this is for the reader.

**Do not add to the list once it is written.** "The gate is a snapshot, not a
moving target" governs: findings made while clearing it go to the next gate,
with the `P0`/`safety`/`science` re-entry rule as the only exception.

**Done when.** `bin/docket wave` reports the beat as clearing v0.2.8's gate
with 17 entries counted from `docs/items/`; `python3 tools/doc_check.py check`
passes on the renumbered train; and no sentence under the timeline refers to a
row by its old number.
