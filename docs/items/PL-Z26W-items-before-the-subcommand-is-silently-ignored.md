---
id: PL-Z26W
title: `--items` before the subcommand is silently ignored, so docket answers about the wrong store
status: done
priority: P2
effort: S
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-08-25
closed: 2026-08-25
commit: c7728e2
---

**Problem.** The shared options are attached to the top-level parser *and* to
every subcommand, so that `docket --items X check` and `docket check --items X`
both work. Only the second does. Each subparser's `--items` carries
`default=None`, and argparse writes that default into the same namespace after
the top-level value is already there, overwriting it. Reproduce:

```
docket --items /tmp/other check   # reads this project's store
docket check --items /tmp/other   # reads /tmp/other
```

`--today` and `--no-git` have the same defect.

**Why it matters.** It fails silently and in the wrong direction. A user who
points `--items` at another project's queue before the subcommand gets a
confident, correct-looking answer about *this* project's queue, with nothing
to indicate the flag was dropped. For a tool whose whole purpose is answering
"what should I work on", a plausible answer to the wrong question is the worst
available failure. The comment in `cli.py` asserting both orders work makes it
worse, since it tells a reader not to check.

**Where.** `subprojects/docket/src/docket/cli.py`, `build_parser`. Every
existing test passes `--items` after the subcommand, which is why the suite
never caught it.

**First step.** Give the shared options `default=argparse.SUPPRESS` so an
unsupplied subcommand copy does not write to the namespace at all, and put the
real defaults on the top-level parser with `set_defaults`. Then whichever
position supplies the value wins and neither erases the other.

**Done when.** Both orders resolve to the same store, `--today` and `--no-git`
included, with a regression test asserting the before-subcommand form - the
one that was broken.
