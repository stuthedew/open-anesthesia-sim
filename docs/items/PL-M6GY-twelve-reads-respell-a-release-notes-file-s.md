---
id: PL-M6GY
title: Twelve reads respell a release notes file's name, version or bullets instead of docket.release's notes_name, VERSION_RE, SEMVER_RE, version_key and NOTES_BULLET_RE, and vcs's cut window takes the version by string order, so v0.5.9 outranks v0.5.10 and an added docs/releases/README.md reads as a version
status: untriaged
feature: read-facts-through-docket
touches: tools/doc_check.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/vcs.py
added: 2026-10-01
---

**Problem.** Twelve reads respell a release notes file's name, version or bullets instead of docket.release's notes_name, VERSION_RE, SEMVER_RE, version_key and NOTES_BULLET_RE, and vcs's cut window takes the version by string order, so v0.5.9 outranks v0.5.10 and an added docs/releases/README.md reads as a version

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/doc_check.py:3499` builds `v{version}.md` (`release.notes_name`), `:3566` is its own `VERSION_RE`, `:585` its own `SEMVER_RE` and `:3297` its own `version_key`; `subprojects/docket/src/docket/cli.py:5057` repeats release's notes scan; `subprojects/docket/src/docket/claims.py:1517` builds the notes path; `subprojects/docket/src/docket/roadmap.py:1006` is `version_key` again; `subprojects/docket/src/docket/release.py:284` and `:598` write the notes scan twice, and `:263` (`NOTES_ENTRY_RE`) and `:571` (`NOTES_BULLET_RE`) one bullet grammar twice; all agree. `subprojects/docket/src/docket/vcs.py:3499` takes the newest version a branch adds as `sorted(paths)[-1]` over strings, so `0.5.9` outranks `0.5.10` and an added `docs/releases/README.md` becomes the version `README`; `:3602` takes any added leaf as a version, `README.md` included; `:3611` builds the notes path by hand.
