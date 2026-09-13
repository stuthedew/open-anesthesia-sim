---
id: PL-MGF9
title: The process-work grooming advisory only examines the top band, so it cannot fire for the P2 and P3 bands where all the process work actually sits
priority: P2
effort: S
status: dropped
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-02
closed: 2026-09-13
reason: Superseded by `bin/docket trend` (PL-QPJZ, #424), which landed 2026-09-07, five days after this was captured, and already reports the process-to-product balance over the whole open queue - the Done when's own requirement. It places an item by its `touches` rather than by its `classes`, which docket.toml records as the better reading (the classes reading put 33 of 145 open items on the wrong side), and it carries a seven-day history this item never asked for. The advisory specified here also could not fire: measured 2026-09-13, 74 of 244 open items are process-classed and a majority needs 123, so building it as written would add a permanently silent advisory - the shape CLAUDE.md calls a defect in the check. Project owner, 2026-09-13. The one residual - that `trend` answers only on demand, and the session-start digest does not carry its balance line - is recorded in the re-measurement section below and deliberately not refiled.
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_process_majority_is_measured_over_the_open_queue' subprojects/docket/tests/test_checks.py
---

**Problem.** `_groom` in `subprojects/docket/src/docket/checks.py:773` builds
`top = _top_band(report)` and returns early when it is empty. Every advisory
below that line — the band-size limit, the needs-decision majority, and the
process-work majority at `checks.py:788` — reads only `top`. `_top_band`
returns the *highest* band holding anything, which in this store is `P1`.

`docket.toml` refuses to seat a `safety`- or `science`-classed item below
`P1`, and its own comment records that "every `P1` item this project has ever
held carries one of those classes". So `top` is, structurally, the band that
contains no process work — and the advisory that exists to warn when process
work outnumbers product work is evaluated exclusively against the one band
where it can never be true.

Measured 2026-09-02 in this checkout: 0 of 7 open `P1` items are
process-classed, so the advisory is silent. Below it, 13 open `P2` and 17 open
`P3` items carry `session-cost`, `docs` and `infra` and nothing else — 30
items the advisory is blind to by construction.

**Why it matters.** `CLAUDE.md` names the apparatus "at permanent risk of
becoming the work instead", and this advisory is the only automated instrument
pointed at that risk. It is aimed at the one band where the risk cannot appear.

The point is that the balance is *unreportable*, not that today's balance is
wrong. Measured 2026-09-02, and none of it visible from any command: 177 of 311
items ever created carry an apparatus `feature` against 84 carrying a product
one; 53 of 109 open items are apparatus; `git diff --shortstat` from the root
commit gives 41,183 apparatus insertions against 16,517 product; and
`subprojects/docket/src` is 7,013 lines against `src/`'s 3,992.

Whether that is the right balance for a solo project whose measure of success
is that it is still being worked on and enjoyed years from now is the owner's
judgment and nobody else's - building the apparatus is legitimately part of
the fun, and this item takes no position on the numbers. What it fixes is that
a session reads `0 errors` and a band-size advisory and has no way to raise
the question at all.

Structural health is measured and is not the concern here: `docket`'s modules
form an acyclic layering (`model`/`config` -> `store`/`release`/`concurrency`
-> `vcs`/`roadmap` -> `plan`/`verify` -> `checks` -> `render` -> `cli`) with a
median function length of 13 lines across 217 functions. The apparatus is
large and well-factored. This advisory is about proportion, which only the
owner can rule on, so it must report and never gate.

**Where.** `subprojects/docket/src/docket/checks.py:773-794` (`_groom`), which
already holds `config.process_classes`. `_top_band` at `checks.py:797` is read,
not changed — the band-size and needs-decision advisories above are correct to
scope themselves to the top band, and only the process-work one is not.

**Approach.** Two changes at the same site, the second optional:

1. Compute the process-work ratio over `report.open_items` rather than over
   `top`, and advise when process work is the majority of the open queue.
   Report the counts, not a verdict, so the reading is auditable — `docket`
   cannot decide whether 49% apparatus is right for a given week.
2. The `P3` half of the same problem: nothing forces a decision on an aged
   process-classed item in the bottom band, so it accumulates without ever
   being either promoted or dropped. `untriaged_stale_days` already
   establishes the pattern for a capture that has gone stale; a companion
   threshold over `P3` process items would make the same decision explicit
   instead of letting the band absorb them silently.

Do not make either an error. The ratio is a judgment the project owner makes
with the roadmap in view, and a gate that blocks `make check` on it would be a
tool guessing at the judgment half, which `CLAUDE.md` forbids.

**Found.** 2026-09-02, during an independent audit of the open workflow and
dev-tooling items. The audit's own headline numbers had to be computed by hand
from `git diff --shortstat` and a script over `docs/items/*.md`, because no
command reports them — which is the finding.

**Done when.** `bin/docket check` reports the process-to-product balance of the
whole open queue rather than of the top band alone, the advisory fires against
the current store, and a test pins it against a store whose top band is
entirely product work and whose lower bands are entirely process work.

## Re-measured 2026-09-13: `bin/docket trend` has since answered this, and better

This item was captured 2026-09-02. `bin/docket trend` landed 2026-09-07
(`PL-QPJZ`, #424), five days later, and it reports exactly what the **Done
when** asks for — the process-to-product balance of the whole open queue
rather than of the top band. On this store it prints:

```
Open now           107 workflow, 107 product, 29 crossing, 1 unplaced
P1 band            0 workflow, 10 product, 3 crossing, 0 unplaced
```

with a seven-day history beside it and three separate measures, because no
one of them is honest alone. It is a better instrument than the one this
item specifies, on the reading `docket.toml` itself already settled: `trend`
places an item by its `touches`, and the comment beside `workflow_paths`
records that the `classes` reading this item would use put **33 of 145** open
items on the wrong side, because `classes` says what *kind* of work an item
is and a defect in the tooling carries the same `defect` label as a defect in
the simulator.

**The advisory this item specifies also cannot fire.** Measured 2026-09-13
against the live store: 74 of 244 open items are process-classed under
`process_classes`. A majority test needs it to exceed 122. So implementing
this as written would add an advisory that is silent today and whose own
**Done when** ("the advisory fires against the current store") is unmeetable.

This is the shape `PL-LKGL` describes: an item whose problem was solved
another way stays red forever and reads as outstanding work.

**What is genuinely left is smaller than this item.** `trend` answers on
demand; nothing pushes the balance in front of a session that did not think
to ask. The session-start digest does not carry it. So the residual is one
line in the digest, not a classes-based majority advisory — which is a
different and much cheaper item than the one this brief describes.

**Decided 2026-09-13: dropped.** Three dispositions were put to the project
owner and the first was taken:

1. **Drop**, `reason:` superseded by `bin/docket trend` (`PL-QPJZ`) — taken.
   Clears a Gate 1 entry honestly.
2. **Re-scope** to "the session-start digest carries `trend`'s open-queue
   balance line", `S`, rewriting the **Done when** accordingly.
3. Build as written — it adds a permanently silent advisory on the reading
   this project has already measured as the worse one.

**The residual is recorded here rather than refiled, deliberately.** Option 2
was the alternative on the table and was not chosen, so filing it as a fresh
item would reintroduce as work what was just declined. The finding is not lost
— it is the paragraph above, and this file is never deleted, which is what
`docket`'s drop semantics are for. Anyone reaching for it again should start
by re-measuring rather than by reviving this brief: the counts here are dated
2026-09-13 and the balance moves with every release.

**What this drop does not say.** It takes no position on the apparatus-to-
product balance itself, which is the project owner's judgment and is now
reportable by `bin/docket trend` at any time. It says only that *this
mechanism*, a `classes`-based majority advisory over the open queue, is the
wrong instrument for measuring it and could not have fired in any case.
