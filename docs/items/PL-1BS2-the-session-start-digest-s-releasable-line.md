---
id: PL-1BS2
title: The session-start digest's Releasable line reads readiness without the interrupted-cut resume, so during an unfinished cut it reports the short remainder with nothing saying why
priority: P2
effort: S
status: ready
classes: defect, infra
feature: release-process
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
added: 2026-09-13
verify: grep -rq 'def test_the_digest_names_an_interrupted_cut_behind_the_releasable_line' subprojects/docket/tests/ && uv run pytest subprojects/docket/tests/test_cli.py -q
---

**Problem.** The session-start digest's Releasable line reads readiness without the interrupted-cut resume, so during an unfinished cut it reports the short remainder with nothing saying why

**Why it matters, and why the missing argument is not the bug.**
`release.py`'s `readiness()` takes `resuming` and its docstring says only
`cmd_release` supplies it, deliberately: "every other caller is asking what is
shippable *now*, and an interrupted cut's stamps are not that question." That
contract is right, and a session that starts here by threading `resuming` into
the digest has fixed the wrong half. The defect is the second half of the
title - the line reports the remainder with nothing saying why.

During an unfinished cut the already-stamped items drop out of `shippable`, so
`Releasable: N finished item(s) since <version>` counts only what the stopped
run never reached. The number is wrong in the direction that hides work rather
than inventing it, which is the harder direction to notice: a twenty-item cut
interrupted after fifteen reads as five, and every session opened in the
meantime sees a small, ordinary-looking release offer. `PL-1MKQ` is the same
state seen from `bin/docket check`, which does report it. The digest is what a
session reads *first*, and it is the one reading that stays silent.

**Done when.** The digest's `Releasable:` line names an interrupted cut where
one is open - the version being resumed, and that its notes were never written
- instead of presenting the remainder as an ordinary offer, with
`readiness()`'s contract left as it is. `bin/docket status` answers the same
way, and a test covers a store holding items stamped for a version whose notes
file is absent.
