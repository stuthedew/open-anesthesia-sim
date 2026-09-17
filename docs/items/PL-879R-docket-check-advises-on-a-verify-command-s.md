---
id: PL-879R
title: docket check advises on a verify: command's outcome but never its shape, so a grep for an id, or for a file another item is known to create, is only reported once it has already started passing
priority: P2
effort: S
status: dropped
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-10
closed: 2026-09-17
reason: The shape route is refused on a count, and the goal is carried by PL-XMNC. Measured 2026-09-17 across the 168 open items carrying a verify:. The four narrow subsets this item named are 1, 5, 1 and 4 items, and the five-item one is a touches under-declaration rather than a command that fails to discriminate. The fifth and only populated subset - 36 negated discriminating halves, 31 of them the command's sole assertion - was executed against an untouched tree: 31 of 31 still discriminate, so a shape advisory would print 31 correct ids on every run, which is CLAUDE.md's 'a check that fires every run without changing a decision is a defect in the check'. A negation is the honest specification of work that deletes something; what broke PL-D1RT and PL-C4RS was another branch editing the file they read. The goal in this item's title is latency, and the mechanism for it already exists: the pull-request replay (bin/docket check --verify --verify-base, PL-SDHR) scopes to the items whose item file the branch edited, and widening that to the items whose command reads a file the branch changed catches all six recorded instances on the pull request that broke them, against four of six for the shape check. Full counts, the six-instance table and the cost measurement are in the brief.
---

**Problem.** docket check advises on a verify: command's outcome but never its shape, so a grep for an id, or for a file another item is known to create, is only reported once it has already started passing

**Raised by `PL-X7VY`** (main is red: `PL-XH1D`'s `verify:` passes because
`PL-78JQ` created the `CONTRIBUTING.md` it tests for), whose brief names it as
worth considering once that item is fixed and not required by it. Filed rather
than built, because it is a judgment about a command's wording and the line
between the decidable half and the judgment half has not been drawn yet.

