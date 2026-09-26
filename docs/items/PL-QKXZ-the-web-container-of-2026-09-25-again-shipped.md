---
id: PL-QKXZ
title: The web container of 2026-09-25 again shipped uv 0.8.17 and no libegl1, so a session there has to repair both before make check will run; only the owner's environment setup script can fix it for every container
priority: P2
effort: S
status: needs-decision
classes: infra, session-cost
feature: projects-trial
touches: docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-26
recurrences: 2026-09-26 PL-7TH9
---

**Problem.** The web container of 2026-09-25 again shipped uv 0.8.17 and no
libegl1, so a session there has to repair both before `make check` will run.
Only the owner's environment setup script can fix it for every container.

**Evidence.** On `claude/pl-batch-01-s8d258`, `uv --version` read 0.8.17
against `pyproject.toml`'s `required-version = ">=0.12.5"`, `uv self update`
failed on GitHub's API rate limit, and `make check` stopped with seven
collection errors, `ImportError: libEGL.so.1`. `PL-K6B2`'s pull request, `#1031`,
records the same `libegl1` install in another container of the same run.
Repaired here with `python3 -m pip install -U 'uv>=0.12.5'` (0.12.19, landing
at `/usr/local/bin/uv`, behind the stale `/root/.local/bin/uv` on `PATH`, so it
was linked over it) and `apt-get update && apt-get install -y libegl1`, after
which `make check` exited 0.

**What this changes.** `PL-SPZT` (the stale `uv`) was left open after it did
not reproduce on 2026-09-15, on the reasoning that one container meeting the
floor proves no pin; it has now reproduced. `PL-VHLZ` (nothing installs
`libegl1`) is done, with its environment half recorded as the owner's since no
file in the tree can prove it; this container did not have it. Whether the
setup script lacks the lines or they did not run is not visible from inside a
session.

