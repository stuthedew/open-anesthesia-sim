---
id: PL-0T8L
title: An armed pull request whose required check failed is skipped by update-armed and flagged by nothing: #1845 sat red from 19:13 CDT on 2026-10-25 for about 24 hours after its session reported nothing needed from the owner, while bin/docket flight listed it only as 'open'
priority: P2
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_claims.py
deferred-from: v0.7.0 - captured after the freeze; an apparatus defect in the workflow lane, not safety or science
added: 2026-10-27
payoff: an approved pull request whose required check failed is named as failed where sessions look, instead of waiting a day while every report calls it open
verify: grep -q 'def test_flight_names_an_armed_pull_request_whose_required_check_failed' subprojects/docket/tests/test_claims.py
reenters: PL-WNCT
---

**Problem.** An armed pull request whose required check failed is skipped by update-armed and flagged by nothing: #1845 sat red from 19:13 CDT on 2026-10-25 for about 24 hours after its session reported nothing needed from the owner, while bin/docket flight listed it only as 'open'

**Checked 2026-10-31.** `verdict` in `tools/update_armed.py` skips an armed pull request whose required check failed, and says so only in the workflow run's summary, which no session reads. `cmd_flight` in `subprojects/docket/src/docket/cli.py` reports the pull request's state and nothing about its checks. So the premise still holds.

**Why it matters.** An armed pull request is the project's promise that approved work will reach `main` without anyone acting. A required check that fails breaks that promise silently. The session has already told the owner that nothing needs them, and `bin/docket flight` and the session-start digest go on listing the pull request as open. #1845 waited about 24 hours that way, and nothing but chance would have found it sooner.

**Done when.** `bin/docket flight`, and the digest's in-flight line that reads the same report, name an armed pull request whose required check has failed on its head as failed, not merely open. The read of the check runs stays in `docket.vcs`, which owns the GitHub API reads. A test pins the answer.

**Generator check.** The fact misread is whether pushed branch work has an open pull request that will carry it to `main`, which `PL-WNCT`'s `misread:` states. Arming made "open and armed" stand for "will merge", and a red required check is the case that reading misses. So this is an instance of that head's fact, filed after the head closed on 2026-09-22.
