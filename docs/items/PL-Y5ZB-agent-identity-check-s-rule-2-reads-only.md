---
id: PL-Y5ZB
title: agent_identity_check's rule 2 reads only construction (self.X = <agent colour>), so a method other than _apply_agent_color_scheme writing self.X.color = AGENT_COLOR_SCHEMES[...] is a second writer of agent colour that neither rule sees
status: untriaged
added: 2026-09-14
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
