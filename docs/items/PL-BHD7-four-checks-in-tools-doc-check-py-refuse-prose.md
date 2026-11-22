---
id: PL-BHD7
title: Four checks in tools/doc_check.py refuse prose by guessing its meaning from words - a "not yet" under the timeline, a word of refusal beside a host, and the two frozen-list entry counts - where the apparatus standard makes the judgment half an advisory; decide which stay errors
priority: P2
effort: M
status: done
classes: defect
feature: regex-review
milestone: v0.6.20
touches: tools/doc_check.py, subprojects/docket/src/docket/checks.py
deferred-from: v0.7.0 - present at the freeze, but a workflow check with no connection to anything on the frozen list or in v0.7.0 Required scope, and it changes nothing a learner sees
added: 2026-11-16
closed: 2026-11-22
pr: 2224
payoff: a correct sentence under the timeline or beside a host name is no longer refused for one word, so sessions stop rewording true sentences to pass a check
reenters: PL-GPJ7
---

**Problem.** Four checks in tools/doc_check.py refuse prose by guessing its meaning from words - a "not yet" under the timeline, a word of refusal beside a host, and the two frozen-list entry counts - where the apparatus standard makes the judgment half an advisory; decide which stay errors

**What each one does.** `PL-8FT2` kept these patterns unchanged and wrote a
`regex:` reason beside each one. Each reason says the pattern guesses at what
a sentence means from its words. The apparatus standard says a hard check
matches a syntax the writer put there on purpose, and the judgment half is an
advisory, never a refusal (`.claude/rules/apparatus-standard.md` § "Read the
fact from its record; where none exists, write one", `PL-GPJ7`). These four
readers in `tools/doc_check.py` raise an error:

1. `NOT_YET_RE`, in `check_timeline_status`, refuses the words "not yet"
   anywhere in a sentence under `ROADMAP.md` § "The timeline" (`PL-0B22`,
   2026-10-24).
2. `HOST_REFUSAL_RE`, in `check_host_claims`, refuses an undated sentence that
   names a host beside a word such as "blocked", "refused", "denied",
   "unreachable" or "cannot reach". It reads every Markdown file, comment,
   docstring, YAML file and JSON string (`PL-CLW5`). `PL-79DP` already moved
   "block" and "blocks" to an advisory after they refused a correct sentence.
3. `ENTRY_COUNT_RE`, in `check_gate_counts`, reads "N entries" in a cell of
   the version table or the timeline that names a release, and refuses a
   count that differs from that release's frozen list (`PL-H8MQ`).
4. `NOT_DELEGABLE_COUNT_RE`, in `check_gate_counts`, reads "N entries are
   marked `not-delegable`" inside a gate subsection, and refuses a count that
   differs from the items' `not-delegable:` fields (`PL-GLBF`).

`DIRECTION_RE` also feeds an error. It reads "above" or "below" after a
quotation to choose which file's headings a section citation is checked
against. It is left out of this question, because the § mark it follows is
the explicit syntax `PL-GPJ7` settled for a section citation.

The seven prose readers in `subprojects/docket/src/docket/checks.py` raise
advisories only, through `brief_contradictions`, so they need no change. The
other two doc_check readers, `HOST_BLOCK_RE` and `UNMARKED_CITATION_RE`, are
advisories already.

**Recommendation.** Keep readers 3 and 4 as errors. Each reads a phrase only
in a place that fixes its meaning, a table cell naming the release or the gate
subsection, and `check_gate_counts` was designed that way so that prose
elsewhere is never read. Demote readers 1 and 2 to advisories, because each
refuses on a word anywhere in a sentence, which is the form `PL-GPJ7` moved
every hard gate off. Both were added after `PL-GPJ7` closed. The count that
would change this is the number of correct sentences each has refused. Take it
first, from the commits that reworded a sentence to pass the check and the
items filed against it. If it is zero for a reader across its history, keep
that reader as an error and record the count here.

**Checked 2026-11-22.** All four readers still raise errors in `tools/doc_check.py`: `NOT_YET_RE` in `check_timeline_status`, `HOST_REFUSAL_RE` in `check_host_claims`, and `ENTRY_COUNT_RE` and `NOT_DELEGABLE_COUNT_RE` in `check_gate_counts`. All four were in the file at the freeze (`git show 0947408:tools/doc_check.py`). A fifth pattern now sits beside them, `HEADING_ENTRY_COUNT_RE`, which reads "N entries" in a gate group's heading. It reads only a heading, a place that fixes its meaning, as readers 3 and 4 do.

**Why it matters.** A hard check that guesses a sentence's meaning from one word refuses correct sentences. A session then rewords a true sentence to pass, at the cost of a red run, and learns to write for the check rather than for the reader. `PL-79DP` already moved two of reader 2's words to an advisory after they refused a correct sentence.

**Done when.** Each of the four readers either raises an advisory rather than an error, or stays an error with this item recording how many correct sentences it has refused across its history and why that count keeps it.

**Generator check.** The fact misread is whether a sentence makes the claim a hard gate checks, when the gate recognises it by wording, which `PL-GPJ7`'s `misread:` states. `PL-GPJ7` closed on 2026-09-26, and readers 1 and 2 were added after it, by `PL-CLW5` (closed 2026-10-06) and `PL-0B22` (closed 2026-10-24). So this is an instance of that head's fact filed after the head closed, recorded as a re-entry of `PL-GPJ7`.

**Result, counted 2026-11-22: all four readers stay errors.** The item asked
for the number of correct sentences each reader has refused, from the items
filed against it and the commits that reworded a sentence to pass it.

1. `NOT_YET_RE` (a "not yet" under `ROADMAP.md` § "The timeline"): 0. No item
   other than `PL-0B22`, which added it, and this one names it or
   `check_timeline_status` (`grep -l` over `docs/items/`). A rewording made to
   pass it happens on a branch before its commit, so `main`'s history cannot
   show one. It reads one section only, whose rows state a milestone's
   status, so the place fixes the meaning, as it does for readers 3 and 4.
2. `HOST_REFUSAL_RE` (a refusal word beside a host): 0 for the words it still
   reads. `PL-79DP` counted 139 sentences on 2026-10-12 that named a host
   beside a word this reader read. The only false refusals were 2 sentences
   whose word was "block", meaning a block of text, and `PL-79DP` moved
   "block" and "blocks" to an advisory. The words left, such as "blocked",
   "refused" and "unreachable", refused no correct sentence in that count.
3. `ENTRY_COUNT_RE` and 4. `NOT_DELEGABLE_COUNT_RE`: 0. Of the 28 items that
   name `check_gate_counts` or either pattern, none reports a correct count
   that either reader refused. The ones about the check report a count it
   could not reach (`PL-4RHP`) or faults in the reader of a gate group's
   heading (`PL-L0K3`, `PL-V7CG`, `PL-VQBY`).

A count of zero keeps each as an error, as § "Recommendation" said it would.
