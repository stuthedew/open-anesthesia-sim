---
id: PL-H7XN
title: CLAUDE.md is 547 lines against a documented 200-line target, which reduces adherence to all of it
status: untriaged
feature: worker-instructions
touches: CLAUDE.md, .claude/rules
added: 2026-08-30
---

**Problem.** `CLAUDE.md` is 547 lines. Claude Code's documentation targets
under 200 per file and states plainly that longer files consume more context
and reduce adherence, and that instructions are context rather than enforced
configuration. Every rule in the file is therefore slightly less likely to be
followed than it would be in a shorter one, and the file grows every time a
behavior change is agreed — three sections were added on 2026-08-30 alone.

**Why it matters.** The file is the whole of this project's working agreement
with its agents, including the safety-critical standard. A rule that is
present but not followed is worse than one that is absent, because the absence
would at least be noticed. This is also self-worsening: the rule that a
behavior change takes effect in the session that asks for it guarantees the
file keeps growing, with nothing that ever shortens it.

**Where.** `CLAUDE.md`, and a new `.claude/rules/` directory. Rules without
`paths:` frontmatter load at launch with the same priority as
`.claude/CLAUDE.md`; rules *with* `paths:` frontmatter load only when the
session touches matching files, which is the mechanism that actually reduces
resident context rather than merely relocating it.

**Approach, to be settled before doing it.** The obvious split is by audience,
and the file already names it: "Two standards, deliberately unequal" separates
the simulator from the workflow apparatus. Candidates for extraction, roughly
largest first:

  - the queue and how the project owner works (~150 lines), which only matters
    once a session is choosing or closing work;
  - session and tool-use efficiency plus deterministic tooling (~90 lines);
  - the safety-critical clinical-output standard (~40 lines), which is the one
    argument *against* extracting anything — it must be resident in every
    session and must never be the rule that failed to load.

Path-scoped extraction is the only version that saves context rather than
moving it, and the safety standard cannot be path-scoped. So the honest target
is probably "under 300 with the safety standard resident", not "under 200".

**Do not confuse this with tidying.** The file is long because it says useful
things; the failure mode of this item is deleting content to hit a number.
Extraction to a rules file keeps the words and changes where they load.

**Done when.** `CLAUDE.md` is materially shorter with no rule lost, the
safety-critical standard is still resident in every session, and a session
starting cold still finds every rule it needs from what loads at launch.
