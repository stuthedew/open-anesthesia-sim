---
id: PL-WX87
title: bin/docket claim reads the clone's remote-tracking ref as the remote's copy of the branch, so on a session branch whose tracking ref the harness created at startup with nothing pushed, claim skips its push-at-once and says the branch is on the remote when ls-remote shows it is not
priority: P2
effort: S
status: done
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_claiming.py, .claude/skills/docket/modes/start.md
deferred-from: v0.6.0 - filed after the freeze by PL-NLXK's cut (2026-09-24), and not safety or science; a defect in PL-0TD9's claim writer, which merged after the freeze
added: 2026-09-24
closed: 2026-09-25
payoff: a claim written in a fresh session reaches the remote at once, which is the window claim's push-at-once exists to close
verify: grep -q "stale_tracking_ref" subprojects/docket/tests/test_claiming.py
---

**Problem.** bin/docket claim reads the clone's remote-tracking ref as the remote's copy of the branch, so on a session branch whose tracking ref the harness created at startup with nothing pushed, claim skips its push-at-once and says the branch is on the remote when ls-remote shows it is not

**What happened, 2026-09-24.** `PL-NLXK`'s session ran `bin/docket claim
PL-NLXK` on `claude/epic-faraday-f4yl2h`, a branch the harness created at
session start. `git ls-remote origin` listed no such branch, but the clone held
`refs/remotes/origin/claude/epic-faraday-f4yl2h` at `main`'s commit, its
reflog's one entry written at 06:57:47Z, five seconds after the session was
created, and by no fetch. `claim` printed "not pushed: the branch is on the
remote as origin/claude/epic-faraday-f4yl2h, so a pull request may be open on
it and armed", and the claim stayed in the checkout until the session pushed
it by hand.

**Why.** `claiming._publish` chooses between pushing and refusing on
`branch.upstream or _remote_copy(root, branch.name)`, and `_remote_copy` is
`git rev-parse --verify` of the clone's `refs/remotes/origin/` ref for the
branch. The fetch `claim` runs first does not prune, so a tracking ref the
remote no longer has, or never had, survives it and reads as the remote's
copy. The docstring's own rule - "the remote's copy decides, not the tracking
setting" - is right; the clone's tracking ref is simply not the remote's copy.

**Why it matters.** The failure is loud and safe: the message says the claim
was not pushed, and a push by hand is what it asks for. But the push-at-once is
the point of `claim` on a fresh branch - `PL-0HPV`'s session ran twenty minutes
before its first push, and another reported the item unstarted inside that
window (`PL-7TVT`). If every session in this environment starts with such a
ref, the push-at-once never fires on a fresh branch here, and the message tells
each session something false about the remote. Whether the harness writes the
ref for every session is not measured; two sessions showed it. The second was
`PL-DDYD`'s, on `claude/jolly-davinci-60g2iy`, 2026-09-24: its tracking ref's
reflog held one entry with an empty message at `main`'s commit, and the push
made by hand afterwards reported `[new branch]`.

**Remedies to weigh, none decided.** Ask the remote itself (`git ls-remote
--heads origin` for the branch), one round trip beside the fetch `claim`
already pays for; or fetch with `--prune` before reading, which also deletes
every other stale tracking ref in the clone. Either wants a real-git test in
`subprojects/docket/tests/test_claiming.py` whose clone holds a tracking ref
the remote does not have.

**Second observation, 2026-09-24.** `PL-J9S0`'s session hit it too, on
`claude/affectionate-feynman-h9m9tv`: the clone's
`refs/remotes/origin/claude/affectionate-feynman-h9m9tv` was written at
07:31:46Z, five seconds after the session was created, with an empty reflog
message and `main`'s commit; `branch.<name>.remote` and `.merge` were
configured; `claim` said "not pushed: the branch is on the remote"; and the
push by hand then reported `[new branch]`. Two sessions of two, so the harness
seeds the ref for every session here.

**Done when.** `bin/docket claim` on a branch the remote does not have
pushes the claim even where the clone holds a tracking ref for it, and says
the branch is on the remote only when the remote says so, with a real-git test
named for the stale tracking ref pinning it.

**Generator check.** An instance of `PL-4Q9B`'s fact, filed after that head
closed on 2026-09-19: "The remote's current refs and tags, and whether the
clone's local copies still match them". It is the first post-close instance on
record; three would count as a generator whose fix did not hold.

**Resolved, 2026-09-25: the remote is asked.** `claiming._on_remote` runs
`git ls-remote origin refs/heads/<branch>` and `_publish` decides on that
answer alone, so neither the tracking setting nor the clone's tracking ref
decides whether a claim is pushed; `_Branch.upstream`, read by nothing else, is
gone. `--prune` was the other remedy and was not taken: `vcs.fetch_remote`
refuses it deliberately, because a deleted branch's tracking ref can be the
only surviving copy of its work, which `stranded` exists to catch. The same
misreading sat in `_published`, the retry's test of whether the claim is
already on the remote: a branch the remote had deleted still read as carrying
the claim, so `claim` said "already holds it first; nothing written" of a
claim no other session could see. It now reads the remote's tip too. Where the
remote cannot be asked, nothing is pushed and the answer is `LOCAL_ONLY` with
git's words, rather than an "on the remote" nobody established. Reproduced
live at pickup: this session's own branch, `claude/eager-johnson-8v3qgw`, held
a tracking ref at `main`'s commit with no upstream configured, and `claim
PL-WX87` printed "not pushed: the branch is on the remote" while `git
ls-remote` listed nothing; the push by hand reported `[new branch]`. Three
sessions of three now.
