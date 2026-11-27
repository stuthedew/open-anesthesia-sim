# Write plainly

Write all prose that a person will read in plain English: docstrings, comments,
error messages, documents, rules, item briefs, commit messages, pull request
titles and bodies, replies, and every question or review request sent to the
project owner, including each field of the line `bin/docket arm` prints. In
a question or a review request, say what changes for the owner or a user,
and never name a test, check or tool by its internal name (project owner,
2026-11-02, `PL-BGN1`). Write for the readers that the table below names for
that kind of text. They should understand each sentence the first time they
read it (project owner, 2026-11-02, ratified, `PL-H76S`). The readers of each
document are in `.claude/rules/document-readers.md`, which loads when a
session opens the document (`PL-7YHK`).

**Choose what goes in before you write.** Keep a text short by being selective
about what it includes: leave out each detail that does not change what its
reader does next. The last column of the table says what each reader does. Do
not shorten a text by writing fragments, abbreviations or jargon. What the
session did, tried, measured and checked is the record of the work, and it
goes in the item file. A text for any other reader takes from that record only
what its reader acts on. § "Examples" shows how much each kind of text holds
(project owner, 2026-11-11, ratified, over a copy edit of each branch's text
after it is written, `PL-J1ZM`).

| Kind of text | Reader | What they know | What they do not know | What they will do with it |
| --- | --- | --- | --- | --- |
| Docstrings and comments in `src/` and `tests/` | A Python developer who knows the basics of anesthesia | Python, and the basics of anesthesia. | This repository's own names and history, and any numerical-methods term the code does not explain. | Change the code, or check that it is right. |
| String literals in `src/`, such as interface notices and refusal messages | A user: a clinician in anesthesiology or critical care using the simulator | Anesthesia and critical care. | Software terms, numerical-methods terms, and this repository's own names. | Act on a notice beside a value, or learn from a refusal which condition failed and the value that failed it. |
| String literals in `src/`, such as interface notices and refusal messages | A Python developer who meets the message in a log, a traceback or a test | Python, and the basics of anesthesia. | This repository's own names and history. | Find the input that failed and its value, and fix it. |
| Replies, and questions and review requests to the project owner | The project owner, an anesthesiologist and intensive-care physician | Anesthesia, critical care, and what the project is for. | The internal names of tests, checks and tools, and what the session did. | Make a decision, or learn what changed. |
| Item briefs in `docs/items/`; the workflow's files in `.claude/`, `tools/`, `subprojects/docket/src/`, `CLAUDE.md`, `docs/apparatus.md`, `docs/maintainer.md`, `docs/worker.md`, `docs/resident-instructions.md`, `docs/WORKING_NOTES.md`, `docs/dead-ends.md` and `docs/prose-review/README.md`; and commit messages | A later session, or the owner reading the history | Python, anesthesia, and this repository's rules. | What the writing session knew and did not write down. | Pick up the work, or find out why a change was made. |
| Pull request titles and bodies, which the squash merge makes the commit message on `main` | The project owner deciding whether a change can merge, or anyone reading `main`'s history later | Python, anesthesia, and this repository's rules. | What the writing session knew and did not write down. | Decide whether the change can merge, or find out why it was made. |

**Where the rest goes.** Decision history goes in the item.

1. **Write whole sentences.** Keep the small words that show how a sentence
   fits together: "a" and "the", "that", "which" and "who", and the verb.
   Start a docstring or a paragraph with a sentence, not a phrase and a colon.
2. **Show where each clause begins.** Keep the word that opens a clause, such
   as "which", "that" or "at which", so the reader can see where it ends:
   "Each entry at which the plan was not read in full."
3. **Use words in their everyday sense.** Prose here has drifted into private
   senses that a newcomer cannot guess. Write "returns" and "result", not
   "answers" and "answer"; "review", not "read" as a noun; "treats as", not
   "reads as"; "enforces", not "holds"; "still applies", not "stands";
   "applies to", not "reaches"; "less than", not "under"; and "bypasses", not
   "writes past". Name the rule or the exception you mean instead of calling it
   a "floor" or a "door". When the project needs a term of its own, define it
   where it first appears.
4. **Make one point per sentence.** Put the subject and its verb early and
   close together. When a sentence needs a semicolon, a dash or a second
   parenthesis, split it. Keep a cause and its consequence in one sentence
   where they fit: "One step for all agents keeps the last MAC digit worth the
   same amount whatever the agent", not three sentences joined by "So".
5. **State the reason in words.** An item id, a pull request number or a
   section name can follow as a pointer, but the sentence must make sense
   without it.
6. **Say who does what.** Make each "it", "this" and "that" point at a noun the
   reader can find.
7. **Say each thing once**, where the reader needs it, and cut words that add
   nothing. Give each clause a fact that the rest of its sentence does not
   already state.
8. **State the claim directly.** Name an alternative only where a reader would
   otherwise assume it, and then say why it does not apply.
9. **Write about the subject.** A sentence in a document describes the model,
   the code or the clinical fact. A citation gives the source and its pages.
   Who supplied a source and how a choice was reached go in the item.
10. **Say what the text relies on.** Name a source the text does not use only
    where a reader would otherwise assume it does, and then say it once, as a
    limitation.
11. **Give separate points their own structure.** When a table cell or a
    paragraph holds several separate points, make them a numbered list or a
    short section, and keep the cell to one sentence and a pointer.
12. **Check every sentence before the text goes to its reader.** Go through
   the finished text one sentence at a time. Is each word used in its everyday
   sense? Does the text say which one each paper, file, rule or item is? Does
   each value, unit, condition and count match its source? Is any phrase
   copied from the files the text describes? Would you say the sentence that
   way to a colleague? Fix what fails, and recommend a text to the project
   owner only after this check (project owner, 2026-11-11, `PL-J1ZM`).

The `pull-request` skill says how to write a pull request's title and body.

**Match the code around you, not its prose.** Copy the structure, naming and
idiom of the code you are working in. Much of the existing prose here breaks
the points above, so do not copy its sentences. Write each sentence you add or
change plainly, even when the text around it is dense. Rewriting sentences you
did not need to touch is work for its own item, in the `prose-quality`
feature.

This rule decides how a text is worded and what it leaves out. It never cuts a
unit, a value, a condition or a citation that `CLAUDE.md`'s safety-critical
standard requires. Code, commands, paths and quoted output stay as they are.

## Examples

**A reply**, for the project owner. Lead with the result. Then give what
differs from what the owner was told or expects. Then the closing block, with
each request stated in full, so that the owner can act without opening a file
or an earlier reply. Leave out the record of the work: which checks ran, where
an id was put and what each new item holds are in the item.

> The design round is recorded in three new items, and pull request #2108
> carries them. It merges by itself when its checks pass.
>
> Two things differ from what I told you. About half of the app's style sheet
> calls style a control, where I said a third. The mock-up scripts are not
> saved, and PL-HS9M (the design round's record) describes their colours,
> sizes and layout instead.
>
> **What needs you**, in any order:
>
> 1. Answer the three questions in PL-HS9M (the design round's record). Is
>    the order of work agreed: tasks, evaluation, wireframes, style, then
>    residents? I recommend it. Who is the first-pass user, and are the
>    four candidate tasks right? Can you supply the full text of Zhang et al.
>    2003?
> 2. Approve or decline the one-control trial in PL-BVC5 (how the controls
>    are drawn). I recommend approving it.
> 3. Press Tab in the app on your Mac and tell me whether Start shows a focus
>    mark. That settles PL-CXYV (the run buttons' missing pressed and focus
>    states).
