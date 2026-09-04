---
id: PL-KCQ7
title: 40 percent of the suite's wall clock (29.2 s of 70 s) tests subprojects/docket, so the workflow apparatus dominates the simulator's own gate
priority: P3
effort: S
status: done
classes: perf
feature: dev-tooling
milestone: v0.3.5
touches: subprojects/docket/tests
added: 2026-09-03
closed: 2026-09-04
pr: 277
verify: python3 tools/doc_check.py check && grep -qF 'Decided: leave it (project owner, 2026-09-04)' docs/items/PL-KCQ7-40-percent-of-the-suite-s-wall-clock-29-2-s-of.md
---

**Problem.** Measured 2026-09-03 on four cores, before `PL-WCZV` put `-n auto`
on the suite: `tests/` (the simulator) took 40.8 s and
`subprojects/docket/tests` took 29.2 s of a 70 s run. So two fifths of the
project's most expensive check tests the workflow apparatus rather than the
thing the project is for.

**Why it matters, and why it is P3 rather than higher.** `CLAUDE.md` holds the
simulator and the apparatus to deliberately unequal standards - the apparatus
to "working reliably and staying streamlined" - and this is the clearest
measure yet of what the apparatus costs the simulator. But it is a ratio, not a
defect: those tests are the reason `docket` is trustworthy enough to be relied
on, and `PL-LXR3`, `PL-T940` and `PL-VG7G` are each a case where the suite
caught a check that would have lied.

`PL-WCZV` also changed the arithmetic that made this look urgent. The whole
suite now runs in 26.9 s rather than 70 s, so docket's share is roughly the
same fraction of a much smaller number, and the largest item in `make check` is
now `bin/docket check` instead (`PL-8BFV`). This is worth knowing and is not
worth acting on by itself.

**Where.** `subprojects/docket/tests` - `test_cli.py`, `test_vcs.py` and
`test_verify.py` are the three largest files and `test_verify.py` is the one
that shells out most.

**Options, none recommended yet.** Leave it, which is a real answer and
probably the right one. Or narrow the shell-outs in `test_verify.py`, which are
what make it slow and are also what make it honest. Or split the apparatus
suite out of the default `testpaths` so `make test` runs the simulator alone -
cheap, and it costs the property that one command proves the whole tree.

**Done when.** A decision is recorded, including the decision to accept it as
the cost of a trustworthy queue.

**Decision needed.** Whether to act on the ratio at all. Leaving it is
recommended - `PL-WCZV` took the suite to 26.9 s, so the absolute cost is now
small, and the three named options each trade away something the apparatus is
trusted for. Recording that answer is what closes this; it is here so the ratio
is not rediscovered and treated as new.

## Decided: leave it (project owner, 2026-09-04)

The owner put the question in its sharpest form - should `subprojects/docket`
come off the uniform Class C bar, and would fewer checks there be faster
without costing bugs? No, on all three parts, and the third is the one that
settles it.

**There is no classification to move it off.** IEC 62304 classifies items of
the *medical device software system*. A backlog tool that never runs in the
product and computes no displayed value is outside its scope rather than
Class A within it, so re-classing changes no check either way - the gate is set
by `Makefile`, not by a letter. The only place this project was ever going to
write a class down is `PL-BLHV`, still `needs-decision`, and its subject is the
application. `CLAUDE.md`'s unequal standards, quoted above, are already the tier
the question was reaching for.

**The gate is already tiered, and this tree is already on the low tier.** The
one Class-C-grade check in it - 100% of statements *and* branches - is scoped to
`anesthesia_sim.core` by `--cov=`. `subprojects/docket` has no coverage floor at
all. What still reaches it is `ruff` at 0.1 s and `mypy` at 6.9 s repo-wide, so
there was never anything to relax except the tests themselves.

**Cutting those tests would cost bugs, and the store says so numerically.**
63 of its 125 `defect`-classed items touch `subprojects/docket` - about half
this project's defects, out of ~3,600 source lines - and **39 of the 63 describe
a silent failure**: the check passed and the wrong answer was delivered anyway.
`PL-LXR3`, `PL-T940` and `PL-VG7G`, named above, are three; two more corrupted
the safety classification itself. `PL-BR4G`: `parse_front_matter` silently kept
the last of a duplicate key, so a corrupt item passed `docket check`. `PL-MVC2`:
nothing checked `classes` against a vocabulary, so `classes: safey` left
safety-critical work seatable in the bottom band with zero errors reported.
That is exactly the failure class human use does not catch and a test does.

The governing standard for a tool of this kind is not IEC 62304 at all but
**ISO 13485:2016 clause 4.1.6** - validate software used in the quality system,
proportionate to the risk of its *use*. docket's risk is not patient harm; it is
silently mis-recording the safety class of product work, which the two items
above are worked examples of. Proportionate validation against that history is
roughly what the suite already provides.

**On the three options above.** *Narrowing the shell-outs in `test_verify.py`*
has no fat to take: measured 2026-09-04, the 12 slowest docket tests sum to
13.7 s and the remaining ~520 spend ~16 s at roughly 30 ms each, which is
`git` subprocess startup spread thin rather than a few slow tests. Cutting time
there means cutting coverage broadly. *Splitting the apparatus out of the
default `testpaths`* is worse than doing nothing on this evidence: against a
39-instance silent-failure history, the session editing docket is precisely the
one that has to see the failure. So: leave it, as the recommendation above said.

**And the ratio was answered by removing work rather than checks.** `PL-WCZV`
put `-n auto` on the suite; `bin/docket check` is now the largest item in
`make check` (`PL-8BFV`), not the tests. Deleting the entire docket suite would
have returned 29.8 s of the 122 s gate that then stood; `PL-WCZV` returned
roughly twice that and removed nothing.
