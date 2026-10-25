---
id: PL-J9VC
title: PL-0XDM read the owner's word on Fable as a ban and built an excluded list and a check for it, when Fable was only the example of a stale model named outside one home: drop the exclusion and keep the one-table rule
priority: P2
effort: S
status: done
classes: infra, docs
feature: one-source-of-truth
touches: docs/items, docs/maintainer.md, docs/apparatus.md, subprojects/docket/README.md, subprojects/docket/src/docket/model_choice.py, subprojects/docket/tests/test_model_choice.py, tools/model_home_check.py, tools/model_doc_review.py, tests/unit/test_model_home_check.py, tests/unit/test_model_doc_review.py, docket.toml
deferred-from: v0.7.0 - captured after the freeze, from the owner's correction of PL-0XDM on 2026-10-25
added: 2026-10-25
closed: 2026-10-25
pr: 1792
payoff: the model table carries no Fable rule the owner never asked for, and an open item naming a stale model is still refused
verify: ! grep -q excluded subprojects/docket/src/docket/model_choice.py && ! grep -q 'which \[models\] excludes' tools/model_home_check.py && grep -q 'single source of truth for which model' docs/items/PL-0XDM-keep-which-model-and-effort-each-kind-of-work.md
---

**Problem.** `PL-0XDM` (one table for which model and effort each kind of work uses, merged in #1791) read the owner's word on Fable as a ban. It added an `excluded` list to the `[models]` table naming Fable 5.1's id, a parse rule that the default may not be an excluded model, and a rule in `tools/model_home_check.py` refusing an excluded id outside the table and the records. `docs/maintainer.md` said nothing uses Fable unless the owner names it.

**The owner's correction** (project owner, 2026-10-25): "1791 shouldn't say never fable. It's fable was stale and not currently a used model anywhere. It was more about having a single source of truth (fable just being an example of a stale model)."

**Why it matters.** The owner's word is that the table decides. A rule he never asked for, written into the table and a check, would refuse him a Fable run he chose by adding a rule, and its prose would tell later sessions he had banned a model.

**Done when.** The table has no `excluded` key, and `docket.model_choice` refuses one as an unknown key. `tools/model_home_check.py` has one rule: a model id may appear only in the table, a record, a test or a registered copy. An open item is held to that rule, since the excluded rule was the only thing reading open items and a stale model reached a session through one. `docs/maintainer.md`, `docs/apparatus.md`, the docket README and `tools/model_doc_review.py` say the table decides, with no Fable rule. `PL-0XDM`'s title names the single source of truth rather than Fable, and its brief records the correction. `PL-5S71`'s brief and title no longer prescribe Fable.

**Built, 2026-10-25.** All of the above. `PL-6FX6`'s model-comparison commands name the two models the trial compares, so that item is registered in `COPIES` with that reason. `PL-5S71` was retitled to "the models table's review model", and the owner's answer on it, to run it once on the table's model, is recorded there.

**Generator check.** None. This is one misread of one owner message in one item, not a mechanism that causes items: the fix removes the misread rule and adds nothing that could generate work.
