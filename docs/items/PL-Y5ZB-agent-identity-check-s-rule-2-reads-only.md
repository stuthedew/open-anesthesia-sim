---
id: PL-Y5ZB
title: agent_identity_check's rule 2 reads only construction (self.X = <agent colour>), so a method other than _apply_agent_color_scheme writing self.X.color = AGENT_COLOR_SCHEMES[...] is a second writer of agent colour that neither rule sees
priority: P3
effort: M
status: done
classes: defect, infra
feature: qt-port
touches: .claude/rules/ui-color.md, tests/unit/test_agent_identity_check.py, tools/agent_identity_check.py
added: 2026-09-14
closed: 2026-10-11
pr: 1410
verify: uv run python tools/agent_identity_check.py && grep -q 'def test_a_property_write_in_another_method_is_a_second_writer' tests/unit/test_agent_identity_check.py
---

**Problem.** agent_identity_check's rule 2 reads only construction (self.X = <agent colour>), so a method other than _apply_agent_color_scheme writing self.X.color = AGENT_COLOR_SCHEMES[...] is a second writer of agent colour that neither rule sees

**Found 2026-09-14** while merging the second triage pass's brief for `PL-V53R`
(agent_identity_check reads only simulation_view.py) into the item. That pass's
"Done when" asked that "a writer outside `_apply_agent_color_scheme` is found
rather than ignored". What landed finds a *second definition* of that method in
any class of any module and refuses it, and rule 2 finds a control
*constructed* from a colour table anywhere. It does not find a method under
another name that writes a colour *property* - `self.X.color =
AGENT_COLOR_SCHEMES[agent_id].fill` outside the writer - because
`constructed_with_agent_color` reads `self.X = ...` targets only, and
`self_attribute` returns `None` for `self.X.color`. The tool's docstring states
this as its known limitation ("a control coloured by neither route ... is
invisible to both rules"), and none exists today.

**Why it matters.** The single-writer design is what makes the identity set
definitional rather than a hand-kept list. A second writer under another name
is exactly the thing that design exists to prevent, and it is the one route the
check cannot see; a session porting the colour writes to `setStyleSheet` or to
a helper could open it without anything going red.

**Done when.** Rule 2 also reads property writes: any `self.X.<prop> = <expr>`
reaching a colour table, outside the writer's method, is reported as a second
writer, with a test that plants one in another method and one in another
module.

**Triaged 2026-09-15 at P3, deliberately, despite the subject.** The check
guards a presentation-safety property - that agent colour has exactly one writer,
so the identity set is definitional rather than hand-kept - but the item is not
itself a safety defect: the tool's own docstring already states this limitation,
and the brief above records that no control takes the uncovered route today. So
it is a gap in a guard rather than an open hole, and it is seated below the port
items that are live defects in what a reader sees.

What keeps it from being dropped is that the gap is in the one direction the
design cannot tolerate. The single-writer rule holds only while every route to a
colour is visible, and a session porting the colour writes to `setStyleSheet` or
to a helper would open the second writer without anything going red - the exact
thing the check exists to prevent, arriving through the one door it does not
watch.

## Closed 2026-10-11

Rule 2 now reads `self.X.<prop> = ...` beside `self.X = ...` and the call
statement: `agent_colorings` takes `written_control(target)` for a property
target, one attribute deep, which is the shape `identity_controls` reads inside
the writer, and the success line counts the three spellings apart.

Read as rule 2's own rule rather than as the Done-when's wider "any ... is
reported": a property write is reported when its control is outside the
identity set, as the other two spellings are. One on an identity control in the
writer's class is counted and passes, since the writer re-writes that control
on every agent change; reporting it would make one spelling stricter than the
other two for the same control.

Three tests: a write planted in another method of the writer's class and one in
another module are both reported (the tool before this change reported neither,
0 findings each), and a write on an identity control is quiet and counted. The
shipped tree reads 0 property-write colourings, as the brief said it would.
`.claude/rules/ui-color.md` now names the property route beside the other two.
