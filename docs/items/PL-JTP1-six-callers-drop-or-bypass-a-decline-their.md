---
id: PL-JTP1
title: Six callers drop or bypass a decline their shared reader names, so a reader should return its declines in a type the strict mypy run makes every caller handle
priority: P3
effort: M
status: done
classes: refactor
feature: reader-checks
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/frontmatter.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/cli.py, tools/dead_ends.py, tools/doc_check.py, tools/item_reads.py, tools/pr_body_check.py, subprojects/docket/tests, tests/unit/test_doc_check.py, docs/items/PL-K23D-bin-docket-record-merge-leaves-a-notes-bullet.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-17
pr: 1475
payoff: A caller that drops a shared reader's declines fails mypy at the pull request that writes it, instead of answering from a partial reading until a sweep files it
verify: ! grep -qF 'unread: list[UnreadEntry] | None = None' subprojects/docket/src/docket/roadmap.py && ! grep -qF 'document_entry_lines(lines, [])' subprojects/docket/src/docket/release.py
---

**Problem.** Six of link 23's members read their format through a shared
reader and then lose the decline it names: `PL-L4X3`, `PL-4DM0`, `PL-63Y5` and
`PL-DQ9C` drop it, and `PL-J8ML` and `PL-7CQ5` fall back to a line at a time
without saying so. A decline a caller can ignore is a check repeated at each
way in, which `.claude/rules/expert-review.md` § "Domains to review against,
and the design principles they carry" refuses under "Parse, don't validate".
If each shared reader returned its declines in its result type, the strict
`mypy` run that already covers docket, `tools` and `.claude/hooks` would make
every caller handle one.

**Found 2026-10-10** by the parsing review in `PL-R417`'s closing sweep thread
(link 23). The owner chose to have `PL-R417`'s last batch add the review's two
differential tests in CI, and this follow-up to be filed as an ordinary item.

**Reproduced 2026-10-11** on main at `16a20a4f`:
`docket.roadmap.document_entry_lines` takes its declines through an optional
out-parameter, `unread: list[UnreadEntry] | None = None`, so a caller that
omits it or passes `[]` type-checks under the strict `mypy` run.
`tools/dead_ends.py`'s `entries` passes `[]` through `_bullets` (`PL-DQ9C`),
and `docket.release.notes_ids` passes `[]` as well, there on purpose: its
docstring says a declined bullet still claims the id leading it. So the type
the work introduces needs an explicit way to set a decline aside, which that
caller is the case for.

**Why it matters.** Each of the six is a reader answering from a partial
reading without saying so, which the apparatus floor refuses, and each was
found by a sweep rather than by a tool. A result type carrying the declines
turns the next such caller into a type error at the pull request that writes
it, rather than an item a later sweep files.

**Generator check.** Not a member of `PL-R417`: a guard that would make its
members fail loudly, not a reader that misreads where a statement ends.

**Done when.** Each shared reader that declines a statement returns the
decline in a type its callers must unpack, and none of the six callers can
drop one without a type error.

