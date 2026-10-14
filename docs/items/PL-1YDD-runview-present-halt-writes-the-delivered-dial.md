---
id: PL-1YDD
title: RunView.present_halt writes the delivered dial's name from settings().agent_display_name while the subtitle, chip, substance heading, selector and colour scheme stay the last frame's, so a halt on the first frame after a successful set_agent would show two agents; no control reaches it today, since _start_new_case halts on a refused snapshot before set_agent (found reviewing PL-85LJ)
status: untriaged
added: 2026-10-12
---

**Problem.** RunView.present_halt writes the delivered dial's name from settings().agent_display_name while the subtitle, chip, substance heading, selector and colour scheme stay the last frame's, so a halt on the first frame after a successful set_agent would show two agents; no control reaches it today, since _start_new_case halts on a refused snapshot before set_agent (found reviewing PL-85LJ)
