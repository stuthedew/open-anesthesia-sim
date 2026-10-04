---
id: PL-CL8R
title: docket's release.unreferenced and restate_references, and doc_check's _pull_requests_named, read a release-notes bullet one line at a time, so a bullet continued on an indented line is reported unreferenced, restated with a second reference, and dropped from the tag-span check; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/roadmap.py, tools/doc_check.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1352
payoff: a release-notes bullet is read as its own paragraph, so a wrapped reference is neither reported missing nor written a second time, and the span check declines what it could not read
verify: grep -qF '"release notes, ' tests/unit/test_doc_check.py && grep -qF '"tag span, ' tests/unit/test_doc_check.py
---

**Problem.** docket's release.unreferenced and restate_references, and doc_check's _pull_requests_named, read a release-notes bullet one line at a time, so a bullet continued on an indented line is reported unreferenced, restated with a second reference, and dropped from the tag-span check; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. `- PL-ZK3X A long title that goes on\n  and on - #123` gives `unreferenced` ('PL-ZK3X',) where () is meant; `restate_references` (pr 123) writes a second reference into a released file; `_pull_requests_named` returns nothing for that bullet and drops #198 from `- PL-VG7G, PL-ZZZZ - #198 - described\n  in v0.2.11`, which `check_tag_span_covers_its_notes` would then report as named nowhere (by reading). Latent: every span bullet in the notes is one line.

**Reproduced 2026-10-04, at triage.** `unreferenced` reads `- PL-ZK3X A long title that goes on\n  and on — #123` as `('PL-ZK3X',)`, `restate_references` appends a second reference to its first line, and `check_tag_span_covers_its_notes` reports `#11` named nowhere in a span whose notes name it on a wrapped bullet.

**Why it matters.** A release's notes are its permanent record: the restate writes a wrong second reference into a released file, and the span check turns `make check` red over notes that are right.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** Every reader takes a notes bullet's text whole through docket's list walker, and declines one carried on from the margin by name, pinned by `release notes, ...` and `tag span, ...` cases in `PL-R417`'s guard.

**Built 2026-10-04 (`#1352`).** `release.notes_bullets` reads a notes file's bullets through `roadmap.document_entry_lines`, and each bullet's text as its own paragraph through `statement_lines`, joined: a list nested under a bullet is the bullet's but not its text, as `PL-QYBW`'s bullet in v0.5.9's notes shows. `unreferenced`, `restate_references` and doc_check's `_pull_requests_named` read through it, so a wrapped bullet's reference is read, and restated, on its last line. A bullet carried on from the margin is left out and named: on `bin/docket check`'s declined list, and by the span check, which declines that version rather than report what may be named there. Over the 1,421 shipped bullets nothing changed - no restate, no unreferenced bullet, the span check as before. Five guard cases: four fail on main's readers, and the fifth pins the nested list, which main read right by reading one line.
