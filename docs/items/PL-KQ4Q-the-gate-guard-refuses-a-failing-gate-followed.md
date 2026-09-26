---
id: PL-KQ4Q
title: The gate guard refuses a failing gate followed by an or-fallback that keeps it red - make check || exit 1, a bare exit, false, or a group ending in exit 1 - because it reads every or-fallback as one that succeeds
priority: P2
effort: S
status: done
classes: defect
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py, docs/worker.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-26
pr: 1103
payoff: a session can stop a multi-step command on a red gate with make check || exit 1, or a fallback group ending in exit 1 or false, without a refusal that calls the fallback successful, while a fallback that does lose the status is still refused and told the spelling that keeps it
verify: grep -q 'def test_a_fallback_that_fails_too_keeps_the_status' tests/unit/test_gate_status_guard.py
recurrences: 2026-09-26 PL-W9XN withdrawn 2026-09-26 PL-W9XN
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

**Reproduced 2026-09-26 at `0d8ffd1a`**, by piping each command as a hook payload into the guard: `make check || exit 1`, `|| exit`, `|| false`, `|| { echo red; exit 1; }` and `for t in a b; do make check || exit 1; done` are each refused with the `||` text, and `make check || echo "exit=$?"` passes.

**Where the line falls, measured the same day** in bash 5.2.21, each string run by `bash -c` with the gate replaced by a function returning 3:

```text
string, the gate returning 3                  exit
g || exit                                     3    the status that ran the fallback
g || { exit; }       g || (exit)              3
g || exit 1; echo after                       1    exit leaves before the rest runs
g || { exit 1; echo x; }                      1
g || (echo red; exit 1)                       1    the subshell exits 1
g || { echo red; false; }                     1
g || exit 010     g || exit +2     g || exit -1     10, 2, 255
g || exit 0       g || exit 256               0    the status is N modulo 256
g || { echo red; exit; }                      0
g || { echo red || exit 1; }                  0
g || false; echo after                        0
g || exit 1 | tail -1                         0    a pipeline stage is a subshell
g || exit 1 &                                 0
( g || exit 1 ); echo after                   0    exit leaves the subshell only
for t in a b; do g || exit 1; done | tail -1  0    a piped loop is a subshell
{ g || exit 1; } | tail -1                    0
set -o pipefail; g || exit 1 | tail -1        1
if g || exit 1; then echo then; fi; echo after  1
```

So an `exit` leaves the shell running it, which is the whole string only outside a subshell; `false` hands a failure to whatever follows the fallback; and `exit` with no argument keeps the failure only where nothing has run between the `||` and it.

**Why it matters.** A refusal a session can see is wrong teaches it that the guard can be argued with, the one lesson a guard must not teach: `PL-1SFZ` was filed on that ground, and the hook's own header credits its `$?` exemption to a firing that changed no decision. `make check || exit 1` is the ordinary way to stop a multi-step command on a red gate, and the refusal it meets says the fallback succeeds, which is false; `.claude/rules/apparatus-standard.md` holds the guard to answers that are true.

**Done when.** The guard reads an `||` fallback the way bash runs it, and passes one that provably keeps a failing gate's status non-zero: `exit` with no argument as the fallback's first command; `exit N`, N a decimal literal that is not 0 modulo 256, as its first command or as the last command of a `{ }` or `( )` group, run after a `;`; and `false` as the fallback or as such a group's last command. After an `exit` the walk stops, unless the shell it leaves is a subshell - a `( )`, or a group, `if` or loop that is piped or backgrounded - where it resumes at that subshell's end; after `false` it goes on from the fallback's end. Every other fallback is still refused, and so are the strings above that exit 0 with `make check` in place of `g`. The `||` refusal no longer says the fallback succeeds, and names the spellings that keep the status. `tests/unit/test_gate_status_guard.py` pins both lists, each against the exit measured above.

**Generator check.** One-off. The fact misread is what status an `||` list exits with once its fallback has run, and the gate guard's walk is its only reader: nothing else in the tree models how a status travels across bash's operators. `PL-1SFZ` (a group's `set` and closing `;`) and `PL-0X0G` (an `if` or a loop) were other operators of that same walk, each closed by reading its operator as bash runs it, which is what this item does for `||`. Neither fix should have covered it, and no head's `misread:` states the fact.

**Joined the Fix generators project's list 2026-09-26** (project owner, 2026-09-26). Asked in the project timeline whether anything else was left for generators, the coordinator named the seven items filed overnight, this one among them, as staying out of scope unless the owner added them, and the owner answered "Add them". Recorded here by the thread that took it.