**The evidence that it is a class.** Two commands broke the same rule on the
same day - a `verify:` must name something *only this item's work* creates.
`PL-XH1D`'s discriminating half was `test -f CONTRIBUTING.md`, satisfied when
`PL-78JQ` created the file. `PL-X9T3`'s was `grep -q 'PL-X9T3'
docs/WORKING_NOTES.md`, satisfied when `PL-55DH` wrote a section whose heading
cites that id. Neither command ever discriminated; another item's work merely
made that visible, and in both cases the outcome check reported it only after
it had started passing - on `main`, where no pull request shows it.

**What a shape check could decide, and what it could not.** Decidable from the
text alone: a discriminating half that is a bare `grep` for an item id, since
any note may legitimately cite one; a `grep` for a path the item's own
`touches` does not name; a `test -f` on a file some other open item's `touches`
declares. Not decidable: whether the phrase a `grep` names is one only this
item's work can produce, which is the judgment `CLAUDE.md` says not to script -
a tool that guessed at it would be worse than none, because its output would
look authoritative.

**Weigh it against the check that already works.** `_check_landed` in
`subprojects/docket/src/docket/checks.py` catches both instances above as an
error, late but reliably, and `CLAUDE.md`'s "A check earns its place every run,
or it is retired" is the bar a new advisory has to clear. So the question this
item answers is not "would a shape check find these" - it would - but whether
the subset it can decide without guessing is large enough to be worth an
advisory that fires on every run.

**Why it matters.** The outcome check reports the defect at the latest possible
moment: after the item was written, after it was pushed, and after some
unrelated item's work has satisfied the command. A shape check would report it
at the moment it is written, which is the only moment its author is still
holding the reasoning. Nothing is failing today - this is a question about
moving an existing finding earlier, not about a gap in coverage.

**Done when.** Either the decidable subset is implemented in `checks.py` with
tests, or this item is `dropped` with the reason recorded - that the subset is
too small, or too noisy, to earn a check that fires on every run.

**Decision needed.** Whether the decidable subset - a discriminating half that
is a bare `grep` for an item id, a `grep` for a path the item's own `touches`
does not name, or a `test -f` on a file another open item's `touches` declares -
is large enough to be worth an advisory that fires on every run. `_check_landed`
already catches both known instances as an error, reliably but late; this would
move the finding to the moment the command is written, at the cost of a check
that must clear `CLAUDE.md`'s "a check earns its place every run, or it is
retired".

Re-checked 2026-09-12: `checks.py` carries shape checks for re-entrancy
(`reenters_verify`), for reading the project check's own output
(`reads_check_output`), for multi-line commands and for a `verify:` with no
`touches` - so the shape half is an established pattern here rather than a new
kind of check. What none of them inspects is whether the command is
*tautological*, which is this item's subset.

## A third instance, and it is a sharper rule than the two above (2026-09-12)

`PL-MMWX`'s `verify:` was `grep -q 'coupled package' ROADMAP.md`, written having
been run and seen to fail - the practice this project asks for, followed
exactly. It began passing **inside the same branch that wrote it**, and
`bin/docket check --verify` caught it in CI.

The two earlier instances were another *item's* work satisfying the command.
This one is different and worse, because one of its two causes is
unavoidable: **a gate-listed item's entry in `ROADMAP.md` is its own title.**
So a file-wide `grep` for any phrase in the title of an item that will be listed
in a frozen list, a Required scope or a declined subsection stops discriminating
the moment it is listed, no matter how carefully it was run first. Running the
command beforehand cannot catch it, because the listing has not happened yet.

That makes a genuinely decidable case for the shape check this item is weighing,
and a narrow one: **a `verify:` whose discriminating half greps a file that
`ROADMAP.md`-style listings quote item titles into, for words that appear in the
item's own title.** Both halves are read from the store - the title is there,
and whether the command's grep pattern is a substring of it is a string test. No
judgment about whether the phrase is one only the work can produce is required.

The repair was to scope the grep to the section the work touches (`sed -n
'/^30\. Add patient factors/,/^31\./p' ROADMAP.md | grep -q ...`), which is
probably the advice a warning should carry.

**Two live instances, 2026-09-13, and they fell on opposite sides of the line
this item draws** (found while closing the stale-name batch of Gate 1).

- **Shape was checked, and it worked.** `PL-YTDN`'s `verify:` was written as
  `bin/docket check` piped into `grep`. `docket check --verify` refused it by
  shape - a nested run does not replay the open items' commands, so the grep
  matches nothing whether the work is done or not. It was caught *before* it
  could pass, which is what this item asks for, and the session had already run
  the command and watched it exit 1 for the wrong reason without noticing.
- **Shape was not checked, and it cost a red CI run.** `PL-L9FC`'s command was
  `doc_check check && grep -qi 'elimination' README.md`. `PL-B9VL` renamed the
  module that item's paragraph cites to
  `test_published_wash_in_and_elimination.py`, so the grep began matching the
  *filename in the citation* while the README paragraph it is about was
  untouched. Reported only as "already passes", on the branch that broke it,
  after the push.

The second is the case this item names: a `grep` loose enough that another
item's work satisfies it, invisible until it has already started passing. The
pair is also the argument for the shape check being worth extending rather than
retired - it caught one of the two at the right moment, and the one it missed
was a bare case-insensitive word grep, which is a shape.

**A fourth shape, and it is a different failure from the three above**
(`PL-32Z9`/`PL-D1RT`, 2026-09-16). Those three never discriminated; this one
discriminated correctly and was then **invalidated by another item's work**.
`PL-D1RT`'s command asserted an *absence*:

```
python3 tools/doc_check.py check && ! grep -qF '`v0.5.x — the interface pass` row of "The timeline"' ROADMAP.md
```

The phrase was present when the command was written (measured: 1 occurrence at
`c31449e`, 2 at `57fdb8c`), so it failed as intended. `PL-PHKP` (`#634`)
renumbered the row `v0.7.x`, the phrase went to 0, and the command began passing
on a tree whose work `PL-D1RT` had not done. `main` went red on that commit and
stayed red for three.

