# The copy editor's test set and examples

Close-out step 8 in `.claude/skills/docket/modes/close-out.md` has the copy
editor edit each long passage that a branch changed, for the readers that
`.claude/rules/plain-writing.md` names. The copy editor's prompt is
`.claude/agents/copy-editor.md`, and `tools/copy_edit.py` runs it. Where the
first read rewrites a passage, that tool has the copy editor read its own edit
a second time and merges the two replies, as experienced technical editors
work in two passes (`PL-HGZS`). Its `--reads DIR` option keeps each read's
request and reply, so that what the second read changed can be judged on its
own. This folder
holds the paragraphs it must never pass again (`PL-FYGJ`, from `PL-H76S`) and
the gold-standard paragraphs it must keep (`PL-556C`).

- `rejected/` holds one file for each paragraph that the review passed and the
  owner then rejected.
- `gold/` holds one file for each paragraph that the owner named a gold
  standard. Without them, a review that flagged every paragraph would pass.
- `runs/` holds one record for each run of the review on the test set.
  `tools/rejected_prose.py` writes them, and nothing else does.
- `examples/` holds one file for each before-and-after pair that the owner
  approved. The copy editor is shown none of them until there are three
  pairs of different kinds (project owner, 2026-11-04, ratified, `PL-J1ZM`).

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

`file` decides which readers the copy editor judges the paragraph for, so it
must be a file that a row of the reader table names. The paragraph must read
as one unit of `MIN_WORDS` words or more, as `tools/new_prose.py` reads that
file, because the review never sees a shorter one.

## Adding a gold-standard paragraph

Add one only when the owner names a paragraph a gold standard, in those words.
A paragraph the owner calls acceptable, or says needs no change, stays out. A
rewrite could still improve it, and the review must stay free to propose one
(project owner, 2026-11-03, 03:17Z). The paragraph must read as one unit of
`MIN_WORDS` words or more, as for a rejected entry. Name the file
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
and could compare them, which a real review never can. `check` refuses a
gold-standard entry that repeats a rejected paragraph or an accepted rewrite.
The gold-standard entries share the cap of `CAP_PER_KIND`, as one more kind.

A gold-standard entry needs a run of the current prompt before `check` passes,
because nobody knows whether that prompt keeps it until a run reads it. A new
rejected entry needs none, because it is a known miss of the current prompt.

## Running the set

Run it whenever `.claude/agents/copy-editor.md` changes, a reader-table row
changes for a file that the set holds, or a gold-standard paragraph is added:

1. Run `python3 tools/rejected_prose.py show > show.txt`.
2. Run `python3 tools/copy_edit.py show.txt`, as close-out step 8 does, and
   save its whole reply to a file.
3. Run `python3 tools/rejected_prose.py record REPLY`, with that file's path.

The copy editor must flag every rejected entry and keep every gold standard.
If it misjudges one, change the prompt and run the set again. `show` mixes the
two kinds of entry in a fixed order, so a unit's position does not tell the
copy editor which kind it is. `python3 tools/rejected_prose.py check` runs in
`make check` and CI. It refuses a prompt with no run, or with a run that
misjudged an entry. It also refuses a gold-standard entry that no run of the
current prompt has read.

## Judging edits blind

Run this once the copy editor's instructions have settled, on sections that
they were not tuned on. It shows whether a reader who does not know which
version is the edit prefers the edit (`PL-HGZS`):

1. For each section, make a directory named for it, such as `reset/`.
2. In that directory, save the output of
   `python3 tools/new_prose.py --section FILE --heading "HEADING"` as
   `request.txt`.
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
