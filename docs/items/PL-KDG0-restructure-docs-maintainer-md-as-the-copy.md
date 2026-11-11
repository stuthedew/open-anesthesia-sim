---
id: PL-KDG0
title: Restructure docs/maintainer.md as the copy editor's structure read proposes: state each decision once where it applies, give subagent rules, auto mode and the cloud environment their own sections
status: done
feature: repo-copy-edit
milestone: v0.6.17
touches: docs/maintainer.md
added: 2026-11-07
closed: 2026-11-07
pr: 2047
verify: grep -q "^### Subagents run on the session's model and effort" docs/maintainer.md && grep -q '^## Make auto mode the default on your Mac' docs/maintainer.md
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

The closing prose review read the 18 changed passages and rewrote 15, and every price, command and file name a step needs is still in the guide.

**Done when.** Each decision in the guide is stated once, where the owner acts on it, and no step lost a command, value or link.

**Generator check.** The owner asked for this work (2026-11-05, "copy edit entire repo", and "Structure first" for this file). It is one area of a repository-wide copy edit, not a defect, so no mechanism caused it.
