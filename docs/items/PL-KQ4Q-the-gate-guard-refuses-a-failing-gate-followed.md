---
id: PL-KQ4Q
title: The gate guard refuses a failing gate followed by an or-fallback that keeps it red - make check || exit 1, a bare exit, false, or a group ending in exit 1 - because it reads every or-fallback as one that succeeds
status: untriaged
added: 2026-09-26
---

**Problem.** The gate guard refuses a failing gate followed by an or-fallback that keeps it red - make check || exit 1, a bare exit, false, or a group ending in exit 1 - because it reads every or-fallback as one that succeeds

Found while working `PL-0X0G` (the Bash guards reading a reserved word as a command's name), and not fixed there because it is a different question from that item's. `.claude/hooks/gate-status-guard.sh` sets `lost = separator` for every `||`, with the `LOSS` text "The `||` fallback succeeds, so a failing gate still exits 0". That holds for `make check || true` and `make check || echo failed`. It does not hold for a fallback that fails itself. Measured on 2026-09-26, bash 5.2.21:

```text
command                             guard   bash exit with the gate failing
make check || exit 1                deny    1
make check || exit                  deny    1   (a bare exit returns the last status)
make check || false                 deny    1
make check || { echo red; exit 1; } deny    1
make check || echo "exit=$?"        allow   the $? reader, already exempt
```

It is a false refusal, not a false allowance, so it costs a session a retry rather than a red tree reported green. It predates `PL-0X0G`, whose walk leaves `||` as it was. What a fix has to decide is how far to read the fallback. A fallback ending in `exit` with a non-zero argument, or in `false`, provably keeps the status, and so does a bare `exit` straight after the `||`. A bare `exit` after anything else returns that command's status, so `make check || { echo red; exit; }` exits 0 (measured). Anything else is the loss the guard exists for. The same shape inside a loop, `make check || exit 1; done`, also keeps the status, because the `exit` leaves before the next pass.
