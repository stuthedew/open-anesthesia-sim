---
id: PL-PZ6T
title: verify --self runs whichever verify: command the branch holds, so a close-out can replace a failing commissioned command with a weaker passing one and ACCEPT; the only trace is the front-matter NOTE every close-out prints, the one PL-KSV2 found readers skim
status: untriaged
feature: verify-close-out
added: 2026-09-23
---

**Problem.** verify --self runs whichever verify: command the branch holds, so a close-out can replace a failing commissioned command with a weaker passing one and ACCEPT; the only trace is the front-matter NOTE every close-out prints, the one PL-KSV2 found readers skim

**Generator check.** A re-entry of `PL-KSV2` (closed 2026-09-23) at a
sibling site. `PL-KSV2` stopped a close-out that *deletes* its failing
`verify:`, and this is one that *replaces* it. The shared fact is that `verify
--self` runs the command from the branch under audit, although `falsifies:` is
read from the base's copy of the item. One instance, so there is no cluster.
