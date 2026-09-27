---
id: PL-S1BG
title: The push guard runs doc_check and branch_id_check but not bin/docket check --verify, which make check also runs and which refused all 40 branch-caused store-rule red runs in PL-1BGP's sort locally; adding it in parallel costs no wait (6.7 s against doc_check's 10.5 s) but refuses a push when main itself is wrong (2 runs in the census, none since 2026-09-23)
priority: P2
effort: S
status: done
classes: infra
feature: fewer-red-runs
touches: .claude/hooks/push-check-guard.sh, tests/unit/test_push_check_guard.py, docs/items
added: 2026-09-27
closed: 2026-09-27
pr: 1216
payoff: a push whose tree fails bin/docket check --verify is refused before it leaves the container, so a branch's own store error stops turning its pull request red
verify: grep -q 'Grooming advisories (' .claude/hooks/push-check-guard.sh && grep -q 'def test_a_push_whose_store_check_fails_is_refused' tests/unit/test_push_check_guard.py
---

**Problem.** `.claude/hooks/push-check-guard.sh` (`PL-PLSJ`) runs the two
checks that the census's `doc_check` and `branch_id_check` failures needed.
`PL-1BGP` then sorted the 43 store-rule red runs and found 40 were the
branch's own. `make check` runs `bin/docket check --verify --verify-base
origin/main`, and that check refuses all 40 locally.

**Why it matters.** The census counted those 40 runs, alongside the 40 that
the guard now covers. Each cost a session a fix cycle.

**Done when.** The push guard runs `bin/docket check --verify --verify-base
origin/main --no-fetch` beside its other two checks. It refuses a push that
check fails and shows the store's errors alone, and a test pins that refusal.

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

**Recommendation: yes** (recorded 2026-09-27). The failure it prevents has
recurred every week. The false refusal has not occurred since the pr-record
gate landed, and when it does occur it names the item on `main` that is
wrong.

**Approved 2026-09-27: add it** (project owner, 2026-09-27, ratified, over
leaving the store check to `make check` and CI). The request lifts the
generator pause for this build (`PL-6Q9L`).

**Generator check.** Work the owner asked for, and not a generator. The fact
misread is `PL-PLSJ`'s: a push can send a tree that nothing has checked. This
extends that item's fix to the one check it left out.

**What the build needs:**

- Add `bin/docket check --verify --verify-base origin/main --no-fetch` to
  `CHECKS`. Use `--no-fetch` so a push never waits on the network: the base
  is at least as new as the branch's last merge of it.
- The excerpt must also stop at the "Grooming advisories (" heading.
- Add a test for a refusal from this check, beside the other two.

**Worked 2026-09-27.** Built as listed. `bin/docket` is a bash wrapper, so
`CHECKS` now spells each check the way a session types it, and the runner
starts `bin/docket` under bash. On this repository, with the real checks:

- The clean tree passed in 11.7 s, against 12.0 s with two checks.
- A planted open item whose `verify:` passed was refused in 11.4 s. The
  refusal showed the store's one error and no advisories.
- With no `origin/main`, the store check exits 0 and reports under "Not
  checked", so the push goes through.
- An uncommitted new item is replayed too, so this check has no gap in
  `git commit ... && git push`.

**One correction to the question above.** It called a refusal on `main`'s bad
day one "the branch cannot fix". The branch can. The census's `main`-caused
error, a closure with no `pr`, reads the branch's own copy of the item, and
the error names the command that writes the fix, `docket record N --merge
SHA`. So the refusal offers no second bypass. A bypass for errors that name
only items the branch never changed would be wrong as well. The replay also
runs items whose `verify:` reads a file the branch changed, and that is
`PL-1BGP`'s 10 runs where a branch did an item's work and left the item open.
There the fault is the branch's.
