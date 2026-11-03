---
id: PL-3D2F
title: PL-ZCF9's 'generator: spent' does not hold: new phrasings in its own four contexts were refused 14 times in 18, and 20 of 33 unlisted asks passed, so the owner-ask guard is still a wording gate under PL-GPJ7
priority: P1
effort: M
status: done
classes: defect
feature: owner-ask-by-state
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .claude/hooks/gate-status-guard.sh, docs/maintainer.md, docs/resident-instructions.md, tools/regex_baseline.py
added: 2026-11-03
closed: 2026-11-03
pr: 1984
payoff: an ask the owner gets is a recorded question, never a bare read or merge request or a made-up question, while progress notes still reach them unchecked
verify: ! grep -q 'def unasserted' .claude/hooks/owner_ask_guard.py && grep -q 'def test_a_waiting_threads_ask_is_refused_until_it_records_one' tests/unit/test_owner_ask_guard.py
reenters: PL-ZCF9
---

**Problem.** PL-ZCF9's 'generator: spent' does not hold: new phrasings in its own four contexts were refused 14 times in 18, and 20 of 33 unlisted asks passed, so the owner-ask guard is still a wording gate under PL-GPJ7

**Evidence, 2026-11-03.** A review session ran `owner_ask_guard.asked()` at `66fa48db` over two sets of messages that it wrote for the test. Set A held 51 messages: 33 asks and 18 messages that asked nothing. Twenty of the asks passed, for example "#1993 is green. Can you take a look and merge?" and "I need your sign-off on #1996 before I merge." Four of the non-asks were refused. Set B held 18 new phrasings in the four contexts that `PL-ZCF9` handles: quoted, negated, about a decision card, and foretold. Fourteen were refused, for example "Neither #1950 nor #1951 needs your read." and "I'll split this into two pull requests; each will need your read." Six of seven asks phrased so that an exemption covers them passed, for example "No doubt it needs your read before it merges." The messages were written with the patterns in view, so recall on real traffic is probably better than these counts show. `PL-ZCF9`'s own check of 110 real sentences picked them by the guard's ask words, so it could not count missed asks either.

**Why a reworded ask also passes.** A refusal tells the session to reword the message until it no longer reads as an ask. A session that really is asking can follow the same advice. A false refusal files an item, while a missed ask leaves no trace, so every fix since `PL-TLPH` has narrowed the guard.

**Decision needed.** The decision is whether the guard should keep recognising an ask by its wording.

**Recommendation:** key the refusal on the state that `arm` records, and stop matching wording. Whether the owner may be asked about a pull request is already a recorded fact, and `bin/docket arm --owner-ask` reads it exactly. The changes would be these:

1. Give `--owner-ask` its own exit code for "held for the owner's read, and no Owner-ask records what to ask". This is `PL-R1HT`.
2. In that state, refuse every owner-facing message from that checkout, whatever its wording. The way past the refusal is to record an `Owner-ask:` or an `Owner-read: not needed`. Rewording does not get past it.
3. With an ask recorded, keep the word-for-word check that the message carries the line. Run it on any message that names the pull request.
4. In every other state, keep the coordinator's form check, or make it an advisory.
5. Delete `unasserted` and the exemption patterns, about 150 lines.

The cost is a rewrite of the hook and its tests, about size M. `arm` would also run on every post, not only on matched ones, and it measured 2.2 s on a one-file branch and 28.4 s on a branch changing 62 simulator paths. So step 2 needs a fast path that reads only the trailers and the claims. The owner ratified the wording design in `PL-TLPH` and kept it in `PL-5HQY`. This evidence reopens that choice, so the choice goes back to the owner.

**Decided, 2026-11-03.** Key the refusal on the state that `arm` records, and delete the wording rules, as recommended above (project owner, 2026-11-03, ratified, over keeping the wording rules that `PL-TLPH` built and `PL-5HQY` kept). The owner's answer was "Yes". Build it together with `PL-R1HT`, whose distinct exit code it needs.

**Built 2026-11-03.** `.claude/hooks/owner_ask_guard.py` now asks `arm --owner-ask` before every Projects message and keys its check on the exit status that `PL-R1HT` made distinct:

1. Exit 3, held for the owner's read with no ask recorded: the ask is refused, and so is a question in the recorded form that no record backs (`PL-R1HT`'s reproduction).
2. Exit 0, an ask recorded: the ask must carry the recorded line word for word.
3. Any other status, or none: the coordinator's form check. The ask must carry a line in the recorded form.

The hook checks only an ask: a phrasing in `ASKS`, or a question in the form `arm --owner-ask` renders. Any other message goes through without `arm` being asked. A quoted, negated, foretold or card-bound ask phrasing is now refused, which `test_the_coordinators_check_reads_no_context_around_an_ask` pins.

`unasserted`, the quotation, negation, decision-card and foretelling patterns, and the `_RECORDED` exemptions are deleted. The hook went from 522 lines to 340. The refusal in the coordinator's check still tells a session to file an item when the refusal was wrong.

**The fast path.** `arming.arm(owner_ask=True)` reads only what decides `sendable` and `unasked`: the changed paths, the pinned tests, the `Owner-read` record, and then, only where the owner's read is held, the claims and the `Owner-ask` record. It never runs the prose, blind-review or auto-merge commands, and it counts no commits behind. It asks the forge whether the pull request merged only once the answer is a hold for the owner's read. Measured on 2026-11-03 with `--no-fetch`: 0.32 s against 1.6 s on this one-file branch, and on a scratch branch touching 62 simulator files, 0.26 s against 3.9 s where nothing was held and 1.55 s against 3.1 s where an `Owner-read: needed` record held it. The full answer there did not reach the 28.4 s measured above, because the prose and blind-review counts failed fast in that scratch worktree. `test_arm_owner_ask_reads_no_count_and_asks_the_forge_only_for_a_hold_for_the_read` checks that none of the three commands runs and that the forge is asked only in the held state.

**Owner's answer on the pull request, 2026-11-03.** The first build refused every message from a thread waiting on the owner's read, then every message naming a pull request. The owner rejected both: "Shouldn't be blocking progress updates and you shouldn't be asking me if it should. You should just fix. The goal was only to prevent it from asking me non-questions or asking me to generically review a PR, etc. shouldn't be catching unrelated stuff like progress updates" (project owner, 2026-11-03). A non-question, in the owner's word, is an ask that carries no recorded question: a bare request to read, merge or review a pull request, or a question written into the message when no `Owner-ask` record backs it. A recorded question is the decision or review line that `bin/docket arm --owner-ask` prints (agreed with the owner in the same conversation). So the hook checks only a message that asks, and the state decides what that ask needs. The ask phrasings in `ASKS` still find the ask, with no context rules, so the wording gate this item set out to remove survives in its finding half. A phrase in a sentence that asks nothing is still refused, and the refusal still files an item. A state that tells the hook which messages are progress notes would need a record a thread writes on purpose, and none exists.

**Generator check.** This re-enters `PL-ZCF9`, and through it the fact `PL-GPJ7` names: whether a sentence makes the claim that a gate checks, when the gate recognises it by wording. This change stops reading wording wherever `arm` records the answer. Wording is still read in the coordinator's check, because `arm` cannot answer for a named pull request (project owner, 2026-10-24, ratified, over building that). A wrong refusal there still files an item titled "owner_ask_guard.py refused a message that asked for nothing", so a recurrence will show in the store as items with that title.
