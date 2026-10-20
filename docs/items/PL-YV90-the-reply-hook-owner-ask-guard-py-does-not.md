---
id: PL-YV90
title: The reply hook owner_ask_guard.py does not check the coordinator's project-chat posts, because bin/docket arm judges only the checkout's own branch; checking them needs arm to answer for a named pull request
priority: P3
effort: M
status: needs-decision
classes: defect
feature: review-hold
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py, subprojects/docket/src/docket/arming.py
added: 2026-10-19
reenters: PL-TLPH
---

**Problem.** The reply hook owner_ask_guard.py does not check the coordinator's project-chat posts, because bin/docket arm judges only the checkout's own branch; checking them needs arm to answer for a named pull request

**What happened.** `PL-TLPH` (#1688) added `.claude/hooks/owner_ask_guard.py`,
which refuses a thread's reply, message edit or decision card that asks the
owner to read or merge a pull request, unless the message carries the ask
that `bin/docket arm --owner-ask` prints. It is not wired on the coordinator's
`mcp__hearthbot__post_message`. The coordinator relays thread asks to the owner
in the project chat, so a bare "read #N" can still reach the owner from there.

**Why it was left out.** `arming.arm` judges `HEAD`: the branch name, the
remote copy of that branch, the claims on it and the `base...HEAD` diff. The
coordinator's checkout is on no pull request's branch, so `arm` has nothing
to answer for there. The hook would also have to learn which pull request a
post names, and a post can name several.

**A route, not yet weighed.** Give `arm` a way to answer for a named pull
request: fetch its head into a temporary worktree on a branch of the same name
and run the same verdict there, then let the hook check each `#N` a post names.
The cost is a fetch and a worktree per post, several seconds each. A cheaper
partial check is to refuse a coordinator ask that carries no line in the
rendered Owner-ask form at all, without proving it is the recorded one.

**Why it matters.** The coordinator relays thread asks to the owner. A bare "read #N" sent from there spends the owner's attention exactly as one sent from a thread does, and the guard was built to stop that.

**Decision needed.** Which route to take: make `arm` answer for a named pull request, at the cost of a fetch and a worktree per post, or the cheaper partial check.

**Recommended:** the cheaper partial check first. Refuse a coordinator post that asks for a read or merge but carries no line in the rendered `Owner-ask:` form. It closes the observed failure, a bare ask, with no fetch. Build the named-pull-request route only if a coordinator post is seen carrying a wrong recorded line.

**Done when.** The hook is wired on the coordinator's post tool, a bare ask from it is refused, a post carrying the form passes, and a test pins both.

**Generator check.** An instance of `PL-TLPH`'s fact, "whether the owner may be sent a read or merge ask about a pull request", a gap left at that head's close on 2026-10-19. Recorded as `reenters: PL-TLPH`.
