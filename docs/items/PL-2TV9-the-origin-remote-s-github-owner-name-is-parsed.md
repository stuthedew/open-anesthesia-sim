---
id: PL-2TV9
title: The origin remote's GitHub owner/name is parsed four ways, which disagree on a token-bearing URL, a trailing slash and an ssh port, and the token variables are read in opposite precedence
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/open_pull_requests.py, tools/main_ci_status.py, tools/pr_body_check.py, tools/required_checks_check.py, tests/unit/test_open_pull_requests.py, tests/unit/test_required_checks_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-answer batch
added: 2026-09-25
payoff: every tool that reads the origin's owner/name gets the same answer from one parser, so a new remote URL shape breaks all of them loudly or none of them
verify: grep -q 'def test_repo_slug_reads_a_token_bearing_url' tests/unit/test_open_pull_requests.py && grep -q 'def test_token_is_read_in_one_precedence' tests/unit/test_required_checks_check.py
---

**Problem.** The origin remote's GitHub owner/name is parsed four ways, which disagree on a token-bearing URL, a trailing slash and an ssh port, and the token variables are read in opposite precedence

Reproduced: `https://x-access-token:abc@github.com/o/r.git` gives None to open_pull_requests and the slug to the others; `.../r.git/` gives `o/r.git` and None; `ssh://git@github.com:22/o/r.git` gives main_ci_status `22/o/r`. GH_TOKEN-first vs GITHUB_TOKEN-first (`required_checks_check.py`'s `main`, against `open_pull_requests.open_pull_requests`). The live remote agrees in all four.

**Re-confirmed 2026-09-25 against 46954a81**, calling each parser on each URL (`required_checks_check._repo_from_git` through a scratch repository's `origin`):

- the token-bearing URL gives `None` to `open_pull_requests.repo_slug` and `o/r` to the other three;
- `https://github.com/o/r.git/` gives `o/r.git`, `o/r`, `None` and `o/r`;
- `ssh://git@github.com:22/o/r.git` gives `None`, `22/o/r`, `None` and a `RuntimeError`.

`main_ci_status` and `pr_body_check` read no token at all. On a shape it misparses, a caller says something false and confident: `pr_body_check` prints "origin is not a GitHub remote", and `main_ci_status` returns 0 silently. `left_behind_check` and `pr_title_check` import `open_pull_requests.repo_slug`, so they inherit its answer.

**Why it matters.** Low today; the harness has changed its remote URL shape before.

**Generator check.** It is an instance of PL-PVW2's fact, which spelling of a repeated predicate is the answer. The predicate is the origin's owner/name, and the token variable read is a second one.

**Done when.** One slug parser and one token lookup, imported by all four.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
