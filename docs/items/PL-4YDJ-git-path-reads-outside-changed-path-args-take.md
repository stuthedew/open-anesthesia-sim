---
id: PL-4YDJ
title: Git path reads outside changed_path_args take git's C-quoted spelling of an unusual path for the path: about 15 --name-only, ls-tree and diff reads across vcs.py, claims.py, verify.py, pr_title_check.py and doc_check.py ask for no -z, the fact PL-JTCQ, PL-MR8Z and PL-PXT7 each misread at their own readers
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
milestone: v0.5.29
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/verify.py, tools/generator_check.py, tools/pr_title_check.py, subprojects/docket/tests, tests/unit/test_pr_title_check.py, tests/unit/test_branch_id_check.py, tests/unit/test_pr_record_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
closed: 2026-10-18
pr: 1577
payoff: Every git read of a path in docket and the tools gets the file's real name even where git would quote it, and a new read that forgets -z fails a test, so this fact stops yielding a member one reader at a time
verify: grep -q 'def test_an_item_file_git_would_quote_is_read_by_its_path' subprojects/docket/tests/test_vcs.py && grep -q 'def test_every_path_listing_read_in_docket_asks_for_z' subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_closed_item_whose_path_git_would_quote_is_read' tests/unit/test_pr_title_check.py
root-cause-of: PL-JTCQ, PL-MR8Z, PL-PXT7
generator: spent - every member was found by a sweep or a review and none in use, and no tracked path is one git quotes, so ordinary work cannot meet one
misread: How git spells a path in its output, and when it quotes one
---

**Problem.** Git path reads outside changed_path_args take git's C-quoted spelling of an unusual path for the path: about 15 --name-only, ls-tree and diff reads across vcs.py, claims.py, verify.py, pr_title_check.py and doc_check.py ask for no -z, the fact PL-JTCQ, PL-MR8Z and PL-PXT7 each misread at their own readers

**Filed 2026-10-12 at the triage pass, as the head `PL-JTCQ`'s brief asked
for.** Unless told otherwise git prints a path holding a byte above 0x7f, a
tab, a double quote or a backslash in double quotes with C-style escapes
(git-config's `core.quotePath`); `-z` prints every path as it is. Three items
misread that one fact at different readers: `PL-PXT7` (`contrast_check`'s file
listing, done 2026-10-12), `PL-MR8Z` (verify's quoted diff header, ready) and
`PL-JTCQ` (`_commits_by_landing`, `_baseline`, `_deleted_paths`). No head's
`misread:` states it: `PL-PVW2`'s is which spelling of a repeated predicate is
the answer, and `PL-4W2L`'s, where `PL-MR8Z` is attributed, is whether a diff
weakens its tests. `git grep` for `--name-only` and `ls-tree` lines without
`-z` under `subprojects/docket/src`, `tools` and `.claude/hooks` gave 52 lines
on 2026-10-12, a count of lines rather than of reads, all latent since no
tracked path is one git quotes.

**Generator.** `spent`: every member was found by a sweep or a review, none in
use, and no tracked path is one git quotes, so ordinary work cannot meet one.
Recorded for the audit; the members are worked at their own bands.

**Recounted and reproduced 2026-10-17, at triage.** Fields checked: the front
matter carries `root-cause-of`, `generator: spent - ...` and `misread:` as
fields, and the members' statuses agree with the paragraph above - `PL-PXT7`
done 2026-10-12, `PL-MR8Z` ready, `PL-JTCQ` ready. The 52 is a count of lines,
docstrings included; an AST walk of every call whose own argv holds
`--name-only`, `--name-status`, `--numstat` or `ls-tree` with no `-z`, outside
`vcs.changed_path_args` (which adds it), finds **16 reads** under
`subprojects/docket/src`, `tools` and `.claude/hooks`, plus `verify`'s two
plain `diff`/`show` reads of a unified diff, which are `PL-MR8Z`'s. Of the 16,
three are `PL-JTCQ`'s (`vcs._commits_by_landing`, `doc_check._deleted_paths`,
`doc_check._baseline`) and two only test the listing for emptiness, where the
spelling cannot matter (`verify._added_record`, `doc_check._changed_json_keys`).
That leaves **11 that read the spelling and no member names**: in `vcs`,
`_item_paths_on`, `_notes_on`, `cut_window`, `notes_added`, `filed_with_work`,
`_item_blobs` and `churn`; `claiming._first_add`; `verify._store_at`;
`generator_check.creation_parents`; and `pr_title_check.closed_items_at`. The
title's file list has drifted since filing: `claims.py` no longer holds one (its
read now builds through `changed_path_args`), and `claiming.py` and
`generator_check.py` do. The scan was a throwaway `ast` walk, not kept; the
`Done when` test below is its standing form.

