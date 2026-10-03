---
id: PL-F66M
title: items_dir and notes_dir are never normalized at config load, so items_dir = "./docs/items" reads the store while the hand-built prefixes that test git's paths against it - claims' in-flight read among them - match none
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_config.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
payoff: a store path written with a leading ./ in docket.toml cannot blind the in-flight guard while every other command keeps working
verify: grep -q 'def test_a_dotted_store_path_loads_normalized' subprojects/docket/tests/test_config.py
---

**Problem.** `config.load` keeps `items_dir` and `notes_dir` as written, and the code reads them two ways. The store itself is read through `pathlib` (`cli.py`, `root / config.items_dir`), which collapses a leading `./`. Twelve reads build a git-path prefix by hand instead, in three spellings - `.strip("/") + "/"` in ten (`arming.py` two, `claims.py` three counting `notes_dir`, `vcs.py` five), `.rstrip("/")` in `vcs.lost` and `.strip().strip("/")` in `checks._declared_item_file` - and none removes `./`. Measured 2026-10-03: `Path("/repo") / "./docs/items"` is `/repo/docs/items`, while `"docs/items/PL-X.md".startswith("./docs/items/")` is false. So with `items_dir = "./docs/items"` the store reads correctly while at least five reads that test git's paths with `startswith` match none: `claims._touched` (the in-flight read `flight` and `claim` stand on) sees no item file on any branch, `arming.arms_on_green` reads every item edit as outside the queue, `claims`' release-notes read sees no cut, `vcs.lost` declines, and `checks._declared_item_file` stops checking declared item files. The other sites were not each traced; `vcs`'s `ls-tree` read hands the prefix to git, which resolves `./` itself. `docket.model.is_under` would not help: it strips slashes and whitespace, not `./`.

**Why it matters.** Nothing in this repository writes the dotted form (`docket.toml` has `items_dir = "docs/items"`), so this is latent. It is the silent kind, though: an ordinary way to write a relative path in a settings file would leave every command working on the store while the in-flight guard stops seeing claims, which is the state answer that duplicates work.

**Recommendation:** normalize both once in `config.load` - `PurePosixPath(value).as_posix()` collapses `./` and doubled slashes, then strip `/` - and refuse an absolute path or one holding `..`, the way a malformed config already fails to load rather than being ignored. Every site then reads one spelling; whether the containment tests among them also move to `is_under` is a second, smaller question.

**Done when.** `./docs/items` and `docs/items/` load as `docs/items`, `/docs/items` and a path holding `..` fail to load, for `notes_dir` as for `items_dir`, and a test pins each.

**Found by** `PL-PFD9`'s search for missed path-containment sites (2026-10-03), which read these twelve and left them as a different fact - where the store lives - from `is_under`'s, then found this on the project owner's request to reconsider that call.

**Generator check.** An instance of `PL-NGBM`'s fact, filed after that head
closed on 2026-09-23: where the item store sits, as the path prefix git prints
for it, built by hand at twelve sites in three spellings. The first post-close
instance of NGBM; `PL-74T0` notes it beside its cluster 1.
