---
id: PL-BXB2
title: contrast_check reads only theme.py and simulation_view.py, so a colour declared in any other app/ module is measured by nothing and missed by nothing, and check_colors_live_in_the_theme inspects only the view
status: untriaged
added: 2026-09-14
---

**Problem.** contrast_check reads only theme.py and simulation_view.py, so a colour declared in any other app/ module is measured by nothing and missed by nothing, and check_colors_live_in_the_theme inspects only the view
