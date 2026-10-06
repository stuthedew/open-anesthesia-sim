---
id: PL-1R9S
title: docket check's single-line verify: guard looks for a newline that docket.model's fold never leaves, so a verify: continued on an indented line is never refused though the README calls the field a single-line command, and one continued with a shell backslash runs with an escaped space, where a ! grep -q then passes on grep's exit 2; latent
status: untriaged
feature: front-matter-round-trip
added: 2026-10-06
---

**Problem.** docket check's single-line verify: guard looks for a newline that docket.model's fold never leaves, so a verify: continued on an indented line is never refused though the README calls the field a single-line command, and one continued with a shell backslash runs with an escaped space, where a ! grep -q then passes on grep's exit 2; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`checks.py` and `verify.py`. `_check_item` errors where `item.verify` holds a
newline, and `subprojects/docket/README.md` calls `verify` a single-line
command. The guard dates from `PL-G3TG` (2026-08-25). Since `PL-9HD1`
(2026-09-21) the reader folds a value's indented continuation lines onto it with
a single space, so no spelling the reader accepts leaves a newline in `verify`:
indented continuation, a backslash-ended line, a `\n` escape and a block scalar
were all tried. The guard's one test builds an `Item` with a newline directly,
which the reader can never produce. The value is a POSIX shell command, and the
shell removes a backslash-newline (§ 2.2.1) where the fold leaves the backslash
before a space.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against bash 5.2.21 and dash, with `docs/b.md` holding the old sentence:

```text
verify: ! grep -q 'old sentence' docs/a.md \
  docs/b.md
```

The value folded to the command with an escaped space before `docs/b.md`, the
guard did not fire, and bash and dash both ran it and exited 0: grep was handed
a file named with a leading space, which does not exist, exited 2, and `!` made
that a pass. The two lines as written exit 1 in both shells, the correct
failure. `verify` runs the same folded value for `_check_item`,
`already_passing` and a commission's command. Latent: no tracked item's
`verify:` continues onto a second line or ends in a backslash.

**Why it matters.** A guard that cannot fire reads as protection, and the one
spelling it was meant to refuse turns a failing check into a pass.

**Generator check.** Not a member of `PL-R417`. It reads the item front-matter
value grammar, `PL-HXJY`'s fact: a check stating the grammar (a single-line
`verify`) apart from its one reader. `PL-HXJY` is closed, with a `spent`
verdict about the writers; this guard was written before the fold existed, so
it is stock that head's sweep did not reach rather than new inflow.

**Done when.** Either `docket.model` records which fields it folded, as it
records block-list and block-scalar keys, and `docket check` refuses a folded
`verify:` by name, or the README and the guard say a `verify:` may continue
and `docket check` refuses one whose folded line held a trailing backslash;
the guard's test reads its input through the parser.
