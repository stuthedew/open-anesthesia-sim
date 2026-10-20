---
id: PL-BT70
title: tools/headless_worker.py does not keep the Mac awake, so a batch started without caffeinate stalls when the Mac idles to sleep; on macOS the runner should hold its own 'caffeinate -i -w <its pid>' assertion for the whole batch
priority: P2
effort: S
status: done
classes: defect, infra
touches: tools/headless_worker.py, tests/unit/test_headless_worker.py, docs/maintainer.md, docs/apparatus.md, tools/worker_runs.py
added: 2026-10-20
closed: 2026-10-20
pr: 1698
payoff: a batch started without caffeinate no longer stalls when the Mac idles to sleep
verify: uv run pytest -q tests/unit/test_headless_worker.py -k 'awake or caffeinate'
---

**Problem.** tools/headless_worker.py does not keep the Mac awake, so a batch started without caffeinate stalls when the Mac idles to sleep; on macOS the runner should hold its own 'caffeinate -i -w \<its pid>' assertion for the whole batch

**Why.** The project owner asked on 2026-10-20 what happens if they forget `caffeinate`. The caffeinate(8) manual says `-i` creates "an assertion to prevent the system from idle sleeping", and `-w` "Waits for the process with the specified pid to exit. Once the process exits, the assertion is also released." `-s` prevents system sleep but "is valid only when system is running on AC power" (manual mirrored at https://www.sudo.is/docs/macos/man_caffeinate.html, read 2026-10-20). So the runner can start `caffeinate -i -w <its own pid>` and forget it, and the assertion ends with the runner. The manual does not say what closing the lid does, so the runner's start-up line should say to keep it open.

**What sleep does now.** Every process stops while the Mac sleeps. On waking, open connections have usually dropped. Claude Code retries a failed request a limited number of times, so a short sleep may only delay the run, and a long one ends it as an error. Then PL-44SP applies.

**Build it with PL-NQ0M and PL-44SP**, which change the same `main()`. Off macOS, where `caffeinate` does not exist, the runner says so once and carries on.

**Built, 2026-10-20.** `keep_awake()` starts `caffeinate -i -w <the runner's pid>` on macOS before the first run, and not on a dry run. Its line tells the owner to keep the lid open. Where `caffeinate` is not found, the line says that nothing keeps the machine awake, and the batch carries on.

**Generator check.** A one-off. Nothing else here runs long enough on the owner's Mac for sleep to matter.
