---
id: PL-PFK1
title: bin/docket verify REJECTs a self-audited branch on commission checks alone without ever naming --self, so a session reaching the command from CLAUDE.md or --help still hits the wall PL-7XTS closed for the skill
status: untriaged
added: 2026-09-15
---

**Problem.** bin/docket verify REJECTs a self-audited branch on commission checks alone without ever naming --self, so a session reaching the command from CLAUDE.md or --help still hits the wall PL-7XTS closed for the skill

**Found 2026-09-15**, in `PL-7XTS`, which closed the same defect one layer up.

`PL-7XTS` put `bin/docket verify --self <id>` into the `docket` skill's
close-out, so a session following that procedure now reaches the right mode.
The residual is every other path to the command:

- `CLAUDE.md`'s fix-now rule names `bin/docket verify` bare (see `PL-6QZP`).
- `bin/docket verify --help` lists `--self` but the session has to read the
  flag list to find it.
- `subprojects/docket/README.md` documents it correctly, which is the
  reference a session reads once it already knows what it is looking for -
  `PL-7XTS`'s own observation.

A session arriving by one of those gets the delegated mode on its own branch
and a `REJECT` on correct work, which is the failure `PL-69JZ` fixed in code
and `PL-7XTS` fixed in one document.

**The deterministic fix is in the tool, which is where `CLAUDE.md`'s routing
rule ranks it first.** `cmd_verify` in `subprojects/docket/src/docket/cli.py`
already prints a footer in `--self` mode. The mirror of it is the one worth
having: where the run was *not* `--self` and every failing check is one of the
four commission checks - diff outside `touches`, protected path, gate path,
front matter changed - print one line saying that a session auditing its own
branch runs `--self`, and that a delegated review is what this mode is for.

It fires at the exact moment of the failure, costs no resident context, and is
independent of which document the session followed. Keep it conditional on
*all* failures being commission checks: a branch that also removed an assertion
or failed `make check` must not be told the flag would have helped, because it
would not have.

**Bounding the claim:** this has not been measured. What is known is that
`PL-7XTS` observed it once, on `PL-KY7M`'s close-out, and that three routes to
the bare command survive its fix. Whether any session still takes one of them
now that the skill routes correctly is the number that would decide whether
this is worth building - and the cheapest way to get it is to wait and see
whether a second instance is reported.
