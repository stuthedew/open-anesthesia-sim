---
id: PL-CXK6
title: direct-merge-guard.sh and docket-branch-guard.sh read tool_name and session_id from the hook payload with a sed run a line at a time, so a payload whose value sits on the line after its key reads as no name: the merge guard refuses a call of another tool, and the branch guard keys every such session's markers on one shared unknown and skips its checks after the first such session, where its comment says it would ask once more; latent
status: untriaged
feature: one-answer
added: 2026-10-06
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

**Generator check.** A member of `PL-R417`: a reader takes a physical line of
a JSON document for the member it holds. Both hooks already run python3 on the
payload for the rest of their work.

**Done when.** Both hooks read the two members with `json`, as the rest of each
hook already reads the payload, and a test of each feeds a payload with the
value on the line after its key.
