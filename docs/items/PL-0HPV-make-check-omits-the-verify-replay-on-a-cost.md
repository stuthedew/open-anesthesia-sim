---
id: PL-0HPV
title: make check omits the verify replay on a cost measured before --verify-base narrowed it, so a PR-only failure class is only ever found from CI
priority: P3
effort: M
status: ready
classes: session-cost, infra
feature: ci-cost
touches: Makefile, .github/workflows/quality.yml, docs/items, .claude/skills/docket/modes/triage.md
added: 2026-09-14
verify: grep -qF 'bin/docket check --verify --verify-base origin/main' Makefile
root-cause-of: PL-J3BB, PL-J3WK, PL-PBP5
generator: live - make check and quality.yml are separate lists and make check omits the scoped verify replay, so a failure class reaches CI only; #915 went red this way on 2026-09-22, after a local make check exit 0 (PL-KVDK)
---

**Problem.** make check omits the verify replay on a cost measured before --verify-base narrowed it, so a PR-only failure class is only ever found from CI

**What it cost, 2026-09-14.** `PL-TFX5` pushed a green `make check` and CI went
red on `bin/docket check --verify --verify-base "$VERIFY_BASE"` — an open item
whose `verify:` command already passed. One CI cycle and one round trip, for a
failure the session could have seen before pushing.

**The omission is deliberate and its reasoning is written in the `Makefile`**,
beside the `bin/docket check` line: the replay is left out because it is slow,
and `.github/workflows/quality.yml` runs it on both its events, narrowing the
pull-request one with `--verify-base` to the items that branch changed. So this
is not an oversight to point out — it is a priced decision.

**The price has changed since it was taken, and nobody re-measured.** The
`Makefile`'s own figure is "Measured 2026-09-05, four cores: this target 60.0 s
with the replay against 29.5 s without", and that is the **whole-store** replay.
`PL-SDHR` added `--verify-base`, which is what CI now uses on a pull request,
and the narrowed form is what a session would run. Measured 2026-09-14 on a
branch touching 11 items: **7.1 s**, against the 30.5 s the refusal was priced
against — roughly a quarter, and it falls to nothing on a branch that changes
no item at all, which is most of them.

**So the question is whether `make check` should run the narrowed form**, not
the whole-store one:

```
bin/docket check --verify --verify-base origin/main
```

**The objection to answer first, and it is not the cost.** `make check` is
expected to work in a bare checkout, and `--verify-base origin/main` needs a
ref that may be absent or stale there — the same problem `PL-0999` fixed for
`docket verify` by refreshing rather than trusting a local `main`. Whatever
this does has to degrade to today's behavior when no base can be resolved,
rather than failing the gate for a reason unrelated to the work. That, rather
than the 7 s, is the design.

**Do not treat the 7 s as the argument on its own.** The number that would make
this wrong is how often the replay changes a session's answer: a check firing
every run without changing a decision is a defect in the check by `CLAUDE.md`'s
own standard. One observed instance is not a rate. Count how many pull requests
have been red on this step before recommending it.

**Why it matters.** The gap is real and the item's own brief prices it
honestly: a failure class that only CI can find costs a round trip every time it
fires, and `PL-TFX5` paid one. What the item correctly refuses to do is treat
the 7.1 s as the argument. `CLAUDE.md` holds that a check firing every run
without changing a decision is a defect in the check, so adding one to `make
check` is only right if it changes an answer often enough to earn the seconds it
takes from every session forever - and one observed instance is not a rate.

**Decision needed.** Whether `make check` should run the narrowed verify replay,
`bin/docket check --verify --verify-base origin/main`.

Two things have to be settled, and the cost is the lesser of them:

1. **The rate.** How many pull requests have gone red on
   `bin/docket check --verify` while `make check` was green. That is a countable
   fact from the run history of `.github/workflows/quality.yml`, and nobody has
   counted it. If the answer is one - `PL-TFX5` - the change is not justified
   and this item closes `dropped` with the count as its reason.
2. **The degradation, which is the actual design.** `make check` is expected to
   work in a bare checkout, and `--verify-base origin/main` needs a ref that may
   be absent or stale there. Whatever lands has to fall back to today's
   behaviour when no base resolves, rather than failing the gate for a reason
   unrelated to the work - the problem `PL-0999` already solved for `docket
   verify` by refreshing rather than trusting a local `main`.

