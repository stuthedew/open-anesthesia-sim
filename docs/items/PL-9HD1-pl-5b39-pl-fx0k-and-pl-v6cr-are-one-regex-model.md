---
id: PL-9HD1
title: PL-5B39, PL-FX0K and PL-V6CR are one regex - model.FIELD_RE's line-at-a-time front-matter read - and a rewrite_item round trip was measured deleting 9 of PL-9HDH's 10 reason lines with exit 0
priority: P2
effort: M
status: done
classes: defect, infra
milestone: v0.5.0
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md
added: 2026-09-21
closed: 2026-09-21
pr: 826
payoff: a hand-typed front-matter value - wrapped over lines, quoted for a colon, or written as a block list - is read whole or refused by name, instead of being truncated, mis-read, or deleted by the next field write with nothing reporting it
verify: uv run pytest subprojects/docket/tests/test_model.py subprojects/docket/tests/test_checks.py -q -k "block_list or multi_line or quote or verbatim or continues_nothing"
root-cause-of: PL-5B39, PL-FX0K, PL-V6CR
---

**Problem.** PL-5B39, PL-FX0K and PL-V6CR are one regex - model.FIELD_RE's line-at-a-time front-matter read - and a rewrite_item round trip was measured deleting 9 of PL-9HDH's 10 reason lines with exit 0

**The one mechanism.** `subprojects/docket/src/docket/model.py:33`:

```python
FIELD_RE = re.compile(r"^([a-z][a-z0-9-]*):[ \t]*(.*)$")
```

`_front_matter_pairs` applies it one line at a time and **skips every line it
does not match**. That single decision produces all three open items:

| item | symptom | which part of the regex |
| --- | --- | --- |
| `PL-5B39` | a multi-line value keeps only its first line, and a field write deletes the rest | continuation lines match nothing and are skipped |
| `PL-FX0K` | a YAML-list `touches:` parses as empty, so the item reaches no lane | `touches:` matches with an empty group; the `- x` lines are skipped |
| `PL-V6CR` | a title quoted for an embedded colon keeps its quote characters | `(.*)$` is taken verbatim, with no scalar unquoting |

`PL-V6CR` landed on `origin/main` in `#816` on 2026-09-21, after this item was
filed and while it read as stranded on `origin/claude/triage-f1ahwf`. It is
`untriaged` in the store now, so a `root-cause-of:` naming all three would
validate - the recovery this item's **Done when.** asked for is done.

**Measured 2026-09-21, and the count cuts both ways.** Across the 12 item files
holding a multi-line front-matter value, 67 lines are dropped at parse. A round
trip through `store.rewrite_item` on `PL-9HDH` took the file from 27 lines to
18, deleting 9 of the 10 lines of its `reason:` - the whole recorded argument
for dropping it - and exited 0. `rewrite_item` is what `cmd_set` calls
(`cli.py:970`).

But **0 of those 12 files are open items**: all 12 are `done` or `dropped`, and
what is at risk is their `reason:` and `not-delegable:` fields - the queue's
record of refuted approaches, which `docs/dead-ends.md` exists to preserve.
`cmd_record` uses `insert_field`, not `rewrite_item`, so the routine write onto
a closed item is safe. The live exposure is `bin/docket set` run against a
closed item. The YAML-list form (`PL-FX0K`) fires **0** times in the store
today; the quoted-title form (`PL-V6CR`) fires **59** times and is visible in
`bin/docket show PL-27S8`.

**Why it matters.** Three separately-briefed items, three separate sessions, one
regex - and fixing them one at a time means three passes over the same eight
lines. The reason this is filed rather than promoted to the generator tier is
the count above: two of the three are latent or cosmetic today, so the cluster
is worth working as one item and does not clear the bar for ranking above every
band.

**Done when.** The three are worked as one change - a front-matter reader that
handles continuation lines, block lists and quoted scalars, still standard
library only so `bin/docket` runs from a bare checkout - with `PL-V6CR`
already in the store, or a recorded decision that one of the three is not
worth fixing and why.

**Closed 2026-09-21, with `PL-5B39`, `PL-FX0K` and `PL-V6CR` in one commit.**
`root-cause-of:` records the three, so the claim this brief argued is a stored
fact rather than the next session's inference.

The repair is one sentence long: `_front_matter_pairs` stops skipping the lines
`FIELD_RE` does not match. An indented line now continues the value above it and
is folded on with a single space, which is what YAML does to a plain scalar and
what the 12 hand-wrapped `reason:` fields in this store mean; `PL-9HDH`'s
`reason:` reads 731 characters where it read 63, and a `parse_item`/`render_item`
round trip on it now reflows 27 lines to 18 instead of deleting 9 of them.

The three parts settled differently, and deliberately:

- **Continuation lines are folded, not re-emitted folded and not refused.**
  `PL-5B39` left the shape open between the three. Folding is the only one that
  makes the *existing* files safe without teaching the format a second spelling:
  re-emitting the wrapping means carrying wrap positions through a frozen
  dataclass that nothing reads, and refusing at `docket check` fixes nothing
  already written and does not stop `bin/docket set` rewriting the file.
- **Block lists are refused by name at `docket check`, for `LIST_FIELDS` only.**
  `PL-FX0K`'s own **Done when.** asks for exactly this and says why - two
  spellings of one field is a second thing every reader has to know - so this
  item's one-word "handles" is read as "no longer mis-reads silently". Scoped to
  list fields because that is where the two spellings collide: an indented
  `- ...` under a prose field is prose, and folds.
- **A quoted scalar is unquoted only when the pair closes at the last
  character.** `PL-XF5V`'s `payoff:` opens with a quoted phrase and runs on, so
  a rule stripping the ends of anything that begins and ends with a quote would
  have rewritten a value nobody wrote. Measured: 60 front-matter values open
  with a quote, 59 are complete scalars, and that one is not.

**What the store did with it.** 0 errors, and 0 slugs changed by unquoting 56
titles. 3 `verify:` commands that a shell read as one quoted word - exiting 127
without running - now parse to runnable commands; that is `PL-MZH2` recurring
three times after being repaired by hand on one item.
