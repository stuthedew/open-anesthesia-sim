---
id: PL-06JJ
title: Pin items on the generator tier to P1, so readers of the stored priority field - the queue dashboard among them - see what docket next already ranks: docket check refuses one below P1, and docket set raises it automatically
status: untriaged
added: 2026-09-27
---

**Problem.** Pin items on the generator tier to P1, so readers of the stored priority field - the queue dashboard among them - see what docket next already ranks: docket check refuses one below P1, and docket set raises it automatically

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
open head on 2026-09-27.

**Design.**
- `docket check`: an open item on the generator tier at `P2` or `P3` is an
  error, built like the safety pin in `subprojects/docket/src/docket/checks.py`
  ("safety-critical work starts at P0 or P1") and placed beside
  `_check_generator_verdicts`, which already holds `known`. On the tier means
  `model.ranks_as_generator` (a sound `root-cause-of:` plus `generator: live`)
  or `model.ranks_as_generator_defect` (a sound `impairs-generators:`) - the
  second because the owner's 2026-09-19 rule gives a machinery defect "the same
  priority as a generator". Not pinned: spent heads (their own band, the
  2026-09-21 ratified split), closed heads, unsound claims, and the blockers a
  blocked head lends its rank to.
- `docket set`: a write that leaves an item on the tier below `P1` raises it to
  `P1` in the same write and prints the change, so recording `generator: live`
  needs no second command. `cmd_set` in `subprojects/docket/src/docket/cli.py`;
  first see whether it already refuses writes `check` would fail, and reuse
  that path.
- A head that turns `spent` while still open keeps `P1` until lowered by hand.
  Rare: all 30 spent heads were closed on 2026-09-27.

**Check before building.**
- `subprojects/docket/README.md` says "a `P1` waiting on a `P2` is an error
  rather than a priority". Pinning a blocked head may turn its `P2` blocker
  into that error; decide whether the tier needs an exemption there.
- `PL-927J` (the only open head, live at `P2` on `main`) fails the new pin
  until pull request #1160, which marks it done and spent, merges. Bring
  `origin/main` in after that lands; do not edit `PL-927J` under its session's
  claim.
- List the open items carrying `impairs-generators:` and raise any below `P1`
  in this branch, declared in `touches`.

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
`P2` item leaves it at `P1` and says so.

**Done when.** `docket check` refuses an open item on the generator tier below
`P1`, `docket set` raises one on write, the documents above say so, and `make
check` is green.

The new-mechanism pause is in force while `PL-927J` carries `generator: live`
on `main`. This is the machinery that ranks generators, which the pause
exempts, and the owner's request lifts it regardless (`PL-6Q9L`).
