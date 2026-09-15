---
id: PL-SYG4
title: The digest's RESERVED verdict suppresses the release offer entirely rather than naming the next free patch number, so on the v0.4.x track with v0.5.0 reserved a session never offers a cut the plan actually wants
status: untriaged
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

**Related but distinct.** `PL-Z85N` is the cut path not objecting to a reserved
version (the opposite direction), `PL-VFD8` is the guard failing to see a
milestone with a row but no section (a false negative of the guard itself), and
`PL-1BS2` is the Releasable line during an interrupted cut. None of the three
is this: the verdict is correct and the sentence it produces is unhelpful.
