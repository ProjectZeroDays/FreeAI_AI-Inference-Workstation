#!/usr/bin/env python3
"""
Weather fetcher with caching and automatic fallback.
Fetches weather from wttr.in (primary) with Open-Meteo fallback.
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
from urllib.parse import quote

# Cache settings
CACHE_DIR = Path.home() / ".codex" / ".cache" / "weather"
CACHE_DURATION = 1800  # 30 minutes

def get_cache_path(location):
    """Get cache file path for location."""
    location_slug = location.lower().replace(" ", "_").replace(",", "")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{location_slug}.json"

def get_cached(location):
    """Get cached weather if still fresh."""
    cache_path = get_cache_path(location)
    if not cache_path.exists():
        return None
    
    try:
        base_real = os.path.realpath(CACHE_DIR)
        target_real = os.path.realpath(cache_path)
        if os.path.commonpath([base_real, target_real]) != base_real:
            raise Exception("Invalid file path")
        with open(target_real) as f:
            data = json.load(f)
        
        # Check if cache is still fresh
        if time.time() - data.get("timestamp", 0) < CACHE_DURATION:
            data["source"] = "cache"
            return data
    except (json.JSONDecodeError, KeyError):
        pass
    
    return None

def set_cached(location, data):
    """Cache weather data."""
    cache_path = get_cache_path(location)
    base_real = os.path.realpath(CACHE_DIR)
    target_real = os.path.realpath(cache_path)
    if os.path.commonpath([base_real, target_real]) != base_real:
        raise Exception("Invalid file path")
    data["timestamp"] = time.time()
    with open(target_real, "w") as f:
        json.dump(data, f)

def fetch_wttr_in(location):
    """Fetch from wttr.in using curl with timeout."""
    encoded = quote(location.replace(" ", "+"))
    
    try:
        result = subprocess.run(
            ["curl", "-s", f"https://wttr.in/{encoded}?format=%l:+%c+%t+%h+%w", "--max-time", "5"],
            capture_output=True,
            text=True,
            timeout=6
        )
        text = result.stdout.strip()
        if text and not text.startswith("ERROR") and len(text) > 5:
            return {
                "source": "wttr.in",
                "format": "compact",
                "text": text,
                "location": location
            }
    except (subprocess.TimeoutExpired, Exception):
        pass
    
    return None

def fetch_open_meteo(location):
    """Fetch from Open-Meteo as fallback."""
    # Coordinates lookup for common cities
    COORDS = {
        "raleigh": (35.7796, -78.6382),
        "durham": (36.0014, -78.9382),
        "chapel hill": (35.9132, -79.0558),
        "charlotte": (35.2271, -80.8431),
        "wilmington": (34.2257, -77.9447),
        "asheville": (35.5951, -82.5515),
        "greensboro": (36.0726, -79.7920),
        "winston-salem": (36.0999, -80.2442),
        "cary": (35.7915, -78.7811),
        "new york": (40.7128, -74.0060),
        "los angeles": (34.0522, -118.2437),
        "chicago": (41.8781, -87.6298),
        "houston": (29.7604, -95.3698),
        "phoenix": (33.4484, -112.0740),
        "philadelphia": (39.9526, -75.1652),
        "san antonio": (29.4241, -98.4936),
        "san diego": (32.7157, -117.1611),
        "dallas": (32.7767, -96.7970),
        "san jose": (37.3382, -121.8863),
        "austin": (30.2672, -97.7431),
        "jacksonville": (30.3322, -81.6557),
        "san francisco": (37.7749, -122.4194),
        "columbus": (39.9612, -82.9988),
        "indianapolis": (39.7684, -86.1581),
        "fort worth": (32.7555, -97.3308),
        "seattle": (47.6062, -122.3321),
        "denver": (39.7392, -104.9903),
        "el paso": (31.7619, -106.4850),
        "detroit": (42.3314, -83.0458),
        "washington": (38.9072, -77.0369),
        "dc": (38.9072, -77.0369),
        "boston": (42.3601, -71.0589),
        "memphis": (35.1495, -90.0490),
        "nashville": (36.1627, -86.7816),
        "portland": (45.5152, -122.6784),
        "oklahoma city": (35.4676, -97.5164),
        "las vegas": (36.1699, -115.1398),
        "louisville": (38.2527, -85.7585),
        "baltimore": (39.2904, -76.6122),
        "milwaukee": (43.0389, -87.9065),
        "albuquerque": (35.0844, -106.6504),
        "tucson": (32.2226, -110.9747),
        "atlanta": (33.7490, -84.3880),
        "miami": (25.7617, -80.1918),
        "minneapolis": (44.9778, -93.2650),
        "tulsa": (36.1540, -95.9928),
    }
    
    location_lower = location.lower().strip()
    lat, lon = COORDS.get(location_lower, (35.7796, -78.6382))  # Default to Raleigh
    
    try:
        result = subprocess.run(
            ["curl", "-s", f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto", "--max-time", "5"],
            capture_output=True,
            text=True,
            timeout=6
        )
        data = json.loads(result.stdout)
        temp_c = data["current_weather"]["temperature"]
        wind = data["current_weather"]["windspeed"]
        code = data["current_weather"]["weathercode"]
        
        # WMO weather code to emoji
        EMOJIS = {
            0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
            45: "🌫️", 48: "🌫️", 51: "🌦️", 53: "🌧️", 55: "🌧️",
            61: "🌧️", 63: "🌧️", 65: "🌧️", 71: "🌨️", 73: "🌨️",
            75: "🌨️", 80: "🌦️", 81: "🌧️", 82: "🌧️", 95: "⛈️",
        }
        emoji = EMOJIS.get(code, "🌡️")
        
        # Convert to F
        temp_f = (temp_c * 9/5) + 32
        
        return {
            "source": "open-meteo",
            "format": "compact",
            "text": f"{location.title()}: {emoji} {temp_f:.0f}°F  wind {wind} km/h",
            "location": location,
            "temp_c": temp_c,
            "temp_f": temp_f,
            "wind": wind,
            "code": code
        }
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, Exception):
        return None

def get_weather(location="Raleigh"):
    """Get weather with caching and fallback."""
    # Check cache first
    cached = get_cached(location)
    if cached:
        return cached
    
    # Try wttr.in first
    result = fetch_wttr_in(location)
    
    # Fall back to Open-Meteo
    if not result:
        result = fetch_open_meteo(location)
    
    if result:
        set_cached(location, result)
        return result
    
    return {
        "error": True,
        "text": f"❌ Could not fetch weather for {location}. Please try again later."
    }

if __name__ == "__main__":
    location = sys.argv[1] if len(sys.argv) > 1 else "Raleigh"
    result = get_weather(location)
    
    # Output just the text for human consumption, or full JSON for tool use
    if "--json" in sys.argv:
        print(json.dumps(result))
    else:
        print(result.get("text", result.get("error", "Unknown error")))
