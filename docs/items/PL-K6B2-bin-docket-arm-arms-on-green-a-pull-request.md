---
id: PL-K6B2
title: bin/docket arm arms on green a pull request whose every path is under docs/items/ or subprojects/docket/ except arming.py, and holds the rest for a read
priority: P1
effort: M
status: done
classes: defect
feature: review-hold
milestone: v0.5.12
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, docs/maintainer.md, docs/items/PL-0JGZ-does-a-branch-change-only-the-queue-has-two.md
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
closed: 2026-09-25
pr: 1031
payoff: the review hold fires only where a read matters, on simulator code, so the owner's read is spent where a wrong clinical value could land
verify: grep -q 'def test_arm_arms_a_docket_only_pull_request_on_green' subprojects/docket/tests/test_cli.py
recurrences: 2026-09-25 PL-WW0Q
---

**Problem.** bin/docket arm arms on green a pull request whose every path is under docs/items/ or subprojects/docket/ except arming.py, and holds the rest for a read

`bin/docket arm` holds every pull request that changes a path outside `docs/items/`. The owner's answer of 2026-09-25 under `PL-SQTR` confirmed the hold is clicked through, so it fires on everything and delivers a read on nothing.

**Why it matters.** A hold that fires on every docket change teaches its reader to click through the one that matters, the hold on simulator code.

**Done when.** `arm` answers `arm` on green when every changed path is under `docs/items/` or `subprojects/docket/`, except `subprojects/docket/src/docket/arming.py`, so the gate cannot loosen itself. It answers `hold` for everything else, with a reason saying the pull request waits on a read. Tests in `subprojects/docket/tests/test_cli.py` hold both answers and the `arming.py` exception. `docs/maintainer.md` § "Read a simulator change before you arm it" is updated to the built rule.

**The pause.** This is a new rule in an existing check, which the generator pause holds. The owner's yes to `PL-SQTR`'s recommendation 2, on 2026-09-25, lifts it for this request (`PL-6Q9L`).

**Generator check.** A one-off, from `PL-SQTR`'s owner-raised finding: `arm` reads its paths correctly.

**Worked.** The tooling's path and the gate's are module constants in `arming.py`, `TOOLING` and `GATE`, because `touches` reach neither `config.py` nor `docket.toml`; `claims.CUTOVER_MARKER` is the precedent, and `test_the_gate_arm_holds_for_a_read_is_the_module_that_decides_the_answer` pins `GATE` to the module's real path, as `test_claims` pins the marker. `PL-QFCR` records that a `docket.toml` field is where the package keeps layout. `Verdict` gains a `gate` field, so the hold names the gate as its own reason ("it changes subprojects/docket/src/docket/arming.py, the gate itself") rather than counting it among the paths outside the tooling, which it is not. The hold line now ends ", so its pull request waits on a read" wherever a path or the gate holds it, and the `arm` line reads "changes nothing outside docs/items and subprojects/docket, leaves arming.py alone"; both keep the prefixes the existing tests assert. The paths the hold test is parametrized over are my choice: five simulator paths, `CLAUDE.md`, and `subprojects/docketeer/`, a sibling sharing the tooling's letters. The gate test also moves the module, which reads as its deletion under `--no-renames`. One existing test's docstring changed its "merges on review" to "waits on a read"; no assertion changed. The exception covers `arming.py` alone, as the brief says, though the answer is read through `vcs.py`, `claims.py` and `cli.cmd_arm` too, which arm on green: `PL-WW0Q`.
