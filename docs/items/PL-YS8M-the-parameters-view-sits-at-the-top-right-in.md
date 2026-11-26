---
id: PL-YS8M
title: The Parameters View sits at the top right in the Default Workspace but under the chart on the left in Induction and Maintenance, so the controls move when the reader switches tabs
priority: P2
effort: S
status: ready
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/data/workspaces/default.json
added: 2026-11-26
payoff: a reader switching Workspace tabs finds the setting controls in the same place every time
---

**Problem.** The Parameters View is the top-right Area of the Default
Workspace (`src/anesthesia_sim/data/workspaces/default.json`), but the strip
under the concentration chart on the left in the Induction and Maintenance
Workspaces. A reader who switches tabs finds the controls somewhere else. The
project owner found this on 2026-11-26 before his v0.7.0 test drive: "I don't
like how the controls move between tabs."

**Why it matters.** A reader who changes a setting after switching Workspaces has to search for the control first, and may reach for an empty place. The setting controls change the run, so they are the controls a reader most needs to find without looking.

**Best practice.** Read on 2026-11-26:

1. Nielsen Norman Group's consistency heuristic says to decide where page and
   button elements live and keep them in the same place on every page where
   that applies (Krause R, "Maintain Consistency and Adhere to Standards
   (Usability Heuristic #4)", 10 January 2021,
   https://www.nngroup.com/articles/consistency-and-standards/, full text).
2. Items that keep a fixed position are found again faster, because readers
   learn where they are (Gutwin C, Van Der Kamp M, Storring J, Cockburn A,
   Phillips C, "Testing the Limits of the Spatial Approach", Graphics Interface
   2020, https://graphicsinterface.org/wp-content/uploads/gi2020-22.pdf; full
   text read through section 5.1.2). Scarr et al., CHI 2013,
   doi:10.1145/2470654.2466430, reaches the same conclusion, but only its
   abstract was read.
3. Blender's manual page on workspaces could not be read: docs.blender.org
   refuses automated fetching.

**Decision.** Put the Parameters View under the concentration chart on the
left in all three shipped Workspaces, as Induction and Maintenance already do.
Only `default.json` changes: its left column becomes the chart above the
Parameters strip at 0.9 and 0.1, and its right column holds the bookmarks and
branch Views. This is a placement choice, decided in the session and told to
the owner (`.claude/rules/instruction-writing.md` rule 14). The owner may
still choose the right-hand column instead.

**Generator check.** No generator. The three shipped Workspaces were composed in separate items (`PL-KXTL`, `PL-L59K`), and nothing compared where they put the same View. The test this item adds is that comparison.

**Done when.** The Parameters View is the Area under the concentration chart
in every shipped Workspace, and a test fails if a shipped Workspace puts it
anywhere else.
