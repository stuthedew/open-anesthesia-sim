---
id: PL-2M5T
title: Release notes are generated before bin/docket record runs, so every item whose pr was written by the cut's own commit appears in its own release notes with no pull request link - eight of v0.4.22's fifteen
priority: P2
effort: M
status: ready
classes: defect
feature: commit-provenance
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/cli.py, tests/unit
added: 2026-09-14
verify: python3 -c "import pathlib,re; t=pathlib.Path('docs/releases/v0.4.22.md').read_text(); b=[l for l in t.splitlines() if l.startswith('- ')]; raise SystemExit(1 if [l for l in b if not re.search(r'#[0-9]+', l)] else 0)"
---


**Problem.** Release notes are generated before bin/docket record runs, so every item whose pr was written by the cut's own commit appears in its own release notes with no pull request link - eight of v0.4.22's fifteen

**Measured 2026-09-14.** `docs/releases/v0.4.22.md` carries 15 item bullets and
**9 of them name no pull request at all**. The brief above says eight; nine is
what the file holds today, and the difference does not change the finding.

**Why it matters.** The notes are the permanent record of what a release
contained, and the pull request is where the reasoning behind each item lives -
the review, the discussion, the diff as it was actually read. `bin/docket
record` exists precisely because that number cannot be known before the merge,
and it backfills onto the item; but the notes are written from the item's `pr`
field at cut time, which is *before* the backfill for anything closed in the
cut's own commit. So the items most recently finished - the ones a reader is
most likely to be looking up - are systematically the ones with no route back to
their reasoning, and the gap is permanent because nothing rewrites a cut
release's notes.

**`PL-66X4` is this same finding stated as a mechanism** and is dropped in its
favour; the two differ only in whether they name the count or the cause.

**Done when.** A cut release's notes name a pull request for every item that has
one, including items whose `pr` is written by the cut's own commit - either by
recording before the notes are generated, or by the notes resolving the number
the way `bin/docket record` does rather than reading a field that is not yet
written. `docs/releases/v0.4.22.md` is repaired as part of it, or the item
records why a shipped release's notes are left as they stand.
