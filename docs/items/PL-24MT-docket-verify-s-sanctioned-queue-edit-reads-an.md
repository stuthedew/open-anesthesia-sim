---
id: PL-24MT
title: docket verify's sanctioned_queue_edit reads an item file's diff a line at a time as front matter for its pr and capture forms, so a new item whose brief quotes a status line of untriaged in a fence is sanctioned as a capture whatever its status, and a pr: line inserted inside a value continued on an indented line is sanctioned as a record write while it cuts that value's tail into pr; latent
status: untriaged
feature: one-answer
added: 2026-10-06
---

**Problem.** docket verify's sanctioned_queue_edit reads an item file's diff a line at a time as front matter for its pr and capture forms, so a new item whose brief quotes a status line of untriaged in a fence is sanctioned as a capture whatever its status, and a pr: line inserted inside a value continued on an indented line is sanctioned as a record write while it cuts that value's tail into pr; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`verify.py`. `sanctioned_queue_edit` exempts three edits to another item's file
from the touches audit: a capture, a `pr:` record and a recurrence. `PL-J503`, a
member, moved the recurrence form onto `_recurrences_grew`, which reads the item
before and after through `parse_front_matter`. The other two still read the
diff's lines, each as if it were a front-matter line: in the front matter a value
continues on indented lines (`docket.model`'s fold), and below it is a Markdown
brief, where a line shaped like a field inside a fence is prose.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15, in a
throwaway repository, against `parse_front_matter`. A base item whose `verify:`
continues on an indented line, and a branch adding a `pr: 12` line between the
two:

```text
verify: grep -q 'first half' docs/x.md
pr: 12
  && grep -q 'second half' docs/y.md
```

`sanctioned_queue_edit` answered `pr`. `parse_front_matter` reads the base's
`verify` as both checks and the branch's as the first alone, with `pr` holding
`12 && grep -q 'second half' docs/y.md`: the edit cut the command's second check
off into `pr`, which is the edit to a `verify:` the function's docstring says
still fails the audit. And a branch creating an item at `ready` whose brief
holds a fence quoting a front-matter line reading `status: untriaged` was
answered `capture`, where the file's parsed status is `ready`. Latent: 12
tracked items carry folded values, all closed and none in `verify`, and
`docket record` writes past continuation lines and checks the write by reading
it back, so only a hand edit splits a value.

The same loop skips every line opening `---` or `+++` as a file header, so a
removed brief line that is a thematic break, which the diff shows as `----`,
is never seen: a commit removing one and adding a `pr: 5` line was answered
`pr`. That is `PL-MR8Z`'s second half, open for `_net_line_changes`, in this
function's own copy of the loop; it is a header misread rather than a
statement's extent, and is folded here because reading both copies through the
parser, below, removes the loop.

**Generator check.** A member of `PL-R417`: a reader takes a diff line for a
front-matter statement where the field continues across lines, or where the
line belongs to the brief. `PL-FYV7`, open, would replace the diff-shape guess
with a commit trailer, a different fact.

**Done when.** The `pr` and capture forms read both copies through
`parse_front_matter`, as `_recurrences_grew` does: `pr` sanctioned only where
it is the one field that differs, a capture only where the created file's
parsed status is `untriaged`, and nothing sanctioned where the brief also
changed, pinned by a `queue edit, ` case in `PL-R417`'s guard for each, the
removed thematic break included, failing on today's reader.
