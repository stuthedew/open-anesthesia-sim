---
id: PL-JD4L
title: model._front_matter_pairs passes over a front-matter line that is neither a field nor a continuation, with nothing reporting it, so a value wrapped at column zero loses its tail at docket check exit 0 and a recurrence docket new appends after one vanishes
status: untriaged
added: 2026-09-23
---

**Problem.** model._front_matter_pairs passes over a front-matter line that is neither a field nor a continuation, with nothing reporting it, so a value wrapped at column zero loses its tail at docket check exit 0 and a recurrence docket new appends after one vanishes

**Measured 2026-09-23**, by the session closing `PL-DSPM`, which made every
column-zero line with a colon a field, either known or reported. Two line classes
are still passed over with nothing reporting them: a column-zero line with no
colon, and an indented line before the first field. Scratch inputs, current
parser:

- `reason: first half` then `second half` at column zero reads `first half`,
  with `unknown_fields` empty.
- `  status: done` indented above `id:` reads `status` as empty.
- The writers walk a value's continuation as "non-blank and not `FIELD_RE`",
  where the reader folds only indented lines (`CONTINUATION_RE`), so they
  disagree on exactly this line. `with_front_matter_field(append=True)` puts
  `, 2026-09-20 PL-C3C3` on a stray line below `recurrences:`, and the reader
  then drops the entry. `with_front_matter_value`, the writer `docket withdraw`
  uses, replaces through the stray line and deletes it. `cmd_new`'s guard
  before it records a recurrence reads `unknown_fields`, `duplicate_fields` and
  `block_list_fields`, and none of them carries this line.

No item file carries one today (0 of 1,570, read with the parser's own
regexes).

**Why it matters.** A capture that `docket new` recorded, or the tail of a
hand-wrapped value, is lost at exit 0. That breaks the apparatus floor: an
answer has to be true, or say what it could not read.

**Why it was not fixed in `PL-DSPM`.** That item's Done-when kept a stray line
passed over, and
`test_a_line_at_column_zero_continues_nothing_as_it_continues_nothing_in_yaml`
pins that such a line is not an unknown field. The fix has two halves, and
they sit differently under `PL-6Q9L`, the pause on new workflow mechanisms
while a live generator is open:
- **Aligning the writers' walk with the reader** repairs a defect in what
  exists.
- **Reporting the line** needs a channel beside `unknown_fields` and a message
  in `checks.py`, which is arguably a new check.

**Generator check.** This is `PL-9HD1`'s mechanism: a line-at-a-time read
passing over a line it cannot match. It is the second instance since that head
closed, after `PL-DSPM`, and both were found by reading the code rather than by
use. Once it is closed, no line class is left that the reader passes over
unreported, so this is the repair that would make the head's `spent` verdict
true. `PL-5DPF` is the open item on a spent verdict that goes on gathering
members.

**Not a recurrence of `PL-DSPM`.** `bin/docket new` matched this capture to
`PL-DSPM` on shared paths and recorded it there. The match was withdrawn,
citing this brief. This is a different line class, filed on purpose by the
session closing `PL-DSPM`, and not that item's defect firing again.

**Done when.** `docket check` reports a front-matter line that is neither a
field nor a continuation, and the writers' continuation walks consume only
indented lines, so an append or a replace never reaches a line the reader does
not fold.
