# The prose review's prompt and its test set

Close-out step 8 in `.claude/skills/docket/modes/close-out.md` has a fresh
reviewer judge each long paragraph, docstring and comment that a simulator
branch changed, for the reader that `.claude/rules/plain-writing.md` names.
This folder holds what that reviewer is told, and the paragraphs it must
never pass again (`PL-FYGJ`, from `PL-H76S`).

- `prompt.md` is the reviewer's prompt. `tools/new_prose.py` prints it before
  the units, and this is its only copy.
- `rejected/` holds one file for each paragraph that the review passed and the
  owner then rejected.
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

Optional: the version the owner accepted, once there is one.
````

`file` decides which readers the reviewer judges the paragraph for, so it must
be a file that a row of the reader table names. The paragraph must read as one
unit of `MIN_WORDS` words or more, as `tools/new_prose.py` reads that file,
because the review never sees a shorter one.

## Running the set

Run it whenever `prompt.md` changes, or a reader-table row changes for a file
that the set holds:

1. Run `python3 tools/rejected_prose.py show > show.txt`.
2. Give the whole of `show.txt` to one fresh `general-purpose` reviewer, as
   close-out step 8 does, and save its reply to a file.
3. Run `python3 tools/rejected_prose.py record REPLY`, with that file's path.

The review must flag every entry. If it keeps one, change the prompt and run
the set again. `python3 tools/rejected_prose.py check` runs in `make check` and
CI, and refuses a prompt with no run, or with a run that kept an entry.
