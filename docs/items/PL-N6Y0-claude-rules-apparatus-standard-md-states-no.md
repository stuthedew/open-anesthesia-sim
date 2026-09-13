---
id: PL-N6Y0
title: .claude/rules/apparatus-standard.md states no test bar, so apparatus tests inherit the simulator's instinct
priority: P3
effort: S
status: done
classes: docs
feature: documentation-standard
milestone: v0.4.18
touches: .claude/rules/apparatus-standard.md
added: 2026-09-13
closed: 2026-09-13
pr: 522
verify: python3 tools/rules_paths_check.py && grep -q '## What a test on this side is for' .claude/rules/apparatus-standard.md
---

**Problem.** .claude/rules/apparatus-standard.md states no test bar, so apparatus tests inherit the simulator's instinct

**Notes.** `.claude/rules/apparatus-standard.md` holds the apparatus to "working
reliably and staying streamlined" and says nothing about tests. There are 15
apparatus self-tests under `tests/unit/` (each enumerated in `docket.toml`'s
`workflow_paths` and held complete by `tools/workflow_paths_check.py`) plus 14
files under `subprojects/docket/tests/`, and nothing states what standard they are
held to — so a session imports the simulator's instinct, which is the opposite
bar by that file's own first paragraph.

The outside claim worth weighing here, and only here: "a test exists if and only
if its absence would let a real bug ship. Tests for getters, framework behavior,
or trivial arithmetic do not exist." That is wrong for `src/` — `CLAUDE.md`'s
safety standard requires boundary, invalid-input, pathological-input and
regression tests, and validation against published reference cases — and is
arguable on the apparatus side, where a wrong answer costs a session rather than a
patient. Deciding it is this item; do not let the answer leak across the line
(`PL-6SBB` is what that mirror error cost in the other direction).

**Where.** `.claude/rules/apparatus-standard.md`.

**Found.** 2026-09-13, reviewing an outside article on long AI projects against
this repository.


**Closed 2026-09-13.** `.claude/rules/apparatus-standard.md` gains § "What a test
on this side is for": a test here earns its place if its absence would let a real
defect through — a script's rule, its failure path, and the input that once broke
it, and not a getter, a constructor, or the standard library's behaviour.

The second paragraph is the load-bearing one, because this bar is exactly the one
the simulator's standard refuses. It says so, names what `CLAUDE.md` asks of a
product test instead (boundary, invalid-input, pathological-input and regression
tests, and validation against published reference cases or independently
calculated test vectors), and hands the line to
`tools/workflow_paths_check.py`, which already decides it mechanically: "A test
file under `tests/` is apparatus when it does not import the product package, and
product when it does." So the distinction is not a judgment made per file, and
`PL-6SBB`'s mirror error has one less way to happen.

**Found** reviewing an outside article on long AI projects. Its rule — "a test
exists if and only if its absence would let a real bug ship" — is wrong for
`src/` and arguable here, which is the whole reason this file needed to say which
side it was talking about.