The `Makefile`'s own comment beside the `bin/docket check` line prices the
refusal at "60.0 s with the replay against 29.5 s without", which is the
whole-store form; the narrowed form measured 7.1 s on a branch touching 11
items and falls to nothing on a branch that changes no item. Update that comment
whichever way this is decided, so the recorded price matches the one in force.

**Done when.** `make check` either runs the narrowed verify replay - degrading
to today's behaviour when no base ref resolves, rather than failing the gate -
or this item is closed `dropped` with the pull-request count that showed the
replay would not have changed an answer. Either way the `Makefile` comment
beside `bin/docket check` states the price in force rather than the whole-store
figure it carries today.

**Re-measured 2026-09-21, on four cores - the same core count the `Makefile`
comment's figures were taken on.** The narrowed replay costs **5.9 s**, not the
30.5 s the recorded reason rests on:

| Command | Elapsed |
| --- | ---: |
| `bin/docket check` (what `make docket` runs) | 1.1 s |
| `bin/docket check --verify --verify-base origin/main` | 7.0 s |

Both timed twice, within 0.1 s. The replay reported `15 commands in 5.7 s
(44.8 s serially), scoped to 26 item(s)` - so the serial figure is still large
and it is the parallelism plus `--verify-base`'s narrowing that makes the
difference, which is this item's whole point. The `Makefile` comment's own
numbers - 60.0 s with the replay against 29.5 s without, 2026-09-05, four
cores - predate `PL-SDHR`'s `--verify-base` and are the whole-store sweep.

**One caveat the decision needs:** 26 items is *this* branch's scope, and a
branch touching a widely-cited file scopes more. The number above is a
representative case rather than a bound, and whoever takes this should say
which it needs to be.

**A live instance arrived the same day.** `#830`'s first push was failed by CI
on precisely the class this replay catches and `make check` cannot - see
`PL-J3WK`, which carries it.

**Recommended (a session's, 2026-09-21, not the project owner's), over leaving
`make docket` bare: add the narrowed replay, degrading to a silent skip when
`origin/main` cannot be resolved.** The measurement above is half the case; the
other half is that the `Makefile` comment's argument does not reach the form
being proposed.

That comment refuses the replay because it "finds work that *merged* without
its item being closed, and a pre-commit gate on a feature branch cannot have
changed that". That is correct, and it is an argument about the **whole-store**
sweep - which should stay where it is, on pushes to `main`, where its answer is
a fact about `main`. `--verify-base origin/main` asks a different question:
does *this branch's own* store edit hold up. A session can certainly change
that answer, because it just wrote the thing being checked. So the two forms
are not the same gate run at different prices, and the recorded reason retires
only one of them.

**The design constraint is offline, not cost, and the repository already
solves it.** `make check` has to pass in a bare checkout and with no network,
which is why `tools/pr_title_check.py --discover` states "Every way that can
fail is a silent skip, never a failure" and runs its lookup before the
expensive half. The same rule fits here: where `git rev-parse origin/main`
fails, run `bin/docket check` bare and print one line saying the replay was
skipped for want of a base. A gate that fails when it cannot look would be
worse than the gap it closes - `pr_title_check`'s own words.

**What would make this wrong**, stated so it can be checked rather than argued:
if a representative branch's scope is much larger than the 26 items measured
above, the cost stops being 5.9 s. The number to take before building it is the
replay's elapsed on the widest realistic scope - a branch editing a file many
open `verify:` commands read, `CLAUDE.md` or `ROADMAP.md` - not on this one. If
that comes back above roughly 20 s, the skip-by-default-with-an-opt-in-target
answer is better than putting it in `make check` unconditionally.


## Timed 2026-09-22: the cost does not fit as the commands stand, and one ordering fixes it

**The rate is no longer one instance.** Every `pull_request` run of
`quality.yml` since 2026-09-10 was read (722 completed, 56 failed): **20 runs
on 19 distinct pull requests failed at `verify replay, scoped to what this
branch changed`**, all with "`<id>` is open but its `verify:` command already
passes". It is the single commonest failing step - 20 of 56, ahead of
`doc_check.py check` at 18. Each went green 6 to 13 minutes later (median 8),
`#915` after 71. Run 35783744615 (`#915`) was re-read from the API to confirm
the step. So the check changes a session's answer about once every 18 pull
requests, which is the rate the brief asked for before recommending anything.

