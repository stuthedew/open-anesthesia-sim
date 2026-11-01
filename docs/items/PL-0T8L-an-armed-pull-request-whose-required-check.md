---
id: PL-0T8L
title: An armed pull request whose required check failed is skipped by update-armed and flagged by nothing: #1845 sat red from 19:13 CDT on 2026-10-25 for about 24 hours after its session reported nothing needed from the owner, while bin/docket flight listed it only as 'open'
priority: P2
effort: S
status: done
classes: defect
touches: tools/open_pull_requests.py, tools/update_armed.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/config.py, subprojects/docket/README.md, docket.toml, docs/apparatus.md, tests/unit/test_open_pull_requests.py, tests/unit/test_update_armed.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.7.0 - captured after the freeze; an apparatus defect in the workflow lane, not safety or science
added: 2026-10-27
closed: 2026-11-01
pr: 1907
payoff: an approved pull request whose required check failed is named as failed where sessions look, instead of waiting a day while every report calls it open
verify: grep -q 'def test_flight_names_an_armed_pull_request_whose_required_check_failed' subprojects/docket/tests/test_vcs.py && grep -q 'def armed_failing' tools/open_pull_requests.py
reenters: PL-WNCT
---

**Problem.** An armed pull request whose required check failed is skipped by update-armed and flagged by nothing: #1845 sat red from 19:13 CDT on 2026-10-25 for about 24 hours after its session reported nothing needed from the owner, while bin/docket flight listed it only as 'open'

**Checked 2026-10-31.** `verdict` in `tools/update_armed.py` skips an armed pull request whose required check failed, and says so only in the workflow run's summary, which no session reads. `cmd_flight` in `subprojects/docket/src/docket/cli.py` reports the pull request's state and nothing about its checks. So the premise still holds.

**Why it matters.** An armed pull request is the project's promise that approved work will reach `main` without anyone acting. A required check that fails breaks that promise silently. The session has already told the owner that nothing needs them, and `bin/docket flight` and the session-start digest go on listing the pull request as open. #1845 waited about 24 hours that way, and nothing but chance would have found it sooner.

**Done when.** `bin/docket flight`, and the digest's in-flight line, name an armed pull request whose required check has failed on its head as failed, not merely open. A test pins the answer.

**Re-confirmed 2026-11-01: changed shape.** The problem is real, but the brief placed two things wrongly.

- `docket.vcs` does not own the GitHub API reads. The `docket` package knows nothing about GitHub and asks the forge through commands that `docket.toml` names. `tools/open_pull_requests.py` is the one GitHub client, and `tools/fact_home_check.py`'s `github-api` rule refuses a second one. So the reading goes there. The rule for "a required check's latest run on the head failed" moves there from `update_armed.py`'s `failed_checks`, and `update_armed.py` reads it back, so the two cannot disagree.
- The digest's in-flight line does not read the pull request report. It asks the forge nothing (`render.format_digest`, `PL-7TVT`) and sends the reader to `bin/docket flight` for each branch's pull request. So the digest now asks the forge this one question.

It is a question of its own, `armed_failing_command`, rather than more fields in `open_pull_requests_command`'s listing. The listing is also read by `claim` and `set --status done`. The extra reads cost about 0.9 s plus 0.35 s for each armed pull request (measured 2026-11-01). A timeout there would cost those commands the open-pull-request answer they act on. Only `flight` and the digest ask the new question. The digest speaks only when a check has failed, or when it could not ask.

**Generator check.** The fact misread is whether pushed branch work has an open pull request that will carry it to `main`, which `PL-WNCT`'s `misread:` states. Arming made "open and armed" stand for "will merge", and a red required check is the case that reading misses. So this is an instance of that head's fact, filed after the head closed on 2026-09-22.
