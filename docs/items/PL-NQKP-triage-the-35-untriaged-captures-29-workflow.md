---
id: PL-NQKP
title: Triage the 35 untriaged captures: 29 workflow-lane items need fields and a run verify: command, and the 6 that landed from the #784 adversarial review need a v0.5.0 gate disposition instead
priority: P2
effort: M
status: done
classes: housekeeping
feature: queue-hygiene
touches: docs/items, ROADMAP.md
added: 2026-09-20
closed: 2026-09-20
pr: 810
payoff: the newest 30 findings become rankable by bin/docket next, so the project stops computing every priority answer over a queue that excludes them
verify: grep -qF 'from the 2026-09-20 triage pass over the thirty untriaged' ROADMAP.md
---

**Problem.** Triage the 35 untriaged captures: 29 workflow-lane items need fields and a run verify: command, and the 6 that landed from the #784 adversarial review need a v0.5.0 gate disposition instead

**Why this is filed rather than done.** `CLAUDE.md` files repository work no
item names before doing it, because every in-flight guard this project has
matches a `PL-` id and unfiled work reads as nobody's to all of them. Triage
takes a commit of its own, so it needs one.

**Measured 2026-09-20.** 35 untriaged, and they are not one job:

- **29 workflow-lane captures** wanting the ordinary pass — `priority`,
  `effort`, `classes`, `touches`, `feature`, then `ready`, `needs-decision` or
  `dropped`. 26 of the 35 carry neither `priority` nor `effort`, both required
  by `bin/docket check`, so they are invisible to `bin/docket next` and every
  ranking answer today is computed over a queue that excludes the newest
  findings.
- **6 that are a different job**: `PL-25DD`, `PL-624C`, `PL-FKN7`, `PL-R17Y`,
  `PL-RS3Z` and `PL-WG73`, filed by the adversarial review of #784 and landed on
  `main` 2026-09-20. Each needs a **v0.5.0 gate disposition**, which is a
  release judgment rather than field-filling, and `PL-HZ1B` already owns it —
  "recover the seven items stranded on `claude/vigilant-albattani-3lkcb3` and
  give each a v0.5.0 gate disposition, since a triaged safety item with none
  fails `make check`". Their recovery half is done; the gate half is not.

**Recommended.** Work the 29 here and leave the 6 to `PL-HZ1B`. Folding them
in would put a gate scoping decision inside a field-filling pass, which is the
`needs-decision`-versus-`blocked-by` confusion `.claude/skills/docket/modes/triage.md`
records `PL-B9PY` as the cost of. The seventh of that review's items,
`PL-LHBY`, is already `ready` and `P1` safety-classed, so the gate pressure is
real rather than hypothetical.

**`PL-HZ1B` is itself stranded** on `origin/claude/lucid-dijkstra-i1qy6x`,
whose session is idle and asking whether to keep or delete that branch. If the
branch goes, the item goes with it. `bin/docket stranded` prints the recovery
line.

**Why it is a session of its own.** `.claude/skills/docket/modes/triage.md`
requires, per item reaching `ready`, a `verify:` command that has been **run
and watched to fail**, plus a second command reproducing the fault — the
measured catch rate is about one in thirty-three, against a sweep that cost
145,000 tokens across twelve agents to find the same five (`PL-JB3Z`). At four
to six commands per item that is roughly 150 tool calls, which is a whole
session's budget under `CLAUDE.md`'s 150,000-token handoff rule.

**Verified 2026-09-20: `main` is green *because* those 6 are untriaged, and
triaging them without their gate dispositions in the same commit turns it
red.** `python3 tools/doc_check.py check` passes today with 0 errors.
`PL-HZ1B` records the mechanism: `doc_check` fails `make check` on any
**triaged** debt item that v0.5.0's gate records no disposition for — neither
on the frozen list nor in a `### Declined to Gate ...` subsection — so a
`ready`, `safety`-classed item recovered or promoted into the store reddens the
branch until `ROADMAP.md` carries its entry. `PL-3K9B` hit exactly this on
2026-09-20 and the branch stayed red across #801 and #805. So the disposition
is written in the *same* commit as the promotion, never after it.

**`PL-HZ1B` also carries a ratified owner decision that exists nowhere else.**
Its brief records (project owner, 2026-09-20, ratified, over working `PL-4KZD`
alone and over keeping the three attribution defects separate) that the
marks-panel attribution defect is one problem under `feature:
two-run-attribution`, with **`PL-LHBY` as carrier and `PL-4KZD` folded into
it** — `PL-LHBY` preferred because it reproduces offscreen against the merged
tree and its `touches` reach `app/qt_widgets.py` where `PL-4KZD`'s do not. That
item is unmerged on `origin/claude/lucid-dijkstra-i1qy6x` and its session is
asking whether to drop it. Dropping it deletes the only carrier of that
decision, which is `PL-KQHN`'s failure exactly. Recover it before that branch
goes.

**Done when.** `bin/docket triage` reports nothing outside the 6 that
`PL-HZ1B` holds, `bin/docket check` passes with no error, and the pass's reply
says what each item landed on.

**Why it matters.** 26 of the 35 carried neither `priority` nor `effort`, both
required by `bin/docket check`, so they were invisible to `bin/docket next` and
every ranking answer the project gave was computed over a queue that excluded
its newest findings. The pass is what makes them rankable.

**Reading the gate trap exactly, 2026-09-20.** `check_gate_dispositions` in
`tools/doc_check.py` owes a disposition for every open item that is
`needs-decision` *or* carries a class in `docket.toml`'s `debt_classes`
(`defect`, `safety`, `science`, `refactor`, `perf`). It does not read status
otherwise - an `untriaged` item escapes because triage is what gives it
classes, not because `untriaged` is exempt. So the trap is wider than "the six
from #784": every item this pass classes `defect` owes a v0.5.0 gate entry in
the same commit, and 15 of the 30 did.

**What the pass actually took, and the seventh item it left.** 37 were
untriaged when it started - the 35 measured above plus `PL-HZ1B` and this item,
both recovered off branches at the project owner's request. 30 were triaged; 7
remain, and every one of them is another session's: the six from `#784` that
`PL-HZ1B` disposes, and `PL-HZ1B` itself.

**`PL-HZ1B`'s recovery was withdrawn on the evidence, not skipped.** It was
recovered from `origin/claude/lucid-dijkstra-i1qy6x` at the start of this pass
on the premise recorded above - that the branch's session was idle and asking
whether to delete it. That premise was false by the time it was checked. Read
2026-09-20, that session is `RUNNING`, its summary reads "narrowing `PL-HZ1B`,
preparing for main", and the branch had been force-pushed
(`a9cfe15d` -> `8dd7bcb7`) with `PL-HZ1B` rewritten: 6 insertions against 33
deletions relative to the copy recovered here. Their version keeps the ratified
fold verbatim - `PL-LHBY` as carrier, `PL-4KZD` folded into it - which is the
only thing the recovery existed to protect, and narrows the item's `Done when`
to the six dispositions that are genuinely left. So the recovered copy was a
stale duplicate of a live file, which is `PL-N1JK`'s failure exactly, and it
was dropped rather than carried. `bin/docket stranded` prints the recovery line
again if that branch dies.
