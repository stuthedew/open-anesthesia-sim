---
id: PL-J3WK
title: make check runs bin/docket check without --verify while CI runs it with, so a verify: command that proves nothing - a literal true, or one shared by three items - passes every local gate and fails CI; both halves of that are decidable statically, without running the 17 commands the flag runs
priority: P2
effort: S
status: ready
classes: defect, infra
feature: check-parity
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md
added: 2026-09-20
payoff: closes the gap that let three non-discriminating verify: commands pass every local gate and turn CI red after review had started
verify: grep -q 'def test_a_no_op_verify_command_is_an_error' subprojects/docket/tests/test_checks.py
---

**Problem.** make check runs bin/docket check without --verify while CI runs it with, so a verify: command that proves nothing - a literal true, or one shared by three items - passes every local gate and fails CI; both halves of that are decidable statically, without running the 17 commands the flag runs

**Why it matters.** It is the first of `CLAUDE.md`'s three compounding-friction
tests - a check passes while the guarantee it stands for is void. A session
triaging items sees `make check` green, pushes, and learns from CI that its
`verify:` commands prove nothing. The cost is a red cycle on a branch whose
content was correct, and the red arrives after review has started.

**Where it comes from.** `PL-4W2L`'s own branch, 2026-09-20. Three items were
triaged with `verify: true` as a placeholder. `make check` passed - it runs
`bin/docket check` bare at `Makefile:160`, as does `make docket` at
`Makefile:295`. CI runs `bin/docket check --verify --verify-base "$VERIFY_BASE"`
and refused:

> `PL-34BG`, `PL-4W2L`, `PL-S8JT` are open but their `verify:` command already
> passes (3 of 17 checked) ... `PL-34BG`, `PL-4W2L`, `PL-S8JT` share a command
> with another open item, which cannot prove any one of them done

**The flag is CI-only for a stated reason, and that reason is not in dispute.**
`--verify` shells out to every in-scope item's command - 17 of them on that
branch, 5.6s parallel against 37.0s serially - and `quality.yml` carries the
timeout reasoning. Putting the whole flag into `make check` is not what this
asks for.

**The proposal: take the statically decidable half only.** Both halves of what
fired here need no command run at all.

1. **A literal no-op.** `true`, `:`, `exit 0` and their whitespace variants can
   never discriminate, whatever tree they run against. Reading the field
   answers it.
2. **A command shared by two or more open items.** Also a pure read of the
   store: if one command is recorded on three open items, it cannot prove any
   one of them done, which is the second sentence CI printed.

Neither costs a subprocess, so both belong in the bare `bin/docket check` that
`make check` already runs - which is `CLAUDE.md` § "find the decidable part and
put it in code", and its cheapest-sufficient-tier rule, since the expensive
tier already exists and is not being replaced.

**What stays in `--verify` and must not be faked.** Whether a command that
*looks* discriminating actually fails on the current tree is only answerable by
running it, and guessing at it would be scripting the judgment half. This
proposal does not touch that: it moves the two questions that are decidable
from the store alone, and leaves the third where it is.

**Name the number before tightening.** Per `.claude/rules/expert-review.md`:
this adds a hard failure, so before it lands, count how many open items in the
store would fail each of the two rules today. If the count is large, most of
those are real defects and the check is overdue; if it fires on items nobody
would call wrong, the rule is wrong rather than the items.

**Done when** `bin/docket check`, with no flags, fails on an open item whose
`verify:` is a literal no-op or is shared with another open item, and a test
pins each of the two rules.

**An instance, 2026-09-21, costing one red CI cycle on `#830`.** `PL-PT7M`'s
session filed `PL-J3TV` and gave it
`! grep -q 'delete just that one ref' .claude/hooks/no-prune-guard.sh`. The
phrase is one Python string split across two source lines in that file -
`"…delete just "` then `"that one ref and rebase…"` - so the `grep` could never
match and the negation always passed. `make check` was run in full and reported
green, because `make docket` runs `bin/docket check` bare; CI's
`bin/docket check --verify --verify-base "$VERIFY_BASE"` caught it on the first
push and failed the `checks` job.

That is this item's class exactly, and the shape is worth recording beside it:
the false pass came from a command asserting the *absence* of a string rather
than the presence of one. A command that greps for what the fix **adds** fails
honestly when the string is mistyped or split; one that greps for what the fix
**removes** passes on any typo in the pattern. The replacement asserts
`push origin --delete` or `modes/capture.md`, and was run and seen to fail
before being recorded.

