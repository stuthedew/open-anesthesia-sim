---
id: PL-QJ5F
title: tools/fixture_id_check.py asks whether a file is under .claude/ of its absolute path, so in a checkout under .claude/worktrees/ it reads ROADMAP.md, docs/ and the item store as .claude text and make check fails on 112 ids that are not errors
priority: P2
effort: S
status: ready
classes: defect, test
feature: agent-worktrees
touches: tools/fixture_id_check.py, tests/unit/test_fixture_id_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-27
payoff: make check passes in a desktop worktree, and in the main checkout beside one, exactly as it does on CI
verify: grep -q 'def test_a_checkout_inside_a_claude_directory' tests/unit/test_fixture_id_check.py
---

**Problem.** tools/fixture_id_check.py asks whether a file is under .claude/ of its absolute path, so in a checkout under .claude/worktrees/ it reads ROADMAP.md, docs/ and the item store as .claude text and make check fails on 112 ids that are not errors

**Measured, 2026-09-28, at `main` `2149e938`.** Two failures from one cause:

- **In a desktop worktree**, at
  `/Users/feichtinger/Developer/open-anesthesia-sim/.claude/worktrees/trusting-cerf-468dc8`,
  `python3 tools/fixture_id_check.py` exits 1 on 112 literals. They come from
  `ROADMAP.md` (`PL-AAAA`, `PL-A1B2`, `PL-M01`) and from item briefs such as
  `PL-3BZS`'s. `test_the_repository_carries_no_malformed_id` in
  `tests/unit/test_fixture_id_check.py` runs the tool, so the full suite fails
  there, and `make check` with it.
- **In the main checkout, with three desktop worktrees under it**,
  `python3 tools/fixture_id_check.py --root
  /Users/feichtinger/Developer/open-anesthesia-sim` exits 1 on 502 literals.
  Every one of them is inside `.claude/worktrees/`, and none is in the main
  checkout's own files.

CI passes, because the runner's checkout path holds no `.claude` and has no
worktrees under it.

**Why it happens.** `collect` reads a non-Python file as text when `TEXT_ROOT
in path.parts`, where `TEXT_ROOT = ".claude"`. `_walk` yields
`root.rglob("*")`, so `path` is absolute whenever `root` is, which the default
root is. That produces the two failures:

- A checkout at `<repo>/.claude/worktrees/<name>/` has `.claude` among every
  file's parts. So `ROADMAP.md`, `docs/` and the item store are read as
  `.claude` text, although the module docstring puts exactly those out of
  scope, because prose *about* malformed ids is normal there.
- The main checkout's walk descends into `.claude/worktrees/`, which holds whole
  untracked checkouts. Each of those is under `.claude` relative to the root
  too, so it is read the same way. `PL-2P5L` is the same walk in
  `tools/doc_check.py`. `SKIP_DIRS.intersection(path.parts)` has the same
  absolute-path shape, and would skip the whole tree for a checkout under a
  directory named `.venv` or `node_modules`.

**Why it matters.** Every desktop session works in such a worktree, and the
main checkout has worktrees under it whenever one runs. `make check` there is
red on a tree CI calls green. So a session there either reports a failing gate
that is not failing, or learns to read past this failure, and past the real one
it would sit beside. This one was found by a local full-suite run made for
`PL-4Z5Y`.

**Done when.** The check judges `path.relative_to(root).parts`, and never
walks `.claude/worktrees/`. Asking git for the tracked files instead would do
both. A regression test, `test_a_checkout_inside_a_claude_directory_*` in
`tests/unit/test_fixture_id_check.py`, builds a checkout inside a directory named `.claude`,
and inside it a `.claude/worktrees/<name>/` holding a `ROADMAP.md` with a
malformed id. It asserts that neither is reported, while a malformed id in the
checkout's own `.claude/` still is.

**Sequenced 2026-09-28.** Fix this first, together with `PL-2P5L` and
`PL-M9QW`, the other two worktree defects in `agent-worktrees`, in one session
(project owner, 2026-09-28, ratified, over leaving the three to rank one at a
time).
