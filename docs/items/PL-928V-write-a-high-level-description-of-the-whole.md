---
id: PL-928V
title: Write a high-level description of the whole working method as one document
priority: P2
effort: M
status: needs-decision
classes: docs
feature: project-introduction
touches: docs/workflow.md, README.md, docs/consultant-brief.md
added: 2026-09-13
verify: test -f docs/workflow.md && grep -q 'workflow.md' README.md && python3 tools/doc_check.py check
---

**Problem.** No document describes the working method end to end. The rules are
deliberately scattered — `CLAUDE.md` routes each one to the moment it fires, and
`docs/resident-instructions.md` records why. That is right for sessions and it
leaves nowhere to see the shape of the thing. The readers who need the shape are
the project owner returning after a gap, an outside reviewer arriving through
`docs/consultant-brief.md` (which today hands a cold reviewer no workflow map at
all), and anyone deciding whether a proposed mechanism duplicates one that
already exists.

**Why the neighbours are not it.**

- `docs/ARCHITECTURE.md` is the map of the *code* (`data/` -> `core/` -> `app/`)
  and says so in its own opening. Nothing about how work is chosen or proved.
- `subprojects/docket/README.md` describes the *tool*, framed as reusable and
  standalone. The working method is larger than docket: the two-standards split,
  worker mode, the checks, CI, the consultant brief.
- `CLAUDE.md` and `.claude/rules/*.md` are the rules themselves, scattered by
  policy. A rule is not a description.
- `docs/worker.md` and `docs/consultant-brief.md` are operational prompts.

**Proposed shape.** One pass end to end in `docs/workflow.md`: what a session
is, where state lives, how an item is selected, claimed, verified and closed, how
findings are captured, how two concurrent sessions stay clear of each other, and
which half of each question is scripted versus which stays judgment.

**The constraint that makes or breaks it.** Describe mechanism; cite the file
that governs each rule; never restate the rule's content. Two documents
specifying one thing is the hazard `CLAUDE.md` names by name when it explains
why it states no reply format of its own. A high-level doc that restates rules
becomes a second source of truth, drifts, and then a session reads a stale
description of its own obligations. Pointers instead of restatements also get
upkeep free: `tools/doc_check.py` already verifies that a cited path exists.

**Not resident.** It is for humans and for cold outside readers, not loaded at
launch. `make check` reports the resident character total, and this document
must not enter it.

**Homes considered and rejected.** Inside `subprojects/docket/README.md`
(muddles a standalone tool with this project's method); as a section of the
public field-notes page (different genre — that page is argument-shaped, and a
tour at the front breaks its spine).

**Done when** `docs/workflow.md` exists, is linked from `README.md` and
`docs/consultant-brief.md`, restates no rule it does not cite, and `make check`
passes with the resident character total unchanged.
**Why it matters.** Three readers need the shape and none of them can get it
today. `docs/consultant-brief.md` hands a cold outside reviewer no workflow map
at all, so the first thing a paid review spends its attention on is
reconstructing how the project runs rather than reviewing it. The project owner
returning after a gap has the same problem at lower stakes. And a session
proposing a new mechanism has no way to check whether one already exists, which
is how the apparatus grows a second answer to a question it had already
answered. Verified 2026-09-13: `docs/workflow.md` does not exist.

**Blocked.** (headless worker, 2026-10-20) The item creates a tracked file that
no entry in `docket.toml` places, and `docket.toml` is not in `touches`. I
created a one-line `docs/workflow.md`, staged it with `git add`, and ran
`uv run python tools/workflow_paths_check.py`, which `make check` runs. It
exited 1 with: `"docs/workflow.md" is tracked (1 file(s)) and neither
workflow_paths nor product_paths in docket.toml places it, so an item declaring
it lands on the simulator's side by default rather than by a decision. Add
"docs/workflow.md" to workflow_paths if it exists so sessions can be
productive, or to product_paths if a reader of the simulator needs it`. So
"`make check` passes" in the brief's done-when cannot be met inside `touches`.
I removed the file again and wrote nothing else. Unblocking needs `docket.toml`
added to `touches`, and a decision on which of the two lists places the new
document.

**Reviewed 2026-10-24: the block is correct, and widening `touches` alone
cannot unblock a rerun.** `docket.toml` is in `gate_paths`, so an item that
declares it is no longer delegable: `Item.delegability` returns "touches the
checks themselves". The new entry also cannot land ahead of the document,
because `tools/workflow_paths_check.py` refuses an entry that places no tracked
file. So the question is where the document lives, and it is the owner's,
because it changes the deliverable this brief names.

**Decision needed.** Should the description of the working method be a section
at the top of `docs/apparatus.md`, which a headless worker can write, or the
separate `docs/workflow.md` this brief names, which only a chat session can?

**Recommendation:** the section in `docs/apparatus.md`, for the reasons in the
first option below.

- **Recommended: a "How the work runs" section at the top of
  `docs/apparatus.md`.** That file is already the apparatus's map and is
  already in `workflow_paths`. It did not exist when this brief was written
  (`PL-KRGY` created it on 2026-10-11), so "Homes considered" never weighed
  it. The item stays delegable, the headless rerun needs no `docket.toml`
  edit, and the project keeps one apparatus map rather than two. `touches`
  becomes `docs/apparatus.md, README.md, docs/consultant-brief.md`, and
  `verify:` greps for the section heading instead of `test -f`. The cost is
  that the tour sits above a long `tools/` inventory, so `README.md` and
  `docs/consultant-brief.md` link to the section's anchor.
- **As written: a separate `docs/workflow.md`.** `touches` gains
  `docket.toml`, the file goes in `workflow_paths` (it is addressed to
  participants in the build, as `docs/worker.md` and `docs/maintainer.md`
  are), and a chat session works it, because no worker may edit a gate path.