**It is decidable from the text alone, which puts it on the yes side of this
item's own line:** a discriminating half that is a negated match — `! grep`,
`! test -f`, `grep -v` used as the gate — asserts that a string is gone, and
*anybody* who deletes that string satisfies it. The paired shape
`.claude/skills/docket/SKILL.md` prescribes pins the **presence** of something
only the work creates, which nobody else can supply by deletion. No judgment
about whether the phrase is uniquely the item's is needed to say that, so this
one does not run into the "not decidable" paragraph above.

It also raises the population this item is weighing: the three instances above
are all from one day, and this makes four, from a shape the existing
`_check_landed` reports only after `main` has already gone red.

**A second instance of that fourth shape, 15 minutes later and on the same
branch of main.** `PL-C4RS`'s command was
`! grep -q 'Nineteen items, in the order the dependencies allow' ROADMAP.md`.
`#640` (`e5ad821`) placed one id into v0.5.0's `Required scope` and rewrote the
count word to **Twenty**; the string vanished, the negation began passing, and
run `#2118` reported `PL-C4RS, PL-D1RT are open but their verify: command
already passes`. Neither item's work had landed.

That makes **two** absence-asserting sentinels invalidated on `main` inside two
hours, by two unrelated items whose authors had no reason to look at either
command. It is the strongest argument this item has for the shape check being
worth an advisory: the population is not one command written carelessly, it is
every command of this shape in the store, and each one goes off when somebody
else edits the file it names. `bin/docket check --verify` catches them only on
`main`, after the fact, where no pull request shows it.

**So here is the population, counted rather than estimated** (2026-09-16, at
`4690412`): of the **168 open items carrying a `verify:`**, **36 - 21% - have a
negated discriminating half**, and every one of them is at `ready`. Sixty-three
closed items carry one too, which are records and not exposure. The 36:

`PL-037Y`, `PL-0BSC`, `PL-0R06`, `PL-2GQW`, `PL-2M4X`, `PL-38PN`, `PL-5748`,
`PL-59WB`, `PL-5F26`, `PL-60CQ`, `PL-75R0`, `PL-880Z`, `PL-8BLJ`, `PL-BHJW`,
`PL-C25K`, `PL-CY5H`, `PL-CY8B`, `PL-CZTR`, `PL-DBGT`, `PL-DL4M`, `PL-FT3M`,
`PL-FV7G`, `PL-GDS2`, `PL-GXPP`, `PL-J45M`, `PL-JXVD`, `PL-LM8P`, `PL-LSTW`,
`PL-MSFB`, `PL-S5YM`, `PL-TTMF`, `PL-VYK1`, `PL-W3Q5`, `PL-WHQS`, `PL-WTXB`,
`PL-X5L4`.

That is the number the decision should turn on, in both directions. It is large
enough that two going off in one afternoon is a rate rather than a coincidence,
and large enough that an advisory firing on all 36 at once would be the kind of
check `CLAUDE.md` says to retire rather than promote. The shape that answers
both is a check that fires **as a command is written or an item reaches
`ready`**, not one that re-lists a standing 36 every run - which is the same
distinction this item's own "at the moment it is written" paragraph already
draws, now with a count behind it. `PL-S5YM` is on the list, and is the item
`PL-Y1W6` was filed against when `main` went red once before - by a bare `-k`
selector rather than by this shape, so it is a near neighbour and not a third
instance.

## Decided 2026-09-17: the shape check is refused, and the goal is one scope widening away

**The subsets were counted, and only one of the five has a population.** Across
the 307 open items, 168 carry a `verify:` (625 closed ones do too, which are
records rather than exposure). Each candidate this brief names, counted against
the discriminating clause:

| Candidate subset | Open items |
| --- | --- |
| (a) discriminating half greps a bare item id | 1 (`PL-PQQ2`) |
| (b) discriminating half names a path its own `touches` omits | 5 |
| (c) `test -f` on a path another open item declares | 1 (`PL-46VF`) |
| (d) greps a title-quoting listing file for words from its own title | 4 |
| (e) discriminating half is negated (`! grep`, `! test`, `grep -v`) | 36 (21%) |

