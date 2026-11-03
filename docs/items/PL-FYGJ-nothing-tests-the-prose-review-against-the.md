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

**Plan for the build, 2026-11-03.** Written by the thread that built
`PL-R7Q6`, `PL-TZ7R` and `PL-1XC7`, which stopped for length before starting
this item. The choices below are a session's, within the design above, and
are open to the session that builds it.

1. **Move the prompt to its own file.** Close-out step 8's prompt moves from
   the fenced block in `.claude/skills/docket/modes/close-out.md` to
   `docs/prose-review/prompt.md`, its one home. `tools/new_prose.py` prints
   that file first, so the session hands the reviewer the tool's whole output
   and copies no prompt by hand. Step 8 keeps a one-paragraph description of
   what the reviewer returns, including the words "would not know", which
   `PL-1XC7`'s `verify:` reads. The check in step 4 can then tell a prompt
   change by the file's content.
2. **The entries.** One Markdown file per entry in
   `docs/prose-review/rejected/`, named `KIND-DATE-SLUG.md`. Front matter
   gives `kind`, `file` (the document the paragraph came from, which decides
   its readers through the reader table) and `rejected` (the date). The body
   has `## Paragraph` (the text as it stood, verbatim), `## The owner's words`
   (quoted, with date, time and where) and, where one exists,
   `## Accepted rewrite`. A short `README.md` in the folder says what an entry
   is, that only a miss is added, and how to run the set.
3. **The first five entries**, all from `PL-H76S`'s evidence above and the
   shared evidence file
   (`v0.7.0/pl-zt47/pl-h76s-evidence-release-check-paragraph.md`). None has
   an accepted rewrite yet, because the `docs/MODEL.md` rewrite is paused.
   - `jargon`: the 20:02Z paragraph, "The 5e-3 relative tolerance was chosen
     when the simulator used the operator split...". Owner, 20:03Z: "this is
     still unintelligible to a human".
   - `length`: the 20:10Z paragraph, "The release check, and why it allows
     0.5%. The simulator moves the model forward...". Owner, 20:17Z: "Way too
     verbose".
   - `unusable-reason`: the 20:20Z paragraph, cut to 12 lines. Owner, 20:30Z:
     "I guess it's overly verbose and I still struggle to understand the why
     behind it or if I am a dev or someone who forked the project, how I would
     use this info to modify these values for a particular goal".
   - `unsourced-reason`: the fifth version's "Why 0.5%" bullet ("No record
     says how it was chosen..."). Owner, 20:40Z: "how do we not know where the
     0.5% came from? We should absolutely know where that came from".
   - `jargon`: the fifth version's "How to change it" bullet ("first-order
     method", "1.4e-11"). Owner, 20:40Z: "the last paragraph is starting to be
     unintelligible again".
4. **A tool, `tools/rejected_prose.py`, with three commands.** It holds the
   kinds, each with a one-line meaning, and the cap of 59 entries per kind as
   constants, so the README points at it rather than restating them.
   - `show` prints the prompt from `docs/prose-review/prompt.md`, the readers
     of each entry's file (through `new_prose.reader_table` and
     `readers_of`), then each entry as a unit in `new_prose`'s format, every
     row marked `>`.
   - `record REPLY` reads the reviewer's reply from a file, counts the
     `[N] rewrite` lines against the entries, and appends one record to
     `docs/prose-review/runs.json`: the date, the SHA-256 of the prompt file,
     the number of entries and the number flagged. The tool is that file's
     only writer.
   - `check` exits 1 when an entry does not parse, names an unknown kind or a
     file no reader-table row names, when a kind holds more than 59 entries,
     or when no record for the current prompt's hash flags every entry it
     ran on. It joins `make check`. A new entry needs no new run, because
     only a miss is added. The next prompt change has to flag it.
5. **Run the set now.** `PL-1XC7` changed the prompt, so this item's first
   run tests that prompt on the five entries, with one `general-purpose`
   subagent at the session's effort level, as step 8 runs. Where the prompt
   misses an entry, revise the prompt in this item and run again.
6. **Step 8's habit line.** When the owner rejects a paragraph that the
   review passed, add an entry under the kind it fits, or add a kind to the
   tool with its meaning. At 59 entries of a kind, the new one replaces the
   oldest.
7. **Docs.** `docs/apparatus.md` gains the tool and the folder.

**Done when.** The folder holds the first entries, step 8 says when to add one
and that a prompt change runs the review on the set, and a check refuses a
prompt change with no recorded run.

**Generator check.** Part of the fix for `PL-H76S`, the live generator for
prose that passes every check and fails its reader.
