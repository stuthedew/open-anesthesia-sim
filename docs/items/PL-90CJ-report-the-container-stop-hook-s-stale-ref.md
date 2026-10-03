---
id: PL-90CJ
title: Report the container stop hook's stale-ref unpushed count upstream, since PL-WW08 fixes it for this project only
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
touches: docs/maintainer.md, .claude/hooks/stop_hook_patch.py
added: 2026-09-04
closed: 2026-10-03
pr: 1302
not-delegable: the deliverable is a defect report to the maintainers of the container's stop hook, outside this repository; no command in this tree can prove it filed
---

**Problem.** `PL-WW08` corrected the container's stop hook: it picked its
comparison point from a ref that merely resolved locally, so a merged branch's
stale tracking ref made it demand a push that would have recreated a dead
branch. The fix is `.claude/hooks/stop_hook_patch.py`, which rewrites the hook at
session start - and it fixes it for this repository only. Every other project
using the same container still gets the false demand.

**Why it matters.** The failure it corrects is not cosmetic: acting on the
demand pushes a branch that was deliberately abandoned, and `CLAUDE.md`'s
stale-ref rule exists because such a ref can be the only surviving copy of
captured work. A patch applied per project also has to keep working against a
hook the session does not own, so reporting it upstream is the only route to it
not needing to.

**Where.** Outside this repository. What is here is the evidence a report needs:
`.claude/hooks/stop_hook_patch.py` carries the correction and the commands that
disprove
the demand, `tests/unit/test_stop_hook_patch.py` holds it to what git actually
answers, and `PL-WW08` records the diagnosis.

