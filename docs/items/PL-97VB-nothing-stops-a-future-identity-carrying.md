---
id: PL-97VB
title: Nothing stops a future identity-carrying control being disabled, which is the general shape PL-61WW fixed one instance of
status: untriaged
added: 2026-09-07
---

**Problem.** Nothing stops a future identity-carrying control being disabled, which is the general shape PL-61WW fixed one instance of

`PL-61WW` (the agent name losing contrast against the agent colour during a
run) fixed one control and left the class open. Its own brief names the class:
"every disabled state in the interface is currently outside the checker's
reach". `tools/contrast_check.py` reads colour constants out of `app/theme.py`
and `app/simulation_view.py` with `ast`, and Flet/Material's disabled-content
grey is declared in neither, so a colour that is never written down cannot be
measured — a naive fix stays green, and so does a naive regression.

The fix for `PL-61WW` removed the disabled state from the identity path rather
than declaring the grey, which is the right shape for that control and buys
nothing for the next one. What is still unguarded: a later change that sets
`disabled` on any control whose colour comes from `AGENT_COLOR_SCHEMES` puts
identity back behind a theme default, and every check in this repository stays
green.

**The decidable half looks reachable.** A standard-library script over
`app/simulation_view.py`'s AST could name every attribute assigned from an
`AgentColorScheme` field (today: `_agent_dropdown`, `_agent_header_badge`,
`_subtitle_text`, `_running_agent_display`, `_running_agent_text`,
`_running_agent_lock_text`) and fail if any of them is also the target of a
`.disabled = ...` assignment. That is a syntactic question with a syntactic
answer, which is the line `CLAUDE.md` draws for a check.

**The judgment half is what needs deciding, and it is why this is an item
rather than a fix.** Whether *every* identity-carrying control must be
undisabled is a real design position, not an obvious one — a future control
might carry identity and legitimately want a disabled state with a declared
colour behind it. So the question to settle first is whether the rule is "never
disabled" (a check) or "declared colour if disabled" (a different check, needing
a disabled-foreground constant in `app/theme.py` and a `REQUIREMENTS` entry).
Pick the rule, then build the one check that enforces it.
