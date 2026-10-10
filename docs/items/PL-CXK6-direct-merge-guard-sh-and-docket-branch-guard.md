---
id: PL-CXK6
title: direct-merge-guard.sh and docket-branch-guard.sh read tool_name and session_id from the hook payload with a sed run a line at a time, so a payload whose value sits on the line after its key reads as no name: the merge guard refuses a call of another tool, and the branch guard keys every such session's markers on one shared unknown and skips its checks after the first such session, where its comment says it would ask once more; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: .claude/hooks/direct-merge-guard.sh, .claude/hooks/docket-branch-guard.sh, tests/unit/test_direct_merge_guard.py, tests/unit/test_docket_branch_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
closed: 2026-10-10
pr: 1390
payoff: the merge and branch guards read the tool and the session from any JSON layout, so a payload across lines neither refuses an unrelated tool nor silences the branch guard for later sessions
verify: grep -q 'def test_a_payload_laid_out_across_lines_is_read_as_json' tests/unit/test_direct_merge_guard.py && grep -q 'def test_a_session_id_laid_out_across_lines_is_read_as_json' tests/unit/test_docket_branch_guard.py
---

**Problem.** direct-merge-guard.sh and docket-branch-guard.sh read tool_name and session_id from the hook payload with a sed run a line at a time, so a payload whose value sits on the line after its key reads as no name: the merge guard refuses a call of another tool, and the branch guard keys every such session's markers on one shared unknown and skips its checks after the first such session, where its comment says it would ask once more; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`.claude/hooks/`. Both hooks pull one member out of the JSON payload with a
`sed -n` substitution matching the key, its colon and its quoted value on one
line, and `sed` reads a line at a time. RFC 8259 § 2 allows whitespace,
newlines included, on either side of a member's colon, so a value written on
the line after its key is the same member, and the substitution finds nothing.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, against python3's `json`.
A payload with the value on the next line:

```text
{
  "session_id":
    "abc-123",
  "tool_name":
    "Edit",
  "tool_input": {"file_path": "x"}
}
```

Both seds returned an empty string where `json` reads `Edit` and `abc-123`.
`direct-merge-guard.sh` sends an empty name on to its merge check, so it
refused this call of another tool, which it lets through when the payload is
compact, reproduced end to end with no network reached.
`docket-branch-guard.sh` keys its once-per-session markers on `unknown` when the id is empty, so every such
session shares one pair of markers and, once the first has written them, skips
its checks; the comment above it says an unreadable payload at worst asks once
more than it needed to. Latent: the harness sends one-line JSON, and the merge
guard's matcher routes only merge calls to it.

**Reproduced 2026-10-10 at triage** on this branch at `b6b9c382`, whose readers are `main`'s at `fe2e5132`: over the brief's payload, the
`tool_name` sed and the `session_id` sed both returned an empty string, where
python3's `json` read `Edit` and `abc-123`.

**Why it matters.** `direct-merge-guard.sh` decides whether a pull request is
merged around the owner's read, and `docket-branch-guard.sh` whether a session
is told its base has moved or that its first edit needs a claim. A payload
laid out across lines turns the first into a refusal of a tool it has no say
over and silences the second for every such session after the first, where
its comment promises at worst one question too many.

**Generator check.** A member of `PL-R417`: a reader takes a physical line of
a JSON document for the member it holds. Both hooks already run python3 on the
payload for the rest of their work.

**Done when.** Both hooks read the two members with `json`, as the rest of each
hook already reads the payload, and a test of each feeds a payload with the
value on the line after its key.

**Built 2026-10-10 (`#1390`).** `direct-merge-guard.sh` reads `tool_name`
with `json` in the python block that already read `tool_input`, so its `sed`
and the `case` on its answer went, and `docket-branch-guard.sh` reads
`session_id` with `json` through `python3 -c`, keeping only the characters a
marker file's name may hold. Each guard's test feeds a payload with the value
on the line after its key: the merge guard passes another tool's call laid out
that way, where `main`'s read no name there and refused it as a merge, and the
branch guard keeps a marker per session, where `main`'s read every such
session as `unknown` and asked only the first. The comment above the read now
says what an unreadable payload costs, which it had put as asking once too
often.
