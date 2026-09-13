---
id: PL-21RC
title: docs/maintainer.md is apparatus in docket.toml's workflow_paths but is named in none of the three places that list the apparatus set, and apparatus-standard.md's paths: glob does not load for it
priority: P3
effort: M
status: ready
classes: docs, infra
feature: worker-instructions
touches: CLAUDE.md, .claude/rules/expert-review.md, .claude/rules/apparatus-standard.md, tools/rules_paths_check.py, tests/unit/test_rules_paths_check.py
added: 2026-09-13
verify: uv run pytest tests/unit/test_rules_paths_check.py && grep -q 'docs/maintainer.md' .claude/rules/apparatus-standard.md
---

**Problem.** docs/maintainer.md is apparatus in docket.toml's workflow_paths but is named in none of the three places that list the apparatus set, and apparatus-standard.md's paths: glob does not load for it

**This is `PL-1KTV` one file later, and `PL-1KTV` closed today.** That item
asked whether `.github/` was apparatus, found the three enumerations of the
apparatus half disagreeing about it, and was decided 2026-09-13: yes, and all
three were corrected together. The test it applied is `CLAUDE.md`'s own
definition — the apparatus is what "exists so agent sessions can be productive"
— checked against the simulator half stated by enumeration (`src/`, `tests/`,
`docs/MODEL.md`, `README.md`). `docs/maintainer.md` passes that test as plainly
as `.github/` did: it is notes to the person running the sessions about running
them, and no reader of the simulator opens it. The question was simply never
asked about this file.

**Where the three still disagree.**

| Where | `.github/` | `docs/maintainer.md` |
| --- | --- | --- |
| `CLAUDE.md:437` | present (`PL-1KTV`) | absent |
| `.claude/rules/expert-review.md:13` | present (`PL-1KTV`) | absent |
| `.claude/rules/apparatus-standard.md` `paths:` | present (`PL-1KTV`) | absent |

**`docket.toml`'s `workflow_paths` is not a fourth copy, and this item does not
argue that it is.** `PL-1KTV` settled that too, deliberately: `workflow_paths`
also carries `Makefile`, `docket.toml`, `docs/items` and the named test files,
which are lane facts rather than standard facts, so the two lists agree where
they overlap and are still not the same list. `docs/maintainer.md` happens to be
both — a lane fact, which `PL-GVNS` has now recorded, and a standard fact, which
is what is still missing.

**Why it matters.** The third row is the one with teeth. `apparatus-standard.md`
is path-scoped, so it loads when a session *opens* a matching file — and a
session editing the project owner's own notes therefore loads no apparatus rule
at all and falls through to the specialist standard `CLAUDE.md` reserves for the
simulator. `PL-1KTV` calls that the safe direction to be wrong in, and it is:
the higher bar wins by default, so nothing under-invests. It is a consistency
question rather than a defect, which is why this is `P3`-shaped like its
predecessor and not urgent.

**The half worth costing is the check, not the three edits.** `PL-1KTV` fixed
three prose lists by hand and this item exists because a fourth file was added
to the tree afterwards and nobody revisited them — which is exactly the drift
`PL-JBZK` cost in `workflow_paths` and `PL-BBDD` still carries for `gate_paths`.
A check holding `CLAUDE.md`'s enumeration, `expert-review.md`'s copy of it and
`apparatus-standard.md`'s `paths:` globs to *each other* is decidable: they are
three literal lists, and whether they name the same paths needs no judgment.
What stays judgment is whether a given path belongs on the list at all, which is
the line `CLAUDE.md` draws for scripting. `tools/rules_paths_check.py` already
reads the `paths:` frontmatter and would be the place.

**Where.** `CLAUDE.md:437`; `.claude/rules/expert-review.md:13`;
`.claude/rules/apparatus-standard.md`'s `paths:` frontmatter; possibly a new
rule in `tools/rules_paths_check.py`.

**Found.** Closing `PL-GVNS` (2026-09-13), by the close-out documentation sweep
rather than by the work. Not fixed there: all three files are outside
`PL-GVNS`'s `touches` and two of them are resident instructions, so the fix-now
door is shut on its second test.

**Done when.** The three enumerations of the apparatus half name
`docs/maintainer.md`, a session opening that file loads
`.claude/rules/apparatus-standard.md`, and the next file added to either half is
caught by something other than a sweep that happened to run.
