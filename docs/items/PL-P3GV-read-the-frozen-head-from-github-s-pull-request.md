---
id: PL-P3GV
title: Read the frozen head from GitHub's pull-request record where refs/pull/<n>/head was deleted, so tools/left_behind_check.py answers #297-#386 instead of declining no such ref
status: dropped
classes: infra
feature: parallel-sessions
touches: tools/left_behind_check.py, tests/unit/test_left_behind_check.py
added: 2026-09-23
closed: 2026-09-23
reason: Nothing reaches the decline it would replace. On 2026-09-23 no branch on origin had its newest pull request in #297-#386 (0 of 13). No new pull request can be numbered into that closed range. A decline prints in the session-start digest, so it is never silent. Refile if 'no such ref' ever prints: the listing github_lookup already fetches carries head.sha, so the answer needs no new request.
---

**Problem.** Read the frozen head from GitHub's pull-request record where refs/pull/<n>/head was deleted, so tools/left_behind_check.py answers #297-#386 instead of declining no such ref

**Reproduced 2026-09-23: the mechanism is real.** `git ls-remote origin
'refs/pull/*/head'` resolves 843 of the numbers up to `#933`. The 90 missing
are exactly `#297`-`#386`, the range `PL-0SCG` asked GitHub to delete. The
pull-request record keeps the head after the ref goes. GitHub's API gives
`#312`'s `head.sha` as `7d1615f5`, while `ls-remote` returns nothing for
`refs/pull/312/head`. The listing request `github_lookup` already makes
carries `head.sha` in each entry. For `#793` it equals `refs/pull/793/head`
(`46620e20`). So the fix would add no request. `_pull_request` would read one
more key that it currently drops.

**The count says there is nothing for it to answer.** `python3
tools/left_behind_check.py --all` reads the 13 branches on `origin` besides
`main`, and none has its newest pull request in the range. Eleven have no pull
request at all. For the three whose tips this checkout had not fetched, that
comes from GitHub's listing. The other two map to `#793` and `#810`. Branches
came and went while this was counted, and the answer stayed the same.
Pull-request numbers only grow, and the 89 merges in the
range all landed between 2026-09-03 and 2026-09-06. So a branch can reach `no
such ref` only by being from that window and still carrying work past `main`,
or by being pushed again under its old name. If that happens it is not
silent: every decline prints in the session-start digest.

**Why it matters, and why it is not worth building.** The decline is the
honest answer where the frozen head cannot be read. It is what `PL-R808`
specified, so this is not a defect. Reading one more key from a response the
tool already holds is not a new command, check, field or rule either, so the
generator pause does not hold it. The count decides instead. The code would
replace a decline that fires on nothing today and can fire only on a closed,
three-week-old range, and it would bring a test and upkeep with it.

**Generator check.** A one-off. `PL-R808`'s build found this option and left
it unbuilt on purpose, and filed it in the commit that closed that head. No
other item shares its mechanism.
