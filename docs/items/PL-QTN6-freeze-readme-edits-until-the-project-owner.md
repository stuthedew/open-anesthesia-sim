---
id: PL-QTN6
title: Freeze README edits until the project owner decides what the README is for
priority: P2
effort: S
status: done
classes: docs
feature: project-introduction
touches: README.md, .claude/rules/readme-hold.md, docs/items/PL-N092-rewrite-readme-as-a-human-readable-introduction.md
added: 2026-09-05
closed: 2026-09-05
verify: test -f .claude/rules/readme-hold.md && grep -q '^blocked-by: PL-RM83$' docs/items/PL-N092-rewrite-readme-as-a-human-readable-introduction.md
---

**Problem.** Sessions keep editing `README.md` a paragraph at a time. Each edit
is defensible on its own and the document as a whole is getting worse: the
project owner's assessment on 2026-09-05 was "the readme is a mess ... you are
just making it worse". Nothing in the repository stops the next session from
doing it again. `PL-N092` (rewrite README as a human-readable introduction) sits
at `status: ready`, so `bin/docket next` will hand the rewrite to a session
before the owner has said what the rewrite should aim at; and any session doing
CLAUDE.md's end-of-item doc sweep is pointed at `README.md` lines by
`python3 tools/doc_check.py candidates`.

**Why it matters.** A README is one document with one voice, and it is the
first thing a reader meets. Incremental improvement by uncoordinated sessions is
the specific process that produces the accumulated-notes register `PL-N092`
already describes, so more passes make it worse rather than better. The owner
asked for a stop; a stop that is only stated in a chat reply is not carried by
anything and expires with the session that heard it.

**Where.** `.claude/rules/readme-hold.md`, a new path-scoped rule that loads
when a session opens `README.md`; the `status`/`blocked-by` front matter of
`PL-N092` and `PL-RCTQ` (sweep MODEL.md and README for the new unit, time base
and run rate), both of which reach `README.md`.

**Why a rule and not a check.** A check refusing any `README.md` diff would fire
identically every run and would have to be removed to do the rewrite it is
holding open, which fails CLAUDE.md's "will it genuinely run again" gate. The
hold is temporary by construction, so it goes where it can be deleted in one
commit.

**Done when.** `.claude/rules/readme-hold.md` exists and states the freeze;
`PL-N092` and `PL-RCTQ` are blocked on `PL-RM83` (decide what README.md is for),
so `bin/docket next` cannot hand out README work while the decision is open.
