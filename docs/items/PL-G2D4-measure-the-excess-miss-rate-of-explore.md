---
id: PL-G2D4
title: Measure the excess miss rate of Explore subagent search on Sonnet 5.5 and Haiku 5.5 against Opus 5.5 in one dedicated session, on thorough searches drawn from recent design rounds, before any cheaper Explore default is adopted: PL-2D28's third revision names the break-even lines (about 1 in 20 for Sonnet 5.5, 1 in 11 for Haiku 5.5) but decides on estimates and calls the measurement unaffordable, which its own cost table does not support
priority: P3
effort: L
status: dropped
classes: session-cost
feature: model-evidence
touches: docs/items/PL-G2D4-measure-the-excess-miss-rate-of-explore.md
blocked-by: v0.7.0
added: 2026-10-17
closed: 2026-10-19
reason: Neither arm can change a decision now. The owner stated on 2026-10-19 that neither a cheaper model nor a lower effort level is chosen to save cost, even at no cost. This trial's decision rules were cost break-evens, and 60 searches with no misses bound the excess miss rate below about 1 in 20, not at zero, so they cannot show a cheaper setting is no less correct.
payoff: the Explore subagent's model and effort are chosen on measured miss rates with bounds rather than on three multiplied estimates
verify: grep -qE '^[*][*]Measured on 2026-[0-9]{2}-[0-9]{2}' docs/items/PL-G2D4-*.md
not-delegable: the trial is one dedicated session that dispatches about 240 subagent searches and checks disputed leads against the source; a delegated worker cannot run it
---

**On hold** (project owner, 2026-10-19: "Actually, hold off on that. That
seems like a big can of warms right? With a lot of anaylsis?" and "Let's put a
pin in that and figure out where it goes when I do a roadmap update"). The
owner judged the trial too large an analysis to start now. Where it goes is
the owner's decision at their next roadmap update. Until then the item is
`blocked` on `v0.7.0`, so `bin/docket next`, `concurrent` and the workflow
batches do not offer it. The next roadmap update the docket can see is the
scoping round for v0.7.0. When that milestone is scoped, `bin/docket check`
reports that this item is ready to promote. The session that sees that report
puts the question of where it goes to the owner rather than promoting it. If
the owner updates the roadmap without scoping v0.7.0, nothing in the docket
fires, so the session doing that update has to raise this item itself.

**Problem.** Measure the excess miss rate of Explore subagent search on Sonnet 5.5 and Haiku 5.5 against Opus 5.5 in one dedicated session, on thorough searches drawn from recent design rounds, before any cheaper Explore default is adopted: PL-2D28's third revision names the break-even lines (about 1 in 20 for Sonnet 5.5, 1 in 11 for Haiku 5.5) but decides on estimates and calls the measurement unaffordable, which its own cost table does not support

**Why this item exists.** `PL-2D28`, the design round on which model
exploration subagents run on, revised its recommendation three times on
2026-10-17: Haiku 5.5, then Sonnet 5.5, then the session's own model. No
measurement was taken between the revisions. Each one multiplies three
estimates: the cheaper model's excess miss rate on a thorough search, the
share of misses that escape the deterministic checks, and the cost of an
escape. The sign of the product changes inside the error of those estimates,
and `PL-2D28` says so itself. The `model-evidence` feature's rule is that a
cheaper default is adopted only after a pre-registered trial, so this item is
that trial. Until it runs, the default stays where `PL-2D28` leaves it.

**Pre-registration.**

- *Lines to test*, taken from `PL-2D28`: Sonnet 5.5 pays as the Explore
  default only if its excess miss rate on thorough searches is below about
  1 in 20; Haiku 5.5 only if below about 1 in 11.
- *Sample size*, by the rule of three (Hanley JA, Lippman-Hand A. If nothing
  goes wrong, is everything all right? JAMA 1983;249(13):1743-1745): zero
  excess misses in n searches gives a 95% upper bound of about 3/n. To put
  Sonnet 5.5 under 1 in 20 with no excess miss observed needs n of about 60;
  Haiku 5.5 under 1 in 11 needs about 33. Run 60 thorough searches on each of
  the three models, so one trial answers both lines.
- *Questions*: thorough searches as sessions actually phrase them, drawn from
  recent design rounds and item briefs, such as "find every reader of X under
  `src/`". Not literal-string searches, which go to Grep and are exhaustive.
- *Reference set*: the union of leads returned across the three models. Each
  lead that only some models returned is checked against the source with one
  Read. An excess miss is a verified lead that Opus 5.5 returned and the
  cheaper model did not. Count the reverse too, a verified lead the cheaper
  model returned and Opus 5.5 did not, so Opus 5.5's own miss rate is measured
  rather than assumed to be zero.
- *Cost*, from `PL-2D28`'s table: a medium run is about $0.94 on Opus 5.5,
  $0.47 on Sonnet 5.5 and $0.027 on Haiku 5.5, so 60 runs on each is about
  $86 of subagent runs plus the trial session's own turns. `PL-2D28` puts the
  saving of a cheaper default at $0.67 to $1.30 per session for two runs, and
  at least eight sessions ran on 2026-10-17 (`list_sessions`), so the runs are
  repaid within two to three weeks. `PL-2D28` calls the measurement more than
  several months of the saving; its own figures do not support that.
- *Outcome*: the measured rates with their 95% bounds are written into this
  item and into `PL-2D28`, and into the evidence table `PL-3R6L` builds. The
  model review (`PL-63CB`) decides against the lines above. The Explore
  default does not change before the result.
- *Burden*: one dedicated session. No working session runs paired searches.

- *Effort arm*, added 2026-10-17 after `PL-2D28` recorded that effort sits
  on the same axis as the model: lower effort means fewer and terser tool
  calls, and for a search subagent fewer tool calls is fewer searches
  (platform effort page, https://platform.claude.com/docs/en/build-with-claude/effort,
  read by `PL-2D28` on 2026-10-17). Run the same 60 searches on Opus 5.5 at
  `medium`, its documented default, beside the `xhigh` runs the model arm
  already makes, so the arm costs at most about $56 more. Record both the
  saving per run, which `PL-2D28` could not price because the output-token
  term at `medium` is unmeasured, and the excess miss rate of `medium`
  against `xhigh`. The decision rule has the same break-even form as the
  model lines, computed from the measured saving: `medium` pays only if its
  excess miss rate is below the saving per run divided by the expected cost
  of an escape, which `PL-2D28` puts at about $35 at an escape rate of 3 in
  10. No `effort` line goes into the Explore file before the result.

**Done when.** The per-search records and the three models' excess miss rates
with their bounds, and the effort arm's, are recorded here, `PL-2D28` cites them, and the model
review has issued its decision on the Explore default.

**Note, 2026-10-19.** The model arm's decision rule no longer decides
anything. The owner stated that price never justifies a less correct model,
even at no cost (project owner, 2026-10-19; `docs/maintainer.md`). So the
break-even lines above cannot adopt Sonnet 5.5 or Haiku 5.5. The model arm
could matter only by showing a cheaper model is no less correct. Zero excess
misses in 60 searches bounds the excess rate below about 1 in 20, not at
zero, so this trial cannot show that. The effort arm is a separate question
that the owner's statement does not settle; it still stands as written.

**Generator check.** Not a member of a head. It follows from `PL-2D28`'s
design round deciding on estimates where a measurement was affordable.

**Why it matters.** The Explore default is used by most sessions, so a default
chosen on estimates either pays a miss rate nobody measured or forgoes a saving
nobody priced. The trial replaces three estimates with counts.
