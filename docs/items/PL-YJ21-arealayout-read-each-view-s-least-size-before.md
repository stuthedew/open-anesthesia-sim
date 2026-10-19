---
id: PL-YJ21
title: AreaLayout read each View's least size before Qt had handled the layout requests that drawing a frame posts, so the Areas, and the page around them, were sized from what the Views needed before their first frame
status: untriaged
feature: interface-areas
added: 2026-10-19
---

**Problem.** AreaLayout read each View's least size before Qt had handled the layout requests that drawing a frame posts, so the Areas, and the page around them, were sized from what the Views needed before their first frame
