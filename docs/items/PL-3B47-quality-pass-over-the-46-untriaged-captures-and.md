---
id: PL-3B47
title: Quality pass over the 46 untriaged captures and the triaged tooling items, and repair the apparatus defects it finds
priority: P2
effort: M
status: done
classes: infra, defect
feature: queue-hygiene
touches: docs/items, subprojects/docket, tools, .claude, Makefile, docket.toml, tests/unit
added: 2026-09-12
closed: 2026-09-12
pr: 496
not-delegable: A queue-wide grooming pass has no command that can prove it: 'bin/docket check reports no untriaged items' passes on any tree where nobody has captured anything, and the apparatus repairs it carries are each proven by their own item's verify: command. The pass is judged by those, plus make check.
---

**Problem.** Quality pass over the 46 untriaged captures and the triaged tooling items, and repair the apparatus defects it finds

**Why it matters.** Captures had reached 46 untriaged - past `docket.toml`'s
`untriaged_stale_days` horizon for the oldest of them - which is the state that
turns the capture half of the queue into a second queue nobody reads. Untriaged
items are invisible to `bin/docket next`, so work sitting in them is neither
scheduled nor visible as backlog, and `bin/docket next`'s own open count
understates the total by exactly that number (`PL-ZWBK`).

Two costs compound while it sits. Duplicates accumulate unnoticed - two pairs
were filed three days apart, each costing a second session the same diagnosis -
and captures go stale as ordinary work overtakes them, so a later session spends
a pass rediscovering that a filed defect was fixed four releases ago. Both are
only visible when the pile is read end to end, which is what this pass is.

**Done when.** `bin/docket check` reports zero untriaged items with no errors;
every item that stayed carries `priority`, `effort`, `classes`, `touches` and a
`feature`, with a `verify:` command that was run and watched fail for any set to
`ready`; every item that left carries a `reason` naming what replaced it or what
fixed it; and the apparatus defects this pass found to be real are repaired with
tests, `make check` clean.
