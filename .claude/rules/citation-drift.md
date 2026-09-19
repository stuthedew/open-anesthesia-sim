---
paths:
  - "/docs/items/**"
  - "/docs/WORKING_NOTES.md"
  - "/.claude/skills/*/SKILL.md"
---

# When a citation that has drifted is a finding, and when it is not

A sentence in this repository's apparatus that names a tree fact — a path, a
line, a symbol, another item's title or status — is linked to that fact only in
the reader's head. Nothing can tell a statement that is still true from one the
tree has moved past, so each drift is found by a session reading the file, one
at a time, and each one becomes a queue item.

`PL-4FBP` fixed the product half of this and bound its convention to
`docs/MODEL.md` and `README.md`, deliberately leaving the apparatus out.
`PL-G424` is the apparatus half: 21 open items, each a sentence in an apparatus
document asserting a tree fact that is wrong. This file is its recorded
decision (project owner, 2026-09-19, ratified, over extending the
live-versus-dated-assertion convention across the apparatus documents) and
loads on the files it governs.

**Ratified, not specified, so the bar to reopen it is ordinary evidence.** It
was a session's recommendation that the project owner agreed with on one read -
`CLAUDE.md` § "Working with the project owner" is explicit that this is not the
same as a decision they authored, and that "it is what the owner decided" does
not defend it. A measurement, a cost the case did not carry, or a constraint
that has since appeared is enough to put it back to them. The table below is
the case; the closed-brief row is the load-bearing one.

## The decision

**A closed item's brief is a historical record, not a live assertion.** It says
what was true when the work was done, and the tree has moved since. Drift in a
`done` or `dropped` brief is **not a finding**: do not repair it, do not file an
item about it, and do not count it when sizing a cluster. Nothing reads a closed
brief for instruction — it is read for provenance, where "this is what the tree
looked like then" is the correct meaning and the only one available.

**An open item's brief and the standing documents are live**, and a session
acts on them. Drift found there is repaired in place, by the session that finds
it, in the commit it is already making.

**Repairing one does not need an item of its own.** It changes no behavior, and
`bin/docket verify --self` already expects other items' files in a diff — the
capture and leading-id rules put them there. So it rides the current item's
commit under the current item's id, and it does **not** consume `CLAUDE.md`'s
fix-now cap of two, which exists to stop scope creep in code. Filing it instead
is what produced the cluster: a session that cannot repair another item's brief
must capture it, and the capture is the cost, not the wrong line number.

**A line number is not a citation anchor.** Name the symbol, the heading, or a
quoted string — `app/chart_frame.py`'s `trace_style`, not
`app/chart_frame.py:349`. A symbol survives every edit above it and is
greppable; a line number is wrong the next time anything is inserted, and
re-pointing it at a fresh number mints the next drift rather than ending it.

## Why re-pointing is refused specifically

`PL-38PN` corrected two stale line citations by hand. `PL-JXVD` was then filed
because `PL-38PN`'s corrections had themselves gone stale. By 2026-09-19 the Qt
port had taken `app/simulation_view.py` from 3,850 lines to 580, so `PL-JXVD`'s
own "Actually at" column was dead too — two generations of hand-repair, each one
a filed, triaged, ranked queue item, and none of them ending the loop.

That is the mechanism, and it is why the rule bans the anchor rather than asking
for more careful repair.

## What was measured, so the next session need not re-derive it

Over 676 line citations in this store, 2026-09-19:

| Where the citation sits | Stale | Total | Rate |
| --- | --- | --- | --- |
| Closed item briefs | 196 | 408 | **48.0%** |
| Open item briefs | 36 | 231 | **15.6%** |
| Standing documents | 0 | 5 | **0.0%** |

Two consequences the numbers carry and an argument would not:

- **The standing documents are not drifting.** Extending an annotation
  convention across them — the obvious route, and the expensive one — would have
  checked 2,286 id mentions to find nothing. A check that fires without changing
  a decision is the defect `CLAUDE.md` retires a check for; one that cannot fire
  at all is worse.
- **Closed briefs rot three times as fast as open ones, and nobody has repaired
  one.** The project had already decided this in its behavior; what was missing
  was anyone writing it down, so sessions kept filing items against it. The
  question `PL-G424` called undecided — whether a closed brief is record or
  assertion — is answered by what every session has always done with them.

Dangling ids were counted too and are not a problem: 8 in the standing documents
and 57 in briefs, of which every distinct one is an illustrative placeholder
(`PL-K7QX`, `PL-A1B2`, `PL-XXXX`). A "does this id exist" check would fire only
on documentation examples.

## What the script decides, and what stays yours

`tools/doc_check.py`'s `check_line_citations` fails `make check` on a citation
whose line is past the end of its file, in a live document. That is
*resolvability*: the line cannot be what the sentence says, whatever the
sentence says.

It does **not** check whether a line that exists still holds what the prose
claims. The blame-based test for that — has the cited line changed since the
citation was written — came back 36% across the store, and it is a heuristic: a
reformat moves a line without touching what it says. It was run once to size the
problem and decide this rule, which is the right use of a number that cannot be
trusted per-instance. Shipping it as a check would be scripting the judgment
half, and `CLAUDE.md` refuses that — a tool that guesses at judgment is worse
than no tool, because its output looks authoritative and is not.

An item whose *subject* is a broken citation can quote it inside a fenced block,
which `_without_fences` blanks before the check reads it.

## What this does not reach

Prose drift that is not a citation — a stale measurement, a heading still
reading "Open" over a resolved thread, a claim about what a command prints — is
judgment, and no script here will decide it. It stays under `CLAUDE.md`'s
capture rule, with one change: where the document is a **closed** brief, it is
not a finding, on the same reasoning as above.
