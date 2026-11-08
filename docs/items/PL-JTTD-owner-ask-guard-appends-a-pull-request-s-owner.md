---
id: PL-JTTD
title: owner_ask_guard appends a pull request's Owner-ask line to every thread message and edit while the checkout's branch holds an Owner-read record, including after the owner has said Merge, so replies on #2022 (2026-11-04, 17:19-17:25Z) repeated an ask he had already answered; it stops only once the pull request merges
priority: P2
effort: S
status: ready
classes: defect
feature: owner-ask-by-state
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.7.0 - a new problem: owner_ask_guard began appending to every thread message with a4f1c1f5 (2026-11-04), after the freeze
added: 2026-11-04
payoff: after the owner says merge, thread messages stop repeating the read or merge ask he has already answered
verify: grep -q 'def test_arm_owner_ask_sends_nothing_once_the_owner_has_answered' subprojects/docket/tests/test_cli.py
reenters: PL-X4MD
---

**Problem.** owner_ask_guard appends a pull request's Owner-ask line to every thread message and edit while the checkout's branch holds an Owner-read record, including after the owner has said Merge, so replies on #2022 (2026-11-04, 17:19-17:25Z) repeated an ask he had already answered; it stops only once the pull request merges

**Observed 2026-11-04.** Stuart said "Merge" on #2022 at 17:18:58Z, and the thread armed auto-merge at 17:19Z. Three later messages in the thread "Finish the copy editor items", one of them an edit made to remove the line, came back with the Owner-ask line appended (`PL-X4MD`). Stuart then asked "Didn't I say merge already?" The guard keys on the branch's commit records, which cannot hold the owner's word, so it has no way to see that the ask was answered. The lines were removed only after the merge deleted the branch. A fix needs some record of the answer that the guard can read, such as the pull request being armed after the hold.

**Read at triage, 2026-11-04.** `decide` in `.claude/hooks/owner_ask_guard.py`
appends `recorded_line`, which is the first line of `bin/docket arm --no-fetch
--owner-ask` when it exits 0 or with `NO_ASK`. Neither reads whether the pull
request was armed after its hold. The only state that ends the line is a merge,
which `test_arm_owner_ask_sends_nothing_for_a_held_pull_request_that_has_merged`
in `subprojects/docket/tests/test_cli.py` covers.

**Why it matters.** The owner is asked again for a decision he has already
given, on every message until the merge. With CI taking about 16 minutes, that
can be several messages. A line that repeats after it has been answered teaches
the reader to skip it, and on a pull request that really waits on him, it is
the one line he must act on.

**Done when.** Once the pull request has been armed after its hold, or the
guard can read some other record of the owner's answer, `bin/docket arm
--owner-ask` prints nothing to send, so the guard appends nothing. A test pins
that case beside the merged one.

**Generator check.** The fact is `PL-TLPH`'s: whether the owner may be sent a
read or merge ask about a pull request. This is a re-entry of `PL-X4MD`, closed
on 2026-11-04. That item made the guard append the line to every message about
a waiting pull request, and the append should have stopped once the owner
answered. It is recorded against `PL-X4MD` and not `PL-TLPH`, because
`PL-TLPH`'s fix, refusing an ask that lacks the recorded line, held here.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem began after Gate 3 froze at `817a4d88`, so the item stays deferred to the next gate, and its `deferred-from:` names the commit that began it. `owner_ask_guard.py` existed at `817a4d88` but appended nothing. The append came with `a4f1c1f5` (2026-11-04).