**The cost, four cores.** A branch that changes no item and no file an open
command reads adds nothing (1.3 s against 1.3 s bare). Anything else is set by
the slowest command in scope, not by the number of commands in scope. Four
real file sets from `origin/main`, replayed as working-tree edits:

| merge | files | scope | replay |
| --- | ---: | ---: | ---: |
| `462a34c7` | 21 | 32 | 14.1 s |
| `172f93e1` (widest of the last 80) | 19 | 55 | 41-46 s |
| `c128173a` | 6 | 11 | 52.0 s |
| `9070d8a0` | 5 | 22 | 67.5 s |

Modelled over the last 80 merges from per-command timings (all 222 candidates
run once at eight workers: 1,559 s serial, 217 s wall): **median 31 s, p75
67 s, p90 76 s, 41 of 80 above 20 s.** That is under full contention, so read
it as 15-25% high; the four measured rows are the honest figures. Either way it
fails the 20 s bar above, on the widest scope and on the typical one. `make
check` itself took 118 s on the same box that day, so the typical branch would
add about a quarter to it and the p90 branch nearly two thirds.

**Why, and the fix.** 98 of the 222 open commands run an expensive clause
(`uv run pytest <file>`, `doc_check.py check`) *before* the `grep` that
decides the answer, so an open item pays a whole test file only for the `grep`
to fail. Twenty commands take over 20 s that way (`PL-2M9N` 75 s, `PL-VN6M`
67 s, `PL-1BS2` 31 s). Run cheap clause first, the same model gives **median
1.2 s, p75 3.2 s, p90 27.6 s, mean 4.9 s**. The p90 is `PL-WTXB`, which has no
cheap clause of the strict kind. Swapping the two sides of `&&` leaves exit 0
meaning exactly what it meant before, because neither clause writes what the
other one reads.

**That reopens a ratified decision, which is why this item stays at
`needs-decision`.** `PL-FZ58` records the project owner declining a one-pass
repair of these legacy clauses on 2026-09-19 (ratified), and triage's guidance
says "each loses it as its item is started, never in a pass". The case for that
rested on the whole-store bill falling as the queue turns over. It is falling:
triage's guidance counted 82 pytest-beside-a-clause commands when its refusal
landed (2026-09-19/20), and a looser regex over today's store finds 60. But that case never priced a local gate, whose cost is set by one slow
command in scope rather than by the total. The slowest commands belong to
`ready` items that can sit for weeks.

**Recommended (a session's, 2026-09-22, not the project owner's): reorder
every legacy command cheap-clause-first in one pass, then add
`bin/docket check --verify --verify-base origin/main` to `make check`.** The
reorder was chosen over three alternatives:
- adding the replay as the commands stand, which costs about 30 s a run to
  save one 8-minute round trip in 18;
- teaching the replay to run `grep` clauses first itself, which saves the
  same time without touching any data, but puts a shell parser on the path of
  a check whose failure is a finding silently missed;
- waiting for the drain, which leaves the tail to the slowest `ready` items.

The reorder adds no code, keeps every recorded command literally what runs,
and leaves each command to lose its health-check clause when its item is
started, as `PL-FZ58`'s decision has it. Check it by running old and new forms
of each command and requiring the same exit-zero-ness. Today every one of the
222 exits non-zero.

