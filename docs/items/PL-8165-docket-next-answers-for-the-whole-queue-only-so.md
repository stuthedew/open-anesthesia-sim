---
id: PL-8165
title: docket next answers for the whole queue only, so two simultaneous sessions rank onto the same item
priority: P2
effort: M
status: done
classes: session-cost, infra
feature: parallel-sessions
milestone: v0.3.6
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/config.py, docket.toml, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-04
closed: 2026-09-04
pr: 287
verify: uv run pytest subprojects/docket/tests/test_model.py subprojects/docket/tests/test_plan.py subprojects/docket/tests/test_config.py subprojects/docket/tests/test_cli.py -q
---

**Problem.** `docket next` ranks the whole queue and has no way to be asked
about part of it. The project owner runs two sessions at once — one on the
simulator, one on the apparatus — and both open with the same command, read
the same ranking and are handed the same item. Every guard the project has
built for parallel sessions is *detection after the fact*: `flight` excludes
what a branch already carries, which cannot fire until one of the two has
pushed. Two sessions starting in the same minute have nothing between them.

**Why it matters.** The collision is discovered as a merge conflict, after
both sessions have paid in full. Prevention here is cheap and structural: the
two halves of this repository barely overlap, so confining each session to one
of them removes most of the collision surface before either starts.

**Where.** Four modules and the project's own config.

- `model.py` — `Item.lane(workflow_paths)`, returning `workflow`, `product`,
  `crossing` or `unplaced`. Read from `touches`, not from `classes`: measured
  against this store on 2026-09-04, the `classes` reading placed 33 of 145
  open items on the wrong side, eighteen of them workflow defects a simulator
  session would then have been offered. `classes` says what kind of work an
  item is, and a defect in the tooling carries the same label as a defect in
  the simulator.
- `config.py` / `docket.toml` — `workflow_paths`, the boundary
  `CLAUDE.md`'s "two standards, deliberately unequal" already draws. Empty by
  default and fail-closed, as `protected_paths` is.
- `plan.py` — a `lane` argument to `recommend`, filtering the candidates and
  reordering nothing, plus `set_aside` for what no lane could claim.
- `cli.py` — an optional `lane` positional on `next`. The unfiltered answer
  stays the default.

Work reaching both halves, and work declaring no `touches`, is offered to
neither lane and *named* under the ranking. A filter that silently drops a
fifth of a queue is how work goes missing.

**Done when.** `docket next product` and `docket next workflow` each answer
from one half of the project, `docket next` is unchanged, an undeclared
boundary refuses the lane rather than answering from everything, and the work
neither lane could take is printed with its ids.
