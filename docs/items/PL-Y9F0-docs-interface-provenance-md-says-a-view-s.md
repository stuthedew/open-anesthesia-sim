---
id: PL-Y9F0
title: docs/interface-provenance.md says a View's chrome is the View's business and the Area only allocates the rectangle, but each Area has a header with the Area menu and the View chooser: does the View or the Area own the header? (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: done
classes: defect, docs
feature: interface-provenance-structure
milestone: v0.6.17
touches: docs/interface-provenance.md
added: 2026-11-05
closed: 2026-11-09
pr: 2072
payoff: a contributor building a View knows the Area draws the header, and does not give one View a second header
verify: ! grep -qF "should likewise leave a View's chrome to the View" docs/interface-provenance.md
reenters: PL-4FBP
---

**Problem.** docs/interface-provenance.md says a View's chrome is the View's business and the Area only allocates the rectangle, but each Area has a header with the Area menu and the View chooser: does the View or the Area own the header? (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/interface-provenance.md at cfb15a4a, before the line edit):

- **Query on who owns the header:** rows 441-445 say "A view's chrome is the view's business, and the area only allocates the rectangle". Rows 1081-1100 give each Area a header that opens the Area menu and holds the View chooser. In this project, does the View or the Area own the header? The answer belongs in the Adopted or Diverged list.

**Checked 2026-11-09:** `grep -n "chrome to the View" docs/interface-provenance.md` finds § "What an editor must implement", which ends: "The container supplies no title bar, and the area that holds the editor only allocates the rectangle that the container computes. This project's contract should likewise leave a View's chrome to the View." The code took the other route. `app/area_layout.py` says in its module docstring that "The container draws the header, not the View, so every View gets the same header" (`PL-TH35` Q11, `PL-MS34`, `PL-50PZ`). `app/view_contract.py` lists the Area's header under "What is not the View's". The header holds the View chooser, and a right-click on it opens the Area menu. So in this project the Area owns the header, which departs from Blender. § "Diverged, and each divergence has a specific cause" does not record that departure.

**Why it matters.** A contributor reads a recommendation that the code has refused, and may build a header into a View. That would give one View two headers and break the rule that every View presents the same contract.

**Done when.** § "What an editor must implement" no longer recommends leaving a View's chrome to the View. § "Diverged, and each divergence has a specific cause" has an entry saying that the container draws each Area's header, which holds the View chooser and opens the Area menu, with its reason and `PL-TH35`.

**Generator check.** Instance of `PL-4FBP`'s fact, "The link between a document sentence and the tree fact it restates": the recommendation describes a design that `PL-TH35` settled the other way, and no check holds a `docs/interface-provenance.md` sentence to the code.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/interface-provenance.md` already says "A view's chrome is the view's business" (row 443), while that tree's `app/area_layout.py` already says "The container draws the header, not the View". So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.
