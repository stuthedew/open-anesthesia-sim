---
id: PL-DMNX
title: PL-1DN9's premise that nothing repository-side runs when a pull request is created is now false, so the published-body read-back it bought 337 resident characters for may be scriptable
priority: P3
effort: S
status: done
classes: docs, infra
feature: pr-body-integrity
touches: docs/items
added: 2026-09-20
closed: 2026-10-03
pr: 1297
verify: grep -qF 'Answered 2026-10-03: Q1 ratified' docs/items/PL-DMNX-pl-1dn9-s-premise-that-nothing-repository-side.md
---

**Problem.** PL-1DN9's premise that nothing repository-side runs when a pull request is created is now false, so the published-body read-back it bought 337 resident characters for may be scriptable

**The premise.** `PL-1DN9` placed the published-body read-back in `CLAUDE.md`
rather than in a check, on the reasoning that "nothing repository-side runs at
the moment a pull request is created, which is the same reason `PL-1Q3S` landed
as prose rather than as a hook." That was true when it was written and is not
true now: `.github/workflows/pr-title.yml` triggers on `opened` as well as
`synchronize`, `reopened` and `edited`, and `tools/pr_title_check.py`'s
`open_pull_request()` already fetches the pull request object - whose JSON
carries `body` - from the API.

**What that does and does not license.** It does not make the hazard itself
decidable: a check reads the *published* body, and what was stripped is by
definition no longer in it, so detecting the loss needs the sent copy to
compare against. A `tools/pr_body_check.py --sent <file>` that diffs the two is
the honest shape, and it costs the session a step it does not currently take.
Scanning the published body for the residue of stripping is the tempting
version and is exactly what `CLAUDE.md` means by scripting the judgment half.

**Weak on current evidence.** A survey of the 30 most recently merged pull
requests (#752-#782) found **0 of 30** with any stripped placeholder, stray
closing tag or truncated code span - and one surviving angle-bracket
placeholder, `bin/docket set <id> --status done|dropped` in #779, intact inside
a code span. The convention appears to be working, or the hazard is rarer than
its 337 resident characters imply. So this is a correction to a stale premise
and a note of what is now possible, not a recommendation to build it. The
clearest use is if `CLAUDE.md`'s resident growth ever needs 337 characters back.

**Why it matters.** `CLAUDE.md`'s published-body read-back is 337 characters of
the resident set, which is resent on every request of every session, and the
project owner's 2026-09-19 rule now requires every edit to that set to name
what it replaces. So the 337 characters are a live candidate for recovery the
moment the resident set next needs a cut - and the reasoning that put them
there rather than in a check is now false. Nothing records that. A session
looking for characters to give back reads `PL-1DN9`'s closed brief, finds a
premise it has no reason to doubt, and leaves the rule where it is.

**Done when.** Either `tools/pr_body_check.py` grows a `--sent <file>` clause
that diffs the sent body against the published one and the resident rule is cut
to point at it, or this item records that the read-back stays resident and why,
so the stale premise stops being the reason a later session reads.

**Decision needed.** Whether to build the sent-versus-published diff now, or to
keep this item as the recorded route and build it only when the resident set
needs those 337 characters back.

**Recommended:** do not build it now; keep the route recorded. The survey in
this brief found 0 of 30 recently merged bodies with any stripped placeholder,
stray closing tag or truncated code span, so the hazard the rule guards is not
currently firing, and a check costs the session a step it does not take today
(writing the sent body to a file before every pull request). Build it when the
resident set needs the characters, which is the moment the trade actually pays.
Note that `.claude/rules/citation-drift.md` refuses the other half outright:
`PL-1DN9` is `status: done`, so correcting the premise *in its brief* is not a
finding and must not be done - which is precisely why the correction needs a
live carrier, and this item is it.

**What would change the answer.** One merged pull request whose published body
lost content the sent copy had. That is a measurement `tools/pr_body_check.py`
could take going forward at no cost to the session, and it is the thing to
watch rather than to argue about.

## Design round 2026-10-03: recommendation

**Re-checked against the tree, 2026-10-03.** The premise correction holds:
`.github/workflows/pr-title.yml` triggers on `opened`, `synchronize`,
`reopened` and `edited`, so something repository-side does run when a pull
request is created. `tools/pr_body_check.py` already fetches published bodies
from the API (`fetch_body`) and compares them against squash commits
(`compare`); it has no sent copy to compare a published body against, and
nothing else holds one. The resident passage runs 336 characters from "Then"
to its `PL-1DN9` citation (`CLAUDE.md`, the commit-and-push bullet). The hazard
is still unobserved since `#132`: the 0-of-30 survey above stands, no later
instance has been reported, and the current harness passes at least one kind
of angle bracket through unchanged - every project-thread pull request opens
with an HTML comment (`<!-- ccr-projects-attribution ... -->`), and `#1293`'s
published body, read on 2026-10-03, carries it intact. Whether an unknown tag
such as `<branch>` is still stripped has not been measured since `#132`. No
generator head is marked still generating (`bin/docket generators`,
2026-10-03), so the pause on new mechanisms is not what decides this.

**Q. Build the sent-versus-published diff now, or keep the route recorded?**
**Recommendation: keep it recorded, and close this item on the record.** The
diff needs the sent copy, which costs every session a step on every pull
request to catch a hazard with no instance since `#132`; the 336 resident
characters are the cheaper guard until the resident set needs them back, and
the moment it does is the moment the trade pays. This item is the live carrier
of the corrected premise, which `.claude/rules/citation-drift.md` forbids
writing into `PL-1DN9`'s closed brief. The close-out is the record itself: no
code, no `CLAUDE.md` edit.

**What would change the answer.** A published body found to differ from what
its session sent - a session's own read-back is the only instrument that can
see it - or the resident set needing the characters. Either reopens this with
the `--sent <file>` shape above as the build.

## Answers 2026-10-03

**Answered 2026-10-03: Q1 ratified** (project owner, 2026-10-03, ratified,
over building `tools/pr_body_check.py --sent <file>` now and cutting the
resident rule to point at it). Not built. The read-back stays resident at 336
characters; this item is the live carrier of the corrected premise, that
`.github/workflows/pr-title.yml` runs on `opened`, so `PL-1DN9`'s reason for
prose over a check no longer holds; and the `--sent` diff is the build if a
published body is ever found to differ from what its session sent, or the
resident set needs the characters back. Closed on this record in the design
round's own pull request, with no build thread.
