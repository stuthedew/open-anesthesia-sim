---
id: PL-0VFF
title: ROADMAP.md's 'Declined to Gate 2' list names PL-483K, PL-69JZ and PL-L09X as deferred, but all three closed done in v0.4.14, and nothing distinguishes a still-open entry from a closed one
priority: P2
effort: S
status: done
classes: defect, docs
feature: gate-list-integrity
milestone: v0.4.35
touches: ROADMAP.md
added: 2026-09-12
closed: 2026-09-20
pr: 774
verify: python3 tools/doc_check.py check && grep -qE '^- PL-483K .*v0\.4\.14' ROADMAP.md
---

**Problem.** ROADMAP.md's 'Declined to Gate 2 - 42 entries' lists PL-483K, PL-69JZ and PL-L09X as deferred, but all three closed done in v0.4.14, so the count and the list both overstate the deferral

**Confirmed at triage, 2026-09-12.** The section heading is `ROADMAP.md:1869`,
"Declined to Gate 2 on the refilling-queue ground - 42 entries", and it holds
exactly 42 `- PL-` lines. Three of them name items the store now calls closed:

```text
1950  - PL-483K (S) The stop hook demands a push for work already pushed ...
1951  - PL-69JZ (S) docket verify's 'the checks themselves are unedited' ...
1973  - PL-L09X (M) An item blocked on a milestone that is decided but not ...
```

All three are `status: done` and all three ship in v0.4.14, whose own table row
(`ROADMAP.md:77`) names `PL-69JZ` and `PL-L09X` by id as part of what it
delivered. So the same document says, 1 800 lines apart, that these are deferred
and that they shipped.

**Why it matters.** The entries themselves are a frozen snapshot and stay - that
is what "the gate is a snapshot" means, and deleting them would destroy the
record of what was declined and why. What is wrong is that nothing distinguishes
a declined entry that is still outstanding from one that has since been closed,
so the only number a reader can take from the section is 42, and 42 is now an
overstatement of the deferral by three. A gate list exists to be read when
deciding whether a gate can open; a session or an owner sizing that decision off
this section is off by three items today and by more later, since nothing stops
the next closure from widening the gap silently.

**Done when.** The section states how many of its 42 entries are still open
alongside the frozen total, and each entry the store now calls closed carries
the release that took it - `PL-483K`, `PL-69JZ` and `PL-L09X` with `v0.4.14` -
so the list stays a snapshot and stops reading as a backlog.

**Re-scoped 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
Closed entries carry their release, which is a record fact and cannot go stale.
The **open count is not stated at all** - `bin/docket wave` prints it - which is
the counts rule's second branch: where no check can hold a number to what it
counts, the sentence states the rule without the number rather than dating a
figure that a reader would take as current.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "Not wholly apparatus, but unable to change what a reader of the simulator sees". This item is also named in paragraphs quoted in the briefs of `PL-B60Q`, `PL-2P9L`, `PL-HCTF` and `PL-LPH9`.

> **Two reach `ROADMAP.md` and so are not wholly apparatus.** Their ground is stated here, rather than the refilling-queue ground being stretched to cover them. `PL-0VFF` is this subsection's own bookkeeping. Three of its entries closed in v0.4.14, and nothing marks a closed entry apart from an open one. `PL-880Z` is about the wording of a frozen entry in the workflow-lane list above. That entry repeats `PL-XLQ5`'s title, and with it a mechanism that `_landing_split` does not have. Both are corrections to this document's account of its own queue. So neither can affect a reader of the simulator, which is the test on which the first twenty-nine were declined. Only one item from this pass *could* affect such a reader: `PL-DZFJ`, about what a drawn chart point represents. It is admitted above rather than declined, under the unconditional safety exception.

> - PL-0VFF (S) ROADMAP.md's 'Declined to Gate 2' list names PL-483K, PL-69JZ and PL-L09X as deferred, but all three closed done in v0.4.14, and nothing distinguishes a still-open entry from a closed one
