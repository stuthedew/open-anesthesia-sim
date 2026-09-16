---
id: PL-M352
title: Every layout operation is reachable without a drag, through a menu and the keyboard, so the area system does not ship an interaction a keyboard-only reader cannot perform
status: blocked
feature: interface-areas
added: 2026-09-16
priority: P2
effort: M
blocked-by: PL-2KXB
classes: feature, ux
touches: src/anesthesia_sim/app/, tests/integration
---

**Problem.** Every layout operation is reachable without a drag, through a menu and the keyboard, so the area system does not ship an interaction a keyboard-only reader cannot perform

**Why it matters.** An area system whose whole operation set is corner and
border drags is unusable from a keyboard, and retrofitting reachability after
the affordances exist is the expensive order. This is deliberately *not*
planned-milestone item 20's general accessibility pass arriving early: the rule
is only that this milestone does not introduce an interaction a keyboard-only
reader cannot perform.

**Done when.** Split, join, resize, swap, close, Workspace switch, rename,
duplicate and delete are each reachable from a menu and from the keyboard, and
a test drives the full operation set without synthesising a drag.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 15.
