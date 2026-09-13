---
id: PL-N6Y0
title: .claude/rules/apparatus-standard.md states no test bar, so apparatus tests inherit the simulator's instinct
status: untriaged
added: 2026-09-13
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
