---
id: PL-TLPH
title: bin/docket arm's no-ask hold says send the owner nothing only on line 5 and exits as any hold does, and nothing checks the reply, so a session reading arm through head sent the owner a bare read and merge ask on #1676
priority: P1
effort: M
status: done
classes: defect
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .claude/hooks/gate-status-guard.sh, .claude/hooks/owner_ask_guard.py, .claude/settings.json, tests/unit/test_gate_status_guard.py, tests/unit/test_owner_ask_guard.py, docs/maintainer.md, docs/apparatus.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; the owner agreed to the fix on 2026-10-19
added: 2026-10-19
closed: 2026-10-19
pr: 1688
payoff: a pull request reaches the owner only with arm's recorded ask in the message, because the reply tool refuses a read or merge ask that carries none
verify: grep -q 'NO_ASK = 3' subprojects/docket/src/docket/arming.py && grep -q 'mcp__hearthbot__(reply|update_message|ask_decision)' .claude/settings.json && grep -q 'def test_a_reply_asking_for_a_read_without_a_recorded_ask_is_refused' tests/unit/test_owner_ask_guard.py && grep -q 'bin/docket arm | head -2' tests/unit/test_gate_status_guard.py
root-cause-of: PL-9KHK, PL-DKBG, PL-9JHM
generator: spent - the reply hook refuses a read or merge ask that does not carry arm's recorded line, so a short read of arm's output can no longer reach the owner
misread: whether the owner may be sent a read or merge ask about a pull request
reenters: PL-9JHM
---

**Problem.** bin/docket arm's no-ask hold says send the owner nothing only on line 5 and exits as any hold does, and nothing checks the reply, so a session reading arm through head sent the owner a bare read and merge ask on #1676

**What happened** (measured by the coordinator, 2026-10-19). On `#1676` the
thread ran `bin/docket arm 2>&1 | head -2` twice, at 21:08:40Z and 21:08:58Z.
`arm` printed `READ_ASK`, "Send the owner nothing about this pull request
yet", on line 5 of the hold, so the thread never saw it. The second line it did
see ended "so its pull request waits on the owner's read", which reads like
permission to ask. It sent Stuart a bare "read #1676 and merge it". `#1612`
failed the same way with `head -4`.

`PL-9JHM` (`#1616`) made the ask an `Owner-ask:` record, but its check only
prints text when `arm` runs. Three things let the text be missed:

- the hold puts the instruction after the reasons, the claims, the read paths
  and the auto-merge advice, so a short read of the output drops it;
- every hold exits 1, whether or not an ask is recorded, so the exit status
  says nothing either;
- nothing checks the message that actually reaches the owner. No hook in
  `.claude/settings.json` matches the thread's reply tool, and
  `.claude/hooks/gate-status-guard.sh` does not list `bin/docket arm`.

**Why it matters.** This is the third miss after two prose fixes and one
printed-text fix. Each bare ask spends the owner's attention on a pull request
with nothing recorded to judge, and the owner has said a pull request with
nothing to review must not reach him at all (`PL-9JHM`, 2026-10-18). A rule
that is only printed fails whenever a session reads the output short, so the
refusal has to sit where the ask goes out.

**The fix** (the project owner agreed to the coordinator's recommendation on
2026-10-19, "Agree with your rec").

1. When a hold waits on the owner's read and no valid `Owner-ask` record
   covers it, `arm`'s first line says that no ask is recorded and to send the
   owner nothing, and `arm` exits with a status of its own, 3, apart from a
   hold that has an ask (1). So even `bin/docket arm | head -1` shows it, and
   the exit status alone says it.
2. `.claude/hooks/gate-status-guard.sh` refuses `bin/docket arm` whose output
   goes into a pipe, directly or through a group, since any filter can drop
   the line that matters. Adding `arm` to the guard's list of gates would not
   do it: that list's remedy, `set -o pipefail`, keeps the status and still
   truncates the output.
3. A PreToolUse hook on the thread's `reply`, `update_message` and
   `ask_decision` tools refuses text that asks the owner to read or merge a
   pull request unless `arm` shows a hold for the owner's read with a valid
   recorded ask, and the text carries that ask's line word for word. Ordinary
   progress replies match none of its patterns and pass untouched. It reads
   `arm`'s verdict through a new `bin/docket arm --owner-ask`, which prints
   only the line the owner may be sent (exit 0) or why nothing may be sent
   (exit 3), so the hook does not parse the full output.

**Feasibility, measured 2026-10-19 21:58Z in this thread's container.** A
PreToolUse hook matching `^mcp__hearthbot__update_status$`, written to
`.claude/settings.local.json`, fired before the tool ran and received the
tool's `text` in `tool_input`. A hook returning `permissionDecision: deny`
refused the call with its reason. `bin/docket arm --no-fetch` answered in 2.2 s.

**What it does not reach.** The coordinator's `post_message` is left out: the
coordinator's checkout is not the pull request's branch, so `arm` cannot answer
for it there. A phrasing of an ask that none of the hook's patterns matches is
a known gap, recorded as a test row, as `gate-status-guard.sh` records its own.

**Done when.** A no-ask hold leads with "send the owner nothing" and exits 3;
`bin/docket arm | head` is refused by the guard; and a thread's reply that asks
the owner to read or merge is refused unless `arm` prints a recorded ask that
the reply carries, with each pinned by a test.

**Generator check.** A generator, and fixed in this session. One mechanism
explains `PL-9KHK` (three sessions closed on a bare "read #N"), `PL-DKBG`'s
invented ask on `#1516`, `PL-9JHM` (the bare read of 2026-10-18) and this
item: whether the owner may be sent an ask was only ever text for a session to
read, and nothing checked the message that went out. Each fix so far changed
the text, and each was missed by a session that read it short or not at all.
The reply hook ends the mechanism rather than the instance, because a read or
merge ask can no longer reach the owner without `arm`'s recorded line in it.
