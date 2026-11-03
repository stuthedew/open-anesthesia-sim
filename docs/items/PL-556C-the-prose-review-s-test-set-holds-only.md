---
id: PL-556C
title: The prose review's test set holds only paragraphs the owner rejected, so a review that rewrites every paragraph passes it, and its no-longer-than-rejected word limit is a floor that passed a 149-word rewrite of a paragraph he called overly verbose at 149 words
priority: P1
effort: M
status: done
feature: reader-tested-prose
touches: docs/prose-review, tools/rejected_prose.py, tests/unit/test_rejected_prose.py, .claude/skills/docket/modes/close-out.md, docs/apparatus.md
deferred-from: v0.7.0 - apparatus for the prose review, built on the owner's request of 2026-11-03 rather than ranked by the release gate
added: 2026-11-03
closed: 2026-11-03
pr: 1965
payoff: a review that flags every paragraph it reads fails the prose review's test, so the test shows whether the review keeps the owner's gold-standard paragraphs as well as flags those he rejected
verify: grep -q 'GOLD_DIR' tools/rejected_prose.py && grep -q 'def test_a_run_that_flagged_a_gold_standard_entry_fails' tests/unit/test_rejected_prose.py
---

**Problem.** The rejected-paragraph test (`PL-FYGJ`, `PL-CWRZ`) holds only
paragraphs the owner rejected. A run passes when the review flags each one
and no rewrite has more words than the paragraph it replaces. Two gaps follow.

1. A review that rewrites every paragraph it reads passes the test. Nothing
   in the set is a paragraph the review should keep, so the test cannot see a
   review that flags good text.
2. The word limit is a floor. It catches a rewrite that grows the text, which
   four of five rewrites did on the first run. It passed a 149-word rewrite of
   the paragraph the owner called "overly verbose" at 149 words, in two of the
   last three runs. The reviewer also writes to whatever limit it is given:
   told "no longer than the original", four of its five rewrites came out at
   exactly the original's count.

The owner asked on 2026-11-03 at 02:46Z why the limit is the rejected
paragraph's length, and whether that is arbitrary. The answer is that it is
the one length the owner has judged, and that it is a floor.

**Why it matters.** Close-out step 8 has the writer apply the review's
rewrites. A review that flags text the owner would accept makes the writer
rewrite good prose, and the test as it stands cannot see that.

**Generator check.** Not a generator. The mechanism behind it is `PL-H76S`,
closed spent on 2026-11-03. This item and `PL-HLQK` are two gaps in the test
that `PL-FYGJ` built, fewer than the three items a generator causes.

**What best practice says.**

- Whether text works is measured by testing it with its readers. Counts are
  a weak stand-in: readability formulas "emphasize countable features at the
  expense of more subtle contributors to text comprehension", next to "direct
  usability testing with typical readers" (Redish JC. Readability formulas
  have even more limitations than Klare discusses. ACM J Comput Doc.
  2000;24(3):132-137. https://doi.org/10.1145/344599.344637). The ISO plain
  language standard selects content by the reader's need: "Leave out content
  that readers do not need" (ISO 24495-1:2023, clause 5.1.6 d, quoted from
  the ISO/FDIS draft). Neither sets a word count for a paragraph.
- The review is a language model judging text, so it is checked the way any
  such judge is: by its agreement with human verdicts on cases of both kinds.
  Zheng et al. found strong model judges agree with human preferences over
  80% of the time, and that "all LLMs may be prone to verbosity bias", which
  they define as favouring "longer, verbose responses, even if they are not as
  clear" (Zheng L, Chiang WL, Sheng Y, et al. Judging LLM-as-a-Judge with
  MT-Bench and Chatbot Arena. NeurIPS 2023 Datasets and Benchmarks Track.
  https://arxiv.org/abs/2306.05685, section 3.3).

**Proposed.**

1. Add paragraphs the owner accepted to the set as entries the review must
   keep. A run then fails on a missed rejection or on a flagged acceptance,
   so a review that flags everything no longer passes.
2. Report a run as its agreement with the owner's verdicts, how many of each
   kind it got right, beside the pass or fail.
3. Keep the no-growth limit as a floor. Where the owner has accepted a
   version of a paragraph, its length is the target, as `PL-CWRZ` already
   allows.

The accepted paragraphs come from the owner's reads of the resumed
`docs/MODEL.md` rewrite. Change 1 can be built before any exist, and fails no
run until the first is added.

**Decided 2026-11-03.** Build change 1 now (project owner, 2026-11-03,
03:00Z, ratified, over waiting until the first accepted paragraph exists).
Change 2 is `PL-HLQK`, which waits for the first gold-standard entry. Change 3
needs no work, because `PL-CWRZ`'s accepted rewrite already sets a rewrite's
limit to the length of the version the owner accepted. The owner's request
lifts the pause on new workflow machinery for this change.

**Which paragraphs the review must keep** (project owner, 2026-11-03, 03:17Z:
"gold standard paragraphs should be specifically identified"). Only a
paragraph the owner names a gold standard, in those words, becomes an entry.
At 03:14Z he said that the paragraphs he has accepted so far were acceptable
but not gold standards. A paragraph that is acceptable, or that needs no
change, stays out: a rewrite could still improve it, and a test that the
review must keep it would punish that rewrite. The session first proposed
"needs no change" as the bar, and the owner refused it. So the folder starts
empty.

The design, decided by the building session:

1. Gold-standard paragraphs live in `docs/prose-review/gold/`, one file each,
   named `gold-DATE-SLUG.md`. The front matter gives `file` and `named`, the
   date the owner named the paragraph. The body has the same three sections
   as a rejected entry, and "The owner's words" quotes him naming it. `gold`
   can never be a failure kind, so an entry's name says which folder it
   belongs to, in the run records as well. The folder is named for the bar,
   so that a later session does not read "accepted" as enough.
2. Every run of the current prompt must keep each gold-standard entry it
   read.
3. A new gold-standard entry needs a run of the current prompt, where a new
   rejected entry does not. A rejected entry is a known miss of the current
   prompt, so a run would only confirm it. Nobody knows whether the current
   prompt keeps a gold standard until a run reads it.
4. The gold-standard entries count as one kind under the cap of 59 per kind.
   The bound the cap rests on then applies to flagging a gold standard: if
   the review keeps all 59, the chance that it flags one is below 5%, at 95%
   confidence (Hanley and Lippman-Hand, 1983).
5. `show` numbers the units in the order of each entry's name hashed with
   SHA-256, so a unit's position does not show which folder it came from.
6. A rejected entry's accepted rewrite is not shown as a unit. Shown beside
   its rejected original, it lets the reviewer compare the two versions,
   which a real review never can. `check` refuses a gold-standard entry whose
   text repeats a rejected paragraph or an accepted rewrite.

**Done when.** The set can hold paragraphs the owner named gold standards, and
a run of the current prompt fails when the review flags one or has not read
one.
