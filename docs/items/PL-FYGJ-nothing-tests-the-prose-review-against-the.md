---
id: PL-FYGJ
title: Nothing tests the prose review against the paragraphs the owner has rejected, so the review can pass again a kind of text he has already turned down
priority: P1
owner-priority: P1, 2026-11-02
effort: M
status: ready
feature: reader-tested-prose
touches: .claude/skills/docket/modes/close-out.md, docs/prose-review/rejected
blocked-by: PL-1XC7
added: 2026-11-02
payoff: the prose review cannot pass again a kind of text the owner has already rejected
verify: grep -q 'prose-review/rejected' .claude/skills/docket/modes/close-out.md
---

**Problem.** The owner is the only clinician who reads this project's prose.
When he rejects a paragraph that the review passed, his reading is lost once
the thread ends, and nothing stops the review passing the same kind of text
again. Studies of document testing find that real readers catch problems that
expert review misses (de Jong and Lentz 1996, J Tech Writ Commun
26(4):507-519) (`PL-H76S`, fault 1).

**Why it matters.** Without the owner's rejections kept as a test, each change
to the review can lose what an earlier rejection taught, and the same failure
reaches him again.

**What to build.** Decided in `PL-H76S`'s design round (project owner,
2026-11-02, 23:41Z, ratified, over a sixth plain-writing pattern), with the
limits the owner asked about at 22:14Z.

1. **The set.** A folder, `docs/prose-review/rejected/`, holds one short file
   per entry: the paragraph, the owner's words with their date, the kind of
   failure, and the accepted rewrite where one exists.
2. **What is added.** Only a miss: a paragraph that the review passed and the
   owner then rejected. A rejection that the current review already catches
   adds nothing.
3. **How it stays small.** At most 59 entries for each kind of failure, such
   as jargon, length, a reason a developer cannot use, or a reason with no
   source. A sixtieth miss of a kind replaces the oldest entry, and git
   history keeps the one replaced. If the review flags all 59, the chance that
   it misses a paragraph of that kind is below 5%, at 95% confidence. With
   two entries, the cap first proposed, the same bound is about 78%. The bound
   after zero misses in n tries is 1 - 0.05^(1/n) (Hanley JA, Lippman-Hand A.
   If nothing goes wrong, is everything all right? Interpreting zero
   numerators. JAMA. 1983;249(13):1743-1745. PMID 6827763). It treats the
   entries as independent, so it is a best case. The owner set the cap
   (project owner, 2026-11-03, 00:22Z to 00:26Z: "Let's keep more than two
   examples for each reject type? Seems like slightly too small of a sample
   size?", then, after the bounds for 5% and 10% were given, "Lets keep at
   59"). Entries come only from his rejections, so most kinds will take a long
   time to reach the cap.
4. **The first entries.** One for each kind that `PL-H76S`'s six versions of
   the release-check paragraph show.
5. **The test.** Whenever close-out step 8's prompt changes, the review runs on
   the set and must flag every entry. The branch records the result, and a
   check refuses a branch that changes the prompt without that record.
6. **The habit.** Close-out step 8 says to add an entry when the owner rejects
   a paragraph that the review passed.

**Done when.** The folder holds the first entries, step 8 says when to add one
and that a prompt change runs the review on the set, and a check refuses a
prompt change with no recorded run.

**Generator check.** Part of the fix for `PL-H76S`, the live generator for
prose that passes every check and fails its reader.
