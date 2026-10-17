---
id: PL-8ZTQ
title: The wording in docstrings and docs is awkward in many places, and no rule sets a plain default style for what sessions write
priority: P2
effort: M
status: done
classes: docs
feature: prose-quality
milestone: v0.5.25
touches: .claude/rules/plain-writing.md, CLAUDE.md, .claude/rules/sources-and-docstrings.md, .claude/rules/where-new-code-goes.md, docs/resident-instructions.md, tests/unit/test_doc_check.py, docs/items/PL-1K5X-cut-the-padded-comments-and-docstrings-across.md, docs/items/PL-FDMJ-cut-the-padded-comments-and-docstrings-across.md, docs/items/PL-TPS7-cut-the-prose-in-docs-architecture-md-and-docs.md, docs/items/PL-BZR4-cut-docs-model-md-s-prose-for-a-human-reader.md, docs/items/PL-K7N7-cut-roadmap-md-s-prose-for-a-human-reader.md, docs/items/PL-Y55Q-re-measure-whether-prose-written-under-the.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; a writing rule the owner asked for on 2026-10-17, classed by its own design round
added: 2026-10-17
closed: 2026-10-17
pr: 1478
payoff: sessions write docstrings, docs, item briefs, commit messages and replies that a newcomer understands on the first read, instead of copying the dense style around them
verify: grep -q 'Match the code around you, not its prose' .claude/rules/plain-writing.md && ! grep -q '^paths:' .claude/rules/plain-writing.md && grep -q 'plain-writing.md' CLAUDE.md && grep -q 'The plain-writing rule, added 2026-10-17' docs/resident-instructions.md && ! grep -q 'PL-XXBD' .claude/rules/sources-and-docstrings.md
---

**Problem.** The wording in docstrings and docs is awkward in many places, and no rule sets a plain default style for what sessions write

