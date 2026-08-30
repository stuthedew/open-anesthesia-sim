---
id: PL-0999
title: docket verify defaults to a local main that a fresh checkout leaves stale
priority: P2
effort: S
status: done
classes: defect
feature: dev-tooling
milestone: v0.2.7
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_verify.py
added: 2026-08-30
closed: 2026-08-30
commit: 8c72f1b
pr: 74
verify: uv run pytest subprojects/docket/tests -k base
---

**Problem.** `docket verify` compares the branch against `main` by default —
the *local* branch, not `origin/main`. A session that starts from a fresh
remote checkout can have a local `main` many commits behind the remote, and
`verify` then reports every file that landed on the remote in between as a
path outside the item's commission. Running it during PL-VP7N's close-out
reported 20 paths outside `touches`, of which 16 were other sessions' item
files that this branch never touched; `--base origin/main` gave the true
answer of 4.

**Why it matters.** The output looks authoritative and is not, which is the
specific failure mode `CLAUDE.md`'s "do not script the judgment" warns about.
"Diff stayed inside `touches`" is one of the checks a reviewer is meant to
lean on, and a session that trusted the default would either chase sixteen
phantom scope violations or, having seen the check cry wolf once, stop
reading it. Both are worse than the check not existing.

**Where.** `subprojects/docket/src`, wherever `verify`'s `--base` default is
set; `bin/docket verify --base BASE` already exists and is the workaround.

**Done when.** The default base is the one the branch actually forked from —
prefer `origin/main` where it exists, or at minimum say loudly when the base
being compared against is behind its own remote, so a stale answer cannot be
read as a clean one. A test covering a local base behind its remote.
