---
id: PL-97VB
title: Nothing stops a future identity-carrying control being disabled, which is the general shape PL-61WW fixed one instance of
status: done
priority: P2
effort: M
classes: infra
feature: dev-tooling
touches: tools/agent_identity_check.py, tests/unit/test_agent_identity_check.py, Makefile, docket.toml, docs/ARCHITECTURE.md, .github/workflows/quality.yml, .claude/rules/ui-color.md
added: 2026-09-07
closed: 2026-09-08
verify: uv run pytest tests/unit/test_contrast_check.py && python3 tools/agent_identity_check.py && grep -q 'def test_a_disabled_identity_control_without_the_paired_hide_is_reported' tests/unit/test_agent_identity_check.py
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

**Why it matters.** The class is a safety class even though this item is
tooling. A control carrying agent identity that reaches the screen in
Flet/Material's disabled-content grey is the wrong-context failure
`CLAUDE.md`'s presentation clause names - the correct number under an
identity the reader cannot make out - and `PL-61WW` is the proof that it
reaches the screen without a single check going red. Nothing in the tree
would say so again.

It is classed `infra` and banded `P2` deliberately, rather than `safety`/`P1`.
`docket check` pins a `safety` class to the top band, and the band means "a
clinician could be misled" today; a guard against a defect that does not
currently exist is not that. The bar being guarded stays `presentation-safety`'s;
the work is `dev-tooling`'s.

**The rule, decided by the project owner (2026-09-08): never disabled.** Of the
two candidates the brief above poses - *never disabled*, or *declared colour if
disabled* - the first. It needs no new constant, and it is the position
`PL-61WW` already put the tree in.

"Never disabled" is about what is **rendered**, and that distinction is the
whole design of the check. `_agent_dropdown` is still assigned
`disabled = snapshot.is_running`; it is also assigned
`visible = not snapshot.is_running`, so it renders nothing while disabled. A
check reading `disabled` alone would fail the merged tree and push a later
session into deleting a defensive line to appease it, which is the tail wagging
the dog. So the enforced shape is: **an identity-carrying control may be
assigned `disabled = E` only where it is also assigned `visible = not E`, the
same expression negated.**

**Done when.** `tools/agent_identity_check.py` is wired into `make check` and
CI, and fails a tree where a control carrying the agent colour can be visible
and disabled at once. Two rules, both syntactic:

1. **The identity set is what `_apply_agent_color_scheme` writes.** That method
   is already the project's single writer of agent colour and says so in its
   own docstring, so the set needs no second list to be kept in step. The check
   errors rather than passing where that method is missing or writes nothing -
   a coverage set that can silently go empty is worse than no check.
2. **A control given an agent colour at construction must be in that set.**
   This is what makes rule 1's coverage claim true rather than asserted: a
   control coloured in `__init__` and never re-written by
   `_apply_agent_color_scheme` is outside rule 1 *and* is the stale-label bug
   in its own right - the previous agent's colour under the current agent's
   numbers.

Deliberately not decided by the tool: whether a control's identity is legible,
whether a given pairing is the *right* one, or what colour anything should be.
It answers "is this control both agent-coloured and disabled without the paired
hide", which the source answers by itself. `tools/contrast_check.py` draws the
same line and its docstring is the precedent.

Known limitation, recorded rather than papered over: a control coloured by
neither route - no construction-time agent colour and no write in
`_apply_agent_color_scheme` - is invisible to both rules. No such control
exists today and rule 2 is what keeps the first route closed.

**Landed (2026-09-08).** `tools/agent_identity_check.py`, wired into `make
check` and into CI's floor-adjacent group beside `tools/contrast_check.py` -
under `uv run` for the same reason that one is, its only input being
`app/simulation_view.py`, which targets 3.14 and would be a `SyntaxError` to
the 3.11 parser these tools otherwise promise. `tests/unit/test_agent_identity_check.py`
covers each rule from both sides: a miniature view that breaks it, and one in
the correct shape that must stay quiet.

It reports 6 controls today - `_agent_header_badge`, `_subtitle_text`,
`_agent_dropdown`, `_running_agent_display`, `_running_agent_text`,
`_running_agent_lock_text` - which the test names rather than counts, so
dropping one from the single writer fails a test instead of quietly shrinking
what `make check` covers.

**No `src/` change was needed, which is the result worth recording.** The
merged `PL-61WW` tree already satisfies both rules: `_agent_dropdown` carries
`disabled = snapshot.is_running` beside `visible = not snapshot.is_running`,
and every agent-coloured control is written by `_apply_agent_color_scheme`. The
check was built to the code rather than the code to the check, and it was
watched failing on a mutated tree before being trusted on the real one.

**The pairing shape is enforced structurally, and the test says why.**
`visible = snapshot.is_paused` beside `disabled = snapshot.is_running` may well
be correct, and the check still rejects it: proving two conditions equivalent
is the judgment half, and a tool that guessed would report a pass it cannot
support. One canonical shape, and a failure naming that shape.

**Docs.** `docs/ARCHITECTURE.md` gains the package-map line `doc_check` requires
and a paragraph beside the two sibling tools; `.claude/rules/ui-color.md` gains
the rule at the moment a session picks a colour, which is what its `paths:`
scope delivers. `docs/MODEL.md` is still owed the same statement as one of the
bars this interface holds itself to above AA - that is `PL-K8YM`, filed under
`PL-61WW` and now carrying more weight, since the bar is enforced rather than
merely true.
