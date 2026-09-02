---
id: PL-MGF9
title: The process-work grooming advisory only examines the top band, so it cannot fire for the P2 and P3 bands where all the process work actually sits
status: untriaged
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py
added: 2026-09-02
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
is that it is still enjoyed in a year is the owner's judgment and nobody
else's - building the apparatus is legitimately part of the fun, and this item
takes no position on the numbers. What it fixes is that a session reads `0
errors` and a band-size advisory and has no way to raise the question at all.

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
