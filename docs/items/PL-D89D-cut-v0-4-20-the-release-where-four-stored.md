---
id: PL-D89D
title: "Cut v0.4.20: the release where four stored values' sources were read back against the publications"
priority: P2
effort: S
status: ready
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-13
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.20"' pyproject.toml && test -f docs/releases/v0.4.20.md
---

**Problem.** Cut v0.4.20: the release where four stored values' sources were
read back against the publications.

Five items have finished since v0.4.19 and none has shipped, so `bin/docket
next` and the session-start digest ask every session to offer a release before
taking new work. One of the five is `PL-6BP6`, v0.4.19's own cut item, which is
the open gate entry `PL-KRS6` (release counts the previous release's own cut
item as releasable work) demonstrating itself; the release's real content is the
other four.

**Why it matters.** The four are one piece of work rather than a miscellany, and
the release name should say so. `PL-4YY1` recorded provenance for the circuit
volume and the default fresh gas flow, which had none. `PL-0NQ1` found the
reference patient's cited sources disagreeing on vessel-rich perfusion.
`PL-ZP7Z` found the Workbook attributing the volatile partition coefficients to
Yasuda's *Anesthesiology* abstract and to Abbott package-insert data, which is
not what the agent files say. `PL-ZDWL` re-ran the published elimination
comparison at Yasuda's own measured alveolar ventilation, which the methods text
states and this project had not read out. In every one of the four the stored
number was checked against what the publication actually says, which is the
`docs/MODEL.md` source hierarchy being exercised rather than asserted.

Filed before the cut rather than after it, per `CLAUDE.md`'s rule that
repository work taking a commit of its own is filed first: every in-flight guard
this project has matches a `PL-` id, and a release cut has none until somebody
starts one. `PL-66FP` is what the unfiled version cost - two sessions cut v0.3.7
within the hour and the second was discarded at the merge. Checked before
starting: `bin/docket release --dry-run` reported no ref carrying a cut, `main`
holds no 0.4.20, v0.4.19 is tagged on the remote at `fdb13c9e`, and of the four
live sessions on the list none is cutting a release.

**Known and accepted at the cut.** Three sessions are working and may merge
during it, so work can land inside this tag's span and be absent from its notes.
That is the open entry `PL-028F` (work landing between a cut and its merge is
inside the tag's span but absent from the release notes), a known defect with no
fix yet rather than a reason to hold the release.

**Done when.** `pyproject.toml` is at 0.4.20, `docs/releases/v0.4.20.md` exists,
`ROADMAP.md` carries the version-table row, the moved `current baseline` mark
and the baseline section, and `make check` passes.