**Done when** (rewritten 2026-10-03 from "reported to the container's
maintainers with the reproduction", since the report already existed - below).
`docs/maintainer.md` records the two upstream reports and the comment carrying
the reproduction, and `.claude/hooks/stop_hook_patch.py` names them where a
session meets the patch - so a later session neither re-reports it nor assumes
it was fixed. Posting was the owner's, since a session cannot write to that
repository, and they posted it on 2026-10-03.

**Left standing 2026-09-19 by `PL-4Q9B`** (record clone trust and the permitted ref
operations), which closed with the finding that its ten members are not one
mechanism. It was only ever a loose member: the stop hook's false unpushed-work demand is a different mechanism from the clone's staleness, and the deliverable is a report to the container's maintainers plus a line in `docs/maintainer.md`. Nothing here is blocked on that head; this item stands on
its own merits at its own band.

**Re-confirmed 2026-10-03: still live, and already reported upstream, so the
item changed shape.** What was checked, and what each check showed:

- **Still shipped.** The hook is embedded in `/opt/env-runner/environment-manager`,
  which `~/.claude/environment-manager/code-sign` links to. `grep -a` finds
  `unpushed=$(git rev-list "$upstream..HEAD" --count 2>/dev/null) || unpushed=0`
  in it exactly once, and the script carved out around that line (6,395 bytes)
  is byte-identical to this container's `~/.claude/stop-hook-git-check.sh` but
  for the one line `stop_hook_patch.py` rewrites. Claude Code 2.1.288,
  `cloud_default`.
- **What upstream changed since filing.** The signing check now counts
  `HEAD --not --remotes`, runs only where `origin/$current_branch` resolves, and
  reads the raw `gpgsig` header; its comment cites anthropics/claude-code#69586.
  The unpushed count after it was left alone. So the fix to report is the
  scoping upstream already chose two blocks earlier, under the same condition.
- **Already reported, twice.** anthropics/claude-code#83490, "Stop hook
  (stop-hook-git-check.sh) tells the agent to rewrite published history after a
  PR merges", reports the stale `origin/<branch>` a merge leaves.
  anthropics/claude-code#82624, "Web/CCR git stop hook: two false positives; the
  signature one prescribes an amend loop that can never converge", gives as its
  second the single-branch clone `PL-483K` diagnosed. Both were open. Both were
  read through WebFetch, which summarizes rather than quotes: the container's
  proxy refuses github.com for repositories outside the session (403) and the
  `claudeissues.com` mirror at CONNECT, so no body is quoted here, and the titles
  are the ones WebFetch and a web-search index agree on. A new report would be a
  duplicate, so the reproduction goes to #83490 as a comment.
- **`PL-483K`'s two candidates, which it left to this item.** Candidate 1,
  restoring tracking after the merged-PR restart, is moot: the hook never reads a
  branch's configured upstream, only whether `origin/$current_branch` resolves
  by name, so repointing `branch.<name>.merge` changes nothing it counts.
  Candidate 3, a clone fetching more than `main`, is #82624's second false
  positive, and its cause stands: the `add_repo` tool still prescribes
  `git clone --depth 1` (its response, 2026-10-03). The refspec half of
  `stop_hook_patch.py` stays for that reason.
- **The reproduction, run.** The script in the draft below, against the
  carved-out shipped hook: cases 1 and 2 exit 2 with "There are 1 unpushed
  commit(s)" while `git rev-list HEAD --not --remotes --count` is 0, and case 3
  exits 2 as it should. With the draft's fix, cases 1 and 2 exit 0 and case 3
  still exits 2; this container's patched copy answers the same. Run on the fixed
  script, `stop_hook_patch.py` exits 0, prints nothing and leaves the file as it
  was, because the fixed line contains the line it writes - so if upstream ships
  the fix as drafted, the patch goes quiet by itself.

**Posted** by the project owner on 2026-10-03, as a comment on
https://github.com/anthropics/claude-code/issues/83490, from the text below. It
gives a maintainer a run on the current build, the second route to a stale ref
(the one seeded at session start), and a fix scoped the way upstream already
scoped the signing check. This session could not read the comment back: the
container's proxy refuses that page, and WebFetch's summary of it showed no
comments, which a summary of a page that long cannot settle either way.

````markdown
Still reproducible in the current Claude Code on the web container (Claude Code 2.1.288, checked 2026-10-03). The signing check has since been scoped to `HEAD --not --remotes`, but the unpushed count after it still compares against whatever `origin/<branch>` resolves to locally:

```bash
unpushed=$(git rev-list "$upstream..HEAD" --count 2>/dev/null) || unpushed=0
```

`origin/$current_branch` only has to *resolve locally* to become `$upstream`, so every commit the default branch gained since that ref was last written counts as unpushed. That happens after a merge, when the host deletes the head branch and the tracking ref stays behind. It also happens with the ref the environment manager seeds when it creates the session branch: a session that never pushed, and only fast-forwarded to `origin/main`, is told it has unpushed commits. Obeying either demand pushes a branch with no commits of its own, and after a merge it recreates the deleted head branch.

Hermetic reproduction (pass the hook's path; it ignores your git config):

```bash
#!/usr/bin/env bash
# Reproduce stop-hook-git-check.sh demanding a push when nothing is unpushed.
# Usage: bash repro.sh [path-to-hook]   (default: ~/.claude/stop-hook-git-check.sh)
set -euo pipefail
HOOK=$(realpath "${1:-$HOME/.claude/stop-hook-git-check.sh}")
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1   # hermetic: no signing, no user config
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.com
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
git init -q --bare -b main "$T/remote.git"
git clone -q "$T/remote.git" "$T/team" 2>/dev/null && git -C "$T/team" commit -q --allow-empty -m base && git -C "$T/team" push -q origin main
land() { git -C "$T/team" pull -q origin main && git -C "$T/team" commit -q --allow-empty -m "$1" && git -C "$T/team" push -q origin main; }
hook() { local rc=0 err; err=$(cd "$1" && echo '{}' | bash "$HOOK" 2>&1 >/dev/null) || rc=$?
         printf '  hook exit %s, unpushed by --not --remotes: %s\n  %s\n' "$rc" "$(git -C "$1" rev-list HEAD --not --remotes --count)" "${err:-<no output>}"; }

echo "1. Branch pushed, PR squash-merged, remote branch deleted, branch restarted from origin/main"
git clone -q "$T/remote.git" "$T/s1" && cd "$T/s1"
git checkout -q -b claude/one && git commit -q --allow-empty -m work && git push -q -u origin claude/one
land "squash-merge of claude/one" && git -C "$T/team" push -q origin --delete claude/one   # GitHub deletes it server-side
git fetch -q origin main                                                       # no --prune: origin/claude/one stays
git checkout -q -B claude/one origin/main                                      # restart the branch from main once its PR merged
hook "$T/s1"

echo "2. Session branch seeded at start and never pushed; main moves; branch fast-forwarded to origin/main"
git clone -q "$T/remote.git" "$T/s2" && cd "$T/s2"
git checkout -q -b claude/two && git update-ref refs/remotes/origin/claude/two HEAD   # seeded as by createLocalBranch -> UpdateRemoteTrackingBranch
land "another PR merges"
git fetch -q origin main && git merge -q --ff-only origin/main
hook "$T/s2"

echo "3. Control: a commit that really is unpushed"
git commit -q --allow-empty -m "local only"
hook "$T/s2"
```

Against the shipped hook:

```
1. Branch pushed, PR squash-merged, remote branch deleted, branch restarted from origin/main
  hook exit 2, unpushed by --not --remotes: 0
  There are 1 unpushed commit(s) on branch 'claude/one'. Please push these changes to the remote repository.
2. Session branch seeded at start and never pushed; main moves; branch fast-forwarded to origin/main
  hook exit 2, unpushed by --not --remotes: 0
  There are 1 unpushed commit(s) on branch 'claude/two'. Please push these changes to the remote repository.
3. Control: a commit that really is unpushed
  hook exit 2, unpushed by --not --remotes: 1
  There are 2 unpushed commit(s) on branch 'claude/two'. Please push these changes to the remote repository.
```

Suggested fix: give the count the scoping the signing check already uses, under the same condition, so the `origin/HEAD` fallback is unchanged:

```diff
-  unpushed=$(git rev-list "$upstream..HEAD" --count 2>/dev/null) || unpushed=0
+  if [[ "$upstream" == "origin/$current_branch" ]]; then
+    unpushed=$(git rev-list HEAD --not --remotes --count 2>/dev/null) || unpushed=0
+  else
+    unpushed=$(git rev-list "$upstream..HEAD" --count 2>/dev/null) || unpushed=0
+  fi
```

With it, cases 1 and 2 exit 0 and case 3 still exits 2.
````
