---
id: PL-M6GY
title: Twelve reads respell a release notes file's name, version or bullets instead of docket.release's notes_name, VERSION_RE, SEMVER_RE, version_key and NOTES_BULLET_RE, and vcs's cut window takes the version by string order, so v0.5.9 outranks v0.5.10 and an added docs/releases/README.md reads as a version
priority: P2
effort: M
status: ready
classes: defect
feature: read-facts-through-docket
touches: tools/doc_check.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: the cut window takes v0.5.10 over v0.5.9 and ignores a README in docs/releases, because every reader names, versions and orders notes files through docket.release
verify: ! grep -qF 'sorted(paths)[-1]' subprojects/docket/src/docket/vcs.py && ! grep -qF 'version_tuple(version) or (0, 0, 0)' subprojects/docket/src/docket/roadmap.py && ! grep -qF 'version_tuple(version) or (0, 0, 0)' tools/doc_check.py
---

**Problem.** Twelve reads respell a release notes file's name, version or bullets instead of docket.release's notes_name, VERSION_RE, SEMVER_RE, version_key and NOTES_BULLET_RE, and vcs's cut window takes the version by string order, so v0.5.9 outranks v0.5.10 and an added docs/releases/README.md reads as a version

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/doc_check.py:3499` builds `v{version}.md` (`release.notes_name`), `:3566` is its own `VERSION_RE`, `:585` its own `SEMVER_RE` and `:3297` its own `version_key`; `subprojects/docket/src/docket/cli.py:5057` repeats release's notes scan; `subprojects/docket/src/docket/claims.py:1517` builds the notes path; `subprojects/docket/src/docket/roadmap.py:1006` is `version_key` again; `subprojects/docket/src/docket/release.py:284` and `:598` write the notes scan twice, and `:263` (`NOTES_ENTRY_RE`) and `:571` (`NOTES_BULLET_RE`) one bullet grammar twice; all agree. `subprojects/docket/src/docket/vcs.py:3499` takes the newest version a branch adds as `sorted(paths)[-1]` over strings, so `0.5.9` outranks `0.5.10` and an added `docs/releases/README.md` becomes the version `README`; `:3602` takes any added leaf as a version, `README.md` included; `:3611` builds the notes path by hand.

**Why it matters.** Each site answers from its own spelling of a fact docket exports, so the next change to that fact reaches the export and not the copy, and the two then answer differently with nothing to say so - the mechanism `PL-KGYT` closed as spent.

**Done when.** Each site under **Sites** reads the export instead of its own spelling, and where a site answered differently from the export, a test pins that input.

**Reproduced 2026-10-01.** `sorted(['0.5.9', '0.5.10'])[-1]` is `0.5.9`, and `vcs.py` still takes `sorted(paths)[-1]`.

**Generator check.** A member of `PL-KGYT` (done 2026-10-01), filed by that head's closing sweep and named in its `root-cause-of:`; its fix, the write-time rule in `.claude/rules/apparatus-standard.md` (`PL-HC8P`), covers new readers and these predate it, so this is neither a post-close instance nor a new generator.
