---
id: PL-F23S
title: The release skill and bin/docket release's untagged refusal still hand tag-release.yml's re-run to the project owner, though since 2026-10-03 a missing tag's Run workflow is the session's (project owner)
status: untriaged
added: 2026-10-03
---

**Problem.** The project owner set the rule in his own words (project owner,
2026-10-03): "The tag is the workflow's: tag-release.yml tags each cut when its
pull request merges (PL-2FY6), and the thread confirms it with git ls-remote; if
the tag has not landed, you run Actions > tag-release > Run workflow." The
repository still hands that run to the owner, in two places:

- `.claude/skills/docket/modes/release.md`, in the paragraph opening "Where the
  tag has not landed, the run failed or never ran": "the owner runs the workflow
  from Actions > tag-release > Run workflow, or `python3 tools/tag_release.py
  --apply` from a checkout. Both are theirs, since either pushes a tag."
- `subprojects/docket/src/docket/cli.py`'s `_untagged_warning`, which
  `bin/docket release` prints when the previous release has no tag: "Once the
  cause is fixed the project owner runs it again, from Actions > tag-release >
  Run workflow, or from a clone on the Mac".

The project instructions' Releases rule carries the owner's wording verbatim, so
a thread of the Projects trial (`PL-NZC0`) already follows it. A session outside
the project reads only the repository, and hands the owner a step that is now
its own.

**Why it matters.** `bin/docket release` refuses the next cut while the previous
release is untagged, and the remedy it prints puts the owner back on the step
`PL-2FY6` was built to take off him. The refusal is an answer a session acts on,
and it now names the wrong actor.

**Done when.**

- Both places say that running tag-release again is the session's, on `main`:
  from a session, the GitHub tools' `actions_run_trigger` with
  `method: run_workflow`, `workflow_id: tag-release.yml` and `ref: main`, then
  `git ls-remote` to read the tag back.
- The owner keeps only what a session cannot do: a dispatch GitHub refuses the
  session, `python3 tools/tag_release.py --apply` from a clone (a session's own
  tag push is dropped without an error, `PL-N936`), and a tag origin already
  holds on another commit.
- `PL-S641`, an owner-runbook section in `docs/maintainer.md` for re-running
  tag-release, is dropped or narrowed to the refused-dispatch fallback: its
  premise, "the run is the project owner's", is what this rule reverses.

`test_cli.py` pins only the `python3 {TAG_SCRIPT} --apply` line of the refusal,
which stays. No test pins the sentence that changes.

**Not measured.** Whether a session's GitHub token may dispatch a workflow. The
tool's schema was read on 2026-10-03, and v0.5.21's tag landed on its merge, so
no dispatch was needed or made. The first untagged release is the measurement;
the session that meets it says what it showed.

**Reproduced 2026-10-03.** `grep -n "owner runs"` over the two files finds both
sentences.

**Generator check.** One rule the owner changed, with two carriers of the old
one, and no mechanism producing more. Not a generator.

**Filed, not built (2026-10-03).** The project was paused apart from its Order
items 11 and 12, so the coordinator asked for the item alone, to join the Order
only if the owner picks it.
