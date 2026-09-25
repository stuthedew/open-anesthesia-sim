---
id: PL-2TV9
title: The origin remote's GitHub owner/name is parsed four ways, which disagree on a token-bearing URL, a trailing slash and an ssh port, and the token variables are read in opposite precedence
status: untriaged
feature: one-answer
touches: tools/open_pull_requests.py, tools/main_ci_status.py, tools/pr_body_check.py, tools/required_checks_check.py
added: 2026-09-25
---

**Problem.** The origin remote's GitHub owner/name is parsed four ways, which disagree on a token-bearing URL, a trailing slash and an ssh port, and the token variables are read in opposite precedence

Reproduced: `https://x-access-token:abc@github.com/o/r.git` gives None to open_pull_requests and the slug to the others; `.../r.git/` gives `o/r.git` and None; `ssh://git@github.com:22/o/r.git` gives main_ci_status `22/o/r`. GH_TOKEN-first vs GITHUB_TOKEN-first (`required_checks_check.py:423`). The live remote agrees in all four.

**Why it matters.** Low today; the harness has changed its remote URL shape before.

**Done when.** One slug parser and one token lookup, imported by all four.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
