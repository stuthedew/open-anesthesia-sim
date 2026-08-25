---
id: PL-D7JQ
title: `docket verify` - prove delegated work stayed inside its commission
priority: P2
effort: M
status: ready
classes: infra, session-cost
feature: delegation
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
added: 2026-08-25
---

**Problem.** A passing check proves the check passed. It does not prove the
work is correct, because the check can be satisfied by the wrong route:
weakening an assertion in an existing test, adding `# type: ignore`, `noqa`,
`xfail` or `skip`, editing the gate itself (`Makefile`, `[tool.mypy]`, the CI
workflow, `docket.toml`), or doing the item correctly and also changing three
unrelated files on the way past. Every one of those produces a green
`make check`.

**Why it matters.** This is the item that makes the review cheap, and cheap
review is the whole point — an expensive review defeats delegation entirely.
Without a scope guard, accepting delegated work means reading the diff, which
is exactly the cost being avoided. With one, the reviewer reads a one-screen
report plus the few lines the guard could not decide.

**Where.** A new `subprojects/docket/src/docket/verify.py`, wired into
`cli.py` as `docket verify <id> [--base main]`. `config.py` holds the
gate-file and suppression patterns so they are stated where a reviewer can
read them rather than buried in code.

**First step.** Shell out; do not import. `docket` is standard-library-only
and runs without a virtualenv, and that must not change — the commands it
runs are the project's, the tool itself stays dependency-free. Report, in one
screen: the item's `verify:` command, pass/fail; `make check`, pass/fail;
every path in `git diff --name-only <base>...HEAD` plus the working tree,
checked against the item's `touches`, with anything outside it a failure; any
edit to a gate file; any added suppression or deleted assertion in an existing
test; and the item's front-matter delta restricted to the fields a worker may
change.

State plainly in the output what is *not* proven: whether a new test asserts
the intended value or merely the current one. That residual is covered by the
brief naming the expected exception and message, by the protected partition
bounding the blast radius, and by the reviewer reading the new test bodies —
not by this command, and the command should not imply otherwise.

**Note from PL-69J3.** Do not detect suppressions by string-matching `noqa`.
PL-69J3 established that ten of this tree's `noqa` directives suppress nothing
at all, because they name rules (`BLE`, `SLF`, `RUF`, the `S` family) that
`[tool.ruff.lint] select` does not enable. A guard that flags added `noqa`
text would therefore fire on directives ruff does not enforce, and miss a
suppression written against a rule that *is* enabled. Key on the enabled
ruleset — or let ruff answer it, via `--select RUF100` — rather than on the
text. `# type: ignore`, `xfail` and `skip` are unaffected and can be matched
directly.

**Depends on.** PL-G3TG, which adds the `verify:` field this reads. Not
`blocked-by`, since the store's blocked state is for work that cannot start;
this is ordering within one feature.

**Done when.** `docket verify <id>` exits non-zero for each of the evasions
listed above, each covered by a regression test, and its report is short
enough that reviewing a six-item batch is one screen of reading.
