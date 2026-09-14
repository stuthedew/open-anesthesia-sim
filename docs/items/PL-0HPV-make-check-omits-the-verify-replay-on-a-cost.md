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
