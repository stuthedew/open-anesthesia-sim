---
id: PL-S1BG
title: The push guard runs doc_check and branch_id_check but not bin/docket check --verify, which make check also runs and which refused all 40 branch-caused store-rule red runs in PL-1BGP's sort locally; adding it in parallel costs no wait (6.7 s against doc_check's 10.5 s) but refuses a push when main itself is wrong (2 runs in the census, none since 2026-09-23)
status: untriaged
feature: fewer-red-runs
added: 2026-09-27
---

**Problem.** `.claude/hooks/push-check-guard.sh` (`PL-PLSJ`) runs the two
checks that the census's `doc_check` and `branch_id_check` failures needed.
`PL-1BGP` then sorted the 43 store-rule red runs and found 40 were the
branch's own. `make check` runs `bin/docket check --verify --verify-base
origin/main`, and that check refuses all 40 locally.

**Why it matters.** The census counted those 40 runs, alongside the 40 that
the guard now covers. Each cost a session a fix cycle.

**The question for the project owner: add the store check to the push guard?**

- **What it buys.** In the census, 40 of 391 red runs, including all 8 store
  failures since 2026-09-23.
- **What it costs in time.** None: 6.7 s measured here, run beside
  `doc_check`'s 10.5 s.
- **What it costs in refusals.** The check reads `origin/main`. On a day
  `main` itself is wrong, it refuses pushes the branch cannot fix, until
  `main` is repaired or the session pushes with `--no-verify`. That happened
  on 2 runs in the census, both on 2026-09-19, from a cause that
  `tools/pr_record_check.py` has refused since 2026-09-26.

**Recommendation: yes** (recorded 2026-09-27, awaiting the owner). The
failure it prevents has recurred every week. The false refusal has not
occurred since the pr-record gate landed, and when it does occur it names
the item on `main` that is wrong.

**If approved, what the build needs:**

- Add `bin/docket check --verify --verify-base origin/main --no-fetch` to
  `CHECKS`. Use `--no-fetch` so a push never waits on the network: the base
  is at least as new as the branch's last merge of it.
- The excerpt must also stop at the "Grooming advisories (" heading.
- Add a test for a refusal from this check, beside the other two.
