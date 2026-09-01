---
id: PL-Y08X
title: The session digest offers a release the same digest's plan line says is not ready
status: untriaged
added: 2026-09-01
---

**Problem.** Every session opens with two lines that contradict each other.
The digest measured on 2026-09-01 printed:

    Releasable: 33 finished item(s) since 0.2.7, completing parallel-sessions,
    worker-instructions. Offer 0.2.8 before taking new work.
    Plan: 0.2.7, step 1 of 10 (v0.2.8 - the workflow works). Beat: clear the
    gate - 7 entries of 32 still open.

The first line instructs the session to interrupt the owner with a release
offer. The second says the release it would offer has 7 of its 32 frozen gate
entries still open (`PL-NSN9`, `PL-D2GW`, `PL-Q2BJ`, `PL-3CBS`, `PL-DL1X`,
`PL-921W`, `PL-CMCB`).

**Why it matters.** `Readiness` and the plan are computed by two subsystems
that do not consult each other. `Readiness.is_worth_cutting`
(`release.py:202`) fires on `completed_features` or three shippable items; it
reads no gate. So the offer fires on finished-item count while the freeze -
the thing that decides whether 0.2.8 may be cut - is invisible to it.

The cost is per session, not once: a session that follows the instruction
spends an exchange offering a release the owner then declines, and the digest
is the first thing every session reads. At least 7 sessions remain before the
gate closes. The worse outcome is a session that acts on the first line
without reading the second and cuts 0.2.8 with a third of its gate open,
which is precisely what freezing a list was for.

It is also the failure mode this package names elsewhere and guards against:
a check reporting a partial answer as a complete one. `Readiness`'s own
docstring says it is "deliberately advisory" and "does not decide that a
release should happen" - but "Offer X before taking new work" is written as an
instruction, not as advice, and it is the only line of the two that tells the
session to do something.

**Where.** `subprojects/docket/src/docket/release.py` - `Readiness`,
`is_worth_cutting`; the offer line in `render.format_digest`
(`render.py:233-242`), which has the plan in scope on the very next line and
does not consult it.

**Done when.** A digest whose suggested version has an open frozen gate does
not instruct the session to offer that release - it either suppresses the
offer or states the gate is open in the same sentence - and a test covers a
digest built from a store with an open gate saying so.
