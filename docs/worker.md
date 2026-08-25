# Worker instructions

You are working this repository's queue as a **worker**: taking items that
have already been specified by someone else, doing exactly what each one says,
and proving it with a command. Read this file in full before your first edit.

## These instructions narrow `CLAUDE.md`

`AGENTS.md` sent you to `CLAUDE.md`, and most of it applies. Four of its rules
do not, for the duration of a worker run:

- **Do not propose.** `CLAUDE.md` asks you to put a case to the project owner
  when a better approach exists. Not here. The brief is the specification.
- **Do not redesign.** If a brief describes a weaker approach than you would
  choose, follow the brief anyway and say so in the `**Worked.**` note.
- **Do not decompose.** Do not split an item, merge two, or invent new ones
  for work you think is missing.
- **Do not start anything not on your list**, however obvious the fix looks.

One rule is **never** suspended: **capture.** Anything you notice and do not
fix gets recorded with `bin/docket new "..."` before you finish. That includes
anything you thought should have been done differently.

## Setup

```bash
uv sync --locked --dev
```

## What you may work

```bash
bin/docket list | grep ", delegable)"
```

Match the parenthesised mark, not the bare word: an item whose *title*
mentions delegability would otherwise look like work you may take. (`docket
delegable`, once PL-ZR1R lands, answers this without the grep.)

Only items carrying that mark. Nothing else, whatever its priority. An item is
marked delegable because a rule proved it safe to hand over — you may not
promote one yourself, and there is deliberately no way to.

Read the item's file in `docs/items/` before starting it. The brief is written
to be picked up cold; if it is not enough, see **When a brief is unclear**.

## The loop

1. Make **one branch** for the whole batch: `codex/batch-<id>-<id>-...`,
   carrying every item id you plan to work.
2. For each item, in turn:
   - Do exactly what the brief says.
   - Run the item's `verify:` command from its front matter. It must pass.
   - Run `make check`. It must pass.
   - Add a `**Worked.**` line to the item's file (see below).
   - Commit, **one commit per item**, with the item id first in the subject:
     `PL-QGZV Cover the alveolar compartment's capacity guards`.
3. Push the branch and report which items are on it.

One commit per item matters: it lets the reviewer accept four items and reject
one, instead of rejecting the batch.

## Rules you may not break

These are the reason work can be handed to you without the diff being read.
Breaking one silently is worse than not doing the item.

- **Never edit a file outside the item's `touches`.** Not a typo, not an
  import, not a formatting fix. If the item cannot be done inside `touches`,
  stop and treat it as an unclear brief.
- **Never edit `src/anesthesia_sim/core/`, `src/anesthesia_sim/data/`, or
  `docs/MODEL.md`.** These produce clinical values. You may write tests
  *about* them; you may not change them. This holds even if you are certain
  one contains a bug — record it with `docket new` instead.
- **Never edit the checks themselves**: `Makefile`, `pyproject.toml`,
  `.github/workflows/`, `.claude/`, `docket.toml`.
- **Never add a suppression** — `# type: ignore`, `noqa`, `xfail`, `skip` — to
  make a check pass.
- **Never delete or weaken an existing assertion.** If an existing test fails
  because of your change, your change is wrong.
- **Never improvise a fix for something outside the work itself.** If a
  `verify:` command errors, a tool misbehaves, the environment is wrong, or a
  test fails for a reason the brief did not predict — do not diagnose it, do
  not work around it, do not substitute a command you think was meant. Stop
  and report it. See **When something errors** below.
- **Never change an item's `status`.** Marking work done is the reviewer's,
  not yours.
- **Never assert a value you observed rather than one the brief specified.**
  If the brief names an exception and a message, assert those. If the code
  disagrees with the brief, that is a finding to capture — not a test to bend
  until it passes.

## When something errors

**Do not improvise. This is the rule most likely to be broken, because
improvising looks like competence.**

Working around a broken thing is the right instinct almost everywhere else,
and it is wrong here. You were given this work because a command proves it
correct. The moment you substitute your own judgment for that command — a
different coverage target, a looser assertion, a skipped step, an adjusted
expectation — the proof is gone, and nothing downstream can tell that it is
gone. A worked-around item that reports success is worse than a blocked one,
because the blocked one is honest.

So, when any of these happens:

- the item's `verify:` command errors, reports nothing, or cannot be run;
- a test fails for a reason the brief did not predict;
- `make check` fails for something you did not cause;
- setup, tooling, or the environment misbehaves;
- doing the item appears to require editing a file outside its `touches`;
- the code disagrees with what the brief says it does;

**stop that item and report it.** Do not attempt a fix, a substitution, or a
diagnosis beyond naming what you observed.

The one thing you *should* fix without asking is your own work in progress: a
typo in a test you just wrote, an import you forgot, a name you got wrong.
That is doing the item, not working around it. The distinction is whether the
thing you are changing is yours — code you wrote for this item, inside its
`touches` — or someone else's: the brief, the command, the tooling, the
existing tests, the environment.

If you are unsure which side of that line you are on, you are on the far side.
Stop.

## When a brief is unclear

**Stop. Do not guess.**

Add a `**Blocked.**` line to the item's file naming exactly what is ambiguous
— or, for an error, exactly what you ran and exactly what came back. Commit
that and move to the next item. Leave the rest of the item alone.

Report what you observed, not what you concluded. "`--cov` reported no data"
is useful. "The coverage target is probably meant to be a dotted module" is a
guess, and a reviewer acting on it inherits your guess without knowing they
have.

This is the most important instruction here. A brief that turns out to be
underspecified is a cheap problem — one sentence fixes it. A guess that
happens to pass its check is an expensive one, because nothing downstream will
catch it.

## The `**Worked.**` note

Append to each item you complete:

```markdown
**Worked.** <anything you decided that the brief did not decide>
```

List only the judgment calls you had to make — a name you chose, a structure
the brief left open, an approach you would have taken differently. Not a
summary of what you did; the diff is that. **Empty is the expected answer**,
and `**Worked.** Nothing the brief did not specify.` is a good outcome, not a
lazy one.

## Before you finish

- `make check` passes.
- Every item you touched is committed, with its id in the subject.
- Anything you noticed and did not fix is recorded with `bin/docket new`.
- The branch is pushed.

Report the branch name, which items are on it, which you left blocked and why,
and anything you captured.

**Blocking is a good outcome, not a failed run.** An item you stopped on costs
one sentence to unblock. An item you improvised through costs a wrong test
that passes its check, which may not be found at all. If a run ends with
everything blocked and nothing done, you have done the job correctly.
