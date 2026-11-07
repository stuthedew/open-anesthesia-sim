---
id: PL-KDG0
title: Restructure docs/maintainer.md as the copy editor's structure read proposes: state each decision once where it applies, give subagent rules, auto mode and the cloud environment their own sections
status: untriaged
feature: repo-copy-edit
touches: docs/maintainer.md
added: 2026-11-07
---

**Problem.** Restructure docs/maintainer.md as the copy editor's structure read proposes: state each decision once where it applies, give subagent rules, auto mode and the cloud environment their own sections

**What the structure read found, and what was done** (the project owner ran
the copy editor's structure read on their Mac on 2026-11-06, on the API credit;
its findings are on branch `claude/repo-copy-edit-api` under
`copy-edit-runs/docs-maintainer-md/structure/outline-read.txt`). The owner
chose on 2026-11-05 to apply the structure read before the line edit.

- The rule that price never justifies a less correct model or effort, and the
  model review's schedule, are stated once, in § "Match model capability to
  the work". The effort, ledger and subagent text points there.
- The subagent model and effort rules moved out of the cost section into a
  subsection of their own, § "Subagents run on the session's model and
  effort".
- Auto mode has its own section. The cloud environment's `Default` setting and
  the setup script are one section, § "Set up a Claude Code project's cloud
  environment", and the old effort-trial line's removal sits in the step where
  the setup-script box is open.
- § "Which model each flag means" names both copies Claude Code reads of the
  model table, and says which tools read the table (the headless worker and
  `tools/model_doc_review.py`). Other sections point there instead of
  restating values.
- The merge box's message check sits in the step where the owner clicks. The
  update-armed token section opens with a pointer. The credit address is given
  once. The tag-release command runs under `uv run python`, as every other
  command on the Mac does.

Queries the repository could answer were answered in the text. The rest are
filed as `PL-GZFR`, `PL-M8Z7`, `PL-WP3Z` and `PL-LJY8`.
