# The prose review's prompt and its test set

Close-out step 8 in `.claude/skills/docket/modes/close-out.md` has a fresh
reviewer judge each long paragraph, docstring and comment that a simulator
branch changed, for the reader that `.claude/rules/plain-writing.md` names.
This folder holds what that reviewer is told, the paragraphs it must never
pass again (`PL-FYGJ`, from `PL-H76S`), and the gold-standard paragraphs it
must keep (`PL-556C`).

- `prompt.md` is the reviewer's prompt. `tools/new_prose.py` prints it before
  the units, and this is its only copy.
- `rejected/` holds one file for each paragraph that the review passed and the
  owner then rejected.
- `gold/` holds one file for each paragraph that the owner named a gold
  standard. Without them, a review that flagged every paragraph would pass.
- `runs/` holds one record for each run of the review on that set.
  `tools/rejected_prose.py` writes them, and nothing else does.

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

`file` decides which readers the reviewer judges the paragraph for, so it must
be a file that a row of the reader table names. The paragraph must read as one
unit of `MIN_WORDS` words or more, as `tools/new_prose.py` reads that file,
because the review never sees a shorter one.

A review's rewrite of the entry may have no more words than the entry allows.
That is the accepted rewrite's length where the entry has one, and the
rejected paragraph's length otherwise, both counted as `tools/new_prose.py`
counts a unit's words. Adding an accepted rewrite applies at once to every
run of the current prompt (`PL-CWRZ`).

## Adding a gold-standard paragraph

Add one only when the owner names a paragraph a gold standard, in those words.
A paragraph he calls acceptable, or says needs no change, stays out. A rewrite
could still improve it, and the review must stay free to propose one (project
owner, 2026-11-03, 03:17Z). The paragraph must read as one unit of `MIN_WORDS`
words or more, as for a rejected entry. Name the file `gold-DATE-SLUG.md`,
where `DATE` is the day the owner named it. Its front matter has `file` and
`named`, and its body has the first three sections of a rejected entry:

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
entry's accepted rewrite and not here, even if he names it a gold standard.
The reviewer would otherwise see both versions of one paragraph and could
compare them, which a real review never can. `check` refuses a gold-standard
entry that repeats a rejected paragraph or an accepted rewrite. The
gold-standard entries share the cap of `CAP_PER_KIND`, as one more kind.

A gold-standard entry needs a run of the current prompt before `check` passes,
because nobody knows whether that prompt keeps it until a run reads it. A new
rejected entry needs none, because it is a known miss of the current prompt.

## Running the set

Run it whenever `prompt.md` changes, a reader-table row changes for a file
that the set holds, or a gold-standard paragraph is added:

1. Run `python3 tools/rejected_prose.py show > show.txt`.
2. Give the whole of `show.txt` to one fresh `general-purpose` reviewer, as
   close-out step 8 does, and save its reply to a file.
3. Run `python3 tools/rejected_prose.py record REPLY`, with that file's path.

The review must flag every rejected entry and keep every gold standard, and each
rewrite must be no longer than its entry allows. If it misjudges one or writes
a longer rewrite, change the prompt and run the set again. `show` mixes the two
kinds of entry in a fixed order, so a unit's position does not tell the
reviewer which kind it is. `python3 tools/rejected_prose.py check` runs in
`make check` and CI. It refuses a prompt with no run, or with a run that
misjudged an entry or wrote a longer rewrite, and a gold-standard entry that no
run of the current prompt has read.
