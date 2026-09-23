---
id: PL-SYG4
title: The digest's RESERVED verdict suppresses the release offer entirely rather than naming the next free patch number, so on the v0.4.x track with v0.5.0 reserved a session never offers a cut the plan actually wants
priority: P3
effort: M
status: ready
classes: defect, infra
feature: release-roadmap-seam
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_release.py
added: 2026-09-15
verify: grep -q 'def test_the_reserved_refusal_names_the_way_out' subprojects/docket/tests/test_release.py && uv run pytest subprojects/docket/tests/test_release.py
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

**Update 2026-09-16 (`PL-VFD8` and `PL-188T`, closed together in `#606`).**
The guard now answers from every version the roadmap names ahead of the current
one, so `v0.4.26` - the port's own number - is reserved alongside `v0.5.0`, and
the mechanical bump collides with a reserved number on both of its branches:
`suggest_version`'s minor branch lands on `0.5.0` and its patch branch on
`0.4.26`. The third paragraph's remark that `PL-188T` records the guard not
reserving the port's number is spent.

**That update first read "this item is untouched and slightly sharper", which
was wrong, and correcting it is why this brief is longer than the finding.**
Sharper understates it in the one direction that matters. Before `#606` the
patch bump was *free*: the digest would have offered `0.4.26`, which is exactly
what `ROADMAP.md` says a patch cut on this track does. It says so three times -
the `v0.4.x` timeline row ("any patch cut before the exact step lands would take
it"), the port's own risk paragraph ("a patch cut before this lands takes this
section's number") and planned-milestone item 29 ("a patch cut before this work
lands takes it"), quoted rather than cited by line because two of the three have
moved since - and `PL-G7RD` executed it on 2026-09-14 with the owner's
approval, renumbering the port to `v0.4.26` as its own title records. So "the
next free patch number" in this project's vocabulary has always meant
*current + 1, including a number an unreleased section holds*. `#606` made that
number reserved. The item's original parenthetical - "`0.4.26` today, the port's
section moving as its own risk paragraph provides for" - was right, and reading
"free" off the new reserved set is what produced the wrong gloss.

**Measured on the merged tree, and it is worse than a rename either way.**
Cutting a patch at `0.4.26` *or* at `0.4.27` drops the port's section out of
`wave`'s unreleased set, so the beat moves from `implement v0.4.26 - the
interface moves to Qt` to `implement v0.5.0 - the case you can branch` -
reversing `PL-RKWB`, the owner's 2026-09-14 decision to put the port ahead of
v0.5.0, until somebody hand-edits `ROADMAP.md`. Nothing reports it:
`outstanding_roadmap_edits` returns a byte-identical three-statement list for
`0.4.26`, `0.4.27` and `0.5.0` and never mentions the port's section;
`wave().problems` is empty at both; and no surface prints the reserved set at
all (`reserved` does not occur in `render.py`, and `bin/docket wave` prints
Version, Step, Next, Gate, Scope and Beat only). So the renumber `ROADMAP.md`
provides for is load-bearing for the plan rather than cosmetic, and a cut at
`0.4.27` - stepping *over* the reservation, which no candidate answer below had
noticed the roadmap never contemplates - would also be the first skipped number
in 46 consecutive releases.

**One rule this repository already states does settle part of it.** `PL-66FP`
built the four release refusals in `cli.py` - `_untagged_warning`,
`_unfinished_cut_refusal`, `_duplicate_warning`, `_parallel_cut_warning` - whose
docstrings cite each other for one standard: a release refusal names the
evidence *and* the way out, as commands rather than as intent. Its own "Done
when" extends that to this surface: "naming the evidence and the way out of
each; **the digest says the same** instead of offering a release". The digest's
other refusal, the `held` branch at `render.py:417-424`, does it. The `RESERVED`
sentence is the only release refusal in the subsystem that names evidence and no
way out. That makes "the sentence must name a way out" a session's call by a
rule already written down; *which* way out it names is the part below.

**And the cut path has no guard at all.** `cli.py` contains no `release_offer`,
no `RESERVED` and no read of `plan.reserved`, so `bin/docket release
VERSION=0.5.0` would stamp 49 items and tag it with nothing objecting. The
reading path is the only place a spent number is withheld today, which is what
makes the wording of this one sentence carry more than wording usually does.
`PL-Z85N` is that gap, and it is in direct tension with the roadmap's own
patch-cut mechanic: landing it as written would refuse the cut `PL-G7RD` made
with approval.

**Related but distinct.** `PL-Z85N` is the cut path not objecting to a reserved
version (the opposite direction), `PL-VFD8` is the guard failing to see a
milestone with a row but no section (a false negative of the guard itself, now
closed), and `PL-1BS2` is the Releasable line during an interrupted cut. None of
the three is this: the verdict is correct and the sentence it produces is
unhelpful. `PL-PRQG` (dropped 2026-09-14, same feature) posed the general form -
"a reserved number blocks ordinary patches and moves whenever one is cut" - and
routed it to `PL-YVM1` and `PL-188T`, both now closed; this is the residue that
survived them.

**Why it matters.** The offer is the only line in the digest that tells a
session to *do* something, and it is the line every session reads first. What
this sentence does today is refuse without saying what is available instead,
which breaks the standard `PL-66FP` set for exactly this surface and leaves the
only actionable line in the digest inert on a track that is genuinely cuttable.
`.claude/rules/apparatus-standard.md` states the floor it is closest to: what
this apparatus tells a session must be true, or must say what it could not read.
The sentence is true and says neither what it could not read nor what a reader
may do, and that is not a wording preference: with no guard on the cut path, the
only correction to a session reaching for a wrong number is this sentence.

The claim in the second paragraph that both cuts were "initiated by a human
noticing, which is the condition the offer exists to remove" is weaker than it
reads and is left standing as written for the record. `PL-G7RD` was a `P2`
planning item carrying the renumber plus three roadmap corrections, with
`ROADMAP.md` in its `touches` and the rename asserted by its `verify` - work no
digest line could have produced. The friction an offer removes is a lookup; what
`PL-G7RD` did was judgment.

**Decision needed.** Two questions, and the first decides the second.

1. **Does a patch cut on the `v0.4.x` track still take the Qt port's number and
   rename its section, as `ROADMAP.md` states in three places and as `PL-G7RD`
   executed with your approval on 2026-09-14?** `#606` answered this by
   implication and in the direction of "no longer" - it made `0.4.26` reserved,
   so the apparatus now withholds the very number the roadmap says a patch cut
   takes, and the port's risk paragraph carries both statements a few lines
   apart. That was not a question `PL-188T` put to you, and it is not a
   session's to settle: it is about what the release train promises, which is
   direction. `PL-KQHN` (filed alongside this) carries the contradiction in
   `ROADMAP.md` itself, and `PL-Y1L0` the silent beat swap a cut at either
   number causes.

2. **Given that answer, what should the `RESERVED` sentence say?** Five
   candidates, with the panel's measured objection to each:
   - *Offer the next unreserved patch* (`0.4.27` today). Skips a number for the
     first time in 46 releases, and silently moves the beat off the port.
   - *Name it as an advisory that says what it would displace.* The displacement
     clause cannot be computed: nothing records whether a reserved version has a
     section to rename, so the sentence would assert a cost it cannot read.
   - *Keep the refusal and add that a patch-track cut is available by naming a
     version.* Names no number, so the `0.4.26`/`0.4.27` question above does not
     arise; smallest surface; satisfies `PL-66FP`'s way-out standard. `S`.
   - *Name no mechanical number on either side of the verdict*, honouring
     `version_policy = "manual"` throughout. Removes the only surface that says
     `0.5.0` is spoken for, while the cut path has no guard.
   - *Offer the reserved number itself when it is a patch on the current track,
     naming the renumber as its cost* - the roadmap's documented and executed
     mechanic. Nobody proposed this; it is the only candidate that matches what
     the project actually does, and it is only available if question 1 answers
     "yes, still".

   **Recommendation: answer 1 first; if it is "yes, still", take the fifth
   candidate; if it is "no longer", take the third.** The third is the safe
   answer under either, which is why it is the fallback rather than the pick.

**Done when.** The `RESERVED` branch of `_release_advice` names a way out as
well as its evidence, in whichever of the forms above the decision selects, and
`format_status`'s second copy of the refusal says the same thing rather than
drifting from it (`PL-C6XD` is that de-duplication, and taking it first makes
this item smaller); a test in `subprojects/docket/tests/test_release.py` pins the
sentence on the live arrangement; and the answer to question 1 is written into
`ROADMAP.md` § "the interface moves to Qt" so the paragraph stops carrying both
statements.

**Question 1 is answered (project owner, 2026-09-16, ratified, on `PL-KQHN`).**
A patch cut on the `v0.4.x` track **no longer takes** the Qt port's section
number: the guard withholds it and names it, so a cut at a reserved number is a
deliberate act rather than the release path's default. Chosen over keeping the
documented mechanic and narrowing `PL-VFD8`'s reservation to match; `PL-KQHN`
carries the reasoning, the two measurements behind it, and what it supersedes.

**So question 2 narrows to one candidate, and only its confirmation is left.**
This brief's own recommendation was *"if it is 'no longer', take the third"* -
keep the `RESERVED` refusal and add that a patch-track cut is available by
naming a version. That candidate names no number, so the `0.4.26`/`0.4.27`
question the answer above settles never arises in the sentence at all; it is the
smallest surface of the five; and it satisfies `PL-66FP`'s standard that a
release refusal names the evidence *and* the way out, as a command rather than
as intent. The fifth candidate - offer the reserved number itself, naming the
renumber as its cost - is the one the answer removes, since it was available
only if a patch still took that number.

[superseded 2026-09-17: question 2 is answered below, and the item is `ready`]
Left at `needs-decision` rather than triaged to `ready` because the owner
ratified the `PL-KQHN` recommendation, not this one, and the two were put
separately. What is outstanding is a confirmation rather than an open question:
the four other candidates are spent.

**The last clause of this item's `Done when.` is already satisfied.** "The
answer to question 1 is written into `ROADMAP.md` § 'the interface moves to Qt'
so the paragraph stops carrying both statements" landed with `PL-KQHN`, along
with the same narrowing at the `v0.4.x` timeline row and at planned-milestone
item 29. What is left here is `render.py`'s sentence, `format_status`'s second
copy of it, and the test that pins them.

**Question 2 is answered (project owner, 2026-09-17, ratified).** The `RESERVED`
branch **keeps its refusal and adds that a patch-track cut is available by naming
a version** - the third of the five candidates above. Chosen over offering the
next unreserved patch (`0.4.27`, which would skip a number for the first time in
46 releases and move the beat off the port), over an advisory naming what the cut
would displace (a clause nothing can compute), over removing every mechanical
number from the verdict (which would delete the only surface saying `0.5.0` is
spoken for while the cut path has no guard), and over offering the reserved number
itself - the fifth, which question 1's answer removed, since it was available only
if a patch still took that number.

Marked `ratified` rather than specified: it came as agreement with this brief's
own recommendation rather than in the owner's words, so `CLAUDE.md`'s bar to
reopen it is ordinary evidence rather than a compelling argument.

**What the sentence owes, and the one tension to resolve while writing it.**
`PL-66FP`'s standard is that a release refusal names the evidence *and* the way
out, **as a command rather than as intent** - and this candidate was chosen partly
because it names no mechanical number, so the `0.4.26`/`0.4.27` question never
arises in the sentence. Those pull against each other: `make release VERSION=...`
needs an argument. Resolving that is the implementing session's, and the
constraint is that the sentence must not *recommend* a number while still handing
the reader a runnable command. The other release refusals in `cli.py` -
`_untagged_warning`, `_unfinished_cut_refusal`, `_duplicate_warning`,
`_parallel_cut_warning` - are the precedent for the form.

**Take `PL-C6XD` first, in the same session.** It is `P2 · S · ready`, declares
the same two files, and de-duplicates `format_status`'s independent second copy of
this verdict. Written first, there is one sentence to get right instead of two
that drift; written second, this item ships a digest and a `bin/docket status`
that disagree. That is this brief's own `Done when.` - *"`PL-C6XD` is that
de-duplication, and taking it first makes this item smaller"* - now that the
answer exists to act on.

**Not implemented here.** The session that took the decision was at **308,310
tokens** against `CLAUDE.md`'s 150,000 handoff budget, which says to read the
budget *before starting an item* and hand off rather than start. The decision is
committed on its own so it reaches `main`: left on a branch, the next session
would pick this up still reading `needs-decision` with the answer nowhere in the
store.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Partly overtaken: everything
around the sentence landed, the sentence did not.** `PL-C6XD` closed
2026-09-17 (#652), so `format_status`'s second independent copy of the refusal
is gone - one helper, `_reserved_refusal` at `render.py:1669`, serves both call
sites and is pinned by
`test_release.py:630 test_digest_and_status_render_one_reserved_verdict`. A
surface prints the reserved set (`render.py:1554-1572`; `bin/docket wave` shows
the `Reserved` line). The roadmap clause landed at `ROADMAP.md:1592`
("**A patch cut no longer takes this number**", project owner, 2026-09-16,
ratified). Both decisions are recorded and the item is `ready`.

**What is left is only the sentence and its test.** `render.py:1685-1688` still
returns "No release to offer: the roadmap gives … which is unfinished - …",
and both pointers name what is *due* rather than saying a patch-track cut is
available by naming a version. No test pins it, so the `verify:` fails, and
`render.py:1569` records the item as open in the code itself. The cut path
still has no guard (`PL-Z85N`).

**Every measured number in this brief is spent, so do not reason from them.**
v0.4.26 and v0.4.27 both shipped and v0.4.28 is current; the reserved set is
`0.5.0, 0.6.0, 0.7.0, 0.8.0, 0.9.0` with no `0.4.x` number in it, so only the
minor branch can still collide; the free patch number is `0.4.29` and the
digest *offers* it rather than refusing; nothing was skipped in 46 releases;
the beat is "step 5 of 14: v0.5.0"; `render.py:1466` is no longer the refusal;
the `held` branch is `render.py:464-470`; and `PL-Y1L0` closed 2026-09-19.
The RESERVED branch is dormant rather than dead - which is why the sentence
still has to be right when it next fires.
