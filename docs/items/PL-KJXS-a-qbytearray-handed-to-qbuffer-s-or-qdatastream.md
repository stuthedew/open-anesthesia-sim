---
id: PL-KJXS
title: A QByteArray handed to QBuffer's or QDataStream's constructor, or to QBuffer.setBuffer, is the use-after-free PL-NDKC measured as a segfault and as silently wrong zeros, and nothing fails make check when src/ writes one
status: untriaged
added: 2026-09-26
---

**Problem.** A QByteArray handed to QBuffer's or QDataStream's constructor, or to QBuffer.setBuffer, is the use-after-free PL-NDKC measured as a segfault and as silently wrong zeros, and nothing fails make check when src/ writes one
