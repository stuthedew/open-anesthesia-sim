---
id: PL-DMNX
title: PL-1DN9's premise that nothing repository-side runs when a pull request is created is now false, so the published-body read-back it bought 337 resident characters for may be scriptable
status: untriaged
feature: pr-body-integrity
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
