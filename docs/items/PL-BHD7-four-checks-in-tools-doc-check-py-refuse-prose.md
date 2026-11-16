---
id: PL-BHD7
title: Four checks in tools/doc_check.py refuse prose by guessing its meaning from words - a "not yet" under the timeline, a word of refusal beside a host, and the two frozen-list entry counts - where the apparatus standard makes the judgment half an advisory; decide which stay errors
status: untriaged
feature: regex-review
touches: tools/doc_check.py, subprojects/docket/src/docket/checks.py
added: 2026-11-16
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
