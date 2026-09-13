---
id: PL-928V
title: Write a high-level description of the whole working method as one document
status: untriaged
added: 2026-09-13
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

**Proposed shape.** One pass end to end in `docs/workflow.md`: what a session is,
where state lives, how an item is selected, claimed, verified and closed, how
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

**Homes considered and rejected.** Inside `subprojects/docket/README.md` (muddles
a standalone tool with this project's method); as a section of the public field
-notes page (different genre — that page is argument-shaped, and a tour at the
front breaks its spine).

**Done when** `docs/workflow.md` exists, is linked from `README.md` and
`docs/consultant-brief.md`, restates no rule it does not cite, and `make check`
passes with the resident character total unchanged.
