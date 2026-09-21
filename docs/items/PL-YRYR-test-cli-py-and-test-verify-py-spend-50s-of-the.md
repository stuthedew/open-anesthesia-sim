---
id: PL-YRYR
title: test_cli.py and test_verify.py spend ~50s of the suite's 272s serial cost on per-test git fixtures - 304 tests, no test above 1.3s, a git init plus config plus add plus commit in each
priority: P3
effort: M
status: ready
classes: perf, test
feature: verify-replay-cost
touches: subprojects/docket/tests/conftest.py, subprojects/docket/tests/test_git_isolation.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md
added: 2026-09-19
verify: uv run pytest subprojects/docket/tests/test_git_isolation.py -q
root-cause-of: PL-W6NY, PL-KCQ7, PL-8T83, PL-FZ58
generator: spent - the ambient commit.gpgsign this item isolates the suite from can no longer reach a test repository, so no further measurement can be inflated by it
recurrences: 2026-09-05 PL-W6NY
---

**Problem.** test_cli.py and test_verify.py spend ~50s of the suite's 272s serial cost on per-test git fixtures - 304 tests, no test above 1.3s, a git init plus config plus add plus commit in each

**Where it comes from.** `PL-FZ58` re-measured the whole suite serially on
2026-09-19 (3,180 tests, 272 s accounted). `subprojects/docket/tests/test_verify.py`
is 27.2 s over 121 timed tests and `test_cli.py` 21.2 s over 119, and neither
has an outlier to remove: their slowest single tests are 0.6 s and 1.26 s. The
shape is flat per-test cost, and `user + sys` runs well under wall on both
(13.4 s of 22.6 s, 14.9 s of 28.5 s), which is the signature of waiting on
subprocesses rather than computing. Each test that needs history builds its own
repository — `git init`, two or more `git config`, `git add -A`, `git commit`,
sometimes a tag, a branch and a merge.

**Why it is filed rather than fixed.** It is a real cost and a modest one. The
suite already runs at `-n $(cpu*2) --dist worksteal` and comes in at 77.8 s
wall against 272 s serial on four cores — within 11% of the CPU floor — so
halving these two files buys roughly 6 s of that run. `PL-FZ58` is the item
that went looking for a saving here and concluded the replay's cost was never
where this would help.

**The shape a fix would take**, so a later session does not re-derive it: build
one repository per session in a module-scoped fixture and copy the directory
per test, rather than re-running git. `shutil.copytree` of a small `.git` is
one syscall-bound operation against five to eight process spawns. The tests
that need a *different* history (a squash merge, a rewritten base, a bare
remote) keep building their own; the win is in the majority that need only "a
repository with one commit on it".

**What must not be traded for it.** These are the tests that keep `docket`
correct about refs, and `.claude/rules/apparatus-standard.md` sets the bar at
"its absence would let a real defect through". A shared fixture that leaks
state between tests would do exactly that, silently — so the fix is worth
taking only if each test still gets an independent tree.

**Why it matters, and why it is filed at P3.** The honest case is modest and
the brief above says so: roughly 6 s off a 77.8 s parallel run, on a suite
already within 11% of its CPU floor. What makes it worth recording rather than
dropping is the direction of travel - this is per-test cost rather than an
outlier, so it scales with the number of tests these two files carry, and they
are the files that grow every time `docket` learns something new about refs.
`PL-FZ58` measured the whole suite looking for a saving and concluded the
replay's cost was never here; this is the residue that measurement left, filed
so the next person to go looking does not re-derive it.

The reason it is `perf` and `test` rather than either alone is that the risk
and the reward sit in different places. The reward is wall-clock; the risk is
correctness, because these are the tests that keep `docket` honest about refs
and a fixture leaking state between them would let a real defect through
silently. `.claude/rules/apparatus-standard.md` sets that bar - "its absence
would let a real defect through" - and it is the bar this fix has to clear, not
the stopwatch.

**Done when** the two files' serial cost is materially down with every test
still running against a tree no other test has touched, or the item records
that the sharing cannot be made safe.

**`PL-W6NY` is this same finding and is dropped in its favour** (`PL-JKML`'s
duplicate sweep, 2026-09-20, confirmed on independent refutation). It measured
`test_verify.py`'s `_repo` fixture on 2026-09-05 - 22.5 s for the file, about
12 s of it non-sleep, across what were then 64 call sites and are 113 today -
and filed it as `PL-VJ7W`'s residue. This item reaches the same fixture from
`PL-FZ58`'s whole-suite serial run and additionally carries `test_cli.py`, so
containment runs one way: finishing this leaves nothing of `PL-W6NY` standing,
while finishing `PL-W6NY` would leave `test_cli.py`'s 21.2 s untouched. That
asymmetry is what makes it a drop rather than a grouping.

**Two things from `PL-W6NY` that are carried rather than lost.** Its fallback
is stricter than this item's: where the fixture cannot be made cheaper safely,
`PL-W6NY` requires the negative result to land **as a comment on `_repo` in the
code**, not only in the item - so the next session to open the fixture reads
why it is shaped as it is, rather than re-deriving it. And its framing of the
constraint is the one to keep: the fixture leaks state between tests that
commit into their own repository, so correctness, not speed, sets the ceiling
on any rework.

## What the cost actually was (2026-09-21)

**The premise above is wrong about where the time goes, and the sketched fix
would have bought almost none of it.** Counting and timing every `git`
subprocess the tree spawns - not the five-spawns-per-test shape, but each
spawn's own cost - separates them by a factor of 35:

