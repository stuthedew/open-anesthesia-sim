---
id: PL-3R6L
title: Let bin/docket next print a model and effort recommendation from an evidence table the model review writes, beside the fixed model_guidance flag, only for item types whose pre-registered trial met its bar
priority: P2
effort: S
status: done
classes: session-cost, infra
feature: model-evidence
milestone: v0.6.0
touches: model-evidence.toml, subprojects/docket/src/docket, subprojects/docket/tests, subprojects/docket/README.md
added: 2026-10-17
closed: 2026-10-19
pr: 1681
payoff: a session picking an item sees the evidence-backed model and effort for its type beside the fixed flag, with no judgment scripted into docket
verify: grep -rq 'model-evidence.toml' subprojects/docket/src/docket && grep -q 'model-evidence.toml' subprojects/docket/README.md
---

**Problem.** Let bin/docket next print a model and effort recommendation from an evidence table the model review writes, beside the fixed model_guidance flag, only for item types whose pre-registered trial met its bar

**Why it matters.** `Item.model_guidance` in `subprojects/docket/src/docket/model.py`
is a fixed rule: a safety or science class, or an open decision, warrants the
strongest model, and everything else is silent. The owner wants the queue's
suggestion to come from evidence as the model review (`PL-63CB`) produces it.
Decided (project owner, 2026-10-17, ratified, over docket computing
recommendations from the ledger itself, and over editing the fixed rule by
hand per finding): the review writes a small table, docket reads it and never
derives it, which keeps the judgment out of the script as `CLAUDE.md` § "Prefer
deterministic tooling over repeated model work" asks. Only an item type whose
pre-registered trial met its bar appears in the table, so an empty table
changes nothing a session sees.

**Done when.** `model-evidence.toml`, beside `docket.toml`, holds entries that
map item attributes (class, lane, effort size, decision status, and any
attribute the review found predictive) to a model, an effort level, the
evidence date, the trial id in the register and its n. `docket.model` reads it
through the configuration it already loads; `bin/docket next` and `bin/docket
show` print the matching entry's model and effort beside the existing
`model_guidance` flag, with its evidence date; `delegable` is unchanged; a
test covers the print and the empty-table case; `subprojects/docket/README.md`
documents the file.

**Generator check.** Work the owner asked for on 2026-10-17; a one-off.
