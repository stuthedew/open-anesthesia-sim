---
id: PL-0VFF
title: ROADMAP.md's 'Declined to Gate 2' list names PL-483K, PL-69JZ and PL-L09X as deferred, but all three closed done in v0.4.14, and nothing distinguishes a still-open entry from a closed one
priority: P2
effort: S
status: ready
classes: defect, docs
feature: planning-cadence
touches: ROADMAP.md
added: 2026-09-12
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
