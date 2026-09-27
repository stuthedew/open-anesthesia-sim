---
id: PL-06JJ
title: Pin items on the generator tier to P1, so readers of the stored priority field - the queue dashboard among them - see what docket next already ranks: docket check refuses one below P1, and docket set raises it automatically
priority: P2
effort: S
status: ready
classes: infra
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .claude/skills/docket/modes/picking.md, .claude/skills/docket/modes/triage.md
added: 2026-09-27
payoff: A reader of the stored priority field - the queue dashboard among them - sees a generator-tier item at P1, where docket next already ranks it above every band but P0
verify: grep -q 'def test_an_item_on_the_generator_tier_below_p1_is_refused' subprojects/docket/tests/test_checks.py && grep -q 'def test_set_raises_an_item_it_puts_on_the_generator_tier_to_p1' subprojects/docket/tests/test_cli.py
---

**Problem.** Pin items on the generator tier to P1, so readers of the stored priority field - the queue dashboard among them - see what docket next already ranks: docket check refuses one below P1, and docket set raises it automatically

**Why it matters.** The owner reads the queue on its dashboard, which shows the
stored band, and saw the one live head there at `P2` while `docket next` ranked
it above every `P1`. The display then disagrees with the ranking on exactly the
item the tier exists to surface - one every session it stands through pays
again - and calls it ordinary work.

**Decision (project owner, 2026-09-27).** Asked in their own words: "make
generators automatically P1". The session recommended leaving the stored band
alone and having `docket list` and the session-start digest show a live head as
on the generator tier, because `docket next` already ranks one above every P1
and above the roadmap step's scope (`rank` in
`subprojects/docket/src/docket/plan.py`), so a stored P1 moves nothing in the
order. The owner then said the P2 they saw was on the queue dashboard
(`stuthedew/oas-queue-dashboard`), which that route cannot reach: anything
reading `priority:` straight from the file shows the stored band. So the band
itself is pinned, over the display-only route.

**The cost, accepted.** P1 stops being all clinical. `docket check` pins
`safety` and `science` there, and `.claude/skills/docket/modes/picking.md`'s
"Do not promote process work into P1" reads the band as "a clinician could be
misled"; on 2026-09-27 all three open P1 items were `science`-classed. The
carve-out is narrow and is not promotion: the tier already ranks these above
every band, so the pin changes no order, only what the stored field says. One
open head on the morning of 2026-09-27, and none once #1160 merged.

**Design.**
- `docket check`: an open item on the generator tier at `P2` or `P3` is an
  error, built like the safety pin in `subprojects/docket/src/docket/checks.py`
  ("safety-critical work starts at P0 or P1"). On the tier means
  `model.ranks_as_generator` (a sound `root-cause-of:` plus `generator: live`)
  or `model.ranks_as_generator_defect` (a sound `impairs-generators:`) - the
  second because the owner's 2026-09-19 rule gives a machinery defect "the same
  priority as a generator". It sits beside `_check_generator_defects` rather
  than `_check_generator_verdicts`, because the second entrance needs the
  configured `generator_paths` and only the first is handed them. Not pinned by
  this rule: spent heads (their own band, the 2026-09-21 ratified split),
  closed heads and unsound claims.
- **No exemption from the blocker rule** (decided at build, 2026-09-27).
  `_outranks_its_blocker` refuses a blocked `P1` waiting on an open `P2`, so a
  blocked head pinned at `P1` carries its item blockers up with it. That is the
  edge `plan.tier_standings` passes the tier's rank down, so the stored band
  follows `docket next` there as well; a chain past the first edge is raised by
  that rule as it is for every `P1`, which is the rule's existing reach rather
  than the pin's.
- `docket set`: a write that leaves an item on the tier below `P1` and names no
  `priority` raises it to `P1` in the same write and prints the change, so
  recording `generator: live` needs no second command. The raise takes no
  `--overwrite`: the band it replaces is the rule's to replace, and the line it
  prints says so. An explicit `--priority P2` or `P3` on a tier item is refused
  with the check's own error instead, since a value somebody asked for is never
  silently replaced. Where the raise would add another error - a blocked head
  whose blocker sits below `P1` - the write is refused with that error, which
  names the blocker to raise first; `set` writes one item.
- A head that turns `spent` while still open keeps `P1` until lowered by hand.
  Rare: all 30 spent heads were closed on 2026-09-27.

**Checked before building, 2026-09-27.** No open item carries `generator:
live` or `impairs-generators:` - `PL-927J`, the last live head, closed done and
spent in #1160 - so the pin fires on nothing in the store today and no band in
it has to move.

**Docs to sweep.**
- `.claude/skills/docket/modes/picking.md`, at "Do not promote process work
  into P1": the carve-out, and why it is not promotion.
- `subprojects/docket/README.md`: "the top band is product work by
  construction" stops being true as written; the paragraph opening "`generator`
  is the second half" gains the pin.
- `.claude/skills/docket/modes/triage.md`, where a head's `misread:` is written
  "beside the `root-cause-of:` and the `generator:`": say the band follows on
  its own.
- No `CLAUDE.md` edit: a check enforces it, which is the cheapest disposition.

**Tests** (`subprojects/docket/tests/`): a live head at `P2` and at `P3`
refused; `P0` and `P1` pass; spent at `P2` passes; closed and live at `P2`
passes; an unsound `root-cause-of:` at `P2` passes; a sound
`impairs-generators:` at `P3` refused; `set` recording `generator: live` on a
`P2` item leaves it at `P1` and says so; `set` asking for `--priority P2` on a
live head is refused and writes nothing; `set` recording `generator: live` on a
blocked head whose blocker is at `P2` is refused, naming the blocker.

**Done when.** `docket check` refuses an open item on the generator tier below
`P1`, `docket set` raises one on write, the documents above say so, and `make
check` is green.

The new-mechanism pause ended when #1160 closed `PL-927J`, the last open item
carrying `generator: live`. This is the machinery that ranks generators, which
the pause exempts anyway, and the owner's request would lift it (`PL-6Q9L`).
