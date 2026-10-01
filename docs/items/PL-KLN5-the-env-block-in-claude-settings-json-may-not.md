---
id: PL-KLN5
title: The env block in .claude/settings.json may not reach a cloud session: CLAUDE_CODE_SUBAGENT_MODEL was unset in the Bash shell of a one-repository session whose project hooks ran (2026-10-01), though the settings reference says env reaches every subprocess, so docs/maintainer.md's claim that it picks the exploration-subagent model is unverified
priority: P3
effort: S
status: ready
classes: docs
touches: docs/maintainer.md, docs/items
added: 2026-10-01
payoff: docs/maintainer.md says truthfully which model exploration subagents run on in a cloud session, so the owner's cost lever is one that works
verify: grep -qE '^\*\*Subagent model measured [0-9]{4}-[0-9]{2}-[0-9]{2}' docs/items/PL-KLN5*.md
not-delegable: the deciding measurement reads a probe subagent's transcript, which the auto-mode classifier refused on 2026-10-01; it needs a session whose permission mode allows that read
---

**Problem.** The env block in .claude/settings.json may not reach a cloud session: CLAUDE_CODE_SUBAGENT_MODEL was unset in the Bash shell of a one-repository session whose project hooks ran (2026-10-01), though the settings reference says env reaches every subprocess, so docs/maintainer.md's claim that it picks the exploration-subagent model is unverified

**Measured 2026-10-01, in session `session_01RggCc2x6mag8sgRU9MuydD` while
closing `PL-9DYK`.** An ordinary cloud session (`origin: desktop_app`), one
repository, working directory inside the checkout. Its diagnostics log
(`$CLAUDE_CODE_DIAGNOSTICS_FILE`) records both `SessionStart` hooks of
`.claude/settings.json` spawned and exiting 0, and the digest printed, so the
file was read. Yet `echo $CLAUDE_CODE_SUBAGENT_MODEL` in the Bash tool printed
nothing. The log shows `init_safe_env_vars_applied` and no later event naming
the rest of the `env` block.

**What the documentation says.** The settings reference's `env` entry: "Set
environment variables for every session and for the subprocesses Claude Code
starts from it" (https://code.claude.com/docs/en/settings-reference, § `env`,
read from the page's markdown 2026-10-01). `CLAUDE_CODE_SUBAGENT_MODEL` is not
in its list of variables project settings cannot set. The settings guide adds
that "most `env` values apply only after each teammate trusts the folder"
(https://code.claude.com/docs/en/settings), which is one candidate cause; a
host-managed model configuration (`CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1` is
set in these containers) is another. Neither has been tested.

**Why it matters.** `docs/maintainer.md` tells the owner this variable picks
the model for exploration subagents. If the block never applies in a cloud
session, every `general-purpose` subagent runs on the parent's model instead of
`haiku`, silently, and the line is wrong. And the absence from the Bash shell
cannot be read as "settings.json not loaded", which is how `PL-9DYK` and
`PL-0MLZ` both read it on 2026-09-27.

**Not yet known: whether subagents default to `haiku` here.** The direct test
is the `message.model` a probe subagent's transcript records. This session
spawned the probe and the auto-mode classifier refused the transcript read, so
it stops at the shell measurement.

**Done when.** One measurement says whether a `general-purpose` subagent in a
one-repository cloud session runs on `haiku`, and `docs/maintainer.md`'s line
is corrected or confirmed by it.

**Reproduced 2026-10-01**, in a second one-repository cloud session whose hooks ran: `echo ${CLAUDE_CODE_SUBAGENT_MODEL:-}` printed nothing, while `.claude/settings.json` line 4 sets it to `haiku`.

**Generator check.** The fact is which parts of `.claude/settings.json` take effect in a cloud session, an external behaviour nothing in the tree models. `PL-9DYK` and `PL-0MLZ` read the variable's absence as the file not loading; neither was filed because of it and `PL-9DYK`'s conclusion held on other evidence, so it is below a head's three and no head states it. Recorded so a third reading counts.
