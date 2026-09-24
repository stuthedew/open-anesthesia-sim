---
id: PL-MLR4
title: PL-L4YG's slug-from-title mechanism was judged live, 3 skeptics of 3, by PL-T7Y1's audit, with nine members no head lists, and no record names the nine, so no open item can carry it: name them and record the head
priority: P2
effort: M
status: ready
classes: housekeeping
feature: generator-identification
touches: docs/items
added: 2026-09-23
payoff: the slug-from-title mechanism three auditors judged live is either ranked as a generator or recorded as too small to be one, instead of ranking nowhere
verify: grep -q '^root-cause-of: ' docs/items/PL-MLR4-*.md
---

**Problem.** PL-L4YG's slug-from-title mechanism was judged live, 3 skeptics of 3, by PL-T7Y1's audit, with nine members no head lists, and no record names the nine, so no open item can carry it: name them and record the head

**Evidence.** `PL-5MYR`, under "Verified counts (PL-T7Y1", on #969's branch,
reports that `PL-L4YG` has nine members it does not list and no verdict, and
that three skeptics of three judged it live. No record names the nine. Writing
`live` on the closed head would leave it ranking nowhere, which is what
`PL-TH9K` removed. So the verdict waits on a carrier: an open item whose
`root-cause-of:` names the nine.

**Generator check.** This is bookkeeping for an existing head, not a new
mechanism. This session's own work produced three instances: `PL-MB2W`'s
title was rewritten twice, and each rewrite needed a `git mv` that `docket
check` asked for.

**What triage found, 2026-09-24.** The nine ids cannot be recovered from the
repository. `PL-5MYR` says only "`PL-L4YG` (slug from the title): 9 unlisted,
no verdict, judged live 3 of 3". No commit on any ref lists them
(`git log --all -S'PL-L4YG'`), and `PL-T7Y1`'s audit output lived outside the
tree. So the pool has to be rebuilt from briefs. A title search gives leads,
not members, and each still needs its brief read. `PL-3833`, `PL-D4GS`,
`PL-Y5JX`, `PL-3GKR` and `PL-9KSY` are listed by no head. `PL-5QLP` and
`PL-QMC0` sit under `PL-TZ7T`, `PL-JF5Z` under `PL-WNCT`, `PL-J16N` under
`PL-MB2W`, `PL-S5LB` under `PL-HMZZ` and `PL-HX5C` under `PL-7TVT`. A lead
already under another head is a member with two causes, or a misattribution,
and the brief says which. `PL-L4YG`'s own "nine item files" is `PL-YTDN`'s and
is a different nine.

**Done when.** `PL-MLR4` carries `root-cause-of:` naming the members the briefs
bear out, `misread:` in `PL-L4YG`'s words, and a `generator:` verdict. The other
ending is that it closes with a reason saying the pool holds fewer than three.
