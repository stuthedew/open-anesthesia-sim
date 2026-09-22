---
id: PL-0HPV
title: make check omits the verify replay on a cost measured before --verify-base narrowed it, so a PR-only failure class is only ever found from CI
priority: P3
effort: S
status: needs-decision
classes: session-cost, infra
feature: ci-cost
touches: Makefile, .github/workflows/quality.yml
added: 2026-09-14
root-cause-of: PL-J3BB, PL-J3WK, PL-PBP5
generator: live - make check and quality.yml are separate lists and make check omits the scoped verify replay, so a failure class reaches CI only; #915 went red this way on 2026-09-22, after a local make check exit 0 (PL-KVDK)
---

**Problem.** make check omits the verify replay on a cost measured before --verify-base narrowed it, so a PR-only failure class is only ever found from CI

**What it cost, 2026-09-14.** `PL-TFX5` pushed a green `make check` and CI went
red on `bin/docket check --verify --verify-base "$VERIFY_BASE"` — an open item
whose `verify:` command already passed. One CI cycle and one round trip, for a
failure the session could have seen before pushing.

**The omission is deliberate and its reasoning is written in the `Makefile`**,
beside the `bin/docket check` line: the replay is left out because it is slow,
and `.github/workflows/quality.yml` runs it on both its events, narrowing the
pull-request one with `--verify-base` to the items that branch changed. So this
is not an oversight to point out — it is a priced decision.

**The price has changed since it was taken, and nobody re-measured.** The
`Makefile`'s own figure is "Measured 2026-09-05, four cores: this target 60.0 s
with the replay against 29.5 s without", and that is the **whole-store** replay.
`PL-SDHR` added `--verify-base`, which is what CI now uses on a pull request,
and the narrowed form is what a session would run. Measured 2026-09-14 on a
branch touching 11 items: **7.1 s**, against the 30.5 s the refusal was priced
against — roughly a quarter, and it falls to nothing on a branch that changes
no item at all, which is most of them.

**So the question is whether `make check` should run the narrowed form**, not
the whole-store one:

```
bin/docket check --verify --verify-base origin/main
```

**The objection to answer first, and it is not the cost.** `make check` is
expected to work in a bare checkout, and `--verify-base origin/main` needs a
ref that may be absent or stale there — the same problem `PL-0999` fixed for
`docket verify` by refreshing rather than trusting a local `main`. Whatever
this does has to degrade to today's behavior when no base can be resolved,
rather than failing the gate for a reason unrelated to the work. That, rather
than the 7 s, is the design.

**Do not treat the 7 s as the argument on its own.** The number that would make
this wrong is how often the replay changes a session's answer: a check firing
every run without changing a decision is a defect in the check by `CLAUDE.md`'s
own standard. One observed instance is not a rate. Count how many pull requests
have been red on this step before recommending it.

**Why it matters.** The gap is real and the item's own brief prices it
honestly: a failure class that only CI can find costs a round trip every time it
fires, and `PL-TFX5` paid one. What the item correctly refuses to do is treat
the 7.1 s as the argument. `CLAUDE.md` holds that a check firing every run
without changing a decision is a defect in the check, so adding one to `make
check` is only right if it changes an answer often enough to earn the seconds it
takes from every session forever - and one observed instance is not a rate.

**Decision needed.** Whether `make check` should run the narrowed verify replay,
`bin/docket check --verify --verify-base origin/main`.

Two things have to be settled, and the cost is the lesser of them:

1. **The rate.** How many pull requests have gone red on
   `bin/docket check --verify` while `make check` was green. That is a countable
   fact from the run history of `.github/workflows/quality.yml`, and nobody has
   counted it. If the answer is one - `PL-TFX5` - the change is not justified
   and this item closes `dropped` with the count as its reason.
