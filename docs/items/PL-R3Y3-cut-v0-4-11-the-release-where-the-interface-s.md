---
id: PL-R3Y3
title: Cut v0.4.11 - the release where the interface's cost was measured rather than guessed
priority: P2
effort: S
status: done
classes: planning
feature: release-process
milestone: v0.4.12
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases/v0.4.11.md
added: 2026-09-08
closed: 2026-09-08
pr: 486
verify: python3 tools/doc_check.py check && grep -q 'Current baseline: v0.4.11' ROADMAP.md
---

**Problem.** Cut v0.4.11 - the release where the interface's cost was measured rather than guessed

**Cut on the project owner's instruction, 2026-09-08**, in answer to "Should we
cut version first?" — asked before approving the Qt spike, and the answer is
yes for a reason the spike supplies: a spike churns `app/`, and a release cut
after it would describe a half-migrated tree rather than the work that is
actually finished.

Twenty-one items since v0.4.10, completing the `delegation` feature. `0.4.11`
rather than a minor because no capability boundary is crossed: `core/` is
byte-identical to v0.4.10 and `data/` changes only in what two provenance
entries say about their own numbers.

Three sessions independently recommended `0.4.11` and the mechanical guess
agreed; two of those sessions had gone to `need_input` on the version name and
were archived by the time this one asked, so nothing was in flight against it.

`ROADMAP.md`'s version-table row, the current-baseline mark and the baseline
section were written by hand, which is the half `bin/docket release` stops
before and says so.
