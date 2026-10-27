---
id: PL-D29S
title: Save the backfilled per-finding coding of the blind review passes (41 merged pull requests, #1766 to #1863) as docs/blind-review-findings.tsv with a note on how it was coded, because it is the only per-finding data from before the per-pass Blind-review record and exists only in a session's scratch directory
status: untriaged
feature: review-panel
added: 2026-10-26
touches: docs/blind-review-findings.tsv, docs/blind-review-findings.md
verify: test "$(tail -n +2 docs/blind-review-findings.tsv | wc -l)" -eq 133 && grep -q 'lower bound, not a point estimate' docs/blind-review-findings.md
---

**Problem.** On 2026-10-26 a session coded every blind review finding that the descriptions of 41 merged simulator pull requests describe: 133 rows, each with its pass, severity, outcome, whether it repeats a pass-1 finding, a fault type and a target. Every `Blind-review:` record merged so far uses the older totals form, so this coding is the only per-finding data the project has from before the per-pass record (`PL-0BRY`). It exists only in that session's scratch directory, which is deleted when the session is archived. The project owner asked for it to be saved on 2026-10-26, through the `PL-0BRY` session.

**Done when.** `docs/blind-review-findings.tsv` holds the 133 rows, and `docs/blind-review-findings.md` says how each column was coded, which pull requests the rows cover, what the rows cannot show, and that the capture-recapture figure is a lower bound.
