---
id: PL-YFXG
title: bin/docket record can never supply the pr of an item whose work is the queue itself - _carried_work reads a queue-only diff as a closure that landed without its work, so PL-YTDN left main red with an error no command could clear
priority: P2
effort: S
status: done
classes: defect
feature: commit-provenance
milestone: v0.4.30
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-09-19
closed: 2026-09-19
pr: 717
verify: grep -q 'def test_a_queue_only_closure_supplies_its_pr' subprojects/docket/tests/test_vcs.py
---

**Problem.** bin/docket record can never supply the pr of an item whose work is the queue itself - _carried_work reads a queue-only diff as a closure that landed without its work, so PL-YTDN left main red with an error no command could clear

**Found 2026-09-19 closing `PL-Y5JX`**, as the reason `origin/main` was red and
`bin/docket record` could not clear it.

`_number_closing` in `subprojects/docket/src/docket/vcs.py` walks back to the
commit that wrote `status: done` into an item's file, then asks
`_carried_work` whether that commit changed anything outside `docs/items/`. If
it did not, the number is declined - on the reasoning that a closure landing
without its work would name a pull request whose diff does not hold the work
(`PL-YDL6`).

**That test is right about the hazard and wrong about the shape.** A commit
that changed only the queue is not necessarily a closure separated from its
work; it is also what an item whose work *is* the queue looks like when it
lands correctly. `PL-YTDN` is the worked example: its whole deliverable was
renaming drifted item files and repairing the `touches` declarations naming
them, so `ceb9385` (#712) changed 12 files, all under `docs/items/`, and
carried both the work and the closure. `_carried_work` returned `False`, the
number was declined, and `docket check` raised its error rather than its
recoverable advisory:

```
PL-YTDN-...md: marked done on `origin/main` but records no `pr`
```

**Why it matters.** The error fails `make check`, so it fails CI on every
branch, not only on the one that closed the item - `main`'s own quality run
#2304 on `54b7a97` and every branch cut from it. Nothing clears it by the
documented path: bare `bin/docket record` writes every number the base can
supply and this is a number it decides it cannot, while the `docket` skill
forbids writing `pr:` by hand. The escape used on 2026-09-19 was the explicit
`bin/docket record 712 --merge ceb9385`, which a session only reaches by
reading `vcs.py` to find out why the bare form did nothing.

It recurs by construction rather than by accident. Queue-only work is a
standing category here - a release-tag item, a triage pass, a stranded
recovery, a rename pass - and `.claude/skills/docket/SKILL.md` names it as
such under **Mode: start an item**.

**The project already draws this distinction correctly twice, in other
modules,** and both read the *item's* declaration rather than the commit's
diff:

- `branches_in_flight` exempts an item whose own `touches` never leaves
  `docs/items/`, because for those the queue edit is the work (`PL-7790`).
- `sanctioned_queue_edit` in `verify.py` distinguishes a capture and a `pr:`
  write from an item being tampered with, by reading what the diff *is* rather
  than only where it lands.

So the likely repair is to ask the same question here: a closure commit whose
item declares `touches` wholly inside the store directory carried its work,
whatever its diff looks like. The `PL-YDL6` hazard stays refused for every
item that declares work outside the queue, which is the set that hazard was
measured on.

**Done when.** `bin/docket record`, bare, supplies the number for an item whose
declared work lies wholly inside `docs/items/` and whose closure commit carries
that work, and still declines where the work genuinely landed in a different
pull request. A test drives `PL-YTDN`'s shape: an item whose `touches` names
only the store directory, closed by a commit whose whole diff is item files.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "Its problem did not exist at the 2026-09-06 freeze, so the snapshot rule defers it on its own terms". This item is also named in paragraphs quoted in the briefs of `PL-ZM48` and `PL-WFFX`.

> **A second on that same ground, and it is the rule catching itself** (`PL-YFXG`, 2026-09-19). `_carried_work` was written on 2026-09-12 under `PL-YDL6`, six days after this gate froze. So the mechanism this item describes did not exist when the 2026-09-06 list was made. It is `P2`, classed `defect`, wholly workflow-lane apparatus, and neither `safety` nor `science`. It was found while closing `PL-Y5JX`, as the reason that `main` was red. When a closure's work is queue files, its `pr` cannot be recovered. The resulting `docket check` error then fails `make check` on every branch. Recording it here on the same day is what the disposition rule exists to force, because the session that found it is the one that would otherwise leave it unrecorded.

> - PL-YFXG (S) bin/docket record can never supply the pr of an item whose work is the queue itself - _carried_work reads a queue-only diff as a closure that landed without its work, so PL-YTDN left main red with an error no command could clear — closed in v0.4.30
