---
id: PL-XJ22
title: A triage pass checks the in-flight marks when it starts and not when it pushes, so an item claimed while the pass runs gets a second answer: #1124 triaged PL-QMN0 seven minutes after another branch claimed it, and merged first (2026-09-26)
priority: P3
effort: S
status: done
classes: docs
feature: claim-record
milestone: v0.5.23
touches: .claude/skills/docket/modes/triage.md
added: 2026-10-11
closed: 2026-10-11
pr: 1416
payoff: A triage pass stops pushing a second answer for an item another branch claimed while the pass ran, so a finished fix is not lost to whichever pull request merges first.
verify: grep -qF 'bin/docket flight' .claude/skills/docket/modes/triage.md
reenters: PL-MB2W, PL-7TVT
---

**Problem.** A triage pass checks the in-flight marks when it starts and not when it pushes, so an item claimed while the pass runs gets a second answer: #1124 triaged PL-QMN0 seven minutes after another branch claimed it, and merged first (2026-09-26)

**Found by `PL-99YZ`'s count, 2026-10-11.** It is the same-id half of what
that item measured: every guard keys on the id here, and the id matched. What
missed is the window between the pass reading the marks and pushing its answer.

**The two instances since claims were pushed at start (#987, 2026-09-24).**
About nine multi-capture triage passes have merged since then, read from
`main`'s subjects, and two met a claim made while they ran.

- 2026-09-26. `claude/project-thread-qt3onr` claimed `PL-QMN0` at 19:45:26 UTC
  (`47b3f928`), triaged it to P2 ready at 19:48:57 and committed the fix at
  19:59:48 (`59ea9d1c`). `PL-61FT`'s pass committed its ten triage answers at
  19:52:08 (`8441ef70`), `PL-QMN0` among them as P3, blocked on the generator
  head the same pass recorded, and #1124 merged at 19:59:08. The fix opened as
  #1127 at 20:04 and closed unmerged at 20:09; #1128 parked it on its branch and
  #1138 dropped `PL-QMN0` into a `KNOWN_GAPS` row. The pass did read the marks -
  its body names the branches it left four items to - so it read them before the
  claim reached `origin` (inferred: when the claim was pushed is not recorded).
- 2026-10-01. `claude/read-facts-through-docket-0yo78k` claimed `PL-DHGC` and
  `PL-W560` at 19:13:57 (`0cb10e58`). #1278's pass committed answers for both at
  19:22:11 (`f63d0da5`) and restored `main`'s copies two minutes later
  (`a938142c`): "pushed after this pass read the queue". Its session re-read the
  marks before pushing on its own; nothing in triage mode asks for that.

**What the skill says now.** `.claude/skills/docket/modes/triage.md` has the pass
skip an item marked `IN FLIGHT` or `Its file is already edited on <branch>`, and
says the mark "is bounded by what has been pushed". It says nothing about
reading the marks again once the pass has written its answers, which is when a
claim made during the pass first becomes readable. The first instance cost a
finished fix that had passed `verify --self`; whether it would have merged
otherwise is unknowable, since #1128's bound might have dropped the item anyway.

**Why it matters.** A second answer to a claimed item is discarded work on
one side or the other, and the merge picks which by arrival rather than by
merit: on 2026-09-26 it cost a finished fix that had passed `verify --self`.
Two of about nine passes since claims went out at start met a claim made while
they ran, so the window is not rare, and an item-only triage branch arms
auto-merge at its first push, so nothing between the push and the merge asks.

**Reproduced 2026-10-11** on main at `16a20a4f`: `grep -n -i -E '\bagain\b|before
push' .claude/skills/docket/modes/triage.md` finds two lines, line 78's
retitle for a dropped id and line 495's reopened `verify:`, and no step reading
the marks again before the push. Nor does a tool tell the pass at that moment: `arming.arm`, asked
before an item-only branch arms, reads only the holds on its own branch
(`_head_name(hold.ref, remotes) == branch`), so a rival claim on an item this
branch answered reaches no answer it gives.

**Route (triage, 2026-10-11).** The declared one: a step in triage mode that
fetches and reads `bin/docket flight` against the ids the pass answered, just
before pushing, and restores `main`'s copy of any another branch now claims,
as #1278's session did by hand. A hold in `bin/docket arm` would make it
decidable rather than remembered, and is the stronger answer if the step
proves to be skipped; it is a larger change to a file on the owner's read
list, so it is not taken first. Either is a new rule rather than a repair, so
it would wait under `CLAUDE.md`'s generator pause, but no open item carries
`generator: live` on 2026-10-11, so nothing holds it.

**Generator check.** The fact misread is who holds an item now: the pass took
the marks it read at its start for the holders at its push. `PL-MB2W` (closed
2026-09-26) and `PL-7TVT` state that fact, so this is an instance of their
head's fact filed after the heads closed, at the one moment no reader of the
claims record is asked: a pass's push. The neighbouring `PL-XBV4` fact, how
fresh the refs a read answered from are, is the same window seen from the
reader; one instance, so no head is reopened.

**Done when.** A triage pass cannot push an answer for an item another branch
claimed or edited after the pass read the marks without being told so at that
moment, or the rate above is recorded as not worth the line it would take.

**Done 2026-10-11, by the declared route.** Triage mode now asks for
`bin/docket flight` immediately before every push, and for `origin/main`'s copy
to be restored for any answered id it lists on another branch. Read off
`Holdings.holding` in `subprojects/docket/src/docket/claims.py` before writing
it: a claim sorts ahead of every status move, so a rival claim always reaches
the row even where this branch also answered the item. What `flight` cannot
show - a second pass's later answer, since the earliest move keeps the row, and
an edit with no status move - the step names, with `bin/docket show <id>` as
the read that prints every branch. If a later instance shows the step skipped,
the `bin/docket arm` hold above is the next answer.