(a), (c) and (d) are 6 items between them. (b)'s five are not this item's defect
at all: one is a trailing-slash artifact (`PL-MSFB` declares `docs/items/` and
greps `docs/items`), and the other four grep a **test file the item will add to
and did not declare**, which is a `touches` under-declaration rather than a
command that fails to discriminate. So four of the five subsets are a regex each
for a handful of items, at least one of which fires wrongly.

**And the fifth subset — the one with the population, and the one both
2026-09-16 failures came from — is entirely correct today.** Of the 36 negated
commands, 5 pair the negation with a positive assertion; 31 are negation-only.
Every one of those 31 negation clauses was executed against this untouched
tree on 2026-09-17: **31 of 31 exit non-zero. Not one is satisfied.** Each is
discriminating exactly as written.

That is the number this decision turns on, and it settles it. An advisory on the
negated shape would print 31 ids on every run, all 31 of them correct, forever —
`CLAUDE.md`'s "a check that fires every run without changing a decision is a
defect in the check" describes it exactly, and its "reserve hard failure for
exact rules; a signal needing context is an advisory, and an advisory nobody
acts on is a candidate for retirement rather than promotion" is the rule this
one would be born failing. A negation is not a defect: **31 of these items are
work that deletes something**, and asserting the deleted string is gone is the
honest specification of that work. What made `PL-D1RT` and `PL-C4RS` go red was
not their shape but somebody else editing the file they read.

**So shape was the wrong axis, and the mechanism this item's goal wants already
exists.** The goal in the title is *"only reported once it has already started
passing"* — latency, not wording. `.github/workflows/quality.yml` already
replays commands on every pull request (`bin/docket check --verify --verify-base
"$VERIFY_BASE"`, `PL-SDHR`), and `vcs.changed_items()` scopes that replay to
**the items whose item file the branch edited**. That scope is the whole gap:
every recorded instance was invalidated by a branch that edited a file the
command *reads* while never touching the item's own file, so the pull request
that broke it replayed nothing and the whole-store sweep on push-to-`main`
reported it after the merge, where no pull request can go red.

Checked against the commit that did the invalidating, for all six instances this
brief records:

| Item | Its command reads | Invalidated by | That branch touched it |
| --- | --- | --- | --- |
| `PL-XH1D` | `CONTRIBUTING.md` | `#487` (`4a4a483`) | created it |
| `PL-X9T3` | `docs/WORKING_NOTES.md` | `#490` (`f393e16`) | yes |
| `PL-MMWX` | `ROADMAP.md` | its own branch | already in scope |
| `PL-L9FC` | `README.md` | `#512` (`bc21c32`) | yes |
| `PL-D1RT` | `ROADMAP.md` | `#634` (`52205f6`) | yes |
| `PL-C4RS` | `ROADMAP.md` | `#640` (`e5ad821`) | yes |

**Six of six, at the moment they broke, on the pull request that broke them** —
against four of six for the shape check, which cannot reach `PL-XH1D` without a
cross-item `touches` lookup and cannot reach `PL-L9FC`'s bare `grep -qi
elimination` without flagging every case-insensitive word grep in the store.

**Its cost is bounded and was measured.** 83 distinct files are read by some
open item's discriminating clause. The hottest would add 10 replays
(`docs/WORKING_NOTES.md`), then 8 (`subprojects/docket/tests/test_checks.py`),
7 (`ROADMAP.md`), 6 (`subprojects/docket/tests/test_cli.py`), 6
(`docs/MODEL.md`). A branch touching none of the 83 adds nothing, which is most
of them. Only discriminating clauses count: `tools/doc_check.py` appears in 54
commands and in every one of them it is the health half, so a branch editing it
must not drag 54 replays behind it.

**Dropped on the second of the two dispositions this item's `Done when.`
names** — the subset is too noisy to earn a check that fires on every run — with
the count recorded so the shape route is not re-proposed from the same evidence.
The goal is carried forward by `PL-XMNC`, under `feature: verify-invalidation`.
