---
id: PL-JLYG
title: check_tag_span_covers_its_notes exempts the newest tag's span, not the newest cut's, so a release branch is never told the previous notes owe a tag-span pointer and main turns red only after the owner pushes the new tag
status: untriaged
feature: release-process
touches: tools/doc_check.py, tests/unit/test_doc_check.py, .claude/skills/docket/modes/release.md
added: 2026-09-23
---

**Problem.** check_tag_span_covers_its_notes exempts the newest tag's span, not the newest cut's, so a release branch is never told the previous notes owe a tag-span pointer and main turns red only after the owner pushes the new tag

**Where.** `tools/doc_check.py`: `_tag_spans` sets `newest` to the newest
release *tag* reachable from `HEAD`, and `check_tag_span_covers_its_notes`
skips every closure whose span is `spans.newest`. Its own docstring says the
exemption lasts until "the next cut onward, when the release that describes the
work exists and can be named". The code lifts it at the next *tag*, not the
next cut.

**Observed 2026-09-23, cutting v0.5.6 (`PL-38HD`).** v0.5.5's span held `#920`
(`PL-0HPV`) and `#921` (`PL-WFFX`), neither named in `docs/releases/v0.5.5.md`.
With no v0.5.6 tag, v0.5.5 is `spans.newest` and the check skips its span by
construction. With a local `v0.5.6` tag placed on the cut commit and deleted
afterwards, the same tree failed, asking for exactly the two pointer lines. The
pointer was written in `#931` only because the v0.5.5 baseline's prose promised
it and § "Tags" was read. Nothing in `bin/docket release`'s "owed by hand"
list, and nothing in `.claude/skills/docket/modes/release.md`, names it.

**Why it matters.** The cut is the one moment the previous notes can be edited
alongside the release that describes their stragglers, and the check is silent
then. It fires once the project owner pushes the new tag. From then on it fails
`make check` on `main` and on every branch that fetches the tag, for sessions
that did not cut the release, until one of them writes the pointer. `PL-KFWL`
has the same effect (a tag push turning `doc_check` red on `main` for every
session) through a different mechanism. `docket new` matched this filing to it
by title as a recurrence; that match was removed, because the cause differs.

**Direction, for triage.** This is a defect in what exists, since the docstring
states the intended timing, so the generator pause does not apply. One option:
judge the newest tag's span as soon as a notes file exists for a newer version,
and name that version as "described in". The exemption then covers only a span
whose describing release has no notes yet. The alternative is having
`bin/docket release` list the pointer among what it says is owed by hand. That
tells a session instead of checking it, so it is the weaker route.

**Done when.** On a checkout whose newest tag is vN and which holds the notes
file for vN+1, a `done` closure inside vN's span that vN's notes do not name
fails `tools/doc_check.py` before the vN+1 tag exists. A test in
`tests/unit/test_doc_check.py` drives that case.
