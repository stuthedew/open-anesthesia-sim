---
id: PL-MZH2
title: "PL-D9H6's verify: command is quoted so the shell cannot run it, and exits 127 every time"
priority: P3
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: docs/items/PL-D9H6-quality-yml-runs-the-full-suite-twice-on-every.md
added: 2026-09-01
verify: sh -c "$(sed -n 's/^verify: //p' docs/items/PL-D9H6-*.md)"; test $? -ne 127
---
**Problem.** `PL-D9H6` records:

```
verify: "! grep -qF 'on: [push, pull_request]' .github/workflows/quality.yml"
```

The outer double quotes are part of the recorded string, so a shell reads the
whole thing as one quoted word and looks for a command named `! grep -qF 'on:
[push, pull_request]' .github/workflows/quality.yml`. There is none, so it
exits 127 - "command not found" - on every tree, before and after the work.
Measured 2026-09-01 while running `PL-3CBS`'s new check across the store: it
was the only one of 29 candidates to return 127.

**Why it matters.** The command can never pass, so it can never accept the
work: `docket verify` would `REJECT` a correct branch, and the worker would
have no way to tell a real failure from a quoting bug. It is the mirror of
`PL-L9JS` (eight commands that pass without their work) and has the same root
cause - a command recorded without being run.

It is also load-bearing for the check `PL-3CBS` added, which declines when
*every* candidate returns 127 on the theory that the toolchain is missing. One
genuine 127 in the store is why that threshold is "all of them" rather than
"any", so the malformed command is currently propping up a design decision it
should not be involved in.

**Where.** The `verify:` line of `PL-D9H6`'s item file.

**Done when.** The command runs as written - the outer quotes removed, the
negation expressed so a shell executes it - and it has been run on this tree
and seen to give the exit status the item expects.

**Triaged 2026-09-01.** P3, `defect`/`infra`, `dev-tooling`. The `verify:`
command runs `PL-D9H6`'s own recorded command and requires it not to exit 127,
which is the whole claim; it was run first and fails today with `sh: 1: !
grep -qF ... : not found`. It reads the command out of the file rather than
restating it, so it keeps testing whatever is recorded there rather than a copy
that can drift.

Left out of v0.2.8's frozen list, with `PL-L9JS`: the machinery at fault is the
delegation gate, which that release's goal does not name. Note also that fixing
this removes the store's only genuine 127, which is what `PL-3CBS`'s check
relies on to distinguish "the toolchain is missing" from "one command is
malformed" - so whoever takes it should read that threshold before changing the
line.