**The degradation needs no Makefile logic.** `bin/docket check --verify
--verify-base origin/no-such-branch` already exits 0 with one "Not checked"
line naming the unreadable base (`PL-ZPDM`'s decline), which is the
bare-checkout behaviour this brief asked for.

## Decided: reorder, then add (project owner, 2026-09-22, ratified)

The owner chose this over three alternatives: adding the replay with the
commands as they stand, a replay-side parser that runs `grep` clauses first,
and waiting for the old commands to be fixed as their items start. It reopens
`PL-FZ58`'s never-in-a-pass for the reorder alone. The pass moves each
command's deciding clause to the front and removes nothing, so every command
still loses its health-check clause when its item starts.

**The work, in order.**

1. Reorder every open `verify:` that is a pure `&&` chain and runs an
   expensive clause (`uv run pytest …`, `python3 tools/doc_check.py check`,
   `bin/docket check`) before a cheap read-only one (`grep`, `! grep`,
   `test`). A clause piping read-only commands, such as `PL-WTXB`'s
   `! bin/docket --help | grep -q milestone`, may move too, by judgment.
   Leave anything with `||`, `;`, a redirection or a substitution untouched.
   Write each change with `bin/docket set <id> --verify '…' --overwrite` so
   the field stays canonical. The 98 is a scratch-script regex count; recount
   it rather than trusting it.
2. Prove the pass changed no answer. Run every rewritten command in its old
   and new form, and require the same exit-zero-ness for each; all 222 exited
   non-zero on 2026-09-22. Record the count here.
3. Replace the bare `bin/docket check` in the `Makefile` with
   `bin/docket check --verify --verify-base origin/main`. Rewrite the comment
   above it to state the price in force, re-timed after the reorder on a wide
   file set such as `172f93e1`'s, and the degradation: an unreadable base
   declines with one "Not checked" line and exit 0, so no shell conditional is
   needed.
4. Update the `quality.yml` comment beside the scoped step, which still says
   `make check` leaves the replay out.
5. Rewrite `.claude/skills/docket/modes/triage.md`'s "each loses it as its
   item is started, never in a pass". Say that one reorder pass ran on this
   item's evidence, and that stripping still happens as each item starts.
6. Close this item in the commit that adds the `Makefile` line, because its
   `verify:` passes from that commit on.

## Worked 2026-09-22: the reorder pass, and the proof it changed no answer

**Recounted with a quote-aware split rather than the regex: 96 commands
rewritten.** 94 meet step 1's test exactly - a pure `&&` chain running
`uv run pytest`, `python3 tools/doc_check.py check` or `bin/docket check`
ahead of a `grep`, `! grep` or `test`. Two more moved by the judgment step 1
allows, each a read-only pipe: `PL-T9XJ`
(`head -12 docs/resident-instructions.md | grep -q 'expert-review'`) and
`PL-WTXB` (`! bin/docket --help | grep -q milestone`). The 98 was a scratch
regex's count and was not reused.

**Left as they are, and why.** `PL-LSTW` carries a redirection and `PL-RBMK`
an `||`, both excluded by step 1. Three put an expensive clause ahead of a
`grep` that step 1's list does not name - `PL-M3YJ` (`uv run mypy`),
`PL-TMSN` (`uv run python tools/glyph_check.py`) and `PL-Y5ZB`
(`uv run python tools/agent_identity_check.py`) - and each ran in 0.4-0.5 s on
the warm cache `make check` leaves behind it, so moving them would buy nothing
the replay would notice.

**The proof, step 2.** Every rewritten command was run in its old and its new
form the way `verify.already_passing` runs one - `sh -c` from the repository
root, both docket guards set, a coverage file per run - with a 900 s limit so
that nothing was killed and every run reached a real exit status. **96 of 96
exit non-zero in both forms; none exits 0 in either.** Serial time fell from
1,396 s to 1 s, because none of the 96 cheap clauses passes today, so every new
form stops at its first clause.

**Two exit codes changed category, both still non-zero.** `PL-1FT6` went from
4 to 2: its test file does not exist yet, so pytest's usage error became
`grep`'s missing-file error, and the replay reads neither. `PL-W4XQ` went from
5 to 1, and that one changes what the replay reports: 5 is what
`verify.selects_no_test` reads as "selected no test", so that advisory no
longer fires on it before its work. It also showed the command cannot pass as
written in either order - `-k returning_to_a_mark` does not select the test its
`grep` names - so a line in `PL-W4XQ`'s brief now says to record the `grep`
alone when it starts.

**Only `verify:` changed in value.** `docket set` rendered 28 of the 96 files'
front matter canonically on the way past - key order, one quoted title
unquoted, blank lines after the fence - which is what it does on any field
write. Parsed before and after, every other field and every body is identical.
No branch in flight had edited any of the 96 files at the time of the pass.
