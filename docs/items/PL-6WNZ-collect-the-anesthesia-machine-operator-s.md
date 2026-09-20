---
id: PL-6WNZ
title: Collect the anesthesia machine operator's manuals PL-4DCG's survey could not reach into open-anesthesia-sim-references, so the machine profile parameters have a citable primary source
status: untriaged
added: 2026-09-20
---

**Problem.** Collect the anesthesia machine operator's manuals PL-4DCG's survey could not reach into open-anesthesia-sim-references, so the machine profile parameters have a citable primary source

**Where it came from.** `PL-4DCG`'s survey session (closed, merged as `#742`)
ended with two outstanding asks in its handoff, one of which was to add machine
manuals to the `open-anesthesia-sim-references` repository. That session is now
archived, and an archived session's handoff is deleted silently, so the ask
existed nowhere in the tree. Filed here on 2026-09-20 so it survives.

**Why it matters.** `docs/machine-survey.md` records what could be reached from
published literature and vendor material; several machine parameters a profile
will need — flowmeter floors and ceilings, circuit volumes, minimum deliverable
flow — are published only in operator's manuals, which the survey session could
not obtain. `PL-8PS6` (fresh gas flow range is a machine property, not a global
constant) and planned-milestone item 1 (machine selection) both need those
numbers with a citable source, and `docs/MODEL.md`'s source hierarchy will not
accept a remembered figure.

**Done when.** The manuals for the machines `docs/machine-survey.md` names are
in `open-anesthesia-sim-references` with their edition and date recorded, or
the survey records for each one that it could not be obtained and why.

**Note.** The collection step is the project owner's — it needs vendor accounts
or institutional access a session cannot reach.
