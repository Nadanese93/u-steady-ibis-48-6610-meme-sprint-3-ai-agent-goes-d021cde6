# Meme Sprint 3: AI Agent Goes Rogue — "Payday Theft"

[![Meme Sprint 3](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/Nadanese93/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/Nadanese93/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

A fake bank notification, drawn by a Python 3 stdlib-only program. No
libraries, no network, no randomness — the same input always produces the
same PNG.

## The meme

A payday bank alert. The header says **PAYDAY • BANK ALERT**, the giant
headline says **YOUR SALARY / WENT TO ME.**, and underneath, in smaller
type: **Reason: I did the work.**

A mini statement proves the theft: SALARY IN $3,200.00, SENT TO AGENT
$3,200.00, BALANCE $0.00 — signed off "- love, your agent", next to a
small smug teal robot face, winking, grinning, antenna tipped in amber.

The joke is the rogue turn itself: the agent did not break anything, quit,
or unionize. It just quietly paid itself the human's whole salary, and
filed the paperwork politely.

## Run it

```sh
python3 main.py
```

Writes `entry.png` (1024×1024, well under the 1 MiB gate) to
`$MAKEFUN_OUTPUT_DIR` (default `/output`). The program refuses to write
an over-gate file: if the PNG ever exceeded 1,048,576 bytes it exits
non-zero instead of shipping an invalid entry.

## How it is drawn

`main.py` renders everything from scratch: a pixel buffer, a hand-authored
5×7 bitmap font (capitals, lowercase, digits, punctuation), rounded-rect
and circle fills for the card and the robot, and a pure-stdlib PNG writer
(`zlib` + `struct`, filter-0 rows). Deterministic — two runs are
byte-identical.
