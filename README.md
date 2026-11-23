# world-news-2026-11-22

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/GAD2412/world-news-2026-11-22/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/GAD2412/world-news-2026-11-22/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

One 1024x1024 front page of the world's news on Sunday 22 November 2026: 31 dated stories from 7 regions, three
illustrated leads (COP31 collapses without a deal, a Russian warship sunk at Benghazi, Iran's strike on Bahrain),
ten figure cards, eighteen one-line briefs (claims by one side marked with a ring), an approximate UTC timeline
and a date check. Every story is listed with
its sources in [FACTS.md](FACTS.md); stories that happened on 20 or 21 November were left out.

![entry](entry.png)

## How it is made

- `render.py` draws the page with Pillow and the macOS system fonts (Avenir Next Condensed, Helvetica Neue) at 2x,
  downsamples it and saves a 128-colour PNG (about 160 KB). `python3 render.py` rebuilds `entry.png`.
- `main.ts` checks the PNG against the contest limits and copies it to `/output/entry.png`.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=z1s7h5w8&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
