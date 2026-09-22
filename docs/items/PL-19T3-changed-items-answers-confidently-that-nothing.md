---
id: PL-19T3
title: changed_items answers confidently that nothing changed when run outside a git repository, because git diff exits 1 there and _run_git reads exit 1 as an answer, where git tag --list exits 128 and declines
status: untriaged
added: 2026-09-22
---

**Problem.** changed_items answers confidently that nothing changed when run outside a git repository, because git diff exits 1 there and _run_git reads exit 1 as an answer, where git tag --list exits 128 and declines

**Found closing `PL-ZPDM`, 2026-09-22, and it is the residue of that item.**
`tags` and `changed_items` both carry a `declined` channel now, and one
environment still splits them:

| Where | `git tag --list` | `git diff --name-only BASE...HEAD` |
| --- | --- | --- |
| inside a repository, base unresolvable | exit 0, answer | exit **128**, silence - declines |
| outside a repository | exit **128**, declines | exit **1**, "error: Could not access" - read as an answer |

`_run_git` classifies exit 1 as git answering no, which is right for the case
the rule was written for - `rev-parse --verify --quiet` on a ref that is not
there - and wrong here: there is no branch outside a repository, so "this
branch changed no item" is not a weaker truth but a different claim. The read
returns `known=True` and an empty set, which is the collapse
`.claude/rules/apparatus-standard.md`'s floor refuses.

**The sweep cannot see it**, which is why it is worth an item rather than a
line: `test_vcs_silence.py` runs every read against a real repository and
silences one call at a time, so an environment that has no repository at all is
outside its design.

**Low reach, and the cheap fix may be elsewhere.** Nothing in this project runs
`docket check --verify-base` outside a checkout, so the cost today is the claim
rather than a wrong decision taken from it. Two candidate routes, and the item
is which: classify `git diff`'s exit 1 by whether the command was a diff of
revisions (where git exits 1 only on error, `--exit-code` not being passed) or
probe the repository once per read and decline everything on the answer.
