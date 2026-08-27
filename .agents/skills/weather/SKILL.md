---
name: weather
description: "Use when Codex needs current weather or forecasts with caching, command-line lookup, common-city shortcuts, or fallback between wttr.in and Open-Meteo."
---

# Weather Skill v1.1.0

Fast, reliable weather lookups with caching and automatic fallback between multiple sources.

## Features

- ⚡ **Fast**: Caches results for 30 minutes (instant response for repeated queries)
- 🔄 **Reliable**: Automatic fallback from wttr.in → Open-Meteo
- 📍 **Smart defaults**: Raleigh, NC as default; common cities pre-configured
- 🛠️ **Tool-ready**: Exposes `weather_fetch` tool for direct integration
- 💬 **Slash command**: Can be registered as native Discord/Telegram command

## Usage

### As a Tool

```python
# Fetch weather for default location (Raleigh)
weather_fetch()

# Fetch weather for specific city
weather_fetch(location="San Francisco")
```

### Command Line

```bash
# Default (Raleigh)
python3 weather_fetch.py

# Specific city
python3 weather_fetch.py "New York"

# JSON output
python3 weather_fetch.py "Boston" --json
```

### Discord Slash Command

After installing, the skill can be invoked via:
```
/weather [city]
```

Examples:
- `/weather` — Weather for Raleigh
- `/weather Atlanta` — Weather for Atlanta
- `/weather San Francisco` — Weather for SF

## How It Works

1. **Check cache** — If cached result is < 30 min old, return it instantly
2. **Try wttr.in** — Fast, pretty formatting with emoji
3. **Fallback to Open-Meteo** — Reliable JSON API, no rate limits
4. **Cache result** — Save for next time

## Supported Cities

Pre-configured with coordinates for 50+ major US cities including:
- Raleigh, Durham, Chapel Hill, Charlotte (NC)
- Atlanta, NYC, LA, Chicago, Houston, Phoenix
- Boston, Seattle, Denver, Miami, Austin

**Not in the list?** The skill defaults to Raleigh coordinates. Add more cities to `weather_fetch.py` in the `COORDS` dict.

## Data Sources

| Source | Type | Fallback Order |
|--------|------|----------------|
| wttr.in | Text/Emoji | Primary |
| Open-Meteo | JSON API | Fallback |

## Files

- `skill.yaml` — Skill manifest
- `weather_fetch.py` — Main fetcher with caching
- `weather_fetch.tool.json` — Tool schema
- `SKILL.md` — This documentation

## Cache Location

```
${CODEX_HOME:-$HOME/.codex}/.cache/weather/
├── raleigh.json
├── atlanta.json
└── ...
```

## Version History

- **1.1.0** — Added caching, fallback logic, tool definition, 50+ city coords
- **1.0.0** — Initial documentation-only skill

## License

MIT
