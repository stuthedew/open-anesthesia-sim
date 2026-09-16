---
id: PL-RC86
title: The session-start hook's three network round trips run serially and none is needed before the first turn, so the slow-link cost is their sum rather than their max
status: untriaged
added: 2026-09-16
---

**Problem.** The session-start hook's three network round trips run serially and none is needed before the first turn, so the slow-link cost is their sum rather than their max

**Problem.** `.claude/hooks/docket-digest.sh` runs four stages in sequence and
three of them go to the network: the one-time `git fetch --unshallow`, the
`git fetch --quiet origin` inside `bin/docket branch --brief`, and
`tools/main_ci_status.py`'s two calls to `api.github.com`. Each is separately
bounded - `timeout 60`, `_run_git`'s `subprocess.run(..., timeout=10)`, and
`TIMEOUT_S = 8` respectively - but they run one after another, so a session
start costs their **sum** on a slow link where it could cost their **max**.

`main_ci_status.py` depends on none of the others: it reads a GitHub verdict for
`main` and knows nothing about the checkout's refs. `dead_ends.py emit` touches
no network at all. So the ordering that exists is presentation order - the
comments in the hook are explicit that `main_ci_status.py` sits last because it
is the exception line a session should read immediately before the conversation
- and presentation order can be preserved while the work overlaps: start the
CI read first, collect its output last.

**Why it might not be worth doing.** The hook is currently dead simple and
fails silently on every path, which is a property worth more than a few
seconds. Backgrounding a stage in bash and collecting it in order costs that
simplicity, and the saving is real only if `PL-JH3T`'s attribution lands on the
network stages. **Do not start this before `PL-JH3T` has measured where the time
goes** - on this container the whole hook is 3.0 s warm, and there is nothing
here to win.

**Done when** either the network stages overlap with the hook's output order and
silent-failure behaviour unchanged and `tests/unit/test_docket_digest_hook.py`
still passing, or this item records the measurement that showed the saving was
not worth the complexity.

---

**Refuted the day it was filed, 2026-09-16, before any work started.** The
premise was that a slow link made the hook's serial network stages the cost.
Measured on the machine that actually produces the slow session start:

| stage | owner's macOS machine | session container |
| --- | --- | --- |
| `bin/docket branch --brief` (network) | 0.96 s | 0.81 s |
| `bin/docket digest` (**no network**) | **17.64 s** | 1.50 s |
| `tools/dead_ends.py emit` | 0.08 s | 0.03 s |
| `tools/main_ci_status.py` (network) | 1.32 s | 0.85 s |
| sum | 20.01 s | 3.19 s |

Both network stages together are 2.28 s of a 20.01 s session start, and
overlapping them could save at most about 1 s. The 17.64 s is `digest`, which
goes to the network never - it is git process spawns, 192 of them, at ~92 ms
each on that machine. `PL-MMVF` is the real finding and this one should close
at triage: the complexity it would add to a hook whose silent-failure
simplicity is worth keeping buys a saving that is now measured and small.

This is `.claude/rules/expert-review.md`'s rule arriving the expensive way -
the hypothesis carried a plausible mechanism and no number, and the number was
one command away.
