---
id: PL-XQY6
title: The cloud environment's setup script left uv missing on 2026-09-26: its ln -sf /usr/local/bin/uv /root/.local/bin/uv replaced the uv pip had installed in /root/.local/bin with a link to a file that does not exist, so the second line PL-QKXZ's closing note suggests breaks what the first installs
status: untriaged
feature: projects-trial
added: 2026-09-26
---

**Problem.** The cloud environment's setup script left uv missing on 2026-09-26: its ln -sf /usr/local/bin/uv /root/.local/bin/uv replaced the uv pip had installed in /root/.local/bin with a link to a file that does not exist, so the second line PL-QKXZ's closing note suggests breaks what the first installs

**Evidence, 2026-09-26 02:52-02:58 UTC**, in the container of the "Slam-dunk
batch 13" thread (`claude/pl-batch-13-c1j5i3`), started after the project's
default environment was switched to `Default` at 02:43: `uv` was not on
`PATH`. `/root/.local/bin/uv` was a symlink, dated 02:52 (container start), to
`/usr/local/bin/uv`, which did not exist. Beside it, `/root/.local/bin/uvx`
was a regular file from the same minute, and `python3 -m pip show uv` read
0.12.19 at `/root/.local/lib/python3.11/site-packages`. So pip had done a user
install into `/root/.local/bin`, and the `ln -sf` that follows it in the setup
lines batch 1 suggested (recorded in `PL-QKXZ`'s evidence, where pip had
instead landed at `/usr/local/bin/uv`) replaced that binary with a dangling
link. `libegl1` was installed (`dpkg -s`: "install ok installed"). Repaired by
removing the link and `python3 -m pip install --force-reinstall --no-deps uv`,
which put 0.12.19 at `/usr/local/bin/uv`; `make check` then ran.

**Why it matters.** The link is correct only when pip lands in
`/usr/local/bin`, and here it did not, so the environment-side fix `PL-QKXZ`
waits on is broken as written: every thread in this environment starts
without `uv`, and a session reading `uv: command not found` beside a
`required-version` it cannot see has no hint that the setup script caused it.

**Done when.** `PL-QKXZ`'s recommendation for the setup script installs `uv`
without the unconditional link (for example `python3 -m pip install -U
'uv>=0.12.5'` alone, since `/root/.local/bin` is already on `PATH`, or a link
made only when `/usr/local/bin/uv` exists), and a thread started afterwards
reads `uv --version` at or above 0.12.5 before any repair.