**Reproduced 2026-09-26: not in `Default`, and these threads never ran
there.** A web session in `Default` (`env_01JWikdPctorEBXoFK7bJnCq`, the
account's only environment by `list_environments`) reads `uv 0.12.18` at
`/root/.local/bin/uv` and `libegl1 1.7.0-1build1` installed. Its
`/var/log/apt/history.log` shows `apt-get install -y libegl1` at 2026-09-23
18:39:22, eight seconds after `uv` was rewritten: `Default`'s cached setup
snapshot carries both. `get_session` reads another environment,
`env_011111111111111111111119`, which the account's list does not hold, for
both containers in the evidence and two more: `claude/pl-batch-01-s8d258`
("Slam-dunk batch 1") and `#1031`'s thread, both in the "Clean up PL"
project, and the "Fix generators" trial's coordinator and its Stream A thread
(`claude/pl-xbv4-build-js9j6d`). The Projects docs say why
(https://code.claude.com/docs/en/claude-projects, § "Choose an environment
for threads", fetched 2026-09-26): "Cloud threads use a default
Anthropic-hosted environment until you pick one in **Project settings >
Environment**." So the question above has a third answer: the lines are in
place and ran, in an environment these projects do not use. `PL-NZC0`'s setup
records `Default` as "chosen explicitly" for the trial, and its coordinator's
reading says that choice is not in effect. `PL-H2V3`, captured on that Stream
A branch, is the same observation from that thread (uv 0.8.17, the suite run
tool by tool), dropped on 2026-09-26 as a duplicate of this item.

**Why it matters.** Every thread either project starts pays the repair before
`make check` will run, and the obvious route, `uv self update`, dies on
GitHub's rate limit. A thread that skips the repair runs the suite tool by
tool, as `PL-H2V3`'s did, and meets `make check`'s other gates only in CI.
The trial alone expects 20 to 30 threads (`PL-NZC0`). And the step this
capture proposed would have reached none of them: a setup script belongs to an
environment, and these threads run in one the account's list does not hold.

**Generator check.** One-off. The fact misread is which cloud environment a
Projects thread runs in: Anthropic's default until **Project settings >
Environment** names one, not the account's `Default`. No head's `misread:`
states it (`bin/docket generators --misread`, 2026-09-26), and two items read
it, this one and `PL-H2V3`, one observation between them, where a head needs
three. Not a re-entry of `PL-VHLZ` (closed 2026-09-15): its setup-script line
holds where it was put, in `Default`, and these threads never ran there.

[superseded 2026-09-26: the reading above - a line in `Default`'s setup script
cannot reach a thread that never runs in `Default`, so these lines are the
Recommendation's fallback, not its first step] **The owner's step.** In the
project's environment settings, under Setup script, two lines would cover
both for every new container:

    apt-get update && apt-get install -y libegl1
    python3 -m pip install -U 'uv>=0.12.5' && ln -sf /usr/local/bin/uv /root/.local/bin/uv

**Checked 2026-09-26 05:15 UTC: "Clean up PL" is in `Default`, "Fix
generators" is not.** `get_session` reads `env_01JWikdPctorEBXoFK7bJnCq` for
"Slam-dunk batch 16" (`claude/pl-batch-16-y80jjp`, created 03:31:44 UTC), a
"Clean up PL" thread started after the owner's 02:43 switch that `PL-7TH9`
records, and still `env_011111111111111111111119` for "Stream A: PL-PVW2,
continued" (`claude/pl-pvw2-next-iier2a`, created 04:34:03 UTC), a "Fix
generators" thread. Both projects' coordinators read the old environment too,
as the docs say any session already running will: "Changes to instructions,
repositories, plugins, and environment in **Project settings** reach new
threads, not threads already running" (§ "Project settings reference",
fetched 2026-09-26). `Default`'s setup snapshot was rebuilt at 03:48 UTC, and
a web session started from it at 05:07 (`claude/kind-ride-kkx2ir`) found
`/root/.local/bin/uv` a regular file reading `uv 0.12.19`, no
`/usr/local/bin/uv`, `libegl1 1.7.0-1build1` installed at 03:48:15, and `make
check` exiting 0, 4,745 tests passed, with no repair. So step 2 below is in
effect, the setup script `Default` now runs does not leave `PL-7TH9`'s dangling
link, and step 1 is what is left. That the script was edited between 02:52 and
03:48 is inferred from the rebuild and the missing link; no session can read
the script itself.

**Decision needed.** Point "Fix generators" at `Default` as well, or leave its
threads on Anthropic's default and make the repair each thread's, which is
`PL-SPZT`'s `docs/worker.md` route. "Clean up PL" is answered: the owner moved
it to `Default` on 2026-09-26. Only the owner can reach **Project settings**.

**Recommendation:** point "Fix generators" at `Default`. It fixes every later
thread in it with no script edit, because `Default` carries both tools and
runs `make check` with no repair, as checked above. The cost is one setting,
owed again by any new project, and the coordinator and threads already running
keep the old environment until they end. The steps, checked against the
Projects and cloud-environments docs on 2026-09-26:

1. At claude.ai/code or in the desktop app, open the "Fix generators"
   project, click the gear icon in the project header (or **Settings** in the
   project's sidebar menu) to open **Project settings**, go to
   **Environment**, and set **Cloud environment** to **Default**: the
   account's one environment, the name the cloud icon above an ordinary
   session's message box shows. Settings save as you change them.
2. [done 2026-09-26: the owner's 02:43 UTC switch, read back from batch 16
   above] Do the same in the "Clean up PL" project, if it will start more
   threads.
3. The change reaches new threads only. Open the next new thread and ask it to
   run `uv --version && dpkg-query -W libegl1`. Worked: `uv 0.12.18` or later
   and `libegl1 1.7.0-1build1`, and `make check` runs with no repair. A
   session confirms it outright: `get_session` on that thread reads
   `environment_id` `env_01JWikdPctorEBXoFK7bJnCq`.
4. Only if that thread still lacks either: at claude.ai/code, click the cloud
   icon showing **Default** in the row above the message box, hover over
   **Default**, click the settings icon on its right, add these two lines to
   the **Setup script** field, and save:

       apt-get update && apt-get install -y libegl1 || true
       python3 -m pip install -U 'uv>=0.12.5' && { [ -x /usr/local/bin/uv ] && ln -sf /usr/local/bin/uv /root/.local/bin/uv; } || true

   [corrected 2026-09-26: the link is conditional now. Unconditional, it
   replaced a working user-site uv with a link to nothing in the first
   container after the switch (`PL-7TH9`). Replayed against scratch paths, the
   line links where pip put uv under `/usr/local/bin`, leaves a user-site uv
   alone, and exits 0 when pip fails.] The `|| true` is the docs' "Exit zero"
   rule, since a script that exits non-zero stops the session starting. The
   pip route reaches PyPI rather than GitHub's rate-limited API. Changing the
   script rebuilds the snapshot.

**Done when.** A new thread in each project runs in `Default` and runs `make
check` with no repair step, read as in step 3, or the owner decides the repair
stays each session's and `PL-SPZT`'s `docs/worker.md` route is the whole
answer. "Clean up PL" meets it as far as a session can read: its new threads
start in `Default`, and `Default`'s current snapshot runs `make check` with no
repair. No "Clean up PL" thread has started since the 03:48 rebuild to read it
from inside one.
