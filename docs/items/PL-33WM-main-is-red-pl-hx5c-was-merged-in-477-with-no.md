---
id: PL-33WM
title: main is red: PL-HX5C was merged in #477 with no gate disposition, because #476 added the presence check on a base #477's CI never saw
priority: P2
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.4.11
touches: ROADMAP.md
added: 2026-09-08
closed: 2026-09-08
pr: 480
verify: python3 tools/doc_check.py check && grep -qF 'PL-HX5C (S) Both in-flight guards passed' ROADMAP.md
---

**Problem.** main is red: PL-HX5C was merged in #477 with no gate disposition, because #476 added the presence check on a base #477's CI never saw

**Why it matters.** `make check` fails on a clean `main`, so every session
starts red and the one signal that says the store is sound says nothing.
`ROADMAP.md`'s presence rule allows either answer — admit the item to the
frozen list, or decline it with a reason — and forbids only silence, which is
exactly the state the merge left.

**How the two merges produced it, because the sequence is the finding.**
`#476` (`PL-36R4`) added the check that every open debt item carry a
disposition, and merged at `2c824c28`. `#477` added `PL-HX5C` — `needs-decision`,
therefore debt by `docket.toml`'s rule — and merged at `e299411f`, forty
minutes later. `#477`'s CI was green and correctly so: its base was
`ab338a11`, which predates `#476`, so the check that its new item violates did
not exist on the tree its run measured. Neither pull request was wrong and
neither run was wrong. The base moved between them, and nothing re-ran the
merged result.

This is a semantic conflict rather than a textual one, so no merge-conflict
signal fires and `mergeable_state` stays clean. `PL-7RTN` (an open pull request
can carry no check runs at all) and `PL-J786` (require a green `checks` run
before any merge into main) are the neighbouring entries; neither covers a run
that was green against a stale base. Whether a branch should be required to be
current with `main` before merging is a real question and is **not** this
item — recorded here so the next session meeting it has the case, and left to
`PL-J786`'s ground rather than opened as a fifth guard.

**What was done.** `PL-HX5C` is recorded in v0.5.0's "Declined to Gate 2 on
the refilling-queue ground" subsection, whose four paragraphs of reasoning
apply to it unchanged: found after the 2026-09-06 freeze, `P2` and neither
`safety` nor `science`, and wholly in the workflow lane where it can reach no
reader of the simulator. The count moved from 29 to 30 and a paragraph records
that the thirtieth arrived after the audit that found the first twenty-nine.

**Done when.** `make check` passes on `main`.

**Found.** Running `make check` after `#477` merged, 2026-09-08.
