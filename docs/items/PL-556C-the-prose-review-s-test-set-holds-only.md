---
id: PL-556C
title: The prose review's test set holds only paragraphs the owner rejected, so a review that rewrites every paragraph passes it, and its no-longer-than-rejected word limit is a floor that passed a 149-word rewrite of a paragraph he called overly verbose at 149 words
status: untriaged
feature: reader-tested-prose
added: 2026-11-03
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

**Done when.** The set can hold paragraphs the owner accepted, a run fails
when the review flags one, and `check` reports each run's agreement with the
owner's verdicts.
