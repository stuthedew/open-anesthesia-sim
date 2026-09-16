---
id: PL-SYG4
title: The digest's RESERVED verdict suppresses the release offer entirely rather than naming the next free patch number, so on the v0.4.x track with v0.5.0 reserved a session never offers a cut the plan actually wants
priority: P3
effort: M
status: needs-decision
classes: defect
feature: release-process
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
added: 2026-09-15
---

**Problem.** The digest's RESERVED verdict suppresses the release offer entirely rather than naming the next free patch number, so on the v0.4.x track with v0.5.0 reserved a session never offers a cut the plan actually wants

`render.py:1466` returns "No release to offer" whenever `release_offer` comes
back `RESERVED`, and hands the reader to the beat instead. That is right when
the reserved number is the one a bump would legitimately arrive at. It is wrong
here, because `docket.toml` sets `version_policy = "manual"` and this project
runs a **patch track** - the `v0.4.x` row - alongside a reserved milestone
number. The mechanical guess collides with `v0.5.0` on every cut the track
makes, so the digest suppresses the offer on a fact the manual policy already
says is not an answer: `bin/docket release --dry-run` prints the same guess and
calls it "for reference only".

**Measured, twice.** `PL-G7RD` (2026-09-14) cut `v0.4.25` from ten finished
items and its brief records the same cause in the same words - "the digest
withholds the offer only because the *mechanical* bump is `0.5.0` and that
number is reserved". On 2026-09-15 the digest reported 25 releasable items
under the identical line, and the question reached a session only because the
project owner asked it directly. Both cuts the track has wanted were initiated
by a human noticing, which is the condition the offer exists to remove.

**What it should say instead is the open question, not obviously the fix.** The
next free patch number is computable (`0.4.26` today, the port's section moving
as its own risk paragraph provides for), but naming it turns a rename of a
scoped section into a side effect of a digest line, and `PL-188T` already
records that the release guard does not reserve the port's number. So the
candidate answers are at least: name the free number as an offer, name it as an
advisory that says what it would displace, or keep the refusal and say that a
patch-track cut is available by naming a version - which is the one thing the
current sentence does not say.

**Update 2026-09-16 (`PL-VFD8` and `PL-188T`, closed together).** The guard
now answers from every version the roadmap names ahead of the current one, so
`v0.4.26` - the port's own number - is reserved alongside `v0.5.0`. That leaves
this item untouched and slightly sharper: the mechanical bump now collides with
a reserved number on every patch the `v0.4.x` track cuts, and there are two
numbers ahead of it to collide with rather than one. The third paragraph's
remark that `PL-188T` records the guard not reserving the port's number is
spent; the sentence around it, that naming the free number turns a rename of a
scoped section into a side effect of a digest line, still stands.

**Related but distinct.** `PL-Z85N` is the cut path not objecting to a reserved
version (the opposite direction), `PL-VFD8` is the guard failing to see a
milestone with a row but no section (a false negative of the guard itself), and
`PL-1BS2` is the Releasable line during an interrupted cut. None of the three
is this: the verdict is correct and the sentence it produces is unhelpful.

**Why it matters.** The release offer exists so that a cut is raised by the
tooling rather than by the project owner noticing. On this track it has never
once done that. Both cuts the `v0.4.x` row has wanted were initiated by a
human: `v0.4.25` (`PL-G7RD`, 2026-09-14) and the 25-releasable-item question on
2026-09-15, which reached a session only because the owner asked it directly.
The digest was not silent on either day - it printed `No release to offer`,
which is a verdict rather than an absence, so a session reading it correctly
concludes there is nothing to raise and moves on.

That is `CLAUDE.md`'s first compounding-friction test read narrowly: the check
is not wrong, but the sentence it produces is, and it is wrong in the
direction that produces no signal at all. It also gets worse rather than
better with the tree: `PL-VFD8` and `PL-188T` made the guard reserve every
version the roadmap names ahead of the current one, so the mechanical bump now
collides with two reserved numbers rather than one, on every patch this track
would cut.

**Decision needed.** What the digest should print when the mechanical bump
lands on a reserved version *and a free patch number exists on the current
track*. Three answers, and they differ in what they commit the project to:

1. **Name the free number as an offer** - "0.4.26 is free; want me to cut it?".
   Strongest signal, and the one that would have caught both missed cuts. Its
   cost is that the port's own section is currently *named* `v0.4.26`, so an
   offer that takes the number turns renaming a scoped roadmap section into a
   side effect of a digest line.
2. **Name it as an advisory that says what it would displace** - "0.4.26 is the
   next free patch number, and the Qt port's section currently holds it". Same
   signal, no implicit claim on the number, one more sentence for every
   session to read.
3. **Keep the refusal and say the one true thing it omits** - that a
   patch-track cut is available by naming a version (`make release
   VERSION=0.4.26`), which is exactly what the current sentence does not say.
   Smallest change; leaves the session to work out which number is free.

**Recommendation: 2.** It removes the measured harm - a session reads that a
cut is available and which number it would take - without writing a claim on a
scoped section's name into a digest line, which is what makes 1 hard to undo.
3 is honest but leaves the session doing the arithmetic the tool already did,
and the arithmetic is the part the tool is better at. 2 costs one line, and
only on a track where a reserved number is in the way, so it is silent in the
ordinary case.

This is the project owner's call rather than a session's: it is a question
about what the release train should *do* on a patch track alongside a reserved
milestone, and option 1 changes what a roadmap section's heading means.

**Done when.** The digest, on a checkout where the mechanical bump is reserved
and a free patch number exists on the current track, prints the chosen wording
rather than a bare `No release to offer`; a test in
`subprojects/docket/tests/test_release.py` pins that wording against exactly
this arrangement (a `v0.4.x` row, a reserved `v0.4.26`, a reserved `v0.5.0`);
and the case where the reserved number genuinely *is* the one a bump should
arrive at still prints the refusal unchanged.
