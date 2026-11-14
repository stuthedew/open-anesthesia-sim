---
id: PL-GL45
title: Remove the copy editor, its agents, the blind judge and their tests, keeping the list of facts a change removed
priority: P2
effort: M
status: ready
classes: infra
feature: copy-editor
touches: tools/copy_edit.py, tools/prose_judge.py, tools/rejected_prose.py, tools/new_prose.py, tools/product_paths.py, tools/regex_baseline.py, tools/rules_paths_check.py, tests/unit/test_copy_edit.py, tests/unit/test_prose_judge.py, tests/unit/test_rejected_prose.py, tests/unit/test_new_prose.py, .claude/agents/copy-editor.md, .claude/agents/meaning-check.md, .claude/agents/prose-judge.md, docs/prose-review, Makefile, .github/workflows/quality.yml, docket.toml, docs/apparatus.md, docs/resident-instructions.md, .claude/rules/plain-writing.md, .claude/skills/docket/modes/close-out.md
added: 2026-11-14
payoff: sessions stop picking up work on a tool the owner retired, and every branch stops paying for its test set in make check and CI
verify: ! grep -q rejected_prose Makefile && ! grep -q rejected_prose .github/workflows/quality.yml && ! grep -q copy-editor docket.toml && ! grep -q copy_edit tools/new_prose.py && grep -q 'def compare_report' tools/new_prose.py
---

**Problem.** `PL-J1ZM` (#2119, merged 2026-11-14) removed the copy edit of each branch but kept the copy editor for rewriting a section when the owner asks. On 2026-11-14 the owner asked whether the copy editor itself was gone, and chose "Remove it completely" on a decision card: delete the tool, its agents, the blind judge and their tests, and drop the five items that fix it; keep the list of facts a change removed (project owner, 2026-11-14, ratified, over keeping it for when the owner asks). Four tests under `PL-J1ZM` showed the copy editor did not change how sessions write, and while it exists, sessions pick up items that fix it.

**Why it matters.** While the copy editor exists, sessions keep picking up items that fix or measure it, and `make check` and CI keep running its test set on every branch. The owner has decided it is not worth that cost.

**What goes.**
- `tools/copy_edit.py`, `tools/prose_judge.py`, `tools/rejected_prose.py` and their tests in `tests/unit/`.
- `.claude/agents/copy-editor.md`, `.claude/agents/meaning-check.md`, `.claude/agents/prose-judge.md`.
- `tools/new_prose.py`'s modes that write a request for the copy editor (the default mode, `--draft`, `--section`, the structure and outline reports) and the functions only they use. `--compare` stays.
- The copy editor's test sets and run records under `docs/prose-review/` that only it reads; `docs/prose-review/README.md` is rewritten to say the copy editor was removed, or removed with its directory if nothing else is left there.
- Every reference: `Makefile`, `.github/workflows/quality.yml`, `docket.toml` (test lists, agent roles), `docs/apparatus.md`, `tools/product_paths.py`, `tools/regex_baseline.py`, `.claude/rules/plain-writing.md`, `.claude/skills/docket/modes/close-out.md`, `docs/resident-instructions.md`.

**What stays.** `python3 tools/new_prose.py --compare`, which close-out step 8 runs: it lists each passage a branch changed beside its old text, and each fact the branch removed.

**Dropped with this item.** `PL-6BW8`, `PL-BF6K`, `PL-HLQK`, `PL-HTB9`, `PL-WZC0`, which each fix or measure the copy editor.

**Done when.** None of the removed files exists, nothing in the tree outside closed item files and release notes names them, `python3 tools/new_prose.py --compare` still works with its tests, and `make check` passes.

**Generator check.** A one-off removal that the owner chose. It ends the `copy-editor` feature rather than adding to it, so it records no head.
