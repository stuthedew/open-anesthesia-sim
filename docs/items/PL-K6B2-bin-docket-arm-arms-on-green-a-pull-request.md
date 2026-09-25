---
id: PL-K6B2
title: bin/docket arm arms on green a pull request whose every path is under docs/items/ or subprojects/docket/ except arming.py, and holds the rest for a read
priority: P1
effort: M
status: ready
classes: defect
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, docs/maintainer.md
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
payoff: the review hold fires only where a read matters, on simulator code, so the owner's read is spent where a wrong clinical value could land
verify: grep -q 'def test_arm_arms_a_docket_only_pull_request_on_green' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket arm arms on green a pull request whose every path is under docs/items/ or subprojects/docket/ except arming.py, and holds the rest for a read

`bin/docket arm` holds every pull request that changes a path outside `docs/items/`. The owner's answer of 2026-09-25 under `PL-SQTR` confirmed the hold is clicked through, so it fires on everything and delivers a read on nothing.

**Why it matters.** A hold that fires on every docket change teaches its reader to click through the one that matters, the hold on simulator code.

**Done when.** `arm` answers `arm` on green when every changed path is under `docs/items/` or `subprojects/docket/`, except `subprojects/docket/src/docket/arming.py`, so the gate cannot loosen itself. It answers `hold` for everything else, with a reason saying the pull request waits on a read. Tests in `subprojects/docket/tests/test_cli.py` hold both answers and the `arming.py` exception. `docs/maintainer.md` § "Read a simulator change before you arm it" is updated to the built rule.

**The pause.** This is a new rule in an existing check, which the generator pause holds. The owner's yes to `PL-SQTR`'s recommendation 2, on 2026-09-25, lifts it for this request (`PL-6Q9L`).

**Generator check.** A one-off, from `PL-SQTR`'s owner-raised finding: `arm` reads its paths correctly.
