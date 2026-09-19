---
id: PL-PZ8D
title: Record the delegation trigger the project owner set on 2026-09-19 - a real trade-off rather than the size of the change - and the level-versus-trend distinction that stops PL-9J2W refusing their own convergence question
priority: P2
effort: S
status: done
classes: docs
feature: owner-decisions-2026-09-19
milestone: v0.4.29
touches: CLAUDE.md
added: 2026-09-19
closed: 2026-09-19
verify: grep -qF 'The trigger for involving them is a real trade-off' CLAUDE.md && grep -qF 'That answers the level, not the trend' CLAUDE.md && grep -qF 'And every edit to the resident set names' CLAUDE.md && python3 tools/doc_check.py check
---

**Problem.** Three things the project owner decided in conversation on
2026-09-19 had no carrier, and one of them was actively contradicted by the text
already in `CLAUDE.md`.

1. **The delegation trigger.** A recurring observed issue, or a cheaper route to
   behavior the project already has, is a session's to fix and report — including
   new non-user-facing machinery, asked for or not. It becomes the owner's when
   something has to be weighed. The existing division-of-labour paragraph grants
   a narrower version of this (the version bump, the release notes, the item that
   should have been filed) and the ask-gate turns on a different axis entirely —
   deviating from a *described* deliverable, not acting without one — so neither
   covered it.
2. **Level versus trend.** § "What this project is" refuses the objection "there
   is too much apparatus, the effort belongs on the product instead" and tells a
   session that raising it again wastes a reply (`PL-9J2W`). The owner then asked
   for a sanity check on whether apparatus inflow is declining. Those are
   different claims — one about the level, one about the derivative — and as
   written the refutation would have been quoted back at the owner's own
   question. The premise under it has also expired: the apparatus *was*
   effectively the product while it was being built.
3. **A brake on resident growth.** The set ran 8,903 characters at inception,
   49,991 on 2026-09-13 and 60,199 on 2026-09-19 — 20.4% in six days.
   `tools/doc_check.py` already records the cause and that nothing has ever
   shortened it. Every edit must now name what it replaces or say why nothing can
   be cut.

**Why it matters.** `CLAUDE.md` requires a behavior change to take effect in the
session that asks for it, because an item alone changes nothing while every
session in the meantime keeps doing the thing that was just corrected. Item 2 is
the sharpest case: the instructions would have refused the owner's own request.

**What a bright line would have cost, recorded because it was refused.** A hard
count on the fast path — "adds a standing mechanism, therefore a trade-off,
therefore ask" — was considered and rejected: it would have blocked the
convergence sanity check the owner asked for three times in the same
conversation (`PL-04KR`). The disclosure requirement carries the same weight at
a fraction of the cost: report what the fast path did, in a line, every time.

**Done when.** The three blocks are in `CLAUDE.md`, the resident-growth advisory
has been run and its addition accounted for rather than offset by trimming
unrelated text, and `python3 tools/doc_check.py check` passes. Landed at +2,495
characters, all three blocks owner-requested, which is the second of the two
answers that advisory accepts.
