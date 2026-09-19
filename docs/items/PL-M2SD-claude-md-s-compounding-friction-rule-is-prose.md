---
id: PL-M2SD
title: CLAUDE.md's compounding-friction rule is prose a session must notice, so a cluster that hands back an item for every one it closes sits in the flat P2 band unranked: make the self-generation ratio decidable and report it every run
priority: P2
effort: M
status: done
classes: infra, session-cost
feature: convergence-visibility
touches: tools/generator_check.py, tests/unit/test_generator_check.py, Makefile
added: 2026-09-17
closed: 2026-09-18
pr: 670
verify: uv run pytest tests/unit/test_generator_check.py && grep -q 'python3 tools/generator_check.py' Makefile && grep -q 'generator_check.py' docs/ARCHITECTURE.md && grep -q 'tests/unit/test_generator_check.py' docket.toml
---

**Problem.** CLAUDE.md's compounding-friction rule is prose a session must notice, so a cluster that hands back an item for every one it closes sits in the flat P2 band unranked: make the self-generation ratio decidable and report it every run

**Built 2026-09-17.** `tools/generator_check.py`, standard library only, wired
into `make docket` beside `bin/docket check`.

**The rule.** For a path `p` named in `touches`, `r(p)` is the number of items
spawned by work on `p`'s closed items *that also declare `p`*, over the number
of closed items. `r >= 1.0` with at least 8 closures behind it, and open items
still on it, is reported. Spawn attribution is the project's own method,
already used by hand in `PL-6ZQY`: the commit that adds an item file leads its
subject with the id of the item being worked.

**The same-cluster restriction is the whole design.** A session closing an item
captures whatever else it noticed, and those captures attribute to the item it
was working. Counting every spawned child therefore rates any heavily-worked
file a generator. Measured both ways on this tree the same day:

| path | r loose | r tight | closed | open |
| --- | --- | --- | --- | --- |
| `docs/MODEL.md` | 2.51 | 0.55 | 154 | 40 |
| `subprojects/docket/src/docket/vcs.py` | 2.33 | 0.71 | 52 | 12 |
| `ROADMAP.md` | 2.49 | — | 115 | 32 |
| `src/anesthesia_sim/core` | 5.08 | 0.17 | 12 | 2 |

The loose column is a ranking of how busy a file is. It is not a generator
measure and must not be reported as one.

**Two bugs the tests caught, both of which inflated the ratio.** A commit
created by `bin/docket new` with several titles leads with every id it creates,
so each captured item was being recorded as the others' parent; and a
`touches` entry written `docs/items/` escaped the store exclusion that
`docs/items` matched. Fixing the first alone moved `vcs.py` from 0.90 to 0.71.

**Result on this tree: no cluster reports.** Nothing in the apparatus hands
back an item for every one it closes.

**What this does not do.** It does not rank. `bin/docket next` still ranks on
band, so a reported generator is visible but not preferred. That is the
remaining half of what the project owner asked for and is not built here.
