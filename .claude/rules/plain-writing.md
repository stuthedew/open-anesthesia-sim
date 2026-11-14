# Write plainly

**Resident, with no `paths:`.** It applies whenever a session writes prose. A
path scope would miss item briefs, commit messages, pull request bodies and
replies, because no read comes before them. `PL-8ZTQ` has the sources behind
the points about sentences, and `PL-J1ZM` has the measurements behind choosing
what goes in.

Write all prose that a person will read in plain English: docstrings, comments,
error messages, documents, rules, item briefs, commit messages, pull request
titles and bodies, replies, and every question or review request sent to the
project owner, including each field of the line `bin/docket arm` prints. In
a question or a review request, say what changes for the owner or a learner,
and never name a test, check or tool by its internal name (project owner,
2026-11-02, `PL-BGN1`). Write for the readers that the table below names for
that kind of text. They should understand each sentence the first time they
read it (project owner, 2026-11-02, ratified, `PL-H76S`).

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
| `docs/MODEL.md` | A clinician or educator | Anesthesia pharmacology and physiology. | Numerical-methods terms such as "operator split", software terms, e-notation such as "4e-4", and this repository's own names. | Decide whether to trust a displayed value, or learn how the simulation works. |
| `docs/MODEL.md` | A developer, or someone who forked the project | Python, and the basics of anesthesia. | Numerical-methods terms such as "first-order method", and this repository's own names. | Change a value or an equation for a goal of their own. |
| `README.md` | An educator or trainee in anesthesiology or critical care | Anesthesia and critical care. | Software terms, numerical-methods terms, and this repository's own names. | Decide whether to use the simulator, then install it and run a case. |
| `README.md` | A contributor who knows both anesthesia and code | Anesthesia, Python and software development. | This repository's own names and history. | Decide whether to work on the simulator, then set it up. |
| `docs/ARCHITECTURE.md`, `docs/interface-provenance.md`, `docs/machine-abstraction.md` and `docs/machine-survey.md` | A contributor who knows both anesthesia and code | Anesthesia, Python and software development. | This repository's own names and history, and the outside designs and machines it studied. | Find where a change belongs, and what it must keep. |
| `docs/machine-survey.md` and `docs/references/` | A clinician or educator | Anesthesia pharmacology, physiology and equipment, and how to read a paper's methods. | Software terms, and this repository's own names. | Check a stored value, or a difference between machines, against its published source. |
| `ROADMAP.md` | The project owner, or a contributor deciding what to build next | Anesthesia, critical care, and what the project is for. | The internal names of tests, checks and tools, and decisions taken in sessions they did not see. | Decide what a release holds and what it leaves out. |
| `docs/consultant-brief.md` | An outside reviewer: a new session given the text below the brief's dividing line as its first message | Python, anesthesia and software review. | This repository, its history and its rules. | Review the repository critically, and report what it finds. |
| Docstrings and comments in `src/` and `tests/` | A Python developer who knows the basics of anesthesia | Python, and the basics of anesthesia. | This repository's own names and history, and any numerical-methods term the code does not explain. | Change the code, or check that it is right. |
| String literals in `src/`, such as interface notices and refusal messages | A learner: a trainee in anesthesiology or critical care using the simulator | Anesthesia and critical care. | Software terms, numerical-methods terms, and this repository's own names. | Act on a notice beside a value, or learn from a refusal which condition failed and the value that failed it. |
| String literals in `src/`, such as interface notices and refusal messages | A Python developer who meets the message in a log, a traceback or a test | Python, and the basics of anesthesia. | This repository's own names and history. | Find the input that failed and its value, and fix it. |
| Replies, and questions and review requests to the project owner | The project owner, an anesthesiologist and intensive-care physician | Anesthesia, critical care, and what the project is for. | The internal names of tests, checks and tools, and what the session did. | Make a decision, or learn what changed. |
| Item briefs in `docs/items/`; the workflow's files in `.claude/`, `tools/`, `subprojects/docket/src/`, `CLAUDE.md`, `docs/apparatus.md`, `docs/maintainer.md`, `docs/worker.md`, `docs/resident-instructions.md`, `docs/WORKING_NOTES.md`, `docs/dead-ends.md` and `docs/prose-review/README.md`; and commit messages | A later session, or the owner reading the history | Python, anesthesia, and this repository's rules. | What the writing session knew and did not write down. | Pick up the work, or find out why a change was made. |
| Pull request titles and bodies, which the squash merge makes the commit message on `main` | The project owner deciding whether a change can merge, or anyone reading `main`'s history later | Python, anesthesia, and this repository's rules. | What the writing session knew and did not write down. | Decide whether the change can merge, or find out why it was made. |

