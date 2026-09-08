---
id: PL-X7VY
title: main is red: PL-XH1D's verify: passes because PL-78JQ created the CONTRIBUTING.md it tests for, so docket check --verify errors on every run
status: untriaged
added: 2026-09-08
---

**Problem.** main is red: PL-XH1D's verify: passes because PL-78JQ created the CONTRIBUTING.md it tests for, so docket check --verify errors on every run

**Found 2026-09-08** by `PL-55DH`, checking whether the base was green before
opening a pull request onto it. `origin/main` has been red since `cf6f71f`
(#488) and `4a4a4831` (#487) - runs 1691 and 1689 - on the `checks` job, and
the failure is one line:

> `PL-XH1D` is open but its `verify:` command already passes (1 of 111
> checked).

**Why it started.** `PL-XH1D`'s command is
`test -f CONTRIBUTING.md && python3 tools/doc_check.py check`. `PL-78JQ`
created `CONTRIBUTING.md` in #487, so the first half now passes and the second
half passes whenever the documentation is internally consistent - which it is
before the item is started too. The command was invalidated by another item's
work, and it did not stop discriminating: it never did.

**`PL-XH1D` is genuinely open**, so closing it is the wrong resolution.
`PL-78JQ`'s own brief says so in terms: "Deliberately not covered there: how
the project is developed and what each attribution trailer means. That is
`PL-XH1D`, still open, and saying it twice is how two documents come to
disagree." The item still owes the attribution disclosure in `README.md`, the
trailer scheme in `CONTRIBUTING.md`, and the owner's approval of any statement
made about him.

**Nothing but a push to `main` can see it, and that is the sharper half.**
`make check` runs `bin/docket check` without `--verify`, so no local gate
reaches an open item's command. A *pull request* runs
`bin/docket check --verify --verify-base origin/<base>`, scoped by `PL-P3B6`
and `PL-L17Q` to the items the branch itself edited - correctly, since a branch
cannot have changed whether some other item's work merged. The whole-store
sweep runs only on a push to the default branch.

So the failure is invisible everywhere a session could act on it and visible
only after the merge, on a run nobody is watching and no pull request shows.
Measured 2026-09-08: `#490` is green on exactly the tree whose `main` run is
red. Every merge from here re-reds `main` until this is fixed, and each one
looks like a fresh break rather than the same one.

That is two of `CLAUDE.md`'s three compounding-friction tests at once - it
gives a wrong answer silently to every branch, and the advisory that would
carry it is one nobody is positioned to read - which is why this is worth
raising rather than filing and moving on.

**The fix is one line**, and it is the shape the `docket` skill prescribes -
something that runs and passes today, paired with a `grep` for what this item's
own work adds:

```
verify: python3 tools/doc_check.py check && grep -qF 'Co-authored-by' CONTRIBUTING.md
```

Run against the tree as it stands: `doc_check` passes, and the `grep` exits 1
because `CONTRIBUTING.md` does not mention the trailer scheme. Any phrase only
`PL-XH1D`'s work puts in the file would do; the trailer name is the one the
brief guarantees will be there.

**Not fixed by the session that found it**, deliberately. `CLAUDE.md`'s
fix-now door requires the change to touch no file outside the current item's
`touches`, and `docs/items/PL-XH1D-*.md` is outside `PL-55DH`'s. `PL-XH1D` is
also `not-delegable` on the ground that its wording states publicly what the
project owner did and did not write - so its `verify:` is worth a moment of
his attention rather than a passing edit.

**Done when** `bin/docket check --verify` reports zero errors on `origin/main`,
and `PL-XH1D`'s command fails against a tree that has not done its work.
