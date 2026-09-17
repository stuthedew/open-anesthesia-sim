---
id: PL-FXBS
title: A verify: command that negates a recursive grep over docs/items/ is falsified by the item store itself, so it can never pass: PL-GPYV's greps for set_editor, which its own verify line and its record of the rename both contain
priority: P2
effort: S
status: done
classes: defect
touches: docs/items
verify: bin/docket check && grep -qF "docs/items/PL-WZBX-*.md" docs/items/PL-0BSC-*.md && grep -qF "exclude='PL-FXBS-*'" docs/items/PL-GPYV-*.md
feature: interface-areas
closed: 2026-09-17
added: 2026-09-17
---

**Problem.** A verify: command that negates a recursive grep over docs/items/ is falsified by the item store itself, so it can never pass: PL-GPYV's greps for set_editor, which its own verify line and its record of the rename both contain

**The shape.** `! grep -r <literal> docs/items/` asks the item store to prove a
string is absent from itself. But the `verify:` line stating the command *lives
in* `docs/items/`, so the literal is present by the act of writing it down. The
negation then fails however complete the work is. It is the exact inverse of
`PL-L9JS` (eight commands that passed without their work, closed v0.3.1): that
one accepts a branch that did nothing, this one refuses a branch that did
everything.

**Instance 1, `PL-GPYV` — unlanded, on `origin/claude/wonderful-davinci-8s0cwf`.**

```
    verify: python3 tools/doc_check.py check && ! grep -rl 'set_editor' docs/items/
```

Measured 2026-09-17 against that branch's copy, with the rest of the store
removed so that a *perfect* sweep was simulated. The command still fails, on
five lines of the item's own file:

| Line | Why it matches |
| --- | --- |
| 9 | the `verify:` line itself |
| 28, 31, 145, 158 | the brief's record of the rename — "`PL-1FT6`'s brief, which names `set_editor`", "`set_editor` exists in no code", "`PL-1FT6`'s `set_editor` is now `set_view`", "`set_editor` appears nowhere" |

The four prose lines are not sloppiness to be swept: the item states that the
reversal "is deliberate and the earlier sentence has been rewritten rather than
deleted, so the record shows both". So the item's own `Done when` and its own
`verify:` contradict each other — the record it is required to keep is the
string its command forbids.

**Instance 2, `PL-0BSC` — on `main` today.**

```
    verify: bin/docket check && ! grep -rq 'wave counts the four entries' docs/items/
```

Falsified through a sibling rather than through self-reference: `PL-WZBX`'s
title is "bin/docket wave counts the four entries ROADMAP…", so the string is in
the store regardless of `PL-0BSC`'s own text.

**Instance 3 is this item, and it is the argument.** Filing this finding
required naming the string, so `PL-FXBS`'s own title now contains `set_editor`
and `docs/items/` holds a third match. Measured after filing: `PL-HJPY`,
`PL-1FT6` and `PL-FXBS`. A bug report about a literal cannot be written without
putting that literal in the store, so `! grep -r <literal> docs/items/` is not
a command that happens to be wrong here — it is a command the queue can always
falsify by doing its job. That is the general result, and it holds for any
future item of this shape.

**The count, re-measured 2026-09-17 after an error.** A first pass here said
"801 `verify:` lines, 680 with a `grep`". That conflated open items with closed
ones, whose commands are records of what was run rather than live commands
(`PL-JZ1D`). Corrected, over `docs/items/` in this checkout:

| | Count |
| --- | --- |
| Open items carrying a `verify:` | 170 |
| ...of those, containing a `grep` | 159 |
| ...of those, grepping `docs/items/` without naming a specific file | **2** |
| ...of those, falsified by the store | **2** — `PL-0BSC` and `PL-GPYV` |

Closed items carrying one: 629, not in scope. The head of `main` today is
`PL-879R`, which counted 168 open `verify:` items on this same date and
executed all 31 negation clauses against an untouched tree: **31 of 31 still
discriminate**. That measured the opposite property — whether a negation fails
*before* the work, which is the property it should have. It could not have
caught these two, which fail *after* it as well. The two findings agree:
`PL-879R` is right that a negation is not a defect, and this is the narrow
subset where the negated literal is one the store itself must carry.

**So this does not license a new check**, on `CLAUDE.md`'s gate of whether it
would genuinely run again: n=2 of 170, in a shape `PL-879R` has just finished
arguing is otherwise sound, and a shape advisory printing two ids forever is
what that commit refused. Recording the count so the next session does not
re-derive it and reach the opposite conclusion from enthusiasm. The cheap fix
is per-item and needs no mechanism: anchor the pattern so a line starting
`verify:` cannot match, or name the files rather than recursing.

**Done when.** `PL-GPYV` and `PL-0BSC` each carry a command that fails without
their work and passes with it.

**It does not block `PL-GPYV`'s sweep; it blocks closing it**, since close-out
step 5 runs the item's own command until `ACCEPT`. Cheapest fixed on the
holding branch before it lands.


## Fixed 2026-09-17, on `claude/lucid-darwin-zwishk` with `PL-GPYV`

Both instances now carry a command that fails without its work and passes with
it, by the second of the two routes this item named - naming the files rather
than recursing.

**`PL-GPYV`.** The negation now matches `set_editor` and the capitalized noun
`Editor`, excluding the five item files that legitimately keep Blender's word:
`PL-FTP5`, `PL-C842`, `PL-H620`, `PL-GPYV` and this item (project owner,
2026-09-17 - that list is the sweep's one judgment). Checked against
`origin/main`, where it fails naming the 17 files the sweep changed, and against
the swept tree, where it passes.

**`PL-0BSC`.** `! grep -rq 'wave counts the four entries' docs/items/` became
`! grep -q 'wave counts the four entries' docs/items/PL-WZBX-*.md`. The
recursive form was falsified by three files - `PL-WZBX`'s title, `PL-0BSC`'s own
body, and this item, which had to quote the string to report it. Naming
`PL-WZBX` leaves exactly the file whose title is the work. Measured: exit 1
before the correction, 0 after it.

**This item was recovered from a stranded branch.** It was captured on
`origin/claude/awesome-brown-x29b1e`, whose session stood down on `PL-GPYV`
(held here) and was then archived with the item never merged - so its own
handoff, "merge `claude/awesome-brown-x29b1e` or hand `PL-FXBS` to the `PL-GPYV`
session", was deleted with it. `bin/docket stranded` is what still named it;
that is the mechanism `PL-H1JD` describes working as intended.

The count above is left as measured on the day rather than re-run, per
`PL-JZ1D`: a closed item's numbers are a record.
