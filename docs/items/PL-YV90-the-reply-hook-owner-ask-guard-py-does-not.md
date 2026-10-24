---
id: PL-YV90
title: The reply hook owner_ask_guard.py does not check the coordinator's project-chat posts, because bin/docket arm judges only the checkout's own branch; checking them needs arm to answer for a named pull request
priority: P3
effort: M
status: done
classes: defect
feature: review-hold
milestone: v0.6.2
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py, subprojects/docket/src/docket/arming.py, .claude/settings.json, subprojects/docket/tests/test_arming.py, docs/maintainer.md, docs/resident-instructions.md, subprojects/docket/tests/test_portability.py
added: 2026-10-19
closed: 2026-10-24
pr: 1721
payoff: a bare read or merge ask relayed by the coordinator is refused before it reaches the owner, as one from a thread already is
verify: grep -q 'def renders_owner_ask' subprojects/docket/src/docket/arming.py && grep -q 'ask_decision|post_message' .claude/settings.json
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

**Decided 2026-10-24: the cheaper partial check** (project owner, 2026-10-24, ratified, over making `bin/docket arm` answer for a named pull request with a fetch and a temporary worktree per post). The owner's words: "Whatever route we won't regret implementing down the road. Don't need to over complicate but don't cut corners either. Make sure to consider YAGNI". The route itself was left to the session, and the coordinator chose it. The named-pull-request route guards against a failure nobody has seen, a well-formed but wrong line, and it costs several seconds per post, so YAGNI says not yet. Nothing built now is undone later, because the cheap check becomes that route's first stage. One point is not cut: the hook writes no second regex for the rendered form. `parse_owner_ask` in `subprojects/docket/src/docket/arming.py` renders the line from named constants, and a recognizer beside it, built from the same constants, is what the hook imports.

**Done when.** The hook is wired on the coordinator's post tool, a bare ask from it is refused, a post carrying the form passes, and a test pins both. The form is recognized by `arming.renders_owner_ask`, built from the constants `parse_owner_ask` renders with, and a test pins the round trip between the two.

**Generator check.** An instance of `PL-TLPH`'s fact, "whether the owner may be sent a read or merge ask about a pull request", a gap left at that head's close on 2026-10-19. Recorded as `reenters: PL-TLPH`.

**Built 2026-10-24.** `.claude/settings.json` wires the hook on `mcp__hearthbot__post_message`. For that tool the hook runs no `arm`. It refuses a post that `asked()` matches unless the post carries a line in either rendered form, and the refusal says to forward the thread's Owner-ask line word for word or send nothing. `parse_owner_ask` now renders from `ASK_RISK_SHOWN`, `ASK_DECISION_SHOWN`, `ASK_OPTION_SHOWN`, `ASK_OPTIONS_JOIN` and `ASK_RECOMMEND_SHOWN`. `arming.renders_owner_ask` builds its patterns from those same templates through `string.Formatter().parse`, and the hook imports it as it imports `NO_ASK`. `post_message`'s schema could not be read from the building session, so the hook reads every string field of that tool's input rather than guessing which one carries the text. `tests/unit/test_owner_ask_guard.py` pins a bare ask refused without `arm`, both forms let through, a post asking for nothing let through, and a text in a field other than `text`. `subprojects/docket/tests/test_arming.py` pins the round trip from `parse_owner_ask` to `renders_owner_ask` and four near misses it refuses.
