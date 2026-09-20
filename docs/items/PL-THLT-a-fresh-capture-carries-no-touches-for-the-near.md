---
id: PL-THLT
title: A fresh capture carries no touches for the near-duplicate search to key on, so bin/docket new infers candidate paths from the working tree's own uncommitted and branch-local changes - the gap PL-0KQP fell straight through
priority: P2
effort: S
status: done
classes: infra
feature: recurrence-signal
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/README.md, subprojects/docket/tests
added: 2026-09-20
closed: 2026-09-20
payoff: closes the hole the fifth capture of the suppression defect fell through - a fresh capture has no touches, so the only key that works reads nothing
verify: grep -q 'def test_new_infers_candidate_paths_from_the_working_tree' subprojects/docket/tests/test_cli.py
---

**Problem.** A fresh capture carries no `touches` for the near-duplicate search
to key on, so `bin/docket new` infers candidate paths from the working tree's
own uncommitted and branch-local changes - the gap `PL-0KQP` fell straight
through.

**Why it matters.** The shared-path key is the only one that works - title
similarity catches 0 of 13 known duplicate pairs at any usable threshold
(`PL-TZ7T`) - and a fresh capture is exactly the moment it has nothing to read.
So without this, the detection mechanism is blind precisely where a duplicate is
being created, which is the only moment it can be stopped cheaply.

**Where it comes from, measured 2026-09-20.** Of thirteen known duplicate pairs,
nine share a declared `touches` path and the shared-path key finds them. **All
four misses are `PL-0KQP`**, the fifth capture of the suppression-check defect:
`bin/docket new` writes `status: untriaged` and no `touches`, so the item that
most needed the warning was the one carrying nothing to match on.

**Why the working tree answers it.** The session that filed `PL-0KQP` was on
`origin/claude/nice-wright-cjo9ve`, whose commits touch
`subprojects/docket/src/docket/verify.py` - the exact path all four items it
duplicates declare. The information was present; nothing read it. A capture is
made *while* working on the thing that produced it, which is what makes the
working tree a good proxy for a `touches` the item does not have yet.

**Constraint that shapes it.** The capture rule is deliberately unconditional
and cheap - "`bin/docket new` is the whole procedure". So this may not prompt,
may not refuse, and may not require the session to pass anything. It reads what
git already knows, and where git says nothing the search falls back to title
rank alone and the command behaves as it does today.

**Done when** a capture filed on a branch whose changes touch a path is matched
against the open items declaring that path, with no new argument required of the
session.

**Built 2026-09-20.** `vcs.working_paths` reads three things and unions them:
the branch's own commits (`base...HEAD`, three-dot for the reason
`files_in_flight` gives), the uncommitted tracked changes (`diff --name-only
HEAD`), and the untracked files (`ls-files --others --exclude-standard`). Three
reads rather than one `status --porcelain`, because the porcelain format carries
status codes, rename arrows and shell-quoted paths with spaces, and each of
these prints one path per line and nothing else. It declines like every other
read in that module, so an unanswered git is not reported as a clean tree.

`bin/docket new` uses it only where the capture declares no `--touches`, reads it
once per invocation rather than once per title, and honours `--no-git`. No
prompt, no refusal, no new argument: where git answers nothing the search has no
key and the command behaves exactly as it did before. The warning says which key
it used - "a path this branch is changing" rather than "a path this capture
reaches" - because what a session declared and what it happened to be editing
are different claims and a reader cannot weigh a wrong match without being told
which one selected it.

**Excluding the store was considered and refused.** Every session edits
`docs/items/`, so reading it as noise is tempting - but 28 of the 341 open items
declare a path under it, and they are the triage passes, backfills and
queue-shape decisions a capture *about* the queue genuinely duplicates. Two open
triage items is exactly the warning worth having, and the recurring-by-design
clusters are already dropped by scoring open items alone, which is where that
job belongs.

**Verified against this branch rather than only against a fixture.** A capture
titled "docket verify's suppression check reads prose in a release note as if it
were code", filed with no `--touches` from the branch that built this, read 26
working-tree paths and named `PL-5MFL` (0.421), `PL-BHBZ` (0.242) and `PL-STC4`
(0.240) - all three open members of the suppression cluster, correctly ordered.
Eight of the 26 paths were `docs/items/` files this session had edited, and none
of them produced a candidate, because the title floor filtered them.
