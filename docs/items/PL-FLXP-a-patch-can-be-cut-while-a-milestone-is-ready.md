---
id: PL-FLXP
title: A patch can be cut while a milestone is ready and waiting on the owner's test drive, shipping the milestone's work under another number, and a ready milestone with no item finished since the last tag cannot be cut at all
status: untriaged
feature: release-process
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, .claude/skills/docket/modes/release.md, .claude/skills/docket/modes/coordinator.md, ROADMAP.md
added: 2026-11-26
---

**Problem.** A patch can be cut while a milestone is ready and waiting on the owner's test drive, shipping the milestone's work under another number, and a ready milestone with no item finished since the last tag cannot be cut at all

**Why it matters.** On 2026-11-26 the coordinator nearly cut v0.6.25 from the
33 items finished since v0.6.24, while v0.7.0 had a clear gate and a closed
Required scope and waited only on the owner's test drive. The patch would have
shipped the same 33 items under a second number, and it would then have
blocked v0.7.0 itself: `bin/docket release` prints `Nothing to release` and
exits 0 when no item has finished since the last tag, so a test drive that
changed nothing could never be followed by the milestone's cut. The cut path
never asked the plan whether a release other than the patch was due. Its own
offer already said so (`release_offer` returns `PLANNED`), and
`test_the_plan_names_the_version_when_it_is_the_one_asking_for_a_release`
records why: a patch then "would ship the gate's whole content as a patch and
leave v0.3.0 with nothing in it". The same thing happened in fact from v0.6.20
to v0.6.24, each cut as a patch after `bin/docket status` had begun offering
0.7.0, because `.claude/skills/docket/modes/coordinator.md` § "Releases"
starts a cut whenever a feature finishes and the milestone needs the owner's
word.

**What best practice says.** Read in full on 2026-11-26:

1. Semantic Versioning 2.0.0 (https://semver.org/spec/v2.0.0.html). Item 4:
   below 1.0 "Anything MAY change at any time". Item 3: a released version's
   contents "MUST NOT be modified". Item 9: a pre-release such as `1.0.0-rc.1`
   ranks below its normal version and "indicates that the version is unstable".
2. PEP 440 (https://peps.python.org/pep-0440/), which governs a Python
   package's version: pre-releases are written `X.YrcN`, and SemVer's hyphen
   form "is not compatible with this PEP".
3. The Cargo Book, "SemVer Compatibility"
   (https://doc.rust-lang.org/cargo/reference/semver.html): below 1.0, "changes
   in 'y' [are] a major release, and 'z' a minor release". This is why additive
   work may ship in this project's 0.y.z patches.
4. PEP 602 (https://peps.python.org/pep-0602/) and the Python devguide,
   "Development cycle"
   (https://devguide.python.org/developer-workflow/development-cycle/): after
   beta 1 "no new features are accepted"; in the release-candidate stage only
   severe fixes go in, and "the goal is to have no code changes between an RC
   and a final release".
5. Kubernetes, "Release Cycle" and "Patch Releases"
   (https://kubernetes.io/releases/release/,
   https://kubernetes.io/releases/patch-releases/): a code freeze of about four
   weeks before a minor release in which "only critical bug fixes are merged";
   a patch release carries fixes cherry-picked onto an already released line.
6. Linux, "Everything you ever wanted to know about Linux -stable releases"
   (https://www.kernel.org/doc/html/latest/process/stable-kernel-rules.html): a
   stable patch "must fix a real bug that bothers people", and the fix must
   already be in mainline.
7. Google, *Site Reliability Engineering*, chapter 8 "Release Engineering"
   (https://sre.google/sre-book/release-engineering/): "frequent releases
   result in fewer changes between versions", and a release is built from a
   branch cut at a known revision so that "we know the exact contents of each
   release".
8. DORA, "Working in small batches"
   (https://dora.dev/capabilities/working-in-small-batches/): one named pitfall
   is "regrouping the batches before sending them downstream for testing or
   release", which delays feedback.
9. The Rust Book, appendix G, "How Rust is Made and 'Nightly Rust'"
   (https://doc.rust-lang.org/book/appendix-07-nightly-rust.html): a fixed
   six-week train, in which a regression found in beta is fixed on the main
   branch and backported, and the stable release is produced from beta.

None of these projects cuts a patch on the old line that carries the work the
next minor release is about to ship. Once the next release is frozen or in its
candidate phase, new work waits for the release after it, and a patch on the
old line carries only a fix that is already on the main branch. This project
cuts every release from `main`, so a patch cut while the milestone waits can
only be the milestone's own content under another number.

**Done when.**

1. `bin/docket release` refuses any version other than the plan's own while
   `bin/docket wave`'s beat is `release`, in a dry run too, and says the
   milestone is ready and waits on the owner's word.
2. `bin/docket release` cuts the milestone the beat names when no item has
   finished since the last tag, rather than printing `Nothing to release`.
3. The digest and `bin/docket status` say, beside the milestone's offer, that
   no patch is cut while it waits.
4. `.claude/skills/docket/modes/release.md`, `.claude/skills/docket/modes/coordinator.md`
   and `ROADMAP.md` § "Versioning decision" state the rule, and the reply
   carries replacement text for the project instructions' "Releases" paragraph.