2. **The degradation, which is the actual design.** `make check` is expected to
   work in a bare checkout, and `--verify-base origin/main` needs a ref that may
   be absent or stale there. Whatever lands has to fall back to today's
   behaviour when no base resolves, rather than failing the gate for a reason
   unrelated to the work - the problem `PL-0999` already solved for `docket
   verify` by refreshing rather than trusting a local `main`.

The `Makefile`'s own comment beside the `bin/docket check` line prices the
refusal at "60.0 s with the replay against 29.5 s without", which is the
whole-store form; the narrowed form measured 7.1 s on a branch touching 11
items and falls to nothing on a branch that changes no item. Update that comment
whichever way this is decided, so the recorded price matches the one in force.

**Done when.** `make check` either runs the narrowed verify replay - degrading
to today's behaviour when no base ref resolves, rather than failing the gate -
or this item is closed `dropped` with the pull-request count that showed the
replay would not have changed an answer. Either way the `Makefile` comment
beside `bin/docket check` states the price in force rather than the whole-store
figure it carries today.

**Re-measured 2026-09-21, on four cores - the same core count the `Makefile`
comment's figures were taken on.** The narrowed replay costs **5.9 s**, not the
30.5 s the recorded reason rests on:

| Command | Elapsed |
| --- | ---: |
| `bin/docket check` (what `make docket` runs) | 1.1 s |
| `bin/docket check --verify --verify-base origin/main` | 7.0 s |

Both timed twice, within 0.1 s. The replay reported `15 commands in 5.7 s
(44.8 s serially), scoped to 26 item(s)` - so the serial figure is still large
and it is the parallelism plus `--verify-base`'s narrowing that makes the
difference, which is this item's whole point. The `Makefile` comment's own
numbers - 60.0 s with the replay against 29.5 s without, 2026-09-05, four
cores - predate `PL-SDHR`'s `--verify-base` and are the whole-store sweep.

**One caveat the decision needs:** 26 items is *this* branch's scope, and a
branch touching a widely-cited file scopes more. The number above is a
representative case rather than a bound, and whoever takes this should say
which it needs to be.

**A live instance arrived the same day.** `#830`'s first push was failed by CI
on precisely the class this replay catches and `make check` cannot - see
`PL-J3WK`, which carries it.

**Recommended (a session's, 2026-09-21, not the project owner's), over leaving
`make docket` bare: add the narrowed replay, degrading to a silent skip when
`origin/main` cannot be resolved.** The measurement above is half the case; the
other half is that the `Makefile` comment's argument does not reach the form
being proposed.

That comment refuses the replay because it "finds work that *merged* without
its item being closed, and a pre-commit gate on a feature branch cannot have
changed that". That is correct, and it is an argument about the **whole-store**
sweep - which should stay where it is, on pushes to `main`, where its answer is
a fact about `main`. `--verify-base origin/main` asks a different question:
does *this branch's own* store edit hold up. A session can certainly change
that answer, because it just wrote the thing being checked. So the two forms
are not the same gate run at different prices, and the recorded reason retires
only one of them.

**The design constraint is offline, not cost, and the repository already
solves it.** `make check` has to pass in a bare checkout and with no network,
which is why `tools/pr_title_check.py --discover` states "Every way that can
fail is a silent skip, never a failure" and runs its lookup before the
expensive half. The same rule fits here: where `git rev-parse origin/main`
fails, run `bin/docket check` bare and print one line saying the replay was
skipped for want of a base. A gate that fails when it cannot look would be
worse than the gap it closes - `pr_title_check`'s own words.

**What would make this wrong**, stated so it can be checked rather than argued:
if a representative branch's scope is much larger than the 26 items measured
above, the cost stops being 5.9 s. The number to take before building it is the
replay's elapsed on the widest realistic scope - a branch editing a file many
open `verify:` commands read, `CLAUDE.md` or `ROADMAP.md` - not on this one. If
that comes back above roughly 20 s, the skip-by-default-with-an-opt-in-target
answer is better than putting it in `make check` unconditionally.

