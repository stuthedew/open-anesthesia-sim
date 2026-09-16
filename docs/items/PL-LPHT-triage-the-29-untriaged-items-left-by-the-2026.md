---
id: PL-LPHT
title: Triage the 29 untriaged items left by the 2026-09-16 area-model audit and the release-seam sweep
priority: P2
effort: M
status: done
classes: planning
feature: queue-hygiene
touches: docs/items, ROADMAP.md
added: 2026-09-16
closed: 2026-09-16
pr: 626
verify: bin/docket check && python3 tools/doc_check.py check && bin/docket triage | grep -q '^1 item is untriaged'
---

**Problem.** Twenty-nine items reached the queue untriaged on 2026-09-16 - most
of them from `PL-BNYF`'s area-model audit, the rest from the release-seam and
CI sweeps of the same day - and an untriaged capture is invisible to
`bin/docket next`, so every one of them was work nobody could be offered.

**Why it matters.** `docket.toml` sets `untriaged_stale_days = 14` on the
ground that "past this, an untriaged capture has become a second queue nobody
reads". Twenty-nine at once is that failure arriving in a day rather than a
fortnight: the largest single block of untriaged work this store has held,
filed by an audit whose whole purpose was to make the area model's gaps
visible. Left unfielded they would have been visible only to a reader who
opened the directory.

**Done when.** Every item carries the fields `docket check` requires, a status
that says what its next step actually is, and a brief with the three required
sections; the one item a branch was already editing is skipped and named; the
debt classes the pass creates are dispositioned against the current gate, so
`make check` is green rather than red on eighteen undisposed debt items.

**What the pass decided.** `PL-PX7V` was skipped - `bin/docket show` reports its
file already edited on `origin/claude/wizardly-maxwell-dyzpjt`, and a second
answer here is a second resolution of the same file.

Of the twenty-eight triaged, twelve are `ready` with a `verify:` command that
was run and watched fail for the right reason; five are `needs-decision`; and
eleven are `blocked-by: PL-NMTF`, which is the head of the area-model cluster -
no open item builds `ROADMAP.md` item 34's area system, and none of its design
prerequisites can be answered against an unscoped milestone.

`blocked-by` names `PL-NMTF` rather than a version because item 34 is a
planned-milestone entry that § "The timeline" gives no row, so
`checks.py` `_check_references` has no milestone to hold a version form to -
which is `PL-D584`'s finding, applied.

Four of the eleven are `safety`-classed and are seated at `P2` under
`anticipated`, the exemption `checks.py` grants a `blocked` item whose concern
does not exist until a later feature is built. The hazard each describes needs
the splitter handles to be live, and `src/anesthesia_sim/app/qt_widgets.py:784`
makes them inert until item 34.

**What it cost, and the one thing it left behind.** Assigning those classes
took `tools/doc_check.py`'s safety-class gate advisory from one named item to
five, because that advisory reads only the frozen list and not the
`### Declined to Gate ...` subsection the deferrals were written into.
`PL-R0Q0` is that defect and is now the item to do first.
