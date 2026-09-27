---
id: PL-0FGH
title: The gate-status guard refused make doc-check > log 2>&1 && git add ... && git commit ... && git push ... | grep -v remote, reading the later git push pipeline's grep as doc-check's last stage, though | binds tighter than && so doc-check's status gated the chain (met in ordinary work 2026-09-27, evidence for PL-61FT)
priority: P3
effort: S
status: done
classes: defect
feature: bash-guard-bound
milestone: v0.5.14
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-27
closed: 2026-09-27
pr: 1155
payoff: a session that runs a gate and then an && chain with a pipe on a later step - make doc-check > log 2>&1 && git push | grep -v remote - is let through, as bash exits with the gate's status when it fails, so the && the refusal itself recommends is no longer refused once a later step is piped
verify: grep -q 'def test_a_gate_before_and_skips_the_whole_pipeline_after_it' tests/unit/test_gate_status_guard.py
---

**Problem.** The gate-status guard refused make doc-check > log 2>&1 && git add ... && git commit ... && git push ... | grep -v remote, reading the later git push pipeline's grep as doc-check's last stage, though | binds tighter than && so doc-check's status gated the chain (met in ordinary work 2026-09-27, evidence for PL-61FT)

**Why.** The walk in `.claude/hooks/gate-status-guard.sh` carried a gate's
status across `&&` "to the end of the next command", with `ends`, and then
judged the separator after that command. But an and-list joins pipelines, not
commands: "AND and OR lists are sequences of one or more pipelines separated
by the control operators `&&` and `||`", and "the return status of AND and OR
lists is the exit status of the last command executed in the list" (Bash
Reference Manual § 3.2.4, "Lists of Commands", bash 5.2; the bash 5.2.21
manual page's "Lists" says the same). So the `|` after `git push` belongs to
the push's own pipeline, which a failing `make doc-check` skips whole, and the
chain exits with `make`'s status.

**Why it matters.** The command refused is the refusal's own advice carried one
step further. The deny message offers `&&` as a spelling that keeps the status
(`make check && tail -45 /tmp/gate.log`), and a session that follows it and
pipes a later step - `git push | grep -v remote`, `git status | head` - is
refused and pays a retry for a command that was right. A guard whose advice is
refused is one sessions learn to route around, which is the failure its
one-token remedy exists to prevent. It sits inside `PL-61FT`'s bound on both of
its tests: an `&&` list is among "every list, group and compound the tests
pin", `&&` is a spelling the guard prints, and a session met it.

**Reproduced 2026-09-27 on `origin/main` at `ea193f39`.** Piped to the hook as
payloads, 14 spellings were refused, and each was run in bash 5.2.21 with the
gate a stub exiting 3. Eight keep the status: the item's command with its git
steps stood in by `echo` (exit 3), `make check && git status | head -3` (3),
the same with `{ git status; }` or `( git status )` as its first stage (3),
`true | make check && git status | head -3` (3), `make check && git status |
head -3 && git log | head -1` (3), `make check || false && git status | head
-3` (1), and `make check && git status | head -3; echo "exit=$?"`, which
prints `exit=3`. Six lose it, and their refusals are right by verdict: `( make
check && git status ) | head -3`, `{ make check && git status; } | head -3` and
`( make check && git status | head -3 ) | cat` pipe the group around the gate
(0), and `make check && git status | head -3` followed by `; echo after`, `||
true` or `&` (0) - those three refused at the `|` rather than at the separator
that loses the status.

**Generator check.** The fact misread is `PL-61FT`'s, what a shell command does
when run: here whether a gate's status survives a later pipe, which turns on
bash's binding `|` tighter than `&&`. An instance of that head's fact, filed in
`70c38a6c` (`#1146`) after the head closed in `831493f7` (`#1138`) - the second
filed after its close, `PL-ZS13` the first; `PL-1DW7` was filed in the closing
commit and `PL-7LCY` on a branch before it, both named in the head's build
note. Inside that head's bound and met in ordinary work, so it is worked at its
own rank; it is not a `KNOWN_GAPS` row met, which is what the head's reopening
number counts. No new head.

**Done when.** After `&&` the walk steps over the whole pipeline, a stage that
is a group, an `if` or a loop whole, so the eight spellings above that keep the
status are admitted; a `;`, `||` or `&` after the skipped pipeline still loses
it, and the refusal names that separator; a `|` after a group the gate is
inside still pipes the group, and is refused. A test pins each spelling, with
the exit bash gave.
