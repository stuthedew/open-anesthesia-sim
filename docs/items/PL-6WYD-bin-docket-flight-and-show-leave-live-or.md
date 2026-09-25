---
id: PL-6WYD
title: bin/docket flight and show leave live-or-abandoned to a branch's age, though each claim records its holder's session id and get_session on it answers directly; flight prints no id, and its 'live' means only inside the 7-day lease
priority: P3
effort: S
status: ready
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_claims.py, .claude/skills/docket/modes/start.md
deferred-from: v0.6.0 - new since the freeze (e6cdfd93, 2026-09-21): the claim's session token and flight's lease-state column both arrived with PL-3FYK (#983) and PL-N162 (#1002) on 2026-09-24, and not safety or science
added: 2026-09-25
payoff: a reader of flight or show gets the one call that says whether a claim's session is still running, instead of judging from the branch's age
verify: grep -q 'def test_flight_s_claim_rows_print_the_holder_s_session' subprojects/docket/tests/test_claims.py
---

**Problem.** bin/docket flight and show leave live-or-abandoned to a branch's age, though each claim records its holder's session id and get_session on it answers directly; flight prints no id, and its 'live' means only inside the 7-day lease

Reproduced 2026-09-25 at 22:12 UTC, with `bin/docket` at `4f37ef29` reading `origin/main` at `7556f556`, which changed none of `render.py`, `cli.py` or `claims.py`:

- `bin/docket flight` printed `PL-WX87  origin/claude/eager-johnson-8v3qgw  live  claim  last commit 12 minutes ago  no pull request open`, with no session on any row, under "A branch outlives its session, so no row here says anybody is still on it: the age is how long it has sat. ... nothing a checkout can read tells the two apart sooner." (`render.format_flight`).
- `bin/docket show PL-WX87` printed `live claim, made 2026-09-25 21:59 UTC, session cse_01K7YtoZYBcov6QYr9oiMoAu`, then "A branch outlives its session, so this does not say anybody is still on it; `bin/docket flight` adds whether a pull request is open" (`render._hold_detail`, `render._one_claim`). It prints the key, then points at the command that prints none.
- `get_session` on `cse_01K7YtoZYBcov6QYr9oiMoAu`, exactly as `show` printed it, answered for `session_01K7YtoZYBcov6QYr9oiMoAu`: `SESSION_STATUS_RUNNING`, `connection_status: connected`, bucket `WORKING`. At about 22:00 the same lookup answered RUNNING for the holders of `PL-KX73` and `PL-J16N`, and the holders of the claims on `PL-N162`'s three branches (`claude/exciting-gates-38yfzt`, `claude/funny-babbage-qht2y5`, `claude/intelligent-gauss-0p4vcy`) were all `SESSION_STATUS_ARCHIVED` in `list_sessions`.
- `list_sessions` (`mine: true`, 40 sessions back to 2026-09-23) listed neither the `PL-KX73` nor the `PL-J16N` holder: both are Projects threads (`origin: claude-in-hearth`, tag `hearth-thread`), which is `PL-DR3G`. The lookup by the claim's own token found both.

So the caveat is right that a checkout cannot tell a running session from an ended one, and stops one step short: the claim already records the key, and the call that answers is in every session's hands. ARCHIVED is an announced stop rather than a timeout's inference, so for the abandoned case in particular a branch's age is the weaker of two available answers.

The row's `live` is `claims.LIVE`, a lease state: inside `LEASE_TERM`, seven days, of the branch's last commit. Printed a line above "no row here says anybody is still on it", it reads as the claim the caveat denies.

`.claude/skills/docket/modes/start.md` says the token "reads `cse_...` where `get_session` wants `session_...`". `get_session` took the `cse_` form directly for both tokens tried in that form on 2026-09-25.

**Why it matters.** Whoever reads `flight` or `show` - the owner looking over every branch, a session deciding whether an item is really being worked - is handed a judgment from age where one lookup answers it, and one screen uses `live` in two senses. Taking over a claim already needs the owner's word or `get_session` showing ARCHIVED or failed (`.claude/skills/docket/modes/start.md`, "Taking over a dead claim"), so the payoff is in reading rather than in takeovers: modest, and cheap to take.

**Not the fix.** A session-service call inside `docket`: `PL-SK88` refused it, because `docket` is standard-library only and answers offline, and a live service would make its output unreproducible. A `list_sessions` scan: it cannot see Projects threads (`PL-DR3G`). A shorter lease or heartbeat commits: `LEASE_TERM`'s evidence (92.1 h owner absence, 8.43 h inside a live session) stands, and the lookup answers sooner than any lease could.

**Done when.**

- Each claim row in `flight` prints the holder's session token as the claim records it (`Hold.session`), where it carries one.
- The `flight` caveat and `show`'s line name `get_session` on that token as what tells a running session from an ended one, in place of "nothing a checkout can read tells the two apart sooner".
- The state printed on a row no longer reads as "a session is on it" (`held`, say, or `in lease`); the state can stay `claims.LIVE` in code.
- `.claude/skills/docket/modes/start.md`'s prefix sentence says `get_session` takes the `cse_` token as printed.
- `test_flight_s_claim_rows_print_the_holder_s_session` in `subprojects/docket/tests/test_claims.py` pins the token on the row and the caveat's wording.

**Generator check.** Not a member of `PL-MB2W`'s head. The fact at issue is whether a recorded holder is still running, not who holds the item; the claim record answers "who" and carries the token, so this is a presentation gap at the two readers that print it - a one-off.

Found in a read-only review of the `flight` caveat, which the project owner questioned on 2026-09-25.
