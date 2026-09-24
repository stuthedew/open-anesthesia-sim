---
id: PL-DDYD
title: bin/docket arm decides auto-merge arming, and CLAUDE.md names it instead of restating start mode's catalog
priority: P2
effort: M
status: blocked
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, CLAUDE.md, .claude/rules/instruction-writing.md, docs/resident-instructions.md
blocked-by: PL-NST2, PL-0TD9
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
---

**Problem.** bin/docket arm decides auto-merge arming, and CLAUDE.md names it instead of restating start mode's catalog

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

`arm` answers for HEAD: `arm` (exit 0) when the net `base...HEAD` diff lies under `items_dir`, no unreleased claim is bound to this branch, and the branch is not behind main; `hold` (exit 1) naming the claim or the paths; `behind N` (exit 1, `PL-S5MF`'s clause); `unknown` (exit 2) when the base or a ref could not be read. Replace CLAUDE.md's arming catalog, the subject-parsing sentences at :408 and :488, and rule 14's guard bullet. Name what each replaces (the file gets shorter). Leave blocked-releases on a constant until the owner answers. The arming bullet becomes: "Whether it arms is `bin/docket arm`'s answer, asked before arming and before every later push while a pull request is open."

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- `bin/docket arm` prints one of its four answers with the documented exit code.
- `CLAUDE.md`'s arming rule names `bin/docket arm` and restates no catalog of claim shapes.

**Build order.** After `PL-NST2`, `PL-0TD9`.
