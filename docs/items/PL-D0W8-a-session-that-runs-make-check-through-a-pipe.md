---
id: PL-D0W8
title: A session that runs make check through a pipe - make check 2>&1 | tail - reads the pipeline's exit status, which is tail's and always 0, so a red tree is reported and committed as green: it happened on PL-2JRC and the false claim reached both the commit message and the pull request body
priority: P2
effort: S
status: done
classes: defect, infra
feature: worker-instructions
milestone: v0.5.3
touches: .claude/hooks/, .claude/settings.json, tests/unit/, docs/worker.md, docket.toml, docs/ARCHITECTURE.md
added: 2026-09-21
closed: 2026-09-22
pr: 887
payoff: a red tree can no longer be reported and committed as green: the spellings that discard a gate's exit status are refused at the moment they are written, with the one-token remedy in the refusal
verify: printf %s "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"make check 2>&1 | tail -45\"}}" | bash .claude/hooks/gate-status-guard.sh | grep -q permissionDecision
---

**Problem.** A session that runs make check through a pipe - make check 2>&1 | tail - reads the pipeline's exit status, which is tail's and always 0, so a red tree is reported and committed as green: it happened on PL-2JRC and the false claim reached both the commit message and the pull request body

**Why it matters.** It gives a wrong answer silently, which is the first of
`CLAUDE.md`'s three tests for friction that compounds: the gate passes while the
guarantee it stands for is void, and nothing downstream can tell. The harness
flags a non-zero exit and says nothing about an exit 0, so the pipe does not
merely hide the verdict - it substitutes the opposite one, and the session has
no signal that a substitution happened.

The damage is to the record rather than to `main`. CI catches the red tree at
the pull request, so nothing broken merges; what lands is a permanent,
confident, false claim. `PL-2JRC`'s commit message and `#880`'s body both
asserted the gate green, and the correction is now the block that body opens
with. Every other verification claim in this repository's history rests on the
same reading, so one instance devalues all of them.

It is also not confined to `make check`. Any command whose exit status is the
evidence has the same exposure one spelling down - `uv run pytest -q 2>&1 | tail
-20` is the shape a session runs most often while iterating, and it loses the
status identically.

**Decision (session, 2026-09-22).** Route the rule into a `PreToolUse` deny hook
on `Bash` rather than into prose. The rule has to fire when a command is
*written*, which no read precedes, so no path-scoped rule reaches it; and it has
to fire inside exploration subagents, which carry none of the resident context
but do run these hooks. `permissionDecisionReason` is shown to the model, so the
refusal arrives at the moment the wrong conclusion would have formed.
`no-prune-guard.sh` made the same move out of ten resident lines (`PL-JK0M`).
The resident set does not grow to pay for this.

The remedy the message recommends is `set -o pipefail`, and that choice is what
keeps the guard from being routed around. The session piped because a passing
`make check` is thousands of tokens of output it is asked not to load; a guard
whose answer is "do not pipe" trades a false green for a blown context budget
and gets worked around. `set -o pipefail` is one token, keeps the output just as
short, and is never wrong to add.

**Refused: guarding `make check` alone.** It is the observed instance, not the
fault. The fault is that a verification command's status can be discarded, and
the `Makefile`'s own `--no-cache` comment settles this shape of question the
same way - a fix that treats the instance leaves the next spelling to find it
again. The guarded list is exact rather than inferred, because a wrong guess
here blocks a session: `make check|test|docket|doc-check|prebuild|pr-title`,
`bin/docket check|verify`, `pytest`, `mypy`, `ruff`, and `tools/*_check.py`.

**Done when.**

- `.claude/hooks/gate-status-guard.sh` denies a `Bash` call that runs a guarded
  command and then discards its exit status - through `|` without `set -o
  pipefail`, after `;`, after `||`, or backgrounded with `&` - and its
  `permissionDecisionReason` carries both safe spellings.
- The hook is wired into `.claude/settings.json` under the `Bash` `PreToolUse`
  matcher, beside `no-prune-guard.sh` and `floor-interpreter-guard.sh`.
- It stays silent on `set -o pipefail; make check 2>&1 | tail -45`, on the
  redirect-then-read form, on `&&`, on every unguarded command
  (`bin/docket next | head`, `git log | head`), and on a guarded command quoted
  as text inside an argument or a heredoc.
- It fails open on every error path - no `python3`, an unreadable payload, an
  untokenisable command - like the two guards beside it.
- `tests/unit/test_gate_status_guard.py` covers all of the above, including the
  settings wiring.
- `docs/worker.md` states the rule in prose, because a worker running under
  another harness fires no hook and would otherwise have nothing.

**Worked.** The guard refused its own author on its first live firing, and the
refusal was right about the separator and wrong about the command: `make check >
/tmp/gate.log 2>&1; echo "exit=$?"` loses the status by the `;` and reads it by
the `echo`. Reading `$?` is now accepted, restricted to the segment immediately
after the separator - anything in between replaces `$?` with its own status -
and never after `&`, where `$?` is the background launch rather than the gate.
`CLAUDE.md` retires a check that fires without changing a decision, so this was
the fix rather than a concession.

Two consequences outside the declared `touches`, both forced by the new test
file rather than chosen: `docket.toml`'s `workflow_paths` gains
`tests/unit/test_gate_status_guard.py`, because `tools/workflow_paths_check.py`
fails until the lane list agrees that a test importing no `anesthesia_sim` is
apparatus (`PL-JBZK`); `touches` was widened to match. And the gate-disposition
error this item raised while `status: ready` needed no `ROADMAP.md` entry - the
check counts *open* debt items, and this one closes in the commit that carries
the work.

**Found by the docs sweep.** `docs/ARCHITECTURE.md` § "Wired hooks
(`.claude/hooks/`)" counted the wired scripts and listed them by name, and both
were stale - the count read five against six actually wired, and the list had
never picked up `item_read_log.py`. This change made it stale by two rather
than one, so the count is now seven and the list names every wired script but
`stop_hook_patch.py`, which the paragraph below it covers on its own.
`touches` was widened to declare the file. That document sits outside
`docket.toml`'s `workflow_paths` deliberately, so declaring it puts this item
in neither lane - which costs nothing on an item that closes in the same
commit, and is the honest declaration either way.
