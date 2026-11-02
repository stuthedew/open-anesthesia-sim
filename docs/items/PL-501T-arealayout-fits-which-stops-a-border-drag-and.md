---
id: PL-501T
title: AreaLayout._fits, which stops a border drag and lights the WARNING line, still estimates each Area's drawn size as its window share minus one handle, not from the apportionment the splitters draw: the estimate ignores nested handles and overstates an Area whose split neighbour is held wider than its share, and two adapter tests pin the stop it gives, a handle's width short of the neighbour's need (found building PL-16BG)
status: untriaged
feature: area-layout-sizing
added: 2026-11-01
---

**Problem.** AreaLayout._fits, which stops a border drag and lights the WARNING line, still estimates each Area's drawn size as its window share minus one handle, not from the apportionment the splitters draw: the estimate ignores nested handles and overstates an Area whose split neighbour is held wider than its share, and two adapter tests pin the stop it gives, a handle's width short of the neighbour's need (found building PL-16BG)
