---
id: PL-MF90
title: Choose one token set and one component set for the interface pass, in the NCSA style the owner picked
priority: P3
effort: L
status: blocked
classes: planning, ux
feature: interface-pass-design-round
blocked-by: PL-2V6V
added: 2026-11-11
payoff: every control and readout follows one set of sizes, spaces and colours, so a change to the look is made once
not-delegable: the owner chooses among the token and component sets
---

**Problem.** Choose one token set and one component set for the interface pass, in the NCSA style the owner picked

**Where this comes from.** The fourth step of the order of work the owner
agreed on 2026-11-10 (`PL-HS9M`). It waits for the layouts, `PL-2V6V`, and
for the result of the one-control trial, `PL-BVC5`, which decides whether
the controls are built as a custom Qt style or as style sheets.

**What to do.** Choose one type scale, one spacing scale, one set of
surfaces and one accent, in the NCSA style whose sampled colours `PL-HS9M`
records. Build one set of controls with every state, and the domain
components: a compartment readout, an agent chip, a parameter row and a
reference mark. `ROADMAP.md` planned-milestone item 33 lists what the pass
keeps: the contrast minimums, the fixed ISO 5360 agent colours, dash pattern
as the channel that separates the traces, and no dark mode in this pass.

**Why it matters.** One token set and one component set make every control and readout follow the same rules, so the interface pass changes the look in one place instead of in each widget.

**Done when.** One type scale, one spacing scale, one set of surfaces and one accent are recorded, and one set of controls with every state and the four domain components are built on them, keeping planned-milestone item 33's contrast minimums and agent colours.

**Checked 2026-11-22** against `d4e8200`: still applies, and still blocked. Its blocker `PL-2V6V` (the grey-box layouts) is open and blocked. The other condition named here has been met: `PL-BVC5` closed on 2026-11-11 with the result that the controls are built in a custom Qt style.

**Added 2026-11-27: a walk-through before the resident rounds** (project
owner, 2026-11-27, ratified, `PL-HWZK`). Once the controls and domain
components are built, walk the owner through a clickable mock-up of the
Default Workspace made from them, using the checks from the user stories
(`PL-TJM4`). Keep the grey-box layouts open until then. In the NN/g homepage
redesign, users "said they liked this grid", but "people unanimously
gravitated towards the list version" once both were shown as visual designs
(Whitenton K, Gibbons S. Case study: iterative design and prototype testing of
the NN/g homepage. Nielsen Norman Group, 2018,
https://www.nngroup.com/articles/case-study-iterative-design-prototyping/, read
2026-11-27). The final look can change which layout works, so a layout found
wrong in the walk-through goes back to `PL-2V6V` before the resident rounds.
