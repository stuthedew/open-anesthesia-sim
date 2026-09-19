---
id: PL-D0K3
title: Replace the ten non-discriminating doc_check verify commands with item-specific ones
priority: P3
effort: M
status: dropped
classes: infra
feature: queue-hygiene
touches: docs/items
added: 2026-09-13
closed: 2026-09-19
reason: population is zero on 2026-09-19 - the ten were repaired or closed as their items were started, which is the policy the brief asked to reaffirm; PL-6TP8's contract records the replay error that catches the next one
---

**Problem.** Replace the ten non-discriminating doc_check verify commands with item-specific ones
**Why it matters.** Verified 2026-09-13: eight open items carry `verify: python3
tools/doc_check.py check` and two carry the same with `&& bin/docket wave`
appended. Neither form discriminates. `doc_check.py check` passes whenever the
docs are internally consistent, which they are before the item is started, so
`bin/docket verify` accepts a branch that did none of the work. That is a check
passing while the guarantee it stands for is void, which is the failure the
`verify:` rule exists to prevent.

**Why this is a decision and not a task.** The `docket` skill states the
opposite policy in as many words: a non-discriminating command is repaired *as
its item is started*, because "a command written away from its work is how every
wrong one here came to exist" - all six wrong commands this store has held were
written for items nobody had begun. A ten-item campaign is what that policy
refuses. What has changed is only the count, five to ten, and
`.claude/rules/expert-review.md` is explicit about how a proposal resting on a
count must be argued: state what the suppressed side would have to be worth for
the proposal to be wrong, then measure it.

**Done when.** Either the repair-as-started policy is reaffirmed and this item
is dropped with that reason recorded, so it is not re-raised at fifteen; or the
case for a pass is made in the form `.claude/rules/expert-review.md` requires,
and the ten commands are rewritten in the paired shape - each having been run
and watched fail.

**Decision needed.** Does the repair-as-started policy still hold at ten non-discriminating commands, or has the count earned a single pass - argued in the form `.claude/rules/expert-review.md` requires?

**Dropped under `PL-6TP8`, 2026-09-19.** Recounted against the open store: no
open item carries `python3 tools/doc_check.py check` alone any more, and the
one command still ending in `bin/docket wave` (`PL-4PC5`) now pipes it into a
`grep`. The ten were repaired or closed as their items were started and closed
between 2026-09-13 and today, which is the repair-as-started policy working
without a campaign; the contract records the mechanism that catches the next
one - an open item whose command passes is an error the replay reports the
moment it happens. Recorded so the question is not re-raised at fifteen.
