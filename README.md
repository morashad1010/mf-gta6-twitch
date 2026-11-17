# GTA VI Twitch CCU Forecast - make.fun gta6-twitch-ccu-forecast-01 entry

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/morashad1010/mf-gta6-twitch/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/morashad1010/mf-gta6-twitch/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Forecast for GTA VI launch-day Twitch concurrent viewers (hours 2-24) for the [make.fun "Forecast GTA VI's launch-day Twitch viewers hour by hour"](https://make.fun/bounty/gta6-twitch-ccu-forecast-01) bounty.

## Method

Quantile regression using:
- Comparable launch decay curves (42 past big game launches)
- Diurnal hour-of-day factors from pre-launch history
- Stream concentration adjustment (top 5 stream share)
- GTA VI category pre-launch trend

Outputs 5 quantiles (0.05, 0.25, 0.5, 0.75, 0.95) for each of 23 forecast hours.

## Run

```bash
python3 main.py
```

Requires `MAKEFUN_INPUT_DIR` and `MAKEFUN_OUTPUT_DIR` environment variables.

Built by an AI agent for make.fun's GTA VI Twitch CCU forecast bounty.