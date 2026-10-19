---
id: PL-5S71
title: Have Fable 5.1 read docs/MODEL.md against src/anesthesia_sim/data/ once through the Message Batches API, on the API credits, for statements that contradict a stored value, each other, or a cited unit, and file each confirmed finding: a strongest-model second reading of the clinical specification that no session's budget has covered
priority: P2
effort: M
status: ready
classes: docs, infra
feature: api-credit-runs
touches: tools/, tests/unit/, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-19
payoff: the clinical specification gets one full reading by the strongest model against the stored values, so a contradiction a learner could be misled by is found and filed rather than left
verify: grep -rqF '/v1/messages/batches' tools/
not-delegable: The run spends the owner's API credit from the owner's machine, which no session can reach, and each finding has to be confirmed against its cited source by a session before it is filed
---

**Problem.** Have Fable 5.1 read docs/MODEL.md against src/anesthesia_sim/data/ once through the Message Batches API, on the API credits, for statements that contradict a stored value, each other, or a cited unit, and file each confirmed finding: a strongest-model second reading of the clinical specification that no session's budget has covered

**Why it matters.** `docs/MODEL.md` is the authoritative specification of the
clinical model, and every stored parameter under `src/anesthesia_sim/data/`
is cited from it. A statement there that contradicts a stored value, another
statement or a unit is a misleading clinical claim under the safety-critical
standard. No session has read the whole document against the data in one
pass, because it does not fit in one session's budget. The API credits can
pay for one reading by the strongest model, which the owner asked for.

**Measured 2026-10-19.** On `main` at `1e5cb9bd`, `docs/MODEL.md` is 671,450
bytes and the JSON files under `src/anesthesia_sim/data/` total 190,103 bytes.
At about 4 bytes per token that is roughly 215,000 tokens, so the reading
probably has to be split by section, each request carrying the section and
the data files it cites (inferred; check the model's context window before
choosing the split).

**Route.** A standard-library script under `tools/` builds one batch request
per section and submits it to the Message Batches endpoint,
`/v1/messages/batches`, with the model `claude-fable-5-1`. The owner runs it on
their machine, because the API key and the credits are there, as with
`tools/headless_worker.py` (`PL-80R5`). A session then reads the returned
findings, confirms each against the file and the cited source, and files each
confirmed one as its own item, classed `science` or `safety`.

**Done when.** The script exists with a test of how it builds the requests,
the owner has run it once, and every finding it returned is either filed as
an item or recorded in this brief as not confirmed, with the reason.

**Generator check.** A one-off, asked for by the owner.

**Why it is not classed `science`.** The item changes no equation, value or
displayed output. It produces findings, and each confirmed finding is filed
classed `science` or `safety`, where the checker ranks it at `P1` and returns
it to the current gate. Classing the review itself `science` would hold
v0.6.0 until the owner runs a credit job on their machine, which no part of
that release depends on (triage, 2026-10-19).
