---
id: PL-L9SF
title: quality.yml's item-only fast path skips ruff format --check on the premise that no item file is Python, but ruff 0.16.4 formats fenced python blocks in Markdown, so an item-only pull request passes and main goes red: #1722 did, on main's run 40112594319 at 2f0101bb
status: untriaged
feature: ci-cost
added: 2026-10-24
---

**Problem.** quality.yml's item-only fast path skips ruff format --check on the premise that no item file is Python, but ruff 0.16.4 formats fenced python blocks in Markdown, so an item-only pull request passes and main goes red: #1722 did, on main's run 40112594319 at 2f0101bb

**Found 2026-10-24.** #1722 filed three items, one of whose briefs carried a fenced `python` script that was not in ruff's format. The pull request changed only item files, so `bin/docket ci-scope` answered `items`. The step `uv run ruff format --check .` was then skipped in both parts, and the pull request merged green. `main`'s own run on `2f0101bb` (run 40112594319, job `checks-part-1`) failed at that step with "1 file would be reformatted", naming the item file. It was fixed on the branch `claude/one-source-gaps` by formatting the block.

**The premise that broke.** The comment above the scope step in `.github/workflows/quality.yml` says that "ruff, mypy and `ignore_check.py` read only Python files, and no item file is one". `pyproject.toml` does not configure ruff to read Markdown, yet ruff 0.16.4 formats fenced Python blocks in `.md` files by default (reproduced locally: `ruff format --check docs/items/PL-G84G-*.md` exit 1). `ruff check` passed on the same file, so this has been seen for the formatter only.

**Why it matters.** The fast path gives a wrong answer silently: the pull request is green and `main` goes red. Every later pull request that runs the full job then fails the same step until somebody fixes the file. `main`'s run is the backstop by design, but nobody's pull request shows the failure.

**Options.** (a) Run `ruff format --check docs/items/` on the item-only path. This costs one ruff run of about a second. (b) Exclude `docs/items/` from ruff's formatter, since item briefs quote code rather than ship it. (c) Both, by excluding the store and checking it nowhere. Option (a) keeps the formatter's rule on code that a session may copy out of a brief. Option (b) is cheaper and makes the comment's premise true. Whichever is chosen, the comment's sentence must change to match.
