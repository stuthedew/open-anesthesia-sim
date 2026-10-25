---
id: PL-5S71
title: Have the models table's review model read docs/MODEL.md against src/anesthesia_sim/data/ once through the Message Batches API, on the API credits, for statements that contradict a stored value, each other, or a cited unit, and file each confirmed finding: a strongest-model second reading of the clinical specification that no session's budget has covered
priority: P2
effort: M
status: ready
classes: docs, infra
feature: api-credit-runs
touches: tools/, tests/unit/, docs/items, docs/apparatus.md, docs/maintainer.md, docket.toml
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-19
payoff: the clinical specification gets one full reading by the strongest model against the stored values, so a contradiction a learner could be misled by is found and filed rather than left
verify: grep -qE '^\*\*Findings checked, ' docs/items/PL-5S71-*.md
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
`/v1/messages/batches`, with the model `docket.toml`'s `[models]` table chooses
for the role `review`. The owner runs it on
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

**Built, 2026-10-25.** `tools/model_doc_review.py` builds the batch and
`tests/unit/test_model_doc_review.py` tests how. The model's context is 1M
tokens, so the split the brief inferred is not needed: each of the 25 requests
carries the whole document and all eight data files, about 215,000 tokens,
behind one prompt-cache marker, and asks about one `##` section. That way a
contradiction between two sections can be found, which a request carrying only
its own section would miss. The model returns JSON with three kinds of finding:
`data`, `internal` and `unit`. The cost bound at Fable 5.1's prices, on 2026-10-25, was $66.91. That
bound assumes no cache hit and every request using all 48,000 of its output
tokens. A request after the first that reads the cache pays a fortieth of the
input price, so the bill should be much lower. `docs/maintainer.md` § "Have
a strong model read the model document against the data, once" has the owner's
four steps.

What remains is the owner's run and the check. Until the findings file comes
back, there is nothing here for a session to do. The session that receives it
checks each finding against the document, the data file and the cited source.
It files each confirmed finding as its own item, classed `science` or
`safety`. It records each unconfirmed finding here, with the reason, in a paragraph
that opens `**Findings checked, <date>.**`, which is what this item's
`verify:` looks for, and then closes this item.

**Model, 2026-10-25.** The project owner first refused the Fable 5.1 run:
"Nothing should be using fable anymore unless I specifically say" (project
owner, 2026-10-25). He then corrected that reading. Fable was the example of a
stale model named outside one home, not a ban: "It was more about having a
single source of truth (fable just being an example of a stale model)"
(project owner, 2026-10-25, `PL-J9VC`). `PL-0XDM` (one table for which model
and effort each kind of work uses) moved the choice into `docket.toml`'s
`[models]` table, and `tools/model_doc_review.py` now reads the model, its
effort and its list price from there as the role `review`. Today that is
Opus 5.5 at `high`, the table's default, at a batch price of half its $4 and
$20 list price per million input and output tokens. The cost bound was $27.05
on 2026-10-25.

**Decision** (project owner, 2026-10-25, ratified, over dropping the item):
run the reading once on the model the table chooses for `review`. The reading
is the only full pass of the clinical specification against the stored
values. What is left is the owner's run on his Mac, as `docs/maintainer.md`
§ "Have a strong model read the model document against the data, once" lays
out, and then a session checking and filing each finding.
