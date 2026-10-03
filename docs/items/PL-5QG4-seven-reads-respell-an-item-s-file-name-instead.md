---
id: PL-5QG4
title: Seven reads respell an item's file name instead of vcs.ITEM_FILE_RE - generator_check three times, item_reads, dead_ends, doc_check's brief lookup and claiming's pathspec - and six of them answer differently from it on a file name with no slug
priority: P3
effort: M
status: done
classes: defect
feature: read-facts-through-docket
touches: tools/generator_check.py, tools/item_reads.py, tools/dead_ends.py, tools/doc_check.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/store.py, tests/unit/test_generator_check.py, tests/unit/test_item_read_log.py, tests/unit/test_dead_ends.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-03
pr: 1282
payoff: every reader agrees on which files in docs/items are items, so a slug-less file is an item everywhere or nowhere
verify: ! grep -qF 'parts = path.name.split("-")' tools/item_reads.py && ! grep -qF 'parts = path.name.split("-")' tools/dead_ends.py
---

**Problem.** Seven reads respell an item's file name instead of vcs.ITEM_FILE_RE - generator_check three times, item_reads, dead_ends, doc_check's brief lookup and claiming's pathspec - and six of them answer differently from it on a file name with no slug

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/generator_check.py:250`, `:270` and `:294`; `tools/item_reads.py:62`; `tools/dead_ends.py:155`; `tools/doc_check.py:4150`; `subprojects/docket/src/docket/claiming.py:728`, which agrees. The other six take a slug-less `PL-K7QX.md` as an item, which `vcs.ITEM_FILE_RE` does not, while the store's `ITEM_GLOB` reads every `*.md`; which of the three is the grammar is part of the fix.

**Why it matters.** Each site answers from its own spelling of a fact docket exports, so the next change to that fact reaches the export and not the copy, and the two then answer differently with nothing to say so - the mechanism `PL-KGYT` closed as spent.

**Done when.** Each site under **Sites** reads the export instead of its own spelling, and where a site answered differently from the export, a test pins that input.

**Generator check.** A member of `PL-KGYT` (done 2026-10-01), filed by that head's closing sweep and named in its `root-cause-of:`; its fix, the write-time rule in `.claude/rules/apparatus-standard.md` (`PL-HC8P`), covers new readers and these predate it, so this is neither a post-close instance nor a new generator.

**Decision, 2026-10-03: which of the three is the grammar.** `vcs.ITEM_FILE_RE` - the id, then a hyphen - is the one grammar for whose file a name is, and `store.filename_for` is what writes it. `store.ITEM_GLOB` is not a second one: it says which files the store reads, since the store takes an item's id from the front matter and reads every markdown file so that `docket check` sees each, and a comment beside it now says so. The six sites' acceptance of a slug-less name was a third spelling, and is gone. A hard `docket check` error for a name that does not open with its own id was considered and not taken: 0 of the 1,945 paths ever added under `docs/items` on `main` were named any other way, it would have refused the `item-N.md` stores docket's own CLI tests build (140 uses of one helper in `subprojects/docket/tests/test_cli.py`), and `checks._check_filenames` already names such a file in its drifted-slug advisory and gives the rename.

**Done, 2026-10-03.** All seven sites read `vcs.ITEM_FILE_RE`: `tools/generator_check.py:215` (a new `item_files`, which `citations` and `clusters` both list through) and `:265` (`creation_parents`), `tools/item_reads.py:72`, `tools/dead_ends.py:161`, `tools/doc_check.py:4138` (one listing indexed by id, in place of two globs per cited id), and `subprojects/docket/src/docket/claiming.py:744`, where `_first_add` now lists the adds under the store and keeps the ones the grammar reads as the key, in place of a pathspec spelling it. An `ast` walk of every non-docstring string literal under `tools/`, `subprojects/docket/src/`, `.claude/hooks/`, `.github/` and `bin/` found no eighth reader: the other `*.md` globs read `docs/pr-bodies`, `.claude/rules`, release notes and the docs walk, `cli.py`'s `ID-*.md` is a `git add` line printed for a person, and `tools/pr_title_check.py` already reads both exports. One test per site that answered differently pins the slug-less input, and each fails on the old code: `test_a_file_whose_name_carries_no_slug_is_no_item_here_either` (all three `generator_check` reads), `test_the_summariser_tells_an_item_s_file_by_docket_s_grammar`, `test_an_item_s_id_is_read_off_its_file_name_by_docket_s_grammar` and `test_a_marked_citation_resolves_to_a_brief_only_by_docket_s_name_grammar`. Measured against the readers they replaced on this tree, every answer is unchanged: `generator_check`'s 48-line report, `item_reads`' 1,922 items and 1,632 closed, `dead_ends`' 1,922 ids, `doc_check`'s quoted-source findings over 14 marked citations of 3 ids, and `creation_parents`' reading of each of the 1,945 paths ever added.
