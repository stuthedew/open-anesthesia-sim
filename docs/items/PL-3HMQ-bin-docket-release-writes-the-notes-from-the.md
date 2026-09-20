---
id: PL-3HMQ
title: bin/docket release writes the notes from the items' pr: fields before bin/docket record can supply them, so an item whose pull request merged without one loses its link in the shipped notes permanently - v0.4.33 lost PL-LPLD's #758 and v0.4.34 would have lost three
status: untriaged
added: 2026-09-20
---

**Problem.** bin/docket release writes the notes from the items' pr: fields before bin/docket record can supply them, so an item whose pull request merged without one loses its link in the shipped notes permanently - v0.4.33 lost PL-LPLD's #758 and v0.4.34 would have lost three
