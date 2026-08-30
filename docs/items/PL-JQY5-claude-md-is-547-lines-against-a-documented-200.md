---
id: PL-JQY5
title: CLAUDE.md is 547 lines against a documented 200-line adherence target
status: untriaged
feature: worker-instructions
touches: CLAUDE.md, .claude/rules
added: 2026-08-30
---

**Problem.** `CLAUDE.md` is 547 lines. Claude Code's memory documentation
targets "under 200 lines per CLAUDE.md file", stating that longer files
"consume more context and reduce adherence", and the troubleshooting section
names file size as a first thing to check when instructions are not being
followed.

**Why it matters.** The file is loaded into every session, so its cost is paid
on every turn of every session — and the failure mode is not an error but
quieter compliance with the rules furthest from where attention lands. This
project has spent several sessions adding rules because an earlier rule did not
fire; some of that may be the file's length rather than each rule's wording.
It is also self-reinforcing: every fix for a missed rule makes the file longer.

**Where.** `CLAUDE.md`, and a new `.claude/rules/` directory.

**Approach, not yet decided.** `.claude/rules/*.md` files load at launch with
the same priority as `.claude/CLAUDE.md`, so moving whole sections out changes
nothing about whether they load — it changes how they are organized and lets
some of them become path-scoped, loading only when a session touches matching
files. Candidates, roughly in order of how self-contained they are: "Session
and tool-use efficiency", "Prefer deterministic tooling over repeated model
work", and "Proactive expert review and domain best practices". The
safety-critical clinical-output standard should stay in `CLAUDE.md`
unconditionally.

Path-scoping is the part worth thinking about rather than assuming: a rule that
loads only when `src/anesthesia_sim/core/**` is read is cheaper, but a session
that never opens those files also never sees the standard that would have told
it to.

**Done when.** `CLAUDE.md` is materially shorter with nothing lost, the moved
sections load in the sessions that need them, and `/context` confirms the
files load.
