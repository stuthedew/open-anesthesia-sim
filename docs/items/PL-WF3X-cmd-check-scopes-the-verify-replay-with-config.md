---
id: PL-WF3X
title: cmd_check scopes the verify replay with config.items_dir rather than the store --items actually resolved to, so a queue outside docs/items has its diff taken against a directory it does not live in
priority: P2
effort: S
status: done
classes: defect
feature: count-input-addressing
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-22
closed: 2026-09-22
payoff: a scoped check --verify against a store outside docs/items replays the items the branch changed rather than nothing
verify: grep -q 'def test_the_replay_scope_reads_the_store_the_run_was_pointed_at' subprojects/docket/tests/test_cli.py
---

**Problem.** cmd_check scopes the verify replay with config.items_dir rather than the store --items actually resolved to, so a queue outside docs/items has its diff taken against a directory it does not live in

**Found closing `PL-ZPDM`, 2026-09-22, from the decline it now prints.** A test
store at `<tmp>/items`, passed with `--items`, produced a declined reason naming
`git diff --name-only docket-no-such-ref...HEAD -- docs/items` - a directory the
store is nowhere near. `_load` resolves the store as `args.items or (root /
config.items_dir)`, so `--items` wins for *reading* the queue, while
`config.items_dir` keeps the config value; `cmd_check` then hands that second
value to `changed_items`, so the scope is read from `docs/items` whatever
`--items` said.

**Latent here and wrong anywhere else.** This project's store *is* `docs/items`
and CI passes no `--items`, so the two agree on every run that matters today.
Pointed at another project's queue the scope silently narrows to whatever that
path happens to hold - nothing, usually - and a scoped `--verify` run then
replays nothing while reporting a clean result, which is the direction
`PL-ZPDM` has just taken out of the silence case.

`_tracked(args)` already answers this exact question - "the repository root, and
the queue directory beneath it as git spells it" - and `_flight` uses it for the
same reason. `PL-P757` is the recorded instance of the wrong directory here
reading every commit as work.

**Done when** the scope diff is taken against the directory the run actually
read the store from, with a test driving a store outside `docs/items`.
