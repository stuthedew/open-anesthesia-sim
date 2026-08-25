---
id: PL-RZPX
title: Advise at grooming when an open item declares no touches
status: untriaged
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py
added: 2026-08-25
---

**Problem.** `docket concurrent` reports an item with no declared `touches` as
unanalysed rather than safe, and nothing surfaces that gap.

**Why it matters.** Concurrency is ruled out, never certified. An item with no
`touches` silently weakens that guarantee for every item it is compared
against.

**Where.** `subprojects/docket/src/docket/checks.py` (`_groom`).

**Notes.** From PL-B043. Deliberately an **advisory, not an error**: making
`touches` mandatory taxes capture, which is the objection that dropped PL-035.
`Report` already splits errors from advisories. Currently 0 of 36 open items
lack `touches`, so this guards a clean condition rather than clearing a
backlog.

**Done when.** Grooming reports open items with no declared `touches`, without
failing the build.
