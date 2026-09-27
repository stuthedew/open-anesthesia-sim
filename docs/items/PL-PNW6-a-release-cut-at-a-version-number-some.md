---
id: PL-PNW6
title: A release cut at a version number some withdrawn tag once named leaves every warm checkout pointing v<version> at the old commit, and the handover's own 'git fetch origin main' is the command that leaves it stale silently
priority: P2
effort: S
status: done
classes: defect, infra
feature: release-process
touches: .claude/skills/docket/modes/release.md, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_release.py
added: 2026-09-07
closed: 2026-09-27
pr: 1197
verify: grep -q 'def test_the_tag_lines_clear_a_withdrawn_tag_before_tagging' subprojects/docket/tests/test_release.py && grep -qF 'git ls-remote --exit-code' subprojects/docket/src/docket/release.py && grep -qF 'git ls-remote --exit-code' .claude/skills/docket/modes/release.md
---

**Problem.** A release cut at a version number some withdrawn tag once named leaves every warm checkout pointing v<version> at the old commit, and the handover's own 'git fetch origin main' is the command that leaves it stale silently

**Measured 2026-09-07**, in a scratch pair of repositories, tagging `v0.4.8` at
commit A, cloning, then deleting that tag on the origin and re-tagging at
commit B:

| In the warm clone | Exit | Result |
| --- | --- | --- |
| `git fetch origin main` | 0 | tag never attempted; still at A, nothing printed |
| `git fetch --tags origin` | 1 | `! [rejected] v0.4.8 -> v0.4.8 (would clobber existing tag)`; still at A |
| `git fetch --tags --force origin` | 0 | `t [tag update]`; now at B, `refs/remotes/*` untouched |

The first row is the problem, and it is the row that matters because it is the
command the skill's own release handover tells the owner to run. It exits zero
and says nothing, so a warm checkout keeps `v0.4.8` on a commit that carried no
release, indefinitely, with nothing indicating it.

**This is not the same condition as `PL-LT77`.** That one is a tag deleted on
origin and never replaced, where the local copy is the only one and `doc_check`
reports it in wording that reads as a claim about the repository. This is a tag
deleted and then *re-created at a different commit*, where origin and the warm
checkout both hold `v0.4.8` and disagree about what it means. `doc_check` is
silent here - the ROADMAP row exists and the version matches - so nothing
reports it at all, which makes it the quieter of the two.

**Blast radius is small and pointed at the one reader who cannot escalate.** A
container that clones fresh is correct by construction, so remote sessions
self-heal; what persists is the project owner's own machine, and `git describe`,
`git log v0.4.8..`, and any release-span question asked there answer from the
wrong commit.

**Why it matters.** The failure is silent in the one direction that matters.
The fetch the handover itself prescribes exits zero and prints nothing, so
nothing distinguishes a checkout holding the right tag from one holding the
withdrawn one, and there is no moment at which the reader is told to look.
Every release-span question then answers from the wrong commit while reporting
no fault - `git describe --contains`, `git log v<version>..`, and
`bin/docket release`'s own refusal to cut while the previous release is
untagged, which reads a tag it believes it can trust. `doc_check` is silent
here by construction, because the ROADMAP row exists and the version matches,
so unlike `PL-LT77` there is no red check to prompt a diagnosis at all.

**Shape of a fix, not yet chosen.** Either the release handover carries
`git fetch --tags --force origin` whenever the number being cut is one a tag
has previously named - which the cutting session can decide, since it is the
one that knows the number was re-used - or `bin/docket release` records that a
number was re-used so the handover is generated rather than remembered. Note
that `--prune-tags` is not available here: `.claude/hooks/no-prune-guard.sh`
refuses it, correctly, because a stale `origin/<branch>` ref can be the only
surviving copy of a stranded item (`PL-HKF4`).

**Concrete instance.** v0.4.8, cut 2026-09-07 under `PL-BKDP`, is exactly this
case: the number was previously tagged on `b03a7d03` and withdrawn.

**The sharper failure, measured 2026-09-07 after the above.** A warm checkout
does not merely read the old commit - it cannot make the new tag at all. While
the number is withdrawn on origin, no fetch of any kind clears the local copy:
`--tags --force` has nothing to overwrite it with, because origin holds no
`v0.4.8` to force. So the stale tag survives every safe fetch, and the tag
command the release handover prints then fails outright:

```
$ git tag -a v0.4.8 "$COMMIT" -m "v0.4.8"
fatal: tag 'v0.4.8' already exists
```

