---
id: PL-KX73
title: claim refuses the web harness's own branch shape: every session branch starts with branch.<name>.merge=refs/heads/main, so claim exits 1 with 'pushes to origin/main, and a claim names one branch' until the session pushes with -u or unsets the upstream, and nothing in .claude/ or the README says so
status: untriaged
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claiming.py
added: 2026-09-25
---

**Problem.** claim refuses the web harness's own branch shape: every session branch starts with branch.<name>.merge=refs/heads/main, so claim exits 1 with 'pushes to origin/main, and a claim names one branch' until the session pushes with -u or unsets the upstream, and nothing in .claude/ or the README says so

Confirmed read-only on this session's branch (`branch.claude/upbeat-heisenberg-27vafn.merge` is `refs/heads/main`) and reproduced in the simulation (scenario u). Adjacent to PL-WX87.

**Why it matters.** Every web session's first claim before its first push hits it.

**Done when.** `claim` sets the branch's own upstream (or pushes with `-u`) when the upstream is the default branch, or prints the one command that does; a test holds scenario u.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
