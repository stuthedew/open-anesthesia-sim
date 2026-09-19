---
id: PL-5MT4
title: core/matrix_exponential.py cites a DOI that does not resolve (10.1137/S0036144502418010 has a spurious trailing 10; the real one is 10.1137/S00361445024180) and its provenance note now half-wrongly says the bibliographic indexes are refused by the egress proxy
priority: P2
effort: S
status: done
classes: defect
touches: src/anesthesia_sim/core/matrix_exponential.py
added: 2026-09-19
closed: 2026-09-19
verify: grep -qF 'doi:10.1137/S00361445024180' src/anesthesia_sim/core/matrix_exponential.py && ! grep -qF 'S0036144502418010' src/anesthesia_sim/core/matrix_exponential.py
---

**Problem.** core/matrix_exponential.py cites a DOI that does not resolve (10.1137/S0036144502418010 has a spurious trailing 10; the real one is 10.1137/S00361445024180) and its provenance note now half-wrongly says the bibliographic indexes are refused by the egress proxy

**Where.** `src/anesthesia_sim/core/matrix_exponential.py`, in the module
docstring's citation of Moler and Van Loan — the source the scaling-and-squaring
method is argued against. The anchor is the string `doi:10.1137/` in that file;
it occurs once.

**Two defects in one sentence, both found 2026-09-19 under `PL-BSYZ`.**

1. **The DOI does not resolve.** The file cites
   `doi:10.1137/S0036144502418010`. `https://doi.org/10.1137/S0036144502418010`
   returns `404` and the DOI Foundation's "Error: DOI Not Found" page; Crossref
   returns `Resource not found` for the same string. The registered DOI is
   `10.1137/S00361445024180` — the cited form carries a spurious trailing `10`.
   `https://doi.org/10.1137/S00361445024180` returns `302` to
   `https://epubs.siam.org/doi/10.1137/S00361445024180`.

   **Everything else in the citation is correct** and needs no change. Crossref's
   record for the registered DOI gives *SIAM Review*, volume 45, issue 1, pages
   3-49, 2003 — matching the docstring's `2003;45(1):3-49` exactly. So this is a
   transcription error in the identifier alone, not a mis-citation: the
   first-page reading the docstring describes was accurate.

2. **The provenance note's parenthetical is now half wrong.** It reads "the
   publisher and the bibliographic indexes are both refused by this
   environment's egress proxy, so the volume, issue, pages and PII above are
   read off the article's own first page rather than from an index."

   Measured 2026-09-19 after the network policy moved to `Custom`: the
   **publisher half is still true** — `epubs.siam.org` answers `000`, the
   gateway refusing the CONNECT. The **index half is now false** —
   `doi.org` `301`, `api.crossref.org` `302`, `api.openalex.org` `429`, all
   reached. That asymmetry is the whole point and the fix should preserve it
   rather than delete the sentence: the reason the metadata was read off the
   first page was true when it was written, and the publisher is still
   unreachable today.

**Why it matters.** A citation that does not resolve is a provenance defect in
`core/`, which `CLAUDE.md`'s safety-critical standard holds to traceability:
a reviewer asked to check why this numerical method was chosen cannot reach the
source from the identifier the file gives them. It is also the narrowest
possible failure — four of the five bibliographic fields are right — which is
exactly the kind that survives review by looking correct.

**How it was found.** Only reachable because the policy opened. The DOI had
been unverifiable from this environment since the file was written, which is
what the parenthetical says; the first session able to resolve a DOI found it
dead on the first try.

**Done when.** The identifier is corrected to `10.1137/S00361445024180` and the
parenthetical states the split that now holds — publisher refused, indexes
reachable — with its date, rather than claiming both.

**Not fixed under `PL-BSYZ`** because `CLAUDE.md`'s fix-now door requires the
fix to touch no file outside the current item's `touches`, and `PL-BSYZ` is
scoped to `.claude/rules/citing-sources.md`.
