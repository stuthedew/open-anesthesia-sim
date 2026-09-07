---
id: PL-T7VS
title: A red doc_check voids the whole-store verify replay for the 29 open items gated behind it, and the replay reports green rather than declining to answer
status: untriaged
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py
added: 2026-09-07
---

**Problem.** 29 open items carry a `verify:` command beginning
`python3 tools/doc_check.py check &&`. When `doc_check` itself is red, every one
of those 29 exits non-zero whatever its own substance does, and the replay reads
a non-zero exit as *"the work has not landed; the item is legitimately open"*.
So while `doc_check` is red, `bin/docket check --verify` cannot distinguish an
item whose work is still outstanding from one whose work landed a week ago — and
it reports the second as the first, silently, under a `0 errors` headline.

The guarantee the whole-store replay exists to give — that no finished item is
sitting open — is therefore void for those 29 items whenever `doc_check` is red,
and nothing in the output says so.

**Measured 2026-09-07**, on `b03a7d03` with `doc_check` red (v0.4.8 tagged, no
ROADMAP row):

| | |
| --- | --- |
| open items carrying a `verify:` command | 122 |
| ...gated behind `doc_check` first | 29 |
| `bin/docket check --verify` headline | `0 errors, 4 advisories, 1 not checked` |

**The cost today is zero, and that is measured rather than assumed.** Each of
the 29 was re-run with the `doc_check` clause stripped, so that only the item's
own condition decided the exit: **all 29 still fail**. Nothing is masked right
now. The defect is not that the replay is currently wrong — it is that the
replay cannot tell whether it is, and reports green either way.

**Why it matters.** This is the same class of error as `PL-SR8F` and `PL-0GTC`
(two items open with a `verify:` command that already passed), which sat
undetected long enough to turn `main`'s whole-store replay red across three
merges — the subject of `PL-0ZGK` (the replay runs only on push to `main`, so a
green pull request turns `main` red after it lands), which is still
`needs-decision`. The two failures compose badly: `PL-0ZGK` says the replay's
red is seen by nobody, and this item says its green cannot be trusted.

The window is not exotic. A red `doc_check` is exactly what a half-cut release
looks like — `bin/docket release` writes the version and leaves the ROADMAP
prose to a person, and `doc_check` going red is the intended alarm that the
prose is owed. That is the state `main` is in as this is written. So the
interval in which the replay stops answering for a quarter of the queue
coincides with release time, which is when items have most recently landed and
the replay is most load-bearing.

**Where.** The verify runner in `subprojects/docket/src/docket/verify.py`, and
the reporting in `subprojects/docket/src/docket/checks.py` /
`render.py`.

**Done when.** A `verify:` command that could not run its own condition is
reported under **"Not checked (this checkout cannot answer; nothing is
claimed)"** rather than counted as an item legitimately open. That category
already exists and already carries exactly this meaning — `render.py:1042`, used
today for the two commands killed at the 120 s limit — so this is a routing
question, not a new concept.

**Two design notes for whoever scopes it.** First, the cheap and general form is
to run `doc_check` once, up front, and route every command gated behind it to
"not checked" when it is red; the narrow form — pattern-matching the prefix — is
fragile against a command that puts `doc_check` second. Second, the same 29
commands each shell out to `doc_check` separately, so hoisting it would also
remove 29 redundant runs from a check whose cost is already an advisory.

**No `verify:` command is recorded deliberately.** The obvious shape asserts
something about `docket check`'s output under an artificially red `doc_check`,
and it has not been watched failing. `PL-0GTC`'s own note is the precedent: an
unrun command is the failure mode `.claude/skills/docket/SKILL.md` names, and
this item would rather carry none than carry one that proves nothing.

**Found.** 2026-09-07, closing out `PL-SR8F` and `PL-0GTC` — both already landed
under `PL-CL8J` (#432) — when their `verify:` commands were run by hand and
failed on the shared `doc_check` prefix rather than on either item's own claim.