The two `README.md` rows are the readers that `README.md` § "What it is for"
names. `docs/releases/` has no row, because `bin/docket release` writes each
note from item titles, and an edit there would make a note disagree with its
item. `python3 tools/new_prose.py --compare`, which close-out step 8 runs,
reads this table to choose the files it compares, so the table keeps its five
columns.

**Where the rest goes.** Decision history goes in the item. In `docs/MODEL.md`,
detail of the numerical method goes in a note for developers at the end of its
section, a paragraph that opens with "**For developers.**", because the
document must specify the numerical method (`PL-TZ7R`). That note may name the
tests for the paragraphs directly above it (`PL-W8FL`). State a model
limitation only where it could change what a clinician concludes from a
displayed value (`PL-BS6N`).

**Take the reason for a chosen value from a record.** Where a docstring, a
comment or a note for developers explains a chosen value, such as a tolerance
or a limit, take the reason from the code or test that uses the value, or from
a cited record. When the reason is not at hand, trace the value's history
first, with `git log -S` and the items. Search for the value as the code
writes it: a 0.5% tolerance was `5e-3` in the test that used it. When the
trace finds no reason, file an item for the missing record, and say in the
text what the trace found. Never state a reason that no record holds.

1. **Write whole sentences.** Keep the small words that show how a sentence
   fits together: "a" and "the", "that", "which" and "who", and the verb.
   Start a docstring or a paragraph with a sentence, not a phrase and a colon.
2. **Do not stack clauses.** "Each entry the plan was not read whole at" makes
   the reader work out where each clause ends. Write "Each entry at which the
   plan was not read in full."
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
   nothing.
8. **Check every sentence before the text goes to its reader.** Go through
   the finished text one sentence at a time. Is each word used in its everyday
   sense? Does the text say which one each paper, file, rule or item is? Does
   each value, unit, condition and count match its source? Is any phrase
   copied from the files the text describes? Would you say the sentence that
   way to a colleague? Fix what fails, and recommend a text to the project
   owner only after this check (project owner, 2026-11-11, `PL-J1ZM`).

**A pull request title names the change plainly and briefly.** The title
becomes the squash commit's subject, the one line of `main`'s history that a
reader sees for the change. After the item ids that the `pr-title` check
requires, write a short phrase rather than a whole sentence: what the change
does, to what, and the reason when it fits. Use names a reader of the
repository already knows, such as a CI job, a check or a panel, not a term
coined while building the change. Give each number the thing it counts. When a
branch closes several items, name what they change together.

**Match the code around you, not its prose.** Copy the structure, naming and
idiom of the code you are working in. Much of the existing prose here breaks
the points above, so do not copy its sentences. Write each sentence you add or
change plainly, even when the text around it is dense. Rewriting sentences you
did not need to touch is work for its own item, in the `prose-quality`
feature.

This rule decides how a text is worded and ordered, and what it leaves out. The
safety-critical standard in `CLAUDE.md` and `.claude/rules/sources-and-docstrings.md`
decides which facts a docstring, an error message or a displayed value must give,
and this rule never cuts one of those: a unit, a value, a condition or a citation.
`.claude/rules/instruction-writing.md` decides the shape of a reply. Code,
commands, paths and quoted output stay exactly as they are.

