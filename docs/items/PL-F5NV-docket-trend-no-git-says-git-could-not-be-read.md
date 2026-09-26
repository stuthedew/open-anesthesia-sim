---
id: PL-F5NV
title: docket trend --no-git says git could not be read where it was not asked, and anchors its windows at the first closure rather than the first commit, so the item columns re-bucket under the flag - the two residuals of dropped PL-RCL9
priority: P3
effort: S
status: done
classes: defect
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/trend.py, subprojects/docket/tests/test_trend.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-23 triage pass
added: 2026-09-23
closed: 2026-09-26
pr: 1051
payoff: a --no-git trend says truthfully why churn is missing and why its weeks differ from an ordinary run
verify: grep -q 'def test_no_git_says_churn_was_not_asked_for' subprojects/docket/tests/test_trend.py && grep -q 'def test_no_git_names_the_day_its_windows_are_anchored_at' subprojects/docket/tests/test_trend.py
recurrences: 2026-09-26 PL-PWH6
---

**Problem.** docket trend --no-git says git could not be read where it was not asked, and anchors its windows at the first closure rather than the first commit, so the item columns re-bucket under the flag - the two residuals of dropped PL-RCL9

**Reproduced at triage, 2026-09-23.** `bin/docket trend --no-git` ends its key
with "churn not shown: git could not be read in this checkout", where the flag
told it not to read git. Its first window is `2026-08-24..08-30` where
`bin/docket trend` starts at `2026-08-21..08-27`, the first commit, so every
item column is bucketed differently under the flag and nothing says why. The
earliest `added:` in the store is 2026-08-23, so no store-only anchor reproduces
git's either.

**Why it matters.** A reader comparing a `--no-git` run with an ordinary one
sees different weekly counts for the same closures and a reason that is false;
the flag exists for bare checkouts and CI, where that comparison is the point.

**Done when.** Under `--no-git` the key says churn was not asked for rather than
that git could not be read, and names the day its windows are anchored at and
why that differs from an ordinary run, pinned in `test_trend.py`.

**Generator check.** One-off, the two residuals `PL-RCL9` named when it was
dropped: `has_churn` is one boolean for two causes, and the key was written when
only a failed read could set it False. The same shape as `PL-27VL`, but two
instances in different subsystems share no function.

**Worked.** The cause is read from `Churn.declined`: `cmd_trend`, outside this
item's `touches`, hands `--no-git` a bare `Churn()` and says nothing else, so
empty and undeclined reads as not asked. A history git answered with no line
counts reads the same way; `PL-PWH6` holds that residual and the `test_cli.py`
trend test now named for the other cause. `Trend.has_churn` became a property
over a new `churn_reading`, with `anchor` beside it, and `format_trend` treats a
missing anchor as no history, which is the same condition as no periods. The key
names its anchor day on every run, not only under `--no-git`, and an ordinary
run calls it "the first day that changed a line or closed an item", because
`_first_day` reads days with line counts rather than every commit. A daily
`--no-git` run carries no re-bucketing caveat, since a day is a day whatever it
is counted from. The two named tests run end to end through `cli.main` with
`--no-git`, via a two-closure store the `_no_git_trend` helper writes, so a
change to what `cmd_trend` passes under the flag fails them; a third, unit-level
test pins that a declined reading still says "could not be read", so the two
causes cannot collapse into one wording.