That is the good case, in the sense that it is loud and stops. The bad case is
the reader who reaches for `-f` to get past it, because `git tag -f -a` will
happily re-point the local tag and the subsequent `git push origin v0.4.8`
succeeds - leaving the release correctly tagged on origin and the *reason* it
failed unexamined, which is the same warm checkout that will misreport
`git describe` for every earlier tag it also holds stale.

**So the handover for a re-used number owes an explicit local delete**, before
the tag and after the fetch:

```bash
git tag -d v0.4.8          # clears the withdrawn tag if this checkout holds it
```

Verified as a whole sequence: delete, resolve the commit by its subject, confirm,
tag, push - which put the tag on the intended commit from a checkout that had
been holding the withdrawn one.

**Done when.** Cutting a release at a version number some tag has previously
named produces a handover that clears the withdrawn tag locally before it
tags - so the owner never meets `fatal: tag 'v0.4.8' already exists`, and never
reaches for `-f` to get past it - and a warm checkout that follows the handover
ends with `v<version>` on the commit the release was actually cut at. Which of
the two shapes above delivers that is the decision this item is waiting on:
put the extra commands in the handover the cutting session writes, since that
session is the one that knows the number was re-used, or have
`bin/docket release` record the re-use so the handover is generated rather
than remembered.

**Decision needed.** Where the extra tag commands come from when a version
number is re-used: (1) the cutting session writes them into the handover it
already produces, since it is the session that knows the number was previously
tagged - no new mechanism, but it depends on a session noticing; or (2)
`bin/docket release` records the re-use and generates the handover, which makes
it deterministic at the cost of teaching the release tool about tag history it
does not read today. Answer this and the item is `ready`; a `verify:` command
cannot be written before it, because the two shapes put the change in different
files.

**Answered 2026-09-19 under `PL-4Q9B`** (record clone trust and the permitted ref
operations): **option 1, the cutting session writes the extra commands into the
handover it already produces** (project owner, 2026-09-19, ratified), chosen over teaching
`bin/docket release` to record the re-use and generate them.

Two reasons, and the second is the one that decided it. The cutting session is
the only party that knows the number was previously tagged, and it is already
composing the handover by hand. And `bin/docket release` would have to read tag
*history* - what a number once pointed at and no longer does - which is not
recoverable from the remote at all once the tag is withdrawn: the evidence has
been deleted. A deterministic mechanism that cannot see its own input is worse
than the prose, because it would report "no re-use" with authority.

So the work is in `.claude/skills/docket/SKILL.md`, Mode: ship a release: where
the number being cut is one a tag has previously named, the handover carries
the local delete before the tag, and says why. The sequence is already verified
in this item's own brief.

**The acute instance is gone, which narrows this to the general case.** v0.4.8
was re-cut for real: the remote and this checkout both hold it at `93f1902`,
`ROADMAP.md` has its row, and `doc_check` is green. What remains is the next
re-used number, not this one.

**The `verify:` command was run 2026-09-19 and fails for the right reason**:
`doc_check` passes and the `grep` half exits 1.

**Re-confirmed 2026-09-27: the problem holds, sharper than recorded, and the
2026-09-19 answer is reopened on two facts it did not have.** The mode this
brief points into moved from `.claude/skills/docket/SKILL.md` to
`.claude/skills/docket/modes/release.md`, and `touches` now says so.

1. **The session no longer writes the handover.** Since `PL-VYK1` (2026-09-25,
   `#1065`), `bin/docket release` prints the tag lines from
   `release.tag_commands`, and `modes/release.md` tells the session to paste
   those rather than edit them. So the ratified shape - the cutting session
   adds the delete when it knows the number was re-used - now means editing
   generated lines against the skill's own instruction. It also still rests on
   a session knowing what a fresh clone cannot show it: a withdrawn tag
   survives only in checkouts that fetched it, and the one that matters is the
   owner's.
2. **The refusal does not stop the handover; the push after it republishes
   the withdrawn tag.** Measured 2026-09-27 in a scratch origin and warm clone,
   with `tag_commands("1.0.0")`'s three lines run as one pasted block:
   `git tag -a` refused with `fatal: tag 'v1.0.0' already exists`, and
   `git push origin v1.0.0` then pushed the clone's withdrawn tag, printing
   `* [new tag]`, so origin held `v1.0.0` on the withdrawn commit again. The
   brief above calls the refusal "the good case ... loud and stops"; pasted as a
   block, which is how the handover is used, it is followed by a push that
   looks like success.

