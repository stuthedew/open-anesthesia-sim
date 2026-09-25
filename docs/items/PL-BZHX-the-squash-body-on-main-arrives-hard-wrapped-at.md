---
id: PL-BZHX
title: The squash body on main arrives hard-wrapped at about 72 columns, which splits Markdown table rows and flattens nested lists in the permanent record: #993's table and sub-bullets are intact on GitHub and broken in a56c86c4
priority: P3
effort: S
status: needs-decision
classes: defect
feature: pr-body-integrity
touches: docs/maintainer.md, tools/pr_body_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-25 triage pass
added: 2026-09-24
---

**Problem.** The squash body on main arrives hard-wrapped at about 72 columns, which splits Markdown table rows and flattens nested lists in the permanent record: #993's table and sub-bullets are intact on GitHub and broken in a56c86c4

**Found by `PL-LWMS`'s re-confirmation, 2026-09-24.** Pull request `#993` (`GET
/repos/stuthedew/open-anesthesia-sim/pulls/993`) carries a four-row Markdown
table with each row on one line, and a two-level list under `CLAUDE.md:`. Its
squash commit on `main`, `a56c86c4` (`git log -1 --format=%B a56c86c4`), breaks
every table row at about column 72: "| `arm` | 0 | Only item files change, no
claim on the branch is" then "unreleased, and ...". It also moves the
sub-bullets to column 0. Markdown renders a broken row as a paragraph and a
flattened sub-bullet as a sibling, so the permanent record loses both
structures. `tools/pr_body_check.py`'s module docstring calls
that record "the permanent
commit message a reader of `main` meets".

[superseded 2026-09-25: re-measured at triage, below] **Scale is unmeasured.**
The re-confirmation's history auditor counted 40 of 57
recent tabled bodies broken this way, but no second pass re-ran it. Re-measure
before sizing the item.

**Re-measured 2026-09-25 against 46954a81**, from `git log --first-parent
origin/main` alone. A table row that does not end in `|` counts as broken; I
spot-checked three hits and all three were real wraps.

- Since 2026-09-10: 96 of the 140 squash bodies that carry a table have a
  broken row.
- Since 2026-09-22, when `PL-WFFX` closed: 9 of 10.

`a56c86c4` still reads as described above, and pull request `#993`'s body on
GitHub still has one-line rows and indented sub-bullets.

**Not every merge wraps.** `5ec938fe` and `f22d5dd0`, both merged after
2026-09-22, landed with whole prose paragraphs on single lines, 14 and 21 body
lines past 80 columns. Other bodies wrapped but kept their sub-bullet
indentation. So there are at least two populations. Git records the same
committer (GitHub) and author for all of them, so the merge path has to come
from the forge, not from git.

[superseded 2026-09-25: `PL-Y1W0` landed in `#998` with the whitespace collapse
kept, so `--compare` still cannot see this] **Nobody owns it yet.**
`PL-Y1W0`'s `pr_body_check.py --compare`, in flight on
`claude/brave-carson-6hbxas`, collapses whitespace on both sides because "the
squash message arrives hard-wrapped". So it treats the wrap as benign by
design, and will not report this.

**Why it matters.** `main`'s commit message is the copy of a pull request's
reasoning that outlives the forge. On nearly every body that carries a table
or a nested list, that copy loses the structure. A table row split over two
lines is still readable. A flattened sub-bullet is not: it reads as a sibling
of its parent, so the hierarchy the author wrote is lost. The cost is in
fidelity, not safety, and it recurs on every merge through the wrapping path.

**First question: which merge path wraps.** A null-armed auto-merge lands the
live body (`PL-M7W1`'s 2026-09-23 evidence). Hand merges go through a client,
and `docs/maintainer.md` names the Mac and the GitHub iPhone app. Compare the
two populations on `main` before choosing a remedy. A merge-client instruction
belongs in `docs/maintainer.md`. Detection belongs in `tools/pr_body_check.py`,
which is new check work and so held by the generator pause.

**Decision needed.** Which remedy, once the wrapping path is known: a
merge-path instruction (`docs/maintainer.md` for the owner's client, or the
arming call for a session's), detection in `tools/pr_body_check.py`, or
accepting the wrap as the plain-text form of the record. The measurement comes
first, and a session can take it: the issue timeline API's
`auto_merge_enabled` events split the merges by path, and `5ec938fe` and
`f22d5dd0` are two known unwrapped bodies to start from.

**Recommendation:** fix it at the source. If one path wraps and another does
not, send merges through the one that does not, with a line in
`docs/maintainer.md` if the wrapping path is the owner's client, or in the
arming step if it is a session's. Build no detector: a record that is right
when it is written needs no check afterwards. Accept the wrap only if every
path turns out to wrap, and then say so in `tools/pr_body_check.py`'s module
docstring, which today calls the squash body "the permanent commit message a
reader of `main` meets".

**Under `PL-979D`'s answer, 2026-09-25 - a recommendation until the owner
records the form there.** `PL-979D`'s answer (project owner, 2026-09-25,
ratified) makes a copy recorded in the tree before the merge the permanent
record, and its second design round recommends `docs/pr-bodies/<N>.md`,
written by the session while the pull request is open and held by the pull
request's own required check. Under that, the squash body on `main` is a
derived copy, and its wrap is the plain-text form of a copy rather than damage
to the record. So this item's three remedies resolve to the third, taken for a
reason the brief did not have: no detector, no merge-path instruction, and no
measurement of which path wraps, since the remedy no longer turns on it. The
wrap was re-measured for that round at 166 of 248 tabled bodies on
`origin/main`, and stands as the case for a backfill of the store, which
`PL-979D` keeps as a separate decision. What remains of this item's "Done when"
is the decision recorded where `tools/pr_body_check.py` describes the record,
which the `PL-979D` build rewrites. Recommendation: close this item with that
build, citing `PL-979D`, and start no work of its own.

**Done when.** The wrapping path is named in this brief with the evidence that
names it, and either merges through that path stop wrapping or the decision to
accept the wrap is recorded where `tools/pr_body_check.py` describes the
record.

**Generator check.** An instance of `PL-WFFX`'s fact ("The squash commit's
subject and body as the merge sends them, not as the pull request shows
them"), filed after that head closed on 2026-09-22. `PL-Y1W0`, filed
2026-09-23, was the first post-close item, and its brief says a second would
reopen `PL-WFFX`'s `spent` verdict. Its `--compare` collapses whitespace, so it
could not see this one. This item is the second post-close instance, and
`PL-PNJF` is the third. Three post-close instances count as a generator whose
fix did not hold. `PL-WFFX` is closed and outside this triage batch, so the
record is reported to the triage coordinator, not written here. `PL-HMZZ`
("Which pull request carried an item's work") is a different fact.
