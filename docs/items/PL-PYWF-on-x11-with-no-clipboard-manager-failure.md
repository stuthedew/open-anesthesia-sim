---
id: PL-PYWF
title: On X11 with no clipboard manager, failure details copied with Copy details are lost when the application closes, and the refused-Reset banner tells the user to close and reopen it (found in PL-XWCH)
priority: P3
effort: S
status: ready
classes: defect
feature: interface-design-review
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/integration/approved_interface_strings.json
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
filed-pr: 2269
payoff: a user on Linux keeps the failure details they copied when the banner tells them to restart
---

**Problem.** On X11 with no clipboard manager, failure details copied with Copy details are lost when the application closes, and the refused-Reset banner tells the user to close and reopen it (found in PL-XWCH)

**Why it matters.** A user told to close and reopen the application loses the failure details they copied, on a Linux desktop with no clipboard manager, and cannot report the failure.

**Done when.** The refused-Reset banner tells the user to paste the details somewhere before closing, or the details are also saved to a file whose path the banner names. A test pins the banner text.

**Wording decided 2026-11-23.** Tell the user to paste the details before closing. This is a placeholder under the owner's rule that wording is the session's.

**Generator check.** A one-off: an X11 clipboard rule, which keeps a copy only while the owning application runs.

**Reproduced 2026-11-23.** `src/anesthesia_sim/app/dashboard_frame.py` still names closing and reopening the application as the way out.
