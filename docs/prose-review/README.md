# The copy editor's test set and examples

**The copy editor runs only when the project owner asks for it**, to rewrite
a section of a document or a whole document (project owner, 2026-11-11,
ratified, over a copy edit of each branch's text at close-out, `PL-J1ZM`).
It edits the text for the readers that `.claude/rules/plain-writing.md`
names. Until 2026-11-11 close-out step 8 ran it on each passage that a branch
changed, and `bin/docket arm` held a simulator branch until a `Prose-review:`
trailer recorded the edit. Both were removed: the copy editor edits sentences
after they are written, and it did not remove an account that the reader does
not need. A blind judge preferred its edit for six of seven document sections
(`PL-HGZS`), so it stays for that work. The copy editor's prompt is
`.claude/agents/copy-editor.md`, and `tools/copy_edit.py` runs it. Where the
first read rewrites a passage, the tool starts a fresh run of the copy editor
to audit that edit, because experienced technical editors make at least two
passes (`PL-HGZS`). It audits again while the last audit changed something,
up to four reads. The tool's `--reads DIR` option keeps each read's request and
reply, so that what each audit changed can be judged on its own.

A separate meaning check then compares each edited passage with its text
before the edit (`.claude/agents/meaning-check.md`). It sends each statement
the edit lost back to the copy editor to restore. Each round of checks runs
the check `CHECK_PANEL` times, set in `tools/copy_edit.py`, because separate
runs on one edit find different losses. The tool keeps a passage as it was
where a statement is still lost after the last of `MAX_CHECK_ROUNDS` rounds
(`PL-F0Q2`). The tool merges the replies. The copy editor does not edit text
written only for a later session or the project owner, such as an item brief
or a reply, so `tools/new_prose.py` prints none (project owner, 2026-11-10).

This folder holds the paragraphs the copy editor must never pass again
(`PL-FYGJ`, from `PL-H76S`) and the gold-standard paragraphs it must keep
(`PL-556C`).

- `rejected/` holds one file for each paragraph that the review passed and the
  owner then rejected.
- `gold/` holds one file for each paragraph that the owner named a gold
  standard. Without them, a review that flagged every paragraph would pass.
- `runs/` holds one record for each run of the review on the test set.
  `tools/rejected_prose.py` writes them, and nothing else does.
- `examples/` holds one file for each before-and-after pair that the owner
  approved. The copy editor is shown none of them until there are three
  pairs of different kinds (project owner, 2026-11-04, ratified, `PL-J1ZM`).
- `model-reverse-outline.tsv` is a reverse outline of `docs/MODEL.md` as it
  stood at commit `50af1a2e` on 2026-11-10. It has one row for each
  paragraph, list, table, code block and heading, with the reader who needs
  it, what kind of text it is and where it would best live. `PL-9RLM` says
  how it was made, and nothing reads it but a session.
- `model-description-draft.md` is a draft of the model's description for a
  clinician, written from that outline for the project owner to read
  (`PL-B07T`). It is not the specification, which is `docs/MODEL.md`, and
  nothing reads it.

## Adding an entry

Add one only when the owner rejects a paragraph that the review passed. A
rejection that the review already flagged adds nothing, because the set exists
to catch the review's misses.

Name the file `KIND-DATE-SLUG.md`, where `KIND` is one of the kinds that
`FAILURE_KINDS` in `tools/rejected_prose.py` defines and `DATE` is the day of
the rejection. Where the miss fits no kind, add one there with its meaning. A
kind holds at most `CAP_PER_KIND` entries. When a new miss would pass that
number, delete the oldest entry of its kind, which git history keeps.

An entry looks like this:

````markdown
---
kind: jargon
file: docs/MODEL.md
rejected: 2026-11-02
---

## Paragraph

```text
The paragraph, exactly as it stood in its file.
```

## The owner's words

"The owner's words, quoted" (project owner, 2026-11-02, 20:03Z, and where
they were said).

## Where it came from

The item, pull request or commit that wrote the paragraph.

## Accepted rewrite

```text
Optional: the version the owner accepted, once there is one.
```
````

The `file` field decides which readers the copy editor judges the paragraph
for, so it must be a file that a row of the reader table names. The paragraph
must be one unit that `tools/new_prose.py` would print from that file.

Where the owner objected to particular words, add a `fault` field after
`rejected`, holding those words exactly as the paragraph has them:

```text
fault: The three maxima come from two classes of vaporizer.
```

A run that rewrites the paragraph but keeps those words counts as a miss,
because a rewrite that changes only the words around them leaves the fault the
owner rejected. Case, line breaks and bold type do not count as a change.

## Adding a gold-standard paragraph

Add one only when the owner names a paragraph a gold standard, in those words.
Leave out a paragraph that the owner calls acceptable or says needs no change.
A rewrite could still improve it, and the review must stay free to propose one
(project owner, 2026-11-03, 03:17Z). As for a rejected entry, the paragraph
must be one unit that the review would read. Name the file
`gold-DATE-SLUG.md`, where `DATE` is the day the owner named it. Its front
matter has `file` and `named`, and its body has the first three sections of a
rejected entry:

````markdown
---
file: docs/MODEL.md
named: 2026-11-05
---

## Paragraph

```text
The paragraph, exactly as it stands in its file.
```

## The owner's words

"The owner's words naming it a gold standard, quoted" (project owner,
2026-11-05, 14:10Z, and where they were said).

## Where it came from

The item, pull request or commit that wrote the paragraph.
````

When the owner accepts the rewrite of a rejected entry, record it as that
entry's accepted rewrite and not here, even if the owner names it a gold
standard. The copy editor would otherwise see both versions of one paragraph
and could compare them, which a real review never can. The `check` command
refuses a gold-standard entry that repeats a rejected paragraph or an accepted
rewrite. The gold-standard entries share the cap of `CAP_PER_KIND`, as one
more kind.

A gold-standard entry needs a run of the current prompt before `check` passes,
because nobody knows whether that prompt keeps it until a run reads it. A new
rejected entry needs none, because it is a known miss of the current prompt.

## Running the set

Run it whenever `.claude/agents/copy-editor.md` or
`.claude/agents/meaning-check.md` changes, a reader-table row changes for a
file that the set holds, or a gold-standard paragraph is added:

1. Run `python3 tools/rejected_prose.py show > show.txt`.
2. Run `python3 tools/copy_edit.py show.txt` and save its whole reply to a
   file.
3. Run `python3 tools/rejected_prose.py record REPLY`, with that file's path.

The copy editor must flag every rejected entry and keep every gold standard.
If it misjudges one, change the prompt and run the set again. `show` mixes the
two kinds of entry in a fixed order, so a unit's position does not tell the
copy editor which kind it is. `python3 tools/rejected_prose.py check` runs in
`make check` and CI. It refuses a prompt with no run, or with a run that
misjudged an entry. It also refuses a gold-standard entry that no run of the
current prompt has read.

## Reviewing a whole document

Review a rewrite of a whole document, such as `docs/MODEL.md`, in two parts
(project owner, 2026-11-04: "We should just run documents one section at a
time for line by line edits but look at whole documents as well for
structure. Two part review"):

1. Run `python3 tools/copy_edit.py --structure FILE` and save its reply. This
   read rewrites nothing. It lists each fact given in two sections, each
   paragraph in the wrong section or written for another reader, sections out
   of order, and each heading that does not say what its section holds. A
   document of more than about 6,000 words is read one chapter at a time. The
   read of each chapter ends with an outline of one line per paragraph, and a
   last read takes all the outlines together.
2. Apply the findings you accept to the document, before any line edit,
   because a sentence that is about to move would be edited for nothing.
   Never line edit a document ahead of its restructure, even when applying
   the findings by hand would take hours (project owner, 2026-11-07,
   ratified, over filing the restructure as items and line editing first).
   `docs/MODEL.md` was line edited first in `#2049`, and that edit dropped
   about 120 statements that had to be restored. It also edited paragraphs
   that the restructure will cut as repeats. A document that was line edited
   before its restructure gets the restructure next. Step 3 then runs only on
   the sections that the restructure changed.
3. Run `python3 tools/copy_edit.py --sections FILE` and save its reply. It
   line-edits each section alone, from its heading to the next heading of any
   level, with the audits that every run has.

The copy editor does not edit the prose that a branch changes. The writing
session checks that text itself, at close-out step 8.

## Judging edits blind

Once the copy editor's instructions have settled, test whether a reader who
does not know which version is the edit prefers the edit. Use sections that
the instructions were not tuned on (`PL-HGZS`):

1. For each section, make a directory named for it, such as `reset/`.
2. In that directory, save the output of
   `python3 tools/new_prose.py --section FILE --heading "HEADING"` as
   `request.txt`. `HEADING` is the section's heading text without its `#`
   marks. For a whole document, review it in two parts as § "Reviewing a whole
   document" says, and save each section's request this way.
3. Run `python3 tools/copy_edit.py DIR/request.txt` and save its whole reply
   as `DIR/reply.txt`.
4. Run `python3 tools/prose_judge.py OUTDIR reset/request.txt
   reset/reply.txt ...`, with every section's request and reply.

The judge is `.claude/agents/prose-judge.md`. `tools/prose_judge.py` runs it
as `tools/copy_edit.py` runs the copy editor: alone, with Read as its one tool.
For each passage the copy editor rewrote, the judge gets the two versions as
A and B, in an order drawn from a fixed seed, and the readers of the file.
It is not told which version is the edit.

The tool prints one line for each passage: `edit` where the judge chose the
copy editor's version, `original` where it chose the text before the edit, and
`same` where it found no difference that matters to the reader. `OUTDIR` keeps
the judge's request and reply, `key.json`, which says which version was the
edit, and `result.json`, which holds each verdict against the key. Read in
full each passage that the edit lost, and each fact the judge found in only
one version, before the copy editor returns to use. A word count decides no
verdict.
