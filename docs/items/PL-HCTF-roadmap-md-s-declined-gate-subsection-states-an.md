---
id: PL-HCTF
title: ROADMAP.md's declined-gate subsection states an entry count nothing validates: #706 added PL-ZMGR as an entry and left the heading at 174, and doc_check passes the same section at 174, 191 or 999
priority: P3
effort: S
status: needs-decision
classes: docs, infra
touches: ROADMAP.md, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-19
---

**Problem.** ROADMAP.md's declined-gate subsection states an entry count nothing validates: #706 added PL-ZMGR as an entry and left the heading at 174, and doc_check passes the same section at 174, 191 or 999

**Measured 2026-09-19 while closing `PL-2P9L`** (the triage pass that added
seventeen entries to that subsection). `python3 tools/doc_check.py check` was
run against the same tree with the heading reading `174 entries`, `191 entries`
and `999 entries` in turn. All three report `0 errors, 0 advisories`. Nothing
holds that number to anything.

**`origin/main` is stale by one today, which is the instance rather than the
argument.** `#706` (`PL-ZMGR`) added a declined entry to the subsection on
2026-09-19 and left the heading at `174`. Nothing said so, and the session that
wrote it had no way to be told. `PL-2P9L` then added seventeen and bumped to
`191`, which preserves the existing off-by-one rather than repairing it - the
true total is one higher than whatever the heading says until somebody
reconciles it.

**Why it matters.** `tools/doc_check.py`'s own module docstring says a stated
count "in a group heading over the entries it counts" is checked against the
entries below, and gives the reason: "The same number reached six places in
`ROADMAP.md` once." A reader who knows that rule reads this heading as checked.
It is not, and this is the one section where the count carries weight - the
subsection exists to be a *complete* record of what the gate declined, so a
reader comparing "191 entries" against `bin/docket wave`'s figures is comparing
against a number maintained by hand and demonstrably drifting.

**Not `PL-0VFF`**, which is that the list does not distinguish a still-open
declined entry from a closed one. This is the stated total, and it is wrong
before the open/closed question is even asked.

**Shape of a fix, not chosen.** The hard part is that "entry" here is not "id
mentioned" - the subsection names ids for context as well as for disposition,
so a naive count returns 324 against a heading of 174. Two candidates: count
the batch sizes the paragraphs state (each opens with "Eleven more", "Fourteen
more", "One more") and hold the heading to their sum, which is decidable and
matches how the section is actually written; or drop the number from the
heading entirely, on the grounds that a count in a document goes stale the next
time an entry is added - the reasoning the v0.4.0 section already gives for not
recording how many of a gate are closed.

**Done when.** Either the heading's count is held to the entries below by a
check that fails on a drift of one, or the count is removed from the heading
with the reason recorded, and `origin/main`'s current off-by-one is reconciled
either way.

**Decision needed.** Which of the two shapes above governs, since they produce
different work and a `verify:` command cannot be written until one is picked:

1. **Hold the heading to the entries below.** "Entry" here is not "id
   mentioned" - the subsection names ids for context as well as for
   disposition, so a naive count returns 324 against a heading of 191. The
   decidable reading is the batch sizes the paragraphs state ("Eleven more",
   "Fourteen more", "One more"), summed. A check in `tools/doc_check.py` fails
   on a drift of one.
2. **Drop the number from the heading.** A count in a document goes stale the
   next time an entry is added, which is the reasoning the v0.4.0 section
   already gives for not recording how many of a gate are closed.

Either way `origin/main`'s current off-by-one is reconciled. This is a
granular choice whose blast radius is one heading, so it is a session's to
take rather than the project owner's; it sits at `needs-decision` because the
next step is the decision and nothing else can proceed past it.

**Note added by the 2026-09-19 triage pass (`PL-CSV0`).** The heading now
reads `192 entries` rather than the `191` this brief records, and this pass
adds further entries and increments it again. The increments preserve whatever
offset exists rather than repairing it - reconciling the true total is this
item's work, and doing it in a pass that is also adding entries would leave
nobody able to say which number was the corrected one.
