---
id: PL-GPTN
title: docs/interface-provenance.md's Prune entry still says this project's View contract 'should take the shape of Blender's' SpaceType (PL-TH35) and that the project 'should plan to prune such hooks and fields', but PL-TH35 is done: app/view_contract.py defines the View protocol and test_view_contract deletes any member with no call site, so the recommendation reads as open work that has shipped
status: untriaged
added: 2026-11-07
---

**Problem.** The Prune entry in `docs/interface-provenance.md` still describes shipped work as open. It says that this project's contract for a View "should take the shape of Blender's" (`SpaceType`), and that the project "should plan to prune such hooks and fields", but that work is done (`PL-TH35`). `app/view_contract.py` defines the View protocol, and `test_view_contract` deletes any member with no call site.
