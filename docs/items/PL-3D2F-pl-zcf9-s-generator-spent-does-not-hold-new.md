---
id: PL-3D2F
title: PL-ZCF9's 'generator: spent' does not hold: new phrasings in its own four contexts were refused 14 times in 18, and 20 of 33 unlisted asks passed, so the owner-ask guard is still a wording gate under PL-GPJ7
status: untriaged
feature: owner-ask-by-state
added: 2026-11-03
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
