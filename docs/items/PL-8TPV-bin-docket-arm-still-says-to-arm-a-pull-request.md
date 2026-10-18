---
id: PL-8TPV
title: bin/docket arm still says to arm a pull request after the owner switches its auto-merge off to let another one merge first, so its session can re-arm it against the owner's choice
priority: P2
effort: M
status: done
classes: defect
feature: arm-follows-owner
milestone: v0.5.29
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_cli.py, docket.toml, tools/open_pull_requests.py, tests/unit/test_open_pull_requests.py, docs/maintainer.md, docs/apparatus.md, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
closed: 2026-10-18
pr: 1587
payoff: a pull request the owner holds back by switching auto-merge off stays off, so sessions stop merging work out of the order the owner chose
verify: grep -q 'def test_an_owner_disarm_is_not_rearmed' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket arm still says to arm a pull request after the owner switches its auto-merge off to let another one merge first, so its session can re-arm it against the owner's choice

**What happened, 2026-10-17.** Between 05:53 and 06:34 UTC, auto-merge was
switched off ten times on five pull requests: #1475, #1478, #1480, #1481 and
#1483. The owner switched them off so that other pull requests would merge
first. They said so in `PL-8ZTQ`'s thread at 06:52 UTC: "I switched them off to
prioritize other PR".

A session could not tell that the owner had made those switches:

- GitHub attributes every call to the owner's account, whether the owner or a
  session made it. So the pull request's timeline shows the owner's name on
  every arm and every disarm.
- `bin/docket arm` still printed `arm` for #1478 after the second switch. It
  decides from the branch's paths and the open claims, and it does not look at
  the pull request's auto-merge setting.
- The GitHub notice that a session receives when auto-merge is switched off
  tells it to turn auto-merge back on if the pull request should still merge.

So a session that follows its rules turns auto-merge back on, or merges the
pull request itself once CI passes. That night, #1483's session recorded the
plan "auto-merge flipped off again; merge when CI passes". `PL-8ZTQ`'s thread
spent a helper agent reading other sessions' transcripts to find out who had
switched #1478 off, until the owner said.

**What a fix has to achieve.** When the owner switches auto-merge off, the
session that owns the pull request leaves it off. The session still arms a
pull request that `bin/docket arm` clears and that nobody has switched off. To
do that, a fix needs to know who last changed the setting, and GitHub does not
record that in a form a session can read. One route is for each session to
record its own arms and disarms, and to treat any other change as the owner's.
That is the case that `.claude/rules/apparatus-standard.md` calls "Nobody
records the fact". The session that builds this chooses the route.

**Related.** `PL-XTBF` has the same cause in the other direction. There,
`bin/docket arm` tells a session to switch off auto-merge that the owner
switched on after reading the pull request. Both items carry the feature
`arm-follows-owner`. Only two items share the cause, so it is not a generator.

**Why it matters.** The owner switches auto-merge off to decide the order in
which pull requests merge. A session that turns it back on, or merges once CI
passes, overrides that choice and merges work the owner had held back.

**Done when.** After the owner switches auto-merge off on a pull request,
`bin/docket arm` no longer tells its session to arm it, and says why. A pull
request that nobody has switched off is still armed when `arm` clears it. A test
pins both cases.

**Generator check.** Not a member of a head. The fact is "who last changed a
pull request's auto-merge setting", which nothing records. `PL-XTBF` misreads
the same fact in the other direction. Two items share it, which is below the
three a generator needs.

**Route chosen, 2026-10-18: the session records its own switches.** Checked
first whether GitHub could tell the two apart after all. It cannot: on
`#1478`'s timeline every switch is `stuthedew` with no
`performed_via_github_app`, and `#1586`'s, armed by a session through its
GitHub tools at 16:28Z, reads the same. So the brief's "Nobody records the
fact" shape applies, and the record is a commit trailer,
`Auto-merge: off - <why>`, which a session writes on its next commit after it
switches auto-merge off.

**Worked.** `tools/open_pull_requests.py --auto-merge NUMBER` prints the latest
switch from the pull request's timeline as `on TIME` or `off TIME`, through
`docket.toml`'s new `auto_merge_command`. `arm` asks it for an open pull
request. A switch off holds the pull request unless a commit on the branch
carries the record with a committer date at or after the switch. A session
switches it off and then commits, so a record made before the switch cannot be
for it. The hold says the owner switched it off, and to arm or merge it only on
the owner's word. A forge that could not be asked leaves the answer `unknown`.
The ordinary hold line now asks for the record whenever it tells a session to
switch auto-merge off. A session that forgets the record gets the owner's hold,
which fails safe: it asks the owner, or records the switch if its own
transcript shows it made it. `test_an_owner_disarm_is_not_rearmed` covers the
owner's switch, a record before and after it, an armed and a never-armed pull
request, and a forge that could not be asked.
`test_arm_asks_the_auto_merge_command_docket_toml_names` runs the command end
to end.
