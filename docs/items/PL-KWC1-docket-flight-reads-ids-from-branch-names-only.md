---
id: PL-KWC1
title: docket flight reads ids from branch names only, so every harness-named branch is invisible
priority: P2
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-08-31
closed: 2026-08-31
pr: 113
commit: 3fb55ee
verify: uv run pytest subprojects/docket/tests/test_vcs.py -k subject
---

**Problem.** `branches_in_flight` finds an item id by matching `BRANCH_ID_RE`
against the *branch name*. A branch a session creates for itself is named
`claude/pl-k7qx-short-slug` and matches. A branch the web harness creates is
named from the owner's opening prompt — `claude/parallel-session-workflow-kpeet1`,
`claude/roadmap-release-write-failure-nhsjwo` — and carries no id at all.
`CLAUDE.md` already records that such a branch cannot be renamed.

So the mechanism is blind in exactly the case it exists for. Measured
2026-08-31: `bin/docket flight` printed `no branch names carry an item id`
while `origin/claude/roadmap-release-write-failure-nhsjwo` sat there with 22
commits of item work on it.

**Why it matters.** This is not only a quiet digest line. `in_flight_ids`
feeds `docket next` (which excludes in-flight items), `docket concurrent`,
`docket status`, `docket delegable` and `docket list`. With the harness
branches invisible, **`docket next` will hand a session an item another
session is actively implementing**, and the collision is discovered at push
time. The whole point of deriving in-flight state from git rather than storing
it was that git already knows; it knows on the branches this project does not
use.

**Read the commit subjects, and match only at the start of one.** The id is on
the branch — `CLAUDE.md` requires it at the front of every commit subject —
so `git log --source --format='%S %s' ^origin/main <refs>` recovers it in one
call for every ref at once. `%S` is confirmed available here.

The anchoring is the part that must not be got wrong. This project writes
implementation subjects leading with the id (`PL-M5FK Hold the roadmap's tag
claims to git tag`) and bookkeeping subjects mentioning it mid-sentence
(`Capture PL-D2GW, found while answering what to work on next`). Measured over
the last 120 commits on `main`: 79 subjects contain an id, 64 lead with one,
and **all 15 of the difference are captures, recoveries, close-outs or merge
commits — not one is implementation work.** `PL-F5HB Close it out; triage
PL-4CW7 with the environment fix applied` is the case in miniature: the
leading id is the work, the mentioned one had merely been triaged.

Matching an id anywhere in a subject would therefore report roughly 19% false
positives, and a false positive here makes `docket next` skip an item that is
*startable* — the opposite of the defect being fixed. Anchor to the start.

**Report the age, do not threshold it.** "Has an unmerged branch" and "is being
worked right now" are different claims, and only the last-commit timestamp
separates a live session from an abandoned branch. Carry the age into the
report and let the reader judge, the way `stranded` reports rather than
decides.

**This checkout is shallow** (`git rev-parse --is-shallow-repository` → `true`),
so guard as `merged_pull_requests` does: `--merged` and `origin/main..ref`
need only the merge-base and do work here, but where a merge-base does not
resolve the ref is reported as unreadable rather than silently contributing
nothing.

**Where.** `subprojects/docket/src/docket/vcs.py` — `branches_in_flight` and
the `Branch` dataclass. Call sites reading only `item_id` are unaffected.

**Done when.** `bin/docket flight` names an item being worked on a
harness-named branch; a subject that merely mentions an id does not put that
item in flight; each in-flight branch reports how long since its last commit;
and a ref whose merge-base cannot be read is reported as unreadable.
