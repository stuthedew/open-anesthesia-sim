---
id: PL-77QB
title: An owner read ask points at a file ("Please look at: the hazard table's 21 rows") instead of quoting the text to review, so the owner has to dig through the file to find it
priority: P2
effort: S
status: ready
classes: infra
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, tests/unit/test_owner_ask_guard.py, .claude/skills/pull-request/SKILL.md, .claude/skills/docket/modes/coordinator.md, docs/maintainer.md
added: 2026-11-02
payoff: every read ask the owner gets shows the text to judge in the reply itself, so they can decide in the thread without opening a file
verify: grep -q 'quote' subprojects/docket/src/docket/arming.py && ! grep -q 'Please look at' subprojects/docket/src/docket/arming.py
---

**Problem.** When a pull request waits on the owner's read, the reply that
asks for it names a place in a file and stops there. On 2026-11-02 the
`#1944` thread's ask read "Please look at: the hazard table's 21 rows". The
owner then had to open `docs/MODEL.md` and find the rows themselves.

**The owner's words** (project owner, 2026-11-02, 17:04Z):

> "Please look at: the hazard table's 21 rows," It continues to direct me to
> dig into a file. I want it to just show me the relevant text rather than me
> trying to dig through

> I thought we had talked about this before

> I don't want to ask every time. I just want this to be default behavior

**Cause.** The wording comes from `bin/docket arm` itself. The risk-review
form of an `Owner-ask:` record renders as `Risk to review: ... Checked: ...
Please look at: {look}.` (`ASK_RISK_SHOWN` in
`subprojects/docket/src/docket/arming.py`). Its `look` field is described as
"the one thing to look at", so a session fills it with a location. Nothing
that `arm` prints, and nothing in the `pull-request` skill, `docs/maintainer.md`
or the coordinator mode, tells a session to put the text itself in the reply.
The session already knows which text changed, so a pointer hands the owner a
search the session could have done.

**Fix.** Make quoting the default at the moment the ask is written:

1. `ASK_RISK_SHOWN` renders the `look` field as the text to review, quoted
   below the line, instead of "Please look at".
2. `ASK_LINE`, which `arm` prints just before the ask's line, says to quote
   the text under the line: the changed sentences, rows or values, before and
   after, in the reply itself. A generated file is attached only for the full
   set, and never in place of the quote.
3. `READ_ASK`'s description of the risk form's `look` field changes to match.
4. The `pull-request` skill, `docs/maintainer.md` and the coordinator mode
   state the same rule, so a coordinator relaying an ask quotes too.

The `look` keyword in the trailer stays, so `Owner-ask:` records already on
open branches still parse.

**Not done.** Close-out step 6 in `.claude/skills/docket/modes/close-out.md`
was named as a third place to change. On `origin/main` at this branch's base,
step 6 is the adversarial diff review and says nothing about asking the owner,
so it is left alone. `.claude/hooks/owner_ask_guard.py` could refuse a risk
ask that quotes nothing, but repository hooks do not run in Projects threads
(`PL-CR81`), which is where the owner reads these asks, so a check there would
not reach the case that prompted this.
