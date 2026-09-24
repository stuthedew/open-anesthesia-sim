---
id: PL-9F8B
title: render.format_queue_edit tells docket show an item is startable without reading its status, so a done item (PL-6T44) and a blocked one (PL-MB2W) are both called startable
priority: P3
effort: S
status: ready
classes: defect
feature: carrier-detection
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - filed after the freeze by the 2026-09-24 triage pass, and not safety or science
added: 2026-09-24
payoff: docket show stops inviting work on an item that is closed or blocked
verify: grep -q 'def test_show_calls_an_edited_item_startable_only_when_its_status_allows' subprojects/docket/tests/test_cli.py
---

**Problem.** render.format_queue_edit tells docket show an item is startable without reading its status, so a done item (PL-6T44) and a blocked one (PL-MB2W) are both called startable

**Found 2026-09-24 at triage**, while reproducing `PL-4RK2`. `bin/docket show
PL-6T44`, a `done` item, prints "Not work in flight - PL-6T44 is startable - but
a second edit to the same file collides at merge". `bin/docket show PL-MB2W`, a
`blocked` one, prints the same line. `render.format_queue_edit` is right that
an edited file is not work in flight. But it states "startable" as a fact
without being given the item's status, and its docstring says it does so "in
as many words".

**Why it matters.** "Startable" is what `bin/docket next` and a session
choosing work act on. Said of a closed or blocked item, it invites work nobody
should start, from the command a session runs to learn about one item.

**Done when.** The line names an item startable only where its status allows
it, and says nothing about startability otherwise. A test in
`subprojects/docket/tests/test_cli.py`, beside
`test_show_names_the_branch_that_has_already_edited_the_item_file`, pins the
done and blocked cases.

**Generator check.** It misreads an item's current queue state, the fact
`PL-6T44` and `PL-8YXJ` state, and is a lead for `PL-RJLQ`'s family verdict
rather than a head of its own.