## Examples

**A paragraph of `docs/MODEL.md`**, for a clinician. The project owner accepted
the second version on 2026-11-04 (`PL-ZDZ0`).

Before: "One count of the MAC line is therefore 0.02 percentage points of
sevoflurane, 0.012 of isoflurane and 0.06 of desflurane. That is coarser than
the percent readout beside it for every agent. This property keeps the two
units from contradicting each other. A reader must never be able to watch the
MAC digit move while the percent digit stays still. That would assert that the
model resolved something it does not. [...] A per-agent MAC resolution would
put different magnitudes at the same glyph position. That is the failure that
'Why the resolution is uniform rather than per-compartment' rejects below,
arriving across agents instead of across compartments."

After: "The smallest change the MAC readout can show is therefore 0.02
percentage points of sevoflurane, 0.012 of isoflurane and 0.06 of desflurane,
never less than the percent readout's. The two readouts round separately, so
the MAC value can occasionally change while the percent stays the same."

**A docstring**, for a developer. Say what the function returns or does, with
its unit, then what it refuses, then anything a developer would get wrong
without being told. Leave out what the signature, the body or a named type
already shows.

Before: "Return this group's blood flow $`Q_i`$ in L/min, at the given cardiac
output. The flow is the group's perfusion fraction of the cardiac output. The
group stores no flow, so this method computes it wherever the flow is read
(`PL-HQF5`). The cardiac output is an argument because the patient holds it.
For a group in a patient, it is `PatientCompartments.cardiac_output_l_min`.
The result is a plain `float`, and no supported-range check applies to it. It
needs none. The perfusion fraction is above 0 and at most 1, so the flow is
never negative and never more than the checked cardiac output. A cardiac
output of zero, which is circulatory arrest, gives a flow of zero. Raises:
TypeError: `cardiac_output_l_min` was not built as a `CardiacOutput`. A bare
`float` is refused whatever its value, and a value built as another checked
quantity is refused as a swapped argument."

After: "Return this group's blood flow $`Q_i = f_iQ`$ at a cardiac output, in
L/min. `docs/MODEL.md` § "Tissue groups" defines it. The group stores no flow
of its own, so no write can leave its flow out of step with the cardiac output
(`PL-HQF5`). Raises: TypeError: `cardiac_output_l_min` was not built as a
`CardiacOutput` (`core/supported_ranges.py`)."

A docstring that is too compressed is the opposite failure, and the fix is
whole sentences.

Before: "Refuse a volume or tissue:gas coefficient whose capacity is under the
agent held."

After: "Reject a volume or tissue:gas partition coefficient that would make the
tissue's capacity less than the amount of agent it already holds."

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
>    residents? I recommend it. Who is the first-pass learner, and are the
>    four candidate tasks right? Can you supply the full text of Zhang et al.
>    2003?
> 2. Approve or decline the one-control trial in PL-BVC5 (how the controls
>    are drawn). I recommend approving it.
> 3. Press Tab in the app on your Mac and tell me whether Start shows a focus
>    mark. That settles PL-CXYV (the run buttons' missing pressed and focus
>    states).

**A pull request body.** `.claude/skills/pull-request/SKILL.md` § "Write the
title and body" has two.

**A pull request title.** The project owner judged three versions of one
title, on `#1523`, on 2026-10-17:

- Too cryptic: "PL-ZWQS: give the first CI part 2 of every 5 ordinary tests".
  A reader cannot tell what a "CI part" or an "ordinary test" is, or what the
  2 and the 5 count.
- Too conversational: "PL-ZWQS: make CI's two test jobs finish at about the
  same time". It describes a hoped-for effect and does not say what changed.
- Plain: "PL-ZWQS: rebalance the CI test split to offset part 1's lint steps".
  It names the change, what it changes and why.
