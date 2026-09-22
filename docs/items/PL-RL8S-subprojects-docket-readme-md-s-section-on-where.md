---
id: PL-RL8S
title: subprojects/docket/README.md's section on where the settings are resolved from says nothing about where a git read gets the store, which is the sibling question PL-T441 just made uniform
priority: P3
effort: S
status: ready
classes: docs
feature: count-input-addressing
touches: subprojects/docket/README.md
added: 2026-09-22
payoff: a reader pointing --items elsewhere can learn from the README where a git read takes the store from, not only where the settings come from
verify: grep -qF 'PL-T441' subprojects/docket/README.md
---

**Problem.** subprojects/docket/README.md's section on where the settings are resolved from says nothing about where a git read gets the store, which is the sibling question PL-T441 just made uniform

**Reproduced 2026-09-22 (`PL-14QR`, triage).** § "Where the settings are resolved from, and
why the run says so" (`subprojects/docket/README.md` line 3075) runs to line 3126
without the word `git`, and the README cites `PL-T441` nowhere.

**Why it matters.** The section answers "which project's policy governs this
run". `PL-T441` answered the sibling question, which directory a git read takes
the store from: every such read now uses the tracked directory rather than
`config.items_dir`. A reader pointing `--items` somewhere else needs both
answers. The README gives only the first, so the failure `PL-T441` fixed - a
store elsewhere silently finding no closures - is the one a reader has no way to
learn about.

**Done when.** The section, or one beside it, says where a git read takes the
store from and why, citing `PL-T441`.
