---
id: PL-W9XN
title: The gate guard reads a negated gate as the gate, so ! make check, which exits 0 when the tree is red, passes unrefused, and so do ! make check && echo ok and ! make check || exit 1
status: untriaged
added: 2026-09-26
---

**Problem.** The gate guard reads a negated gate as the gate, so ! make check, which exits 0 when the tree is red, passes unrefused, and so do ! make check && echo ok and ! make check || exit 1

Found 2026-09-26 while working `PL-KQ4Q` (the gate guard's reading of an or-fallback), and not fixed there because it is a different operator and the opposite failure. `shell_split.command_words` drops a leading `!` with the grouping ahead of a command, so the guard's `gate()` reads `! make check` as the gate `make check`, and the walk then carries a failure the `!` has already turned into success. Measured the same day in bash 5.2.21, each string run by `bash -c` with the gate replaced by a function returning 3, and piped as a hook payload into `.claude/hooks/gate-status-guard.sh`:

```text
string                        guard   bash exit with the gate failing
! make check                  allow   0
! make check && echo ok       allow   0
! make check || exit 1        allow   0
```

It is a false allowance: a red tree arrives as exit 0, the failure the guard exists for. The first two predate `PL-KQ4Q`. The third was refused before it, only because every `||` then read as a loss; once a fallback that fails too keeps the status, the `!` ahead of the gate is what loses it. A fix reads a `!` ahead of a gate as losing the status at once, with a refusal saying the `!` inverts the verdict. No session is known to have written one, since a `!` in front of a gate turns its answer over, which is why this was filed rather than fixed inside `PL-KQ4Q`.

**Not a recurrence of `PL-KQ4Q`**, which `bin/docket new` matched on the shared files: that item was a false refusal of an `||` fallback, and this is a false allowance of a negated gate, read wrongly by a different step of the same walk.