| git subcommand | calls | total | each |
| --- | --- | --- | --- |
| `commit` | 563 | 40.92 s | 72.7 ms |
| `show` | 685 | 1.42 s | 2.1 ms |
| `add` | 545 | 1.36 s | 2.5 ms |
| `config` | 506 | 0.99 s | 2.0 ms |
| `init` | 194 | 0.71 s | 3.7 ms |

`init`, `config` and `add` together are 3.06 s of a 60.44 s run. The brief
counted them because they are visible in the fixture; the commit is the bill.

**And the commit was slow for a reason no test names.** `/root/.gitconfig` in
the agent container sets `commit.gpgsign = true` with `gpg.format = ssh`, so
every commit these tests make signs an SSH key. Measured in a scratch
repository, 20 commits per arm, interleaved against a control to rule out
warm-up: **69.6 ms signed against 4.3 ms unsigned, and 67.7 / 4.3 on the repeat.**
Nothing under `subprojects/docket/` read or set that config; it reached the
test repositories because git reads `~/.gitconfig` for every repository on the
machine.

**The fix is therefore isolation rather than sharing.** `conftest.py` points
`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` at `/dev/null`, which git
documents as "read no configuration at this level" (git 2.32 and later).
Whole-tree result, same 1,442 tests, same machine, nothing else changed:

| | before | after |
| --- | --- | --- |
| wall clock | 60.44 s | **21.51 s** |
| git subprocess time | 53.19 s | 14.32 s |
| 563 commits | 40.92 s | 2.87 s |

That is 64% off the tree the two named files live in, against the roughly 6 s
the brief predicted for the copytree rework - and it takes no test with it:
`_repo` and every helper in `test_cli.py` still builds its own repository,
`git init` per test, so the constraint under **What must not be traded for it**
is not weakened but untouched. There is no shared fixture to leak.

## Where the saving lands, and where it does not

**`make check` does not get faster, and the brief already said why.** Its
pytest line runs `-n $(cpu*2) --dist worksteal`, and the brief's own reading -
77.8 s wall against 272 s serial, within 11% of the CPU floor - is what that
means: the docket tree's cost was subprocess *waiting*, which xdist was already
overlapping with other workers' CPU work. Measured both ways on this branch,
full suite, 4 cores:

| | without `conftest.py` | with |
| --- | --- | --- |
| `make check`'s pytest line | 77.83 s | 78.78 s |

That is noise, and it is the honest answer to "did the suite get faster". It
did not. Stating it here because the serial numbers above would otherwise be
read as a claim about the gate, and a later session measuring `make check` to
check this item would find nothing and conclude the work did not land.

**Where it lands is the verify replay, which is serial by construction.**
`check --verify` runs one command per open item, one after another, and 44 open
items' `verify:` commands run a file in this tree. Per-command cost, measured
with the conftest moved aside and restored:

| `verify:` names | open items | before | after | saved each |
| --- | --- | --- | --- | --- |
| `test_verify.py` | 10 | 30.91 s | 10.03 s | 20.88 s |
| `test_cli.py` | 15 | 25.13 s | 8.62 s | 16.51 s |
| the whole tree | 3 | 60.44 s | 21.51 s | 38.93 s |
| `test_checks.py`, `test_vcs.py`, `test_release.py`, `test_roadmap.py` | 22 | 0.4-0.5 s | 0.4-0.5 s | none |

**573 s - 9.6 minutes - off the whole-store replay**, which runs on every push
to the default branch. `PL-FZ58` measured that replay at 1,458 s serial, so
this is roughly 39% of it, against the 6 s the sketched rework was predicted to
buy on a run that turns out not to be the one that pays.

The last row is the useful negative: only these two files build real
repositories per test. The other four are already sub-second and this changes
nothing for them, which is also why the brief was right to name these two and
no others.

**Why the correctness half outranks the stopwatch.** A signing key behind a
passphrase or held on hardware does not make this suite slow - it makes `git
commit` block on a prompt or fail outright, and every test here that needs
history fails with it on a machine where nothing is wrong. That is the same
class as `PL-6YL1` and the macOS `python3` items: a suite that is green in one
environment and red in another for a reason it never names. Isolation removes
the class, not just the instance.

**`test_git_isolation.py` is what makes the removal visible.** Deleting
`conftest.py` costs nothing the suite reports - every test still passes, three
times slower - which is the silent failure `.claude/rules/apparatus-standard.md`
sets its floor against. The second test builds a `HOME` whose `.gitconfig`
turns signing on and asserts git ignores it, so the assertion means the same
thing on a machine whose own config is empty. Both were watched failing with
`conftest.py` moved aside: `AssertionError: read commit.gpgsign='true' from
outside`.

**What is recorded rather than done.** The repository's own `tests/` tree pays
the same toll on a smaller bill - 142 commits, 6.20 s of a 257 s run - and
takes the identical two lines in the `tests/conftest.py` that already exists.
It is a separate item because it is the simulator's tree, held to the other
standard, and 2.4% does not justify widening a `P3` into it.

**Done when** - satisfied by isolation rather than by sharing. The cheaper
route the brief could not see was to stop the cost being paid at all, and the
sketched module-scoped copytree is refuted rather than deferred: it is more
code, it buys single-digit milliseconds per test once the commit is cheap, and
it pays for them with the one property these tests cannot give up.
