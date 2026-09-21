---
id: PL-5DPF
title: A generator marked spent that accrues a new recurrence has had its verdict falsified, and nothing says so
status: untriaged
added: 2026-09-21
---

**Problem.** A generator marked spent that accrues a new recurrence has had
its verdict falsified, and nothing says so.

**Where it comes from.** `PL-T7QR` split the two tests `CLAUDE.md` put on
different axes: the count decides a generator is *recorded*, and the
`generator:` verdict decides whether it *ranks* above every band but `P0`. The
verdict is a judgment about future inflow, so it is the recording session's to
write - and it is the one field in the store that a later fact can flatly
contradict. `recurrences:` is that fact: `bin/docket new` appends an entry every
time a capture matches the item, so an entry arriving after a session wrote
`spent` is the mechanism firing again with the store's own record saying so.

**Why the obvious surface is the wrong one.** `plan.generator_candidates` was
widened to cover this while `PL-T7QR` was being built, and the widening was
wrong: the line that list produces asks a reader to run `docket set <id>
--root-cause-of <ids>`, and a head in this state already carries
`root-cause-of:`. An offer naming the wrong field is worse than no offer, so it
was reverted. What this needs is a line of its own, naming the verdict rather
than the cluster.

**What it would take.** Decidable end to end, which is the half `CLAUDE.md`
scripts: compare a `spent` verdict against the item's recurrence entries and
report the ones that arrived after it. The catch is that `generator:` carries no
date, so "after" has nothing to compare against - either the field grows a date,
or the check fires on any `spent` head carrying recurrences at all and accepts
that a session writing `spent` over an already-recurring history sees it once.
Prefer the second: a date on a judgment field is a second thing to keep
truthful, and `CLAUDE.md` retires a check that fires without changing a
decision rather than one that fires rarely.

**Why it matters.** `spent` is the verdict that *demotes*, so a wrong one is
quiet in the direction the tier's whole design worries about: the mechanism
keeps generating, the item keeps ranking on its band, and no session is ever
told the judgment has been overtaken. The opposite error is loud - a wrong
`live` puts an ordinary item above a `safety`-classed `P1`, where the next
reader of `docket next` sees it.

**Done when.** A `spent` head whose store record shows the mechanism still
firing is reported to a session that could act on it, naming the verdict and the
recurrence entries that contradict it, and the report is silent for a spent head
the store has handed nothing since.
