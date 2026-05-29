import requests
import os
import json

WAKATIME_API_KEY = os.environ.get("WAKATIME_API_KEY")

# Fetch summary from WakaTime
headers = {"Authorization": f"Basic {__import__('base64').b64encode(WAKATIME_API_KEY.encode()).decode()}"}

summary = requests.get("https://wakatime.com/api/v1/users/current/summaries?range=all_time", headers=headers).json()
stats = requests.get("https://wakatime.com/api/v1/users/current/stats/all_time?is_including_today=true", headers=headers).json()

data = stats.get("data", {})

# Total time
total_seconds = data.get("total_seconds", 0)
total_hrs  = int(total_seconds // 3600)
total_mins = int((total_seconds % 3600) // 60)
total_str  = f"{total_hrs}h {total_mins}m"

# Daily average
daily_avg  = data.get("daily_average", 0) if data else 0
avg_hrs    = int(daily_avg // 3600)
avg_mins   = int((daily_avg % 3600) // 60)
avg_str    = f"~{avg_hrs}h {avg_mins}m"

# Best day 
best_day_data = data.get("best_day") if data else None

best_day_str = "N/A"
if best_day_data is not None:
    best_day_str = best_day_data.get("date", "N/A")

# Languages (top 5, ordered by seconds)
languages_raw = data.get("languages", [])[:5] if data else []
max_seconds   = languages_raw[0]["total_seconds"] if languages_raw else 1


# Colors per language
COLOR_MAP = {
    "Python":     "#3fb950",
    "HTML":       "#f97583",
    "CSS":        "#a78bfa",
    "JavaScript": "#e3b341",
    "Java":       "#00f5ff",
    "TypeScript": "#00f5ff",
    "C":          "#79c0ff",
    "C++":        "#79c0ff",
    "Kotlin":     "#a78bfa",
    "Rust":       "#f97583",
}
DEFAULT_COLOR = "#8b949e"

BAR_MAX_W = 320  # max bar width in SVG

def make_lang_row(lang, y, delay):
    name     = lang.get("name", "Other")
    secs     = lang.get("total_seconds", 0)
    hrs      = int(secs // 3600)
    mins     = int((secs % 3600) // 60)
    pct      = lang.get("percent", 0)
    bar_w    = max(6, int((secs / max_seconds) * BAR_MAX_W))
    color    = COLOR_MAP.get(name, DEFAULT_COLOR)
    time_str = f"{hrs}h {mins}m"
    pct_str  = f"{pct:.2f}%"

    grad_id  = f"grad-{name.lower().replace('+','p').replace('#','s')}"

    grad = f'''
    <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="{color}"/>
    </linearGradient>'''

    row = f'''
  <g style="opacity:0;animation:fadeup 0.6s ease-out {delay}s both">
    <circle cx="42" cy="{y}" r="4" fill="{color}" style="filter:drop-shadow(0 0 4px {color})"/>
    <text x="58"  y="{y+4}" font-family="Courier New,monospace" font-size="12" fill="#8b949e">{name}</text>
    <text x="148" y="{y+4}" font-family="Courier New,monospace" font-size="12" fill="#e6edf3" font-weight="bold">{time_str}</text>
    <rect x="240" y="{y-6}" width="320" height="10" rx="5" fill="#161b22"/>
    <rect x="240" y="{y-6}" width="{bar_w}" height="10" rx="5" fill="url(#{grad_id})" style="animation:bar-grow 1.2s cubic-bezier(.4,0,.2,1) {delay}s both"/>
    <text x="572" y="{y+4}" font-family="Courier New,monospace" font-size="11" fill="#00f5ff">{pct_str}</text>
  </g>'''
    return grad, row

grads, rows = "", ""
for i, lang in enumerate(languages_raw):
    g, r = make_lang_row(lang, 178 + i * 32, 0.3 + i * 0.15)
    grads += g
    rows  += r

svg_height = 160 + len(languages_raw) * 32 + 20

SVG = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 {svg_height}" width="800" height="{svg_height}">
  <defs>
    <style>
      @keyframes fadeup {{ from{{opacity:0;transform:translateY(6px)}} to{{opacity:1;transform:translateY(0)}} }}
      @keyframes bar-grow {{ from{{width:0}} to{{width:100%}} }}
    </style>
    <linearGradient id="top-line" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"  stop-color="#00f5ff" stop-opacity="0"/>
      <stop offset="50%" stop-color="#00f5ff" stop-opacity="1"/>
      <stop offset="100%" stop-color="#00f5ff" stop-opacity="0"/>
    </linearGradient>
    {grads}
  </defs>

  <rect width="800" height="{svg_height}" rx="12" fill="#0d1117"/>
  <rect x="0" y="0" width="800" height="2" rx="1" fill="url(#top-line)"/>

  <!-- Title -->
  <text x="30" y="35" font-family="Courier New,monospace" font-size="12" fill="#00f5ff" letter-spacing="3"
    style="opacity:0;animation:fadeup 0.6s ease-out 0.1s both">⏱  CODING STATS</text>
  <line x1="30" y1="42" x2="770" y2="42" stroke="#21262d" stroke-width="1"/>

  <!-- Stat boxes -->
  <g style="opacity:0;animation:fadeup 0.6s ease-out 0.1s both">
    <rect x="30"  y="54" width="168" height="64" rx="8" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
    <rect x="30"  y="54" width="168" height="2"  rx="1" fill="#00f5ff" opacity="0.6"/>
    <text x="114" y="90" text-anchor="middle" font-family="Courier New,monospace" font-size="22" font-weight="bold" fill="#00f5ff" style="filter:drop-shadow(0 0 8px #00f5ff66)">{total_str}</text>
    <text x="114" y="107" text-anchor="middle" font-family="Courier New,monospace" font-size="9" fill="#8b949e" letter-spacing="2">TOTAL TIME CODED</text>
  </g>
  <g style="opacity:0;animation:fadeup 0.6s ease-out 0.3s both">
    <rect x="214" y="54" width="168" height="64" rx="8" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
    <rect x="214" y="54" width="168" height="2"  rx="1" fill="#3fb950" opacity="0.6"/>
    <text x="298" y="90" text-anchor="middle" font-family="Courier New,monospace" font-size="22" font-weight="bold" fill="#3fb950" style="filter:drop-shadow(0 0 8px #3fb95066)">{avg_str}</text>
    <text x="298" y="107" text-anchor="middle" font-family="Courier New,monospace" font-size="9" fill="#8b949e" letter-spacing="2">DAILY AVERAGE</text>
  </g>
  <g style="opacity:0;animation:fadeup 0.6s ease-out 0.5s both">
    <rect x="398" y="54" width="168" height="64" rx="8" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
    <rect x="398" y="54" width="168" height="2"  rx="1" fill="#e3b341" opacity="0.6"/>
    <text x="482" y="90" text-anchor="middle" font-family="Courier New,monospace" font-size="22" font-weight="bold" fill="#e3b341" style="filter:drop-shadow(0 0 8px #e3b34166)">{best_day_str}</text>
    <text x="482" y="107" text-anchor="middle" font-family="Courier New,monospace" font-size="9" fill="#8b949e" letter-spacing="2">BEST DAY</text>
  </g>
  <g style="opacity:0;animation:fadeup 0.6s ease-out 0.7s both">
    <rect x="582" y="54" width="188" height="64" rx="8" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
    <rect x="582" y="54" width="188" height="2"  rx="1" fill="#a78bfa" opacity="0.6"/>
    <text x="676" y="90" text-anchor="middle" font-family="Courier New,monospace" font-size="22" font-weight="bold" fill="#a78bfa" style="filter:drop-shadow(0 0 8px #a78bfa66)">{data.get("human_readable_range", "7 days")}</text>
    <text x="676" y="107" text-anchor="middle" font-family="Courier New,monospace" font-size="9" fill="#8b949e" letter-spacing="2">RANGE</text>
  </g>

  <line x1="30" y1="136" x2="770" y2="136" stroke="#21262d" stroke-width="1"/>
  <text x="30" y="157" font-family="Courier New,monospace" font-size="10" fill="#00f5ff" letter-spacing="3"
    style="opacity:0;animation:fadeup 0.6s ease-out 0.2s both">LANGUAGES</text>

  {rows}
</svg>'''

with open("wakatime-stats.svg", "w") as f:
    f.write(SVG)

print("✅ wakatime-stats.svg generated successfully!")
