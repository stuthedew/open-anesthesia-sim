---
id: PL-GPTN
title: docs/interface-provenance.md's Prune entry still says this project's View contract 'should take the shape of Blender's' SpaceType (PL-TH35) and that the project 'should plan to prune such hooks and fields', but PL-TH35 is done: app/view_contract.py defines the View protocol and test_view_contract deletes any member with no call site, so the recommendation reads as open work that has shipped
priority: P2
effort: S
status: ready
classes: defect, docs
feature: interface-provenance-structure
touches: docs/interface-provenance.md
added: 2026-11-07
payoff: a contributor reads the View contract and its pruning as built, and does not start work that has already shipped
verify: ! grep -qF 'should plan to prune' docs/interface-provenance.md
reenters: PL-4FBP
---

**Problem.** The Prune entry in `docs/interface-provenance.md` still describes shipped work as open. It says that this project's contract for a View "should take the shape of Blender's" (`SpaceType`), and that the project "should plan to prune such hooks and fields", but that work is done (`PL-TH35`). `app/view_contract.py` defines the View protocol, and `test_view_contract` deletes any member with no call site.

**Checked 2026-11-09:** `grep -n 'should take the shape\|plan to prune' docs/interface-provenance.md` still finds both phrases in the Prune entry of § "Adopted". The work they recommend has shipped. `app/view_contract.py` defines the `View` protocol (`PL-TH35`, done). `test_every_member_of_the_contract_has_a_call_site_in_the_adapter` in `tests/integration/test_view_contract.py` fails on any member that `app/area_layout.py` never calls, so the contract is pruned by a test.

**Why it matters.** A contributor reads the entry as open work, and may start building a contract and a pruning step that already exist.

**Done when.** The Prune entry says that this project adopted it: the View contract is `app/view_contract.py`'s `View` protocol (`PL-TH35`), and a test fails on any member with no call site.

**Generator check.** Instance of `PL-4FBP`'s fact, "The link between a document sentence and the tree fact it restates": the entry describes the tree as it was before `PL-TH35`, and no check holds a `docs/interface-provenance.md` sentence to the code.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/interface-provenance.md` already says "`PL-TH35` should take the shape and plan for the pruning" (row 438). `PL-TH35` had closed on 2026-10-19, and that tree already holds `app/view_contract.py`. So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.