**What no longer needs this item.** The silent half is reported now. In a
warm checkout that has pulled the re-cut, the withdrawn tag trips
`doc_check`'s tag-on-its-cut error (`PL-QHCW`), and its version error where the
two commits' version files differ (`PL-YKSD`); both name
`git ls-remote --tags origin` and `git tag -d`. `PL-LT77` gave the
version-table error the same clause for a checkout that has not pulled.

**Decision needed.** Where the local clear comes from, now that the handover is
generated: (1) keep the ratified shape, the cutting session adding it by hand
when it knows of the re-use; or (2) generate it in `tag_commands`, guarded.

**Recommendation: (2).** One line between the fetch and the tag, in every
handover:

```bash
git ls-remote --exit-code origin refs/tags/v1.0.0 >/dev/null || git tag -d v1.0.0 2>/dev/null
```

It deletes a local tag only when origin does not list that name. This is not
the 09-19 option 2 re-argued: that one had `bin/docket release` read tag
history the remote no longer holds, and would have answered "no re-use" with
authority. This line reads only origin's current answer, on the machine that
holds the stale tag, at the moment it matters. Measured in the same scratch
pair: it cleared the withdrawn tag and the release tagged its cut
(`Deleted tag 'v1.0.0' (was d57c6f7)`, then `* [new tag]` on the cut commit),
and re-run after success it changed nothing (`already exists`,
`Everything up-to-date`, `git fetch --tags` exit 0). An unguarded `git tag -d`
fails that second case: it re-creates a different tag object, the push is
rejected, and every later `git fetch --tags` exits 1 on
`would clobber existing tag`. Cost: every handover grows from three lines to
four, one of them a network call, silent unless it deletes something. If (2) is
taken, `verify:` becomes a `tag_commands` test in
`subprojects/docket/tests/test_release.py`, and the `grep` above retires, since
it presumes (1).

**Answered 2026-09-27: (2), generate it** (project owner, 2026-09-27,
ratified, over keeping the 2026-09-19 shape, in which the cutting session
writes the delete by hand when it knows the number was re-used). The work:
`release.tag_commands` returns the guarded line above between the fetch and
the tag, filled in for the version and remote; its docstring says why the
guard is there; `.claude/skills/docket/modes/release.md`'s example block and
prose follow it from three lines to four; and a test runs the generated lines
against a scratch origin and a warm clone holding the withdrawn tag, asserting
the tag lands on the cut and origin never receives the withdrawn one, then
re-runs them after success and asserts nothing changes. `verify:` greps for
that test and for the guard in both `release.py` and the skill's example, and
`make check` runs the test; the `grep` for the prose shape retires with shape
(1).

**Closed 2026-09-27.** `release.tag_commands` returns four lines, and the
second, between the fetch and the tag, reads for `v1.0.0`:

```bash
[ -z "$(git tag -l v1.0.0)" ] || git ls-remote --exit-code origin refs/tags/v1.0.0 >/dev/null || [ $? -ne 2 ] || git tag -d v1.0.0
```

That is the answered shape with two guards the line quoted above lacked. Both
were found by measuring it while building it, in a scratch origin with git
2.43.0:

- **It exited 1 on every ordinary handover.** A checkout holding no tag of the
  name reached `git tag -d`, which failed, so a `bash -e` run stopped at line
  two - which is how the existing replay tests run the lines - and a paste
  reported a failure on the first tag of every release. It now asks nothing
  and exits 0 when the checkout holds no such tag.
- **It deleted a published tag when origin could not be asked.**
  `ls-remote --exit-code` exits 2 only when origin answered and holds no such
  ref; pointed at a path that does not exist it exits 128, and the `||` read
  that as withdrawn. Re-run with origin unreachable, the quoted line deleted
  the checkout's correct tag; the tag line re-creates it as a different object,
  and `git fetch --tags` then exits 1 on `would clobber existing tag`. It now
  deletes only on exit 2.

Neither changes what was decided: a generated line that deletes only what
origin says it does not have. `test_the_tag_lines_clear_a_withdrawn_tag_before_tagging`
fails on the three-line handover, where origin takes the withdrawn tag back;
`test_the_tag_lines_delete_nothing_when_origin_cannot_answer` fails on the
quoted line, as do the two existing replay tests. `_run_printed` gained
`keep_going`, since the hazard exists only where every pasted line runs.
`.claude/skills/docket/modes/release.md`'s example is byte-identical to
`tag_commands("0.3.0")`, and two docstrings in `cli.py` that counted three
commands no longer count them.
