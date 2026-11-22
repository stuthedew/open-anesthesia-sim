---
id: PL-49J8
title: When the bump reaches a version the roadmap has given to an unfinished milestone, the release offer says 'No release to offer' and names no patch, so sessions read it as no cut due: 134 items piled up behind v0.7.0's open gate between v0.6.18 and v0.6.19
status: untriaged
feature: release-roadmap-seam
added: 2026-11-22
---

**Problem.** When the bump reaches a version the roadmap has given to an unfinished milestone, the release offer says 'No release to offer' and names no patch, so sessions read it as no cut due: 134 items piled up behind v0.7.0's open gate between v0.6.18 and v0.6.19

**Why it matters.** `suggest_version` in `subprojects/docket/src/docket/release.py`
bumps the minor number whenever any finished item is classed `feature`
(`docket.toml`'s `minor_classes`). Between milestones that number is nearly
always one `ROADMAP.md` has given to an unfinished milestone, so
`release_offer` returned `RESERVED`, and the digest and `bin/docket status`
printed "No release to offer". The way out it offered named no number. The
dry run printed the raw bump as a "mechanical guess". Sessions read both as
"no cut is due". On 2026-11-22 `bin/docket status` showed 134 finished items
since 0.6.18 and still said "No release to offer", with v0.7.0's gate holding
8 open entries.

**The ask (project owner, 2026-11-22).** In the thread "Cut v0.6.19 and fix
release version guess" the owner wrote: "I think release thing is broken. It
anchors when close to 0.7.0 it seems when close and stops recommending 0.6.x
releases. Let's say I implemented 1,000,000 new features before finishing the
eight remaining items, it wouldn't recommend a new 0.6.x release right?", then
"right, but when we get to v0.8.0 down road, it will be fixed for that?", then
"make sure versioning recommendations follow best practice". The coordinator's
brief asked that the guess never suggest a planned milestone's version while
that milestone is unfinished, and suggest the next patch instead, for any
milestone and not only 0.7.0.

**This reopens one ratified decision.** `PL-SYG4` question 2 (project owner,
2026-09-17, ratified) chose a refusal that names no number over offering the
next unreserved patch. Its objection to the patch was that the next patch then,
0.4.26, was itself the Qt port's number, so offering 0.4.27 would skip a
number and strand the port. That objection still holds where the next patch is
spent, and the fix keeps the refusal there. It does not hold where the next
patch is free, which is the case here, and the stall it caused is the new
evidence.

**Best practice, read 2026-11-22.** Semantic Versioning 2.0.0
(https://semver.org/, the page itself) item 4: "Major version zero (0.y.z) is
for initial development. Anything MAY change at any time." Its item 7, the
minor-for-new-functionality rule, is stated for "x > 0". The Cargo Book,
"SemVer Compatibility" § "Change categories"
(https://doc.rust-lang.org/cargo/reference/semver.html, the page itself):
"Initial development releases starting with "0.y.z" can treat changes in "y" as
a major release, and "z" as a minor release." npm's semver documentation,
"Caret Ranges" (https://docs.npmjs.com/cli/v6/using-npm/semver, the page
itself): caret ranges allow "patch updates for versions `0.X >=0.1.0`", and
"Many authors treat a `0.x` version as if the `x` were the major
"breaking-change" indicator." So below 1.0, additive work under the last number
is the common practice, and the middle number is free to mark a boundary, which
is how `ROADMAP.md` § "Versioning decision" uses it.

**What it changes.**

1. `release_offer` gains a fourth answer, `PATCH`. Where the bump's number is
   reserved, it offers `free_patch`: the current version with its last number
   raised by one, provided every reserved version lies above it. It reads
   `plan.reserved`, the roadmap's own list of spent numbers, so it holds for
   v0.8.0 and every later milestone without naming one.
2. `RESERVED` remains only where no patch is free, and its sentence now says
   why nothing can be cut, instead of a way out that does not exist there.
3. The digest says "Offer 0.6.19 before taking new work. It is a patch, because
   the roadmap gives 0.7.0 to "the schematic", which is unfinished."
   `bin/docket status` says the same reason after "Next version would be
   0.6.19." One function, `render.patch_reason`, writes it for both and for the
   dry run.
4. `bin/docket release --dry-run` with no version prints the same suggestion
   from the same offer, replacing the "mechanical guess".
5. `.claude/skills/docket/modes/release.md` says a reserved number means a
   patch, not "no cut due".

**Done when.** `bin/docket status` on `main` with v0.7.0 open offers the next
patch and names 0.7.0 as the reason, and the tests named on this item pass,
including one with a made-up later milestone.

**Generator check.** Not a head. The fact is which version a release should
take, and `plan.reserved` already records it. The defect was that the offer
read it to refuse and not to answer.
