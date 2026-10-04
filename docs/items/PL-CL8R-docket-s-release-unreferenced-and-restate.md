---
id: PL-CL8R
title: docket's release.unreferenced and restate_references, and doc_check's _pull_requests_named, read a release-notes bullet one line at a time, so a bullet continued on an indented line is reported unreferenced, restated with a second reference, and dropped from the tag-span check; latent
status: untriaged
feature: one-answer
added: 2026-10-04
---

**Problem.** docket's release.unreferenced and restate_references, and doc_check's _pull_requests_named, read a release-notes bullet one line at a time, so a bullet continued on an indented line is reported unreferenced, restated with a second reference, and dropped from the tag-span check; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. `- PL-ZK3X A long title that goes on\n  and on - #123` gives `unreferenced` ('PL-ZK3X',) where () is meant; `restate_references` (pr 123) writes a second reference into a released file; `_pull_requests_named` returns nothing for that bullet and drops #198 from `- PL-VG7G, PL-ZZZZ - #198 - described\n  in v0.2.11`, which `check_tag_span_covers_its_notes` would then report as named nowhere (by reading). Latent: every span bullet in the notes is one line.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