**Re-scoped 2026-10-17, at the build** (the session's call, one item's
disposition). Done for the readers the handoff below names, and
`release.unreferenced_by_version` beside them: each returns its declines
beside its result. Two shapes it did not name go to `PL-GC59`: a decline
carried as a field of a record (`PL-L4X3`'s `Scope` and `Wave.unread`,
`PL-7CQ5`'s `shell.Reading.refusal`), and `tools/doc_check.py`'s workflow
readers, which take a list a caller can pass empty. No type makes a caller
handle a decline outright: `result[0]` skips one as quietly as a field read.
What the pair removes is the two ways a caller dropped one by writing nothing,
an out-parameter left out or passed empty and a fallback taken silently.

**Handoff 2026-10-17, for the thread that takes it up.** Claimed on
`claude/workflow-group-ten-nraxmr`, in draft `#1475` beside `PL-NWZM`,
`PL-PBNK`, `PL-W9VC` and `PL-Q8LJ`, which it closes; nothing of this item is
built. The thread stopped for length, not for the work. What it read, on the
branch once `origin/main` at `e0541fba` came in:

- **The six members are closed** (`#1431` to `#1472`), each caller fixed where
  it stood, so what is left is the type change alone. `tools/dead_ends.py`'s
  `_bullets` now passes a list and carries each declined line out with its
  bullet, so the `[]` the reproduction names there is gone; the one in
  `docket.release.notes_ids` stands, there on purpose.
- **The readers.** `docket.roadmap`'s `list_entry_lines(lines, start,
  unread=None)` and `document_entry_lines(lines, unread=None)` share
  `_entries`, which raises the `UnreadEntry` where no list was passed and
  appends it where one was; `docket.release.notes_bullets(text, unread)` reads
  through the second. `docket.frontmatter.statements` reads a line at a time
  where `key_statements` raises `Unread` (`PL-J8ML`), and
  `docket.model.parse_front_matter` leaves block lists, block scalars and
  unread lines to `block_list_keys`, `block_scalar_keys` and
  `unread_front_matter_lines` beside it. Which readers in `vcs`, `verify` and
  `instructions`, which the touches name, decline at all was not read.
- **The callers.** Of the walker: `roadmap`'s `_gate_entries` and
  `_scope_entries` pass their list on, `release.notes_ids` passes `[]`,
  `release.notes_bullets` and `tools/dead_ends.py`'s `_bullets` pass their
  own, and `tools/doc_check.py`'s `_list_members` passes none and turns the
  raise into `UnreadStatement`. Of `notes_bullets`: `release.unreferenced`
  passes `[]` where its own caller passed nothing, `release.restate_references`
  passes `[]`, and `tools/doc_check.py`'s `_pull_requests_named` passes its
  own. `parse_front_matter(` stands 16 times in the source, tools and hooks
  and 6 times in the tests.
- **The route it planned.** A reader that declines returns its result and its
  declines together, so a caller that drops them fails the strict `mypy` run,
  and a caller that sets them aside on purpose, as `notes_ids` does, unpacks
  them into a name that says so beside a comment saying why. Removing the
  `None` defaults alone is cheaper and leaves `[]` legal, which is the case
  the verify names.
- **What the branch changed under it.** `PL-W9VC` added
  `docket.frontmatter.comments` and `block_content` and a private `_Passed`
  record threaded through `frontmatter`'s walk, and moved `BLOCK_SCALAR_RE`
  from `docket.model` into `docket.frontmatter`.
- **The trap.** `bin/docket verify --self` refuses an existing test assertion
  changed in place unless the base names it in `falsifies:`, so keep each old
  asserted text where the new shape allows.

**Built 2026-10-17**, on `#1475`'s branch.

- **The readers.** `roadmap.list_entry_lines` and `document_entry_lines`
  return `(spans, declines)`, and `_gate_entries` and `_scope_entries` pass
  theirs on the same way; `release.notes_bullets` returns `(bullets,
  declines)`; `frontmatter.statements` returns its spans and the `Unread` that
  sent it a line at a time, or `None`; `model.parse_front_matter` returns
  `(fields, body, FrontMatterDeclines)`, the block lists, block scalars and
  unread lines its fold reads no value from, false where there are none.
  `release.unreferenced` reads one file and raises a decline, and
  `unreferenced_by_version` returns `(found, declines)`, where both took an
  optional list.
- **Callers that handle them.** `parse_item` reads its three decline fields
  from the record; `vcs._standing` answers `ahead` from it, which retires
  `_declines_a_line`, and `verify._declines` reads the same predicate;
  `verify.read_commission` returns a commission it could not read, and
  `front_matter_check` refuses, where a copy declines, since a block emptied on
  both sides compared as no change; `doc_check._list_members` and
  `_pull_requests_named` raise or return theirs.
- **Callers that set them aside**, each into `_declined` beside a comment
  saying why: `release.notes_ids` (a declined bullet's span still holds the id
  leading it), `release.restate_references` (dropped, not settled: `PL-K23D`
  is open to carry it to `record --merge`'s report), `doc_check._statements`
  (`rules_paths_check` refuses a rule's unsplittable front matter and `docket
  check` declines an instruction file's by name), and `parse_front_matter`'s
  readers of one field on one copy: `verify._captured` and the record
  exemption, `claims._fields_at`, `claiming`'s HEAD status, `item_reads`,
  which reads the body alone, and `pr_body_check.parse_record`. For the copies
  on a ref or HEAD the set-aside rests on `docket check` refusing all three
  forms on the branch that writes one, so a `status:` written as a block
  scalar, the one decline that would move a claim, is a branch CI refuses;
  a decline channel through the claims record was weighed and not built.
- **Indexing** - `parse_front_matter(text)[0]` in `vcs`, `claiming` and
  `model.with_front_matter_field` - reads one known scalar field and compiles
  unchanged.
