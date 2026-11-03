---
id: PL-CWRZ
title: The prose review's rejected-paragraph test passes when the review flags each paragraph, though its rewrites still grow the text: on the first run it flagged all five, and four of its five rewrites came out longer than the paragraph the owner rejected
priority: P1
effort: M
status: ready
feature: reader-tested-prose
touches: docs/prose-review, tools/rejected_prose.py, tests/unit/test_rejected_prose.py, .claude/skills/docket/modes/close-out.md
deferred-from: v0.7.0 - apparatus for the prose review, ranked through its generator PL-H76S rather than by the release gate, as that head's other members were
added: 2026-11-03
payoff: the prose review's rewrites stop handing writers text longer than what the owner rejected, so its advice no longer repeats the fault it flags
verify: grep -q 'no longer than the rows it replaces' docs/prose-review/prompt.md && grep -q 'def test_a_rewrite_longer_than_its_entry_allows_fails' tests/unit/test_rejected_prose.py
---

**Problem.** `PL-FYGJ` built a test of the close-out prose review: each
change to its prompt is run on the paragraphs the owner rejected, and the
review must flag every one. The first run, on 2026-11-03, flagged all five,
so the test passed. But the rewrites the review proposed would likely fail
the owner again. Four of the five came out longer than the paragraph the
owner rejected, as `docs/prose-review/runs/2026-11-03T011944Z.json` records:

| Entry | Owner's objection | Words before | Words in the rewrite |
| --- | --- | --- | --- |
| How to change the limit | unintelligible | 57 | 118 |
| Tolerance chosen under the split | unintelligible | 94 | 126 |
| Release check in 21 lines | "Way too verbose" | 269 | 225 |
| No record of the half percent | no source for the reason | 68 | 95 |
| Release check in 12 lines | overly verbose, no usable reason | 149 | 152 |

The words were counted with `str.split` on each rewrite's fenced block and on
each entry's paragraph as `tools/new_prose.py` reads it.

The rewrites grow because the reviewer restates each number in the reader's
form and defines each term in place, and the prompt says to keep every fact.
For the "Way too verbose" paragraph it moved three sentences out and kept the
rest. This is the second failure in `PL-H76S`: plain words alone produce
length when nothing decides which facts the reader needs here.

**Why it matters.** Close-out step 8 tells the writer to apply the reviewer's
rewrite or write their own. A test that passes when the review flags a
paragraph cannot tell whether the review's rewrite answers the owner's
objection, so the owner can go on rejecting rewritten text while the test
stays green.

**Options for the design round.**

1. Keep the accepted rewrite in each entry once the owner accepts one, and
   compare the review's rewrite with it, at least for length.
2. For an entry of kind `length`, require the review's rewrite to be shorter
   than the rejected paragraph by a margin.
3. Change the prompt so a rewrite carries only what the reader's takeaway
   needs, and says where each other fact goes, such as the section's note for
   developers.

The third changes the review itself. The first two change only what the test
measures. A run of the set would test the third.

**Decided 2026-11-03**, by the session that built `PL-FYGJ`, on the
coordinator's go-ahead to take this item next. This is an internal design of
the review's prompt and its test, so it is a session's call under
`.claude/rules/instruction-writing.md` rule 14. The choice is options 3 and 1,
with option 2's comparison set at no margin:

1. The prompt tells the reviewer to write each rewrite for the reader that the
   paragraph serves where it stands, and to carry only what that reader's
   takeaway needs. Each other fact moves to a place the reviewer names. The
   rewrite is no longer than the rows it replaces.
2. `check` fails a current run whose rewrite of an entry has more words than
   that entry allows. An entry with an accepted rewrite allows that rewrite's
   length, and any other entry allows the length of the paragraph the owner
   rejected. An accepted rewrite is a fenced block, like the paragraph, so it
   can be counted.

`.claude/rules/plain-writing.md` point 7, "Plain is not longer", is the record
for setting no margin. ISO 24495-1, the plain-language standard, says the
same in its guideline on selecting content: "Leave out content that readers
do not need" (clause 5.1.6 d), quoted from the ISO/FDIS 24495-1:2023 draft,
https://cdn.standards.iteh.ai/samples/78907/35c071a9d3bd4608a23200b512460fba/ISO-FDIS-24495-1.pdf;
the published clause was not checked). A margin above zero was refused
because no record supports one.

**Done when.** A run of the set fails when the review's rewrite of an entry
would repeat the objection the owner gave it, and close-out step 8 says how a
writer uses that result.

**Generator check.** A member of `PL-H76S`, the live generator for prose that
passes every check and fails its reader. `PL-H76S` stays open until this is
decided.
