---
id: PL-G8TR
title: no-prune-guard is evaded by the form it recommends - git branch -dr driven from a generated list is a prune
priority: P2
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
touches: .claude/hooks/no-prune-guard.sh, .claude/hooks/shell_split.py, tests/unit/test_no_prune_guard.py, .claude/skills/docket/modes/capture.md
added: 2026-09-06
closed: 2026-09-27
pr: 1198
payoff: a generated list of remote-tracking refs to delete is stopped at the same question a prune is - is any of this the only copy? - while the one-ref remedy the guard prints still runs
verify: grep -q 'def test_a_generated_list_of_refs_is_refused_as_a_prune' tests/unit/test_no_prune_guard.py && uv run pytest tests/unit/test_no_prune_guard.py
---

**Problem.** `.claude/hooks/no-prune-guard.sh` refuses every spelling git
documents that deletes remote-tracking refs without naming them - the prune
flags and settings, `remote prune`, a deleting push, a removed remote (its
header's promise, `PL-61FT`). It does not match `git branch -dr`,
deliberately: that is the safe remedy the guard's own message prints, on the
reasoning that deleting **one** ref **by name** is a considered act.

Run on 2026-09-06:

```sh
git for-each-ref --format='%(refname:short)' refs/remotes/origin | sed 's#^origin/##' \
  | grep -vxFf <(git ls-remote --heads origin | sed 's#.*refs/heads/##') \
  | xargs -r -I{} git branch -dr origin/{}
```

That is a prune. It computes exactly the set `--prune` computes and deletes
all of it - in the one form the guard whitelists, and with a name supplied for
each, so every property the guard relies on is satisfied while the property it
cares about is not. What made the safe form safe was **quantity and
deliberation**, not the flag; the guard tests the flag.

**Why it matters.** The guard is not advice, it is the project's answer to
`PL-HKF4` coming within one prune of losing an item that existed on no other
ref. Its value is entirely in stopping a session to ask "is any of this the
only copy?" - and a pipeline reaches the same end state with no such stop. It
was harmless this time only because the two refs it removed belonged to
branches whose pull requests had merged (#385, #384), which was checked by
hand before running it; the command cannot check that itself, and nothing
required the check.

**What is not the fix.** Refusing `git branch -dr` outright would break the
remedy the guard recommends and the `stranded` recovery recipe that depends
on it. The distinguishing property is that the ref names are *generated* rather
than typed - piped in, built by the shell, or more than one in a single call.

**Where.** `.claude/hooks/no-prune-guard.sh`: a shape beside `SHAPES`,
`PUSH_SHAPES` and `REMOVE_SHAPES`, and the promise in its header.
`.claude/hooks/shell_split.py`: `commands` reads past `xargs` as a wrapper and
returns only the words of the git call it runs, so `xargs -I % git branch -dr
origin/%` reads as one ref spelled out; it has to say which wrappers ran each
command. The restart recipe in `.claude/skills/docket/modes/capture.md`, which
names the ref as `"origin/$BRANCH"`. `PL-JK0M` for why the prohibition moved
into the hook.

**Done when.** A `git branch` delete of remote-tracking refs (`-d`, `-D` or
`--delete` with `-r` or `--remotes`, bundled or not) that is run by `xargs`,
names a ref the shell builds (a `$`, a backtick, a brace or a glob in it), or
deletes other than exactly one ref in one Bash call is refused with the
`--prune` message, opened by a sentence saying why it counts as one. A single
ref spelled out still passes, so `git branch -dr origin/<branch>` - the
hook's own message, `docs/worker.md` and `capture.md`'s recipe - keeps
working. The item's pipeline is pinned verbatim in
`test_a_generated_list_of_refs_is_refused_as_a_prune`.

**Re-confirmed 2026-09-27, and reshaped.** The defect is live: the pipeline
above passes today's hook, and so do `-I %` in place of `-I{}`, `git branch
-dr $(...)`, a `for` or `while read` loop, and `-dr origin/a origin/b`. Each
deleted refs on git 2.43.0 in a scratch clone, the pipeline the only copy of a
branch the remote had deleted. What moved since filing:

- The four patterns are gone. The hook reads commands through `shell_split.py`
  (`PL-WGFY`, `PL-PVW2`) and states a promise, with `KNOWN_GAPS` rows in its
  test for spellings found by probing rather than met in a session (`PL-61FT`).
  This spelling was met in a session, so it is a defect, not a gap. The rule
  tests the property rather than the spelling, so the loop and substitution
  forms close with it instead of being filed one by one.
- The recipe left `SKILL.md` when the skill split into mode files, and now
  spells the ref with a variable. A single `"origin/$BRANCH"` and a loop's
  `"origin/$b"` read alike to the hook, which does not parse loops, so a
  variable counts as generated and the recipe is written out as `<branch>`, the
  way the hook's message and `docs/worker.md` already write it.
- "Several refs at once" is counted across the whole Bash call rather than per
  git call, since `git branch -dr origin/a; git branch -dr origin/b` is the
  first thing a refused session would try. Zero names is refused with the
  rest: git deletes nothing then, and only `xargs` supplies them.
- `tools/branch_sweep.py` now archives every branch it deletes under
  `refs/archive` (`PL-X8SV`), so the only-copy case narrows to a branch deleted
  outside the sweep - by hand, or on GitHub. It does not close: `fetch_remote`
  still fetches without `--prune`, and `stranded` still exists, for that case.
- Probed siblings this rule does not reach - `git update-ref --stdin` fed
  `delete` lines, and a `git push --delete` given a generated list - go in as
  `KNOWN_GAPS` rows, per `PL-61FT`.

**Left standing 2026-09-19 by `PL-4Q9B`** (record clone trust and the permitted ref
operations), which closed with the finding that its ten members are not one
mechanism. It is an independent apparatus defect with a test behind it, and the strongest of the ten: the guard's whitelisted remedy reaches the same end state as the flag it refuses. Unrelated to clone staleness. Nothing here is blocked on that head; this item stands on
its own merits at its own band.