**The ask** (project owner, 2026-10-17, in this item's thread): "The wording
in the doc strings is really awkward in a lot of places. e.g. "Refuse a volume
or tissue:gas coefficient whose capacity is under the agent held." How do we
make the default doc writing style more human readable repo wide going
forward?" The end state is that what sessions write from now on reads plainly
the first time through. Rewriting the existing text is filed as its own work,
not done here.

**What was measured, 2026-10-17.** A blind sample of 91 passages, 13 from each
of seven areas, was rated against seven defects. 42 of the 91 read awkwardly
(46%, Wilson 95% CI 36-56%). The share has risen over time. It was 3 of 10 for
text last edited before 2026-09-01, 13 of 46 from then to 09-20, and 26 of 35
after 09-20 (74%, Fisher exact p = 3e-5). The rise holds within every code and
document area and within each length band (Mantel-Haenszel odds ratio 6.8 by
area and 8.3 by length). Code and tests read worst (7 or 8 of 13 per area). The
instruction files (4 of 13) and item briefs (2 of 13) read best.

The defects are compression, not padding. Each count below is the number of
passages where the defect blocked a first reading, then the number where it
appeared at all.

- Dropped small words, such as "a", "the", "that", "which" and verbs: 28 and 42.
- Ordinary words used in a private sense: 25 and 48. The commonest are "read"
  for decide or interpret (12 passages), "answer" for a return value (11),
  "hold" for enforce or keep (7), "stand" for remain in force (6), "refuse"
  (4), and "floor", "claim" and "reach" (3 each).
- An "it", "this" or "that" whose noun is unclear: 15 and 36.
- A sentence carrying several claims: 13 and 27.
- An item id carrying meaning the sentence does not state: 5 and 15.
- Noun stacks (0 and 2) and padding (0 and 1) barely occur.

Two constructions recur. One is a chain of relative clauses with "that" or
"which" left out, often ending in a stranded preposition: "Each list entry the
plan was not read whole at". The other is a docstring or paragraph that opens
with a phrase and no verb: "This tissue group's own closed form, and not how a
run advances:".

Across all 2,630 docstrings, sentences average about 24 words, against 11.4 in
CPython's standard library. The median docstring is 65 words long, against 14.
The share of docstrings that cite an item id rose from 24% to 43%, and in
`src/anesthesia_sim/core/` from 17% to 58%. No cheap count separates awkward
text from plain text: the article rate and the stranded-preposition count both
failed a validity check against the ratings.

Limits: one rater, from the same model family that wrote the text; `git blame`
dates a line's last edit, not its first draft; and commit trailers stopped
naming the model in early September, so a change of model after 09-20 cannot be
ruled out as part of the cause. The sample, ratings, scripts and full results
are in `/mnt/project-files/v0.6.0/plain-writing/`.

**Why the prose reads this way.** Two causes, and the experiment below tests
both.

1. No rule says how to word a sentence. The only prose guidance a session meets
   is a warning against padding, in the last paragraph of
   `.claude/rules/sources-and-docstrings.md`. The five items in the
   `prose-quality` feature (`PL-1K5X`, `PL-FDMJ`, `PL-TPS7`, `PL-BZR4`,
   `PL-K7N7`, all filed 2026-09-05) say "Wordiness is the defect and cutting it
   is the fix." The measurement finds the opposite defect, so a session
   following them would make the text denser.
2. Sessions copy the prose around them. The harness tells every session to
   "match its comment density, naming, and idiom" when it writes code.
   `.claude/rules/where-new-code-goes.md` asks for one existing instance to be
   read whole, "and yours written to match", and
   `.claude/rules/core-domain.md` names `src/anesthesia_sim/core/tissue.py` as
   the instance to read first, which holds some of the densest prose in the
   tree. Anthropic's own guidance says the style of a prompt shapes the style
   of the response. So each dense docstring makes the next one denser, which
   fits the rise after 09-20.

**What the standards say.**

- *Federal Plain Language Guidelines* (plainlanguage.gov, 2011): "Express only
  one idea in each sentence" (p. 50). "Make sure you use pronouns that clearly
  refer to a specific noun" (p. 32). "Make sure you define your terms" (p. 46).
  Putting "modifiers, phrases, or clauses between two or all three of these
  essential parts", the subject, verb and object, "make[s] it harder for the
  user to understand you" (p. 52).
- *Microsoft Writing Style Guide*: "Include that and who. They help to clarify
  the sentence structure." "Include articles, such as the."
- *Google Python Style Guide* § 3.8.6: "Comments should be as readable as
  narrative text, with proper capitalization and punctuation. In many cases,
  complete sentences are more readable than sentence fragments."
- PEP 257: a docstring's summary line "prescribes the function or method's
  effect as a command".
- Fine AB, Jaeger TF, Farmer TA, Qian T. Rapid expectation adaptation during
  syntactic comprehension. *PLoS One* 2013;8(10):e77661: a reduced relative
  clause is read as the main verb at first, and "who" or "that" removes the
  misreading early.
- Redish J. Readability formulas have even more limitations than Klare
  discusses. *ACM J Comput Doc* 2000;24(3):132-137
  (doi:10.1145/344599.344637): formulas "emphasize countable features at the
  expense of more subtle contributors to text comprehension", which is why no
  count is proposed here.
- Anthropic, *Prompting best practices*
  (platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices):
  "The formatting style used in your prompt may influence Claude's response
  style", and "Examples are one of the most reliable ways to steer Claude's
  output format, tone, and structure."

**The experiment, 2026-10-17.** Three functions had their docstrings removed:
`set_cardiac_output` (`src/anesthesia_sim/core/patient.py`),
`set_inspired_partial_pressure_fraction` (`src/anesthesia_sim/core/circuit.py`)
and `waits_on_read` (`subprojects/docket/src/docket/arming.py`). Three fresh
sessions wrote all three with no rule (A). Three more wrote them with a draft
of the rule in their prompt (B). Three fresh reviewers rewrote the A
docstrings under the same draft (C). Two raters then scored all 30
docstrings, the three originals (O) included. Each rater saw a different
shuffle with no labels, and checked every docstring against the code.

| Group | Awkward, rater 1 and rater 2 | Mean readability, 1 to 5 | Judged too long | Errors |
| --- | --- | --- | --- | --- |
| Originals (O) | 3 of 3, 3 of 3 | 2.5 | none (5 of 6 too short) | none |
| No rule (A) | 9 of 9, 9 of 9 | 2.1 | none | none |
| Rule while writing (B) | 4 of 9, 0 of 9 | 4.6 | none | none |
| Review after writing (C) | 5 of 9, 1 of 9 | 4.6 | 3 of 18 | none |

Every B docstring scored higher than every A docstring (exact Mann-Whitney
p = 4e-5, two-sided, on each docstring's mean score). The rule cut the
average sentence from 22 words to 14. It also made the docstrings about 40%
longer than A's for the same task (200 words against 144), but both raters
judged every B docstring the right length. The A writers did worse than the
originals, and two of them reused sentences from the modules they had read,
which is the copying described above. Every B docstring the stricter rater
still flagged used a project word the draft did not list, such as "answer"
or "the owner's read". The final rule lists them.

Limits: the raters and the writers come from one model family, three
functions is a small sample, and the rule sat in the writer's prompt, where it
is more prominent than a resident file is. `PL-Y55Q` checks the rule in real
sessions.

**Decided in the round.** Each is an obvious call on the measurement or on a
rule this repository already states, so none was put to the owner.

1. **A resident rule file, `.claude/rules/plain-writing.md`, with no
   `paths:`.** Item briefs, commit messages, pull request bodies and replies
   follow no read, so a path scope would miss the texts the owner reads most.
   Subagents load the resident rules, so the rule reaches them too.
2. **It covers all prose a session writes, replies included.** The owner
   asked for "repo wide", and replies cost nothing more once the rule is
   resident. Short interface text, such as a label or a unit, is not prose.
3. **It names what the measurement found:** the small words, the private
   word senses with their plain replacements, stacked clauses, one point per
   sentence, reasons in words with ids as pointers, and clear references. Two
   before-and-after examples from this repository follow, because examples
   steer a model's style more reliably than descriptions do.
4. **It tells sessions to match the code around them, not its prose.** For
   wording, this overrides the harness's instruction to match the surrounding
   idiom. `.claude/rules/where-new-code-goes.md` now says the same where it
   asks a session to copy one existing instance.
5. **The rule alone, with no review step.** The fresh review (C) did no
   better than the rule at writing time (B), and each review cost about
   220,000 to 260,000 tokens. `PL-Y55Q` re-measures in real sessions and names
   the result that would add a review step.
6. **No linter.** No cheap count separated awkward text from plain text, and
   readability is judgment, which `CLAUDE.md` refuses to script.
7. **The existing text is not rewritten here.** The owner asked about the
   default from now on. The five `prose-quality` items named padding as the
   defect, so each gained a note re-aiming it at the rule, and `PL-1K5X`
   starts with the code the rules name as the instance to read first.
8. **The pause on new workflow mechanisms.** `PL-X7D5` is a live generator
   head, so the pause holds, and the owner's request lifts it for this rule
   (`PL-6Q9L`).
9. **Two stale pointers fixed.** `.claude/rules/sources-and-docstrings.md` and
   `docs/resident-instructions.md` cited `PL-XXBD` and `PL-3VKZ` as the
   prose-quality work. Both were dropped on 2026-09-05, and both pointers now
   name the rule.

**Done when.** `.claude/rules/plain-writing.md` exists with no `paths:`, and
`tests/unit/test_doc_check.py` fails if it gains one. `CLAUDE.md`'s preamble
names it. `.claude/rules/where-new-code-goes.md` and
`.claude/rules/sources-and-docstrings.md` point at it.
`docs/resident-instructions.md` records the addition. The five
`prose-quality` items are re-aimed, `PL-Y55Q` is filed, and `make check` is
green.

**Generator check.** Not a generator. The cause produces awkward text, not
queue items: the five `prose-quality` items were filed together on 2026-09-05,
and none has been filed since. The `feature:` field records that they are one
problem.
