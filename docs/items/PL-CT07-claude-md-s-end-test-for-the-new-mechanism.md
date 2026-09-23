---
id: PL-CT07
title: CLAUDE.md's end test for the new-mechanism pause - bin/docket next showing the generator tier empty - reads true while live generators are open, because next leaves out items in flight: at this session's start it showed none while PL-8YXJ, PL-J6HP and PL-XYQW carried generator: live
priority: P2
effort: S
status: ready
classes: docs
feature: generator-identification
touches: CLAUDE.md
added: 2026-09-23
payoff: a session checking whether the new-mechanism pause has lifted gets the rule's own answer, instead of being told it is over while live generators are still open
verify: ! grep -qF 'The pause ends when `bin/docket next` shows' CLAUDE.md
---

**Problem.** CLAUDE.md's end test for the new-mechanism pause - bin/docket next showing the generator tier empty - reads true while live generators are open, because next leaves out items in flight: at this session's start it showed none while PL-8YXJ, PL-J6HP and PL-XYQW carried generator: live

**Reproduced 2026-09-23.** This session's start digest printed `Top: PL-1X2C`
(a P2 item) and listed `PL-8YXJ`, `PL-J6HP` and `PL-XYQW` as in flight. All
three were open and carried `generator: live`. So the rule's first sentence
("While any open item carries `generator: live`") said the pause held, and its
stated end test ("The pause ends when `bin/docket next` shows the generator
tier empty") said it was over. `next` leaves out in-flight items, and the
generators most likely to be open are the ones being worked. Found by this
session's triage pass over `PL-TH9K` and `PL-RX3H`.

**Why it matters.** It gives a wrong answer silently. A session asking the
pause's own question is told the pause has lifted and builds a new mechanism,
which is the inflow the pause exists to stop (`PL-6Q9L`, `PL-04KR`).

**Done when.** `CLAUDE.md` § "What this project is" states an end test that
agrees with the rule. **Recommended:** that no open item carries
`generator: live`, readable with `bin/docket generators`, or a `grep` of the
open items, rather than a view that filters out what is in flight. Editing the
sentence changes no mechanism, so the pause does not hold it.

**Generator check.** A one-off. The rule's end test was written against a view
of the queue, and the rule itself against a field. No other item names that
seam.
