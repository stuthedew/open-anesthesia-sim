---
id: PL-C25K
title: ROADMAP.md v0.2.8's definition of done says PL-J786 and PL-S4M2 are both confirmed in effect on a real pull request, but PL-J786 is dropped
status: untriaged
added: 2026-09-13
---

**Problem.** ROADMAP.md v0.2.8's definition of done says PL-J786 and PL-S4M2 are both confirmed in effect on a real pull request, but PL-J786 is dropped

**Found 2026-09-13**, working `PL-GLBF` in the Gate 1 decision batch, while
checking the status of every id that section's subset counts name.

`ROADMAP.md:820-824` reads: "The two entries that change repository
configuration rather than the tree — PL-J786 (a green `checks` run required
before merge) and PL-S4M2 (squash-merge) — are confirmed in effect on a real
pull request, not merely described as done."

`PL-J786` is `dropped`, not `done`. So a definition-of-done line for a shipped
release asserts that something was confirmed in effect which was in fact
dropped.

**Why it matters, and why it is P3 rather than higher.** It is the
release-provenance class of error rather than a clinical one — no displayed
value is affected — but `v0.2.8`'s section is what a reader consults to learn
what that release actually guaranteed, and "a green `checks` run required
before merge" is a repository guarantee somebody might rely on. Read `PL-J786`'s
own `reason` before editing: the honest fix depends on whether the requirement
was dropped as unnecessary, superseded, or never achievable, and the sentence
should say which.

**Not the fix: deleting the clause.** The v0.2.8 counts are history for a
shipped release, and `PL-GLBF` decided they stay for that reason. This wants
the sentence corrected, not removed.

**Where.** `ROADMAP.md:820-824`; `docs/items/PL-J786-*.md` for the reason.