Reproduced on a scratch repository committing `docs/items/PL-BCDF-café.md` and
`docs/items/PL-GHJK-plain.md`: `vcs._item_paths_on("HEAD", "docs/items", ...)`
returned `{'PL-BCDF': '"docs/items/PL-BCDF-caf\\303\\251.md"', 'PL-GHJK':
'docs/items/PL-GHJK-plain.md'}` - the id found, mapped to git's quoted
spelling, quotes included, which names no file - so the reader that answers
"which file holds this item on the base" hands back a path nothing can open.

`spent` still holds on this tree: 0 of 2,965 tracked paths is one git would
quote (`git ls-files -z`, any byte above 0x7f, a tab, a newline, `"` or `\`),
and `store.slugify` folds every title to ASCII before it names an item file, so
the store never writes one. **Near neighbour:** `PL-86H3` (ready, `one-answer`)
folds several of the 11 - the item files at a ref in `pr_title_check`, `verify`
and three in `vcs`, and `generator_check`'s added-item read - into one `vcs`
reader; where it lands first, the reader it leaves is the one to give `-z`.

**Why it matters.** Each of the 11 answers a session with a path git invented
rather than the one in the tree, and does so silently: the id is found, so
nothing looks wrong, and the `show` that follows or the comparison against a
real path fails or matches nothing. Every member so far was found one reader at
a time, by a sweep or a review; with the readers left as they are, the next one
is a member waiting to be filed, and nothing stops a new read being written the
same way.

**Done when.** The 11 reads above ask for `-z` - built through
`vcs.changed_path_args` where it is a change listing, and otherwise with `-z`
read through `vcs.listed_paths` - and the test fakes that assert no `-z` on a
listing are moved with them. `subprojects/docket/tests/test_vcs.py` gains
`test_an_item_file_git_would_quote_is_read_by_its_path`, the reproduction above
against a real scratch repository, and
`test_every_path_listing_read_in_docket_asks_for_z`, which walks docket's
modules and fails on a `--name-only`, `--name-status`, `--numstat` or `ls-tree`
argv without `-z` outside `changed_path_args`; and
`tests/unit/test_pr_title_check.py` gains
`test_a_closed_item_whose_path_git_would_quote_is_read`. The members' own sites
stay theirs, so this lands before or beside `PL-JTCQ` and `PL-MR8Z` without
redoing them.

**Started 2026-10-18; re-sized `L` to `M` and one assertion declared falsified.**
The start mode refuses an `L` item straight from the queue until it is
scoped. This one already is: the `Done when` names each read and each test,
and PL-86H3 has since folded five of the 11 reads into `vcs._item_blobs` and
`vcs.item_additions`, so the work is seven reads, two parsers and the tests,
an `M`. `falsifies:` names the one assertion the fix makes untrue:
`test_the_base_is_read_from_the_ref_rather_than_the_working_tree` pins the
notes listing's argv without `-z`, which is the read this item changes. It is
declared here, on the default branch, because `verify` honours only the base's
copy, and the work lands in a pull request after this one.

**Closed 2026-10-18.** Every path listing in docket and `tools/` now asks git
for `-z`, through `vcs.changed_path_args` or with `-z` in its own argv, and is
parsed by `vcs.listed_paths` or `vcs.logged_fields`. A patch's header path,
which `-z` leaves quoted, is read through `vcs.unquoted_path` (`PL-MR8Z`).
`test_every_path_listing_read_in_docket_asks_for_z` walks docket's modules and
`tools/*.py` and fails on a listing argv without `-z`, so the next reader of
this fact fails a test where it is written instead of waiting for a sweep.

**Generator check.** This item is the head for the fact, how git spells a path
in its output and when it quotes one. Read on 2026-10-17 against every head's
`misread:`: `PL-4YVK` (where a line ends in git output) and `PL-NGBM` (the path
prefix git prints for the store) are neighbouring facts rather than this one,
and no closed head states it, so it is neither an instance nor a re-entry;
`spent` holds, for the reason above.
