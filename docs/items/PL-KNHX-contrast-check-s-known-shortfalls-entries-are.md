---
id: PL-KNHX
title: contrast_check's KNOWN_SHORTFALLS entries are never checked against the requirements they excuse, so a stale one lingers and inflates the reported shortfall count
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.5.11
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py
added: 2026-09-06
closed: 2026-09-24
pr: 996
verify: grep -q 'def test_a_shortfall_naming_no_declared_requirement_is_an_error' tests/unit/test_contrast_check.py && uv run pytest tests/unit/test_contrast_check.py
---

**Problem.** `KNOWN_SHORTFALLS` is keyed by a requirement's identity, but
nothing checks that each key still names a requirement `REQUIREMENTS`
declares. `analyze` only ever reads the dict *from* a requirement - `unexpected`
and `repaired` both start from the evaluated results - so an entry whose
requirement was renamed, retyped or deleted is never visited by anything.

**Why it matters.** It rots silently in the one direction the list was built to
prevent. The docstring's promise is that the list cannot rot, and the mechanism
behind it - a shortfall that starts passing is an error - only fires while the
requirement still exists. Delete or re-key the requirement and its excuse
survives it, unread. `format_report` also prints `len(KNOWN_SHORTFALLS)` as the
shortfall count in its verdict line, so a stale entry overstates the number of
known gaps in the header a reader trusts most.

PL-GNN1 is the near miss: it re-keyed the three agent badges from
`("sevoflurane.fill", "BACKGROUND")` to the disjunction's own key. Removing the
matching shortfall entry was in that item's "Done when" and was done, but had
it been missed nothing would have failed - the verdict line would simply have
read one shortfall higher than the tool could account for.

**Where.** `tools/contrast_check.py` (`analyze`, `Report`, `format_report`);
`tests/unit/test_contrast_check.py`.

**Done when.** A shortfall entry naming no declared requirement is an error in
the same class as one that has started passing, with a message saying the entry
is stale rather than that the pair is fine, and a test covers it.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". No paragraph there named it apart from this entry line, so it rested on the section's opening ground, which is quoted in `PL-36R4`'s brief.

> - PL-KNHX (S) contrast_check's KNOWN_SHORTFALLS entries are never checked against the requirements they excuse, so a stale one lingers and inflates the reported shortfall count
