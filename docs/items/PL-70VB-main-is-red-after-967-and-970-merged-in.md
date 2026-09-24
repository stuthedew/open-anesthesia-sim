---
id: PL-70VB
title: main is red after #967 and #970 merged in sequence: #967 recorded PL-MB2W's v0.6.0 deferral as prose in the subsection #970 replaced, git merged the two cleanly, and bin/docket check fails PL-MB2W for owing a disposition - the third merge-skew instance within 30 days
priority: P2
effort: S
status: done
classes: defect, infra
feature: merge-skew
milestone: v0.5.9
touches: ROADMAP.md, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; housekeeping for main's red docket check
added: 2026-09-23
closed: 2026-09-23
pr: 971
payoff: main goes green again, so no open pull request fails CI on a disposition it never touched
verify: ! grep -q '^- PL-MB2W (M) - \*\*deferred' ROADMAP.md && grep -q '^deferred-from: v0.6.0' docs/items/PL-MB2W-who-holds-an-item-is-derived-by-every-reader.md
---

**Problem.** main is red after #967 and #970 merged in sequence: #967 recorded PL-MB2W's v0.6.0 deferral as prose in the subsection #970 replaced, git merged the two cleanly, and bin/docket check fails PL-MB2W for owing a disposition - the third merge-skew instance within 30 days

**Found 2026-09-23 on `main`.** `quality` run 2985 failed on `1d5b23b0` (#970's
squash), while run 2984 had passed on `5ec938fe` (#967's). Each pull request was
green on the base it was tested against. #967 added PL-MB2W's deferral as a
prose entry under v0.6.0's generator-head subsection. #970 replaced that
subsection with a pointer and made the disposition a `deferred-from:` field.
Git merged the two with no conflict, so the entry sits orphaned above
`### Required scope`, and `bin/docket check` fails PL-MB2W as open debt with no
disposition.

**Why it matters.** A red `main` fails every open pull request's next CI run on
a line none of them touched.

**Done when.** The orphaned prose entry is gone, PL-MB2W carries
`deferred-from: v0.6.0 - ...` like the other deferrals, and `bin/docket check`
reports 0 errors on the branch that lands it.

**Generator check.** A merge-skew instance, the mechanism `PL-Z0SM` records,
and the third in 30 days after `PL-33WM` and `PL-KH3Q`. That fires `PL-Z0SM`'s
ratified trigger, which `PL-6MW8` carries.

