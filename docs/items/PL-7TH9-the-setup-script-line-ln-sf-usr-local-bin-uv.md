---
id: PL-7TH9
title: The setup-script line 'ln -sf /usr/local/bin/uv /root/.local/bin/uv' left uv a dangling link in this project's new default environment on 2026-09-26, because pip placed no uv at /usr/local/bin, so make check stops at uv: command not found
status: untriaged
feature: projects-trial
touches: docs/items
added: 2026-09-26
---

**Problem.** The setup-script line 'ln -sf /usr/local/bin/uv /root/.local/bin/uv' left uv a dangling link in this project's new default environment on 2026-09-26, because pip placed no uv at /usr/local/bin, so make check stops at uv: command not found

**Observed 2026-09-26** in the container of `claude/pl-batch-14-pjd1sh`
("Slam-dunk batch 14"), started 02:52 UTC, after the owner changed the
project's default environment at 02:43 UTC. The setup script ran:
`/var/log/apt/history.log` records `apt-get install -y libegl1` at
2026-09-26 02:52:49, and `/root/.local/bin/uv` was a symlink dated 02:52
pointing at `/usr/local/bin/uv`, which did not exist. `uv --version` failed
with `uv: command not found`, so `make check`, which runs everything under
`uv run`, could not start.

**Cause, as far as a session can see it.** `python3 -m pip show uv` read
0.12.19 at `/root/.local/lib/python3.11/site-packages`, whose `RECORD` puts
the binary at `/root/.local/bin/uv`: a user-site install, already meeting
`>=0.12.5`. So `pip install -U 'uv>=0.12.5'` placed nothing at
`/usr/local/bin/uv`, and the `ln -sf /usr/local/bin/uv /root/.local/bin/uv`
after it replaced the working binary with a link to nothing. Whether the
user-site uv came from the image or from this pip run is not visible from
inside; either way the link line assumes a system install that did not
happen. In batch 1's container (`PL-QKXZ`) pip did land at
`/usr/local/bin/uv`, which is the case the line was written for.

**Repaired here** with `python3 -m pip install --force-reinstall --no-deps
'uv==0.12.19'`, which wrote the binary through the link to
`/usr/local/bin/uv`; `uv --version` then read 0.12.19 and `make check` exited
0.

**Recommendation (marked).** Make the link conditional, so it runs only where
pip actually put uv under `/usr/local/bin`:
`python3 -m pip install -U 'uv>=0.12.5' && { [ -x /usr/local/bin/uv ] && ln -sf /usr/local/bin/uv /root/.local/bin/uv || true; }`.
It keeps batch 1's case (a stale uv at `/root/.local/bin` shadowed by a new
one in `/usr/local/bin`) and leaves a working user-site uv alone. This is the
owner's environment setting, not a file in the tree, so nothing here can
close it but the owner's edit and a container that then reads `uv --version`
at 0.12.5 or later.

**Generator check.** Not a head: it is the second observation of one fact
with `PL-QKXZ` (which environment's setup a thread gets, and what it
installs), recorded there as a recurrence.
