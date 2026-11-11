---
id: PL-694Q
title: ROADMAP.md's v0.5.0 section claims wave 'still prints all thirteen as waiting on work outside it', which it no longer does
priority: P3
effort: S
status: done
classes: docs
milestone: v0.6.17
touches: ROADMAP.md
added: 2026-09-20
closed: 2026-11-09
pr: 2071
payoff: stops the v0.5.0 section telling a session to expect output the command does not produce
verify: ! grep -qF 'still prints all thirteen as' ROADMAP.md
---

**Problem.** ROADMAP.md's v0.5.0 section claims wave 'still prints all thirteen as waiting on work outside it', which it no longer does

**Why it matters.** The paragraph is written to stop a later session "fixing"
the count to agree with the prose, and that instruction is still worth having.
Its evidence is not. Two things have moved under it, and only the first is
`PL-FCM3`'s doing:

- The quoted string changed. `bin/docket wave` now prints `N waiting on M open
  items outside it`, so a session checking the claim against the command finds
  neither the wording nor a count it can match.
- The thirteen are no longer reported that way at all, which predates
  `PL-FCM3`. Measured 2026-09-20: the gate reads `173 cleared, 5 open` with all
  five clearable and no `blocked outside the gate` line, because `PL-FG9D` and
  `PL-4DCG` have closed - so `PL-8PS6` and `PL-WZVZ`, two of the thirteen the
  paragraph names, now have no open blocker at all. `make check` raises them as
  ready to promote on the same reading.

A session reading the section today is told to expect an output the command
does not produce, and given a reason that no longer holds. That is worse than
silence: the paragraph reads as a live verdict and cannot be checked.

**What it is not.** Not an argument for changing the count. `PL-FCM3` deliberately
left membership alone; what the section says about the port's sequencing may
well still be the right reading. This is about the sentence, not the decision.

**The gate has moved again since this was filed, which is the point.** Read
2026-09-20, `bin/docket wave` prints `178 cleared, 3 open` - not the
`173 cleared, 5 open` recorded above, and not the thirteen the paragraph
names. Two readings hours apart disagree, which is exactly why the paragraph
needs a date on its reading rather than a fresh count: any number written into
prose here is stale by the next merge, and `bin/docket wave` is the only thing
that can answer it live.

**Done when.** The paragraph quotes what `bin/docket wave` prints for those
entries with the date its reading was taken, cites this item, and drops the
quoted string the command no longer produces. A session can then check the
claim against the command rather than against prose. Do not replace it with a
fresh count stated as standing fact, because that is the same defect one merge
later.

**Done 2026-11-09, by `PL-G6DP`.** On 2026-11-07 that item's restructure of `ROADMAP.md` moved the paragraph into `PL-SL70`'s brief, which quotes it as the text the roadmap carried until then. `ROADMAP.md` no longer tells a session to expect that output. The `verify:` command was rewritten to test only that the string is gone, because the paragraph it required to be dated no longer exists.
