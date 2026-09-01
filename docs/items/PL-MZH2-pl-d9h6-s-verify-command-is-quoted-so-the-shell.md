---
id: PL-MZH2
title: "PL-D9H6's verify: command is quoted so the shell cannot run it, and exits 127 every time"
status: untriaged
added: 2026-09-01
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
