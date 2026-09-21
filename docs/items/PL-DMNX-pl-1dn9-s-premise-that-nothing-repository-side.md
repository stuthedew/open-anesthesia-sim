---
id: PL-DMNX
title: PL-1DN9's premise that nothing repository-side runs when a pull request is created is now false, so the published-body read-back it bought 337 resident characters for may be scriptable
priority: P3
effort: S
status: needs-decision
classes: docs, infra
feature: pr-body-integrity
touches: CLAUDE.md, tools/pr_body_check.py
added: 2026-09-20
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
