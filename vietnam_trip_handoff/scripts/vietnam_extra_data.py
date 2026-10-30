"""
Vietnam honeymoon (22-28 Jan 2027) - EXTRA DATA, one run.

What it collects (each part can be switched on/off in SETTINGS):
  1. WEATHER  - 12 years of 22-28 January (2015-2026) at Hoi An, Hue, Da Nang beach,
                Ba Na Hills and Hai Van Pass, plus sea wave height.        FREE (Open-Meteo, no account)
  2. BOOKING  - Booking.com prices for YOUR dates + room types (finds ocean-view rooms)
                for the shortlisted hotels, and a wider "Da Nang central" search.  Apify, ~$0.3-0.6
  3. BOOKING REVIEWS - newest Booking.com reviews of the shortlisted hotels
                (traveller type, room type, liked/disliked).                Apify, ~$0.3-0.8
  4. GETYOURGUIDE - reviews of the exact tours you may book (cooking class, My Son sunrise,
                Ba Na Hills, Han River cruise, Hue food tour, Hai Van private car).  Apify, ~$1.0-1.5
  5. X / TWITTER - recent English posts about Hoi An, Da Nang, Hue, Ba Na, Hai Van,
                Vietnam honeymoon, Vietnam from India.                       Apify, ~$0.1-0.3
  6. YOUTUBE TRANSCRIPTS - auto-captions (English, or auto-translated to English) for the
                ~120 most relevant videos from your earlier youtube_videos.csv.  FREE (slow, paced)

Setup (one time):
    pip install -U apify-client yt-dlp

Run (VS Code terminal, in the folder that has youtube_videos.csv):
    python vietnam_extra_data.py

It asks for the Apify token (hidden) only if an Apify part is switched on, shows the
maximum it may spend, and waits for "y" before spending anything.

Safe to re-run: every finished piece is cached in extra_cache/ and skipped next time.
If YouTube starts blocking, the script stops that part politely; re-run later
(or from a phone hotspot) and it continues where it left off.

Output files (in this folder):
  weather_daily.csv, weather_summary.csv, weather_summary.txt
  booking_hotels.csv, booking_rooms.csv, booking_reviews.csv
  gyg_reviews.csv
  x_posts.csv
  youtube_transcripts_v2.csv
  extra_data_log.txt   (everything printed on screen)
"""

import csv
import datetime as dt
import getpass
import json
import os
import random
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# =============================== SETTINGS ===============================
RUN_WEATHER = True
RUN_BOOKING = True
RUN_BOOKING_REVIEWS = True
RUN_GYG = True
RUN_X = True
RUN_YOUTUBE = True

CACHE = "extra_cache"

# ---- 1. Weather ----
YEARS = list(range(2015, 2027))          # 2015 ... 2026  (12 Januaries)
DAY_FROM, DAY_TO = 22, 28                # 22-28 January
TZ = "Asia/Ho_Chi_Minh"
WEATHER_POINTS = {
    # name: (lat, lng, elevation_m or None)
    "Hoi An":         (15.8801, 108.3380, None),
    "Hue":            (16.4637, 107.5909, None),
    "Da Nang beach":  (15.9767, 108.2810, None),   # Non Nuoc / Naman Retreat stretch
    "Ba Na Hills":    (15.9977, 107.9881, 1400),   # summit area, ~1,400-1,487 m
    "Hai Van Pass":   (16.1925, 108.1300, 496),
}
SEA_POINTS = {
    # offshore points for wave height (the script nudges further out if a point has no sea data)
    "Da Nang beach sea": (15.98, 108.31),
    "Hoi An beach sea":  (15.90, 108.38),
}

# ---- 2/3. Booking.com ----
BOOKING_ACTOR = "voyager/booking-scraper"
BOOKING_REVIEWS_ACTOR = "voyager/booking-reviews-scraper"
CURRENCY = "INR"
ADULTS = 2
# (stay block, check-in, check-out, [hotel names to look up])
STAY_BLOCKS = [
    ("Hoi An",           "2027-01-22", "2027-01-24", [
        "La Siesta Hoi An Resort & Spa",
        "Little Hoi An Boutique Hotel & Spa",
        "Cozy An Boutique Hotel Hoi An",
        "Moire Hoi An",
    ]),
    ("Hue",              "2027-01-24", "2027-01-26", [
        "Pilgrimage Village Hue",
        "Azerai La Residence Hue",
        "Melia Vinpearl Hue",
    ]),
    ("Da Nang beach-view (1 night)", "2027-01-27", "2027-01-28", [
        "Naman Retreat Da Nang",
        "Fusion Resort & Villas Da Nang",
        "Pullman Danang Beach Resort",
        "Furama Resort Danang",
        "TMS Hotel Da Nang Beach",
        "Chicland Hotel Danang Beach",
    ]),
]
# wider search for the cheaper central/An Thuong night (Tue 26 Jan)
CITY_SEARCHES = [
    ("Da Nang central (1 night)", "Da Nang", "2027-01-26", "2027-01-27", 80, "8.5"),
]
BOOKING_REVIEWS_PER_HOTEL = 40
BOOKING_REVIEWS_SINCE = "2025-01-01"
SEA_VIEW_WORDS = r"ocean|sea ?view|sea-view|seaview|beach ?front|beachfront|bay view|beach view|partial sea|panoramic sea"

# ---- 4. GetYourGuide reviews ----
GYG_ACTOR = "automation-lab/getyourguide-reviews-scraper"
GYG_REVIEWS_PER_TOUR = 15
GYG_REVIEWS_SINCE = "2024-06-01"
GYG_TOURS = {
    "Cooking class + basket boat": [
        "https://www.getyourguide.com/hoi-an-l831/hoi-an-basket-boat-with-lantern-making-cooking-class-tour-t540267/",
        "https://www.getyourguide.com/hoi-an-l831/hoi-anvisit-local-marketbasket-boat-ride-and-cooking-class-t133461/",
        "https://www.getyourguide.com/hoi-an-l831/hoiandanang-eco-cooking-class-cruise-trip-basket-boat-t218388/",
        "https://www.getyourguide.com/hoi-an-l831/hoi-an-cooking-class-market-visit-coconut-basket-boat-t135501/",
        "https://www.getyourguide.com/hoi-an-l831/hoi-an-bay-mau-cooking-class-w-market-basket-boat-trip-t486228/",
    ],
    "My Son sunrise": [
        "https://www.getyourguide.com/hoi-an-l831/hoi-an-my-son-sanctuary-sunrise-tour-t724941/",
        "https://www.getyourguide.com/hoi-an-l831/sunrise-tour-to-my-son-sanctuary-from-hoi-an-t131565/",
        "https://www.getyourguide.com/hoi-an-l831/4-hour-my-son-valley-sunrise-tour-t125945/",
    ],
    "Ba Na Hills": [
        "https://www.getyourguide.com/da-nang-l939/ba-na-hills-golden-bridge-small-group-tour-t466388/",
        "https://www.getyourguide.com/da-nang-l939/from-da-nang-ba-na-hills-and-golden-bridge-tour-options-t469551/",
        "https://www.getyourguide.com/da-nang-l939/from-da-nang-or-hoi-an-ba-na-hills-golden-bridge-tour-t532798/",
    ],
    "Han River cruise": [
        "https://www.getyourguide.com/da-nang-l939/da-nang-han-river-cruise-and-champa-dance-t469912/",
        "https://www.getyourguide.com/da-nang-l939/da-nang-poseidon-cruise-with-dinner-and-dragon-bridge-show-t887190/",
        "https://www.getyourguide.com/da-nang-l939/da-nang-han-river-dinner-cruise-with-tien-sa-show-t1061177/",
        "https://www.getyourguide.com/da-nang-l939/da-nang-by-night-han-river-dragon-cruise-with-a-local-food-t686658/",
    ],
    "Hue food tour": [
        "https://www.getyourguide.com/hue-vietnam-l833/hue-street-walking-food-tour-t572715/",
        "https://www.getyourguide.com/hue-vietnam-l833/hue-night-street-food-safari-by-cyclo-t444748/",
        "https://www.getyourguide.com/hue-vietnam-l833/hue-food-tour-by-walking-or-cyclo-or-motorbike-with-driver-t543404/",
    ],
    "Hoi An -> Hue private car via Hai Van": [
        "https://www.getyourguide.com/da-nang-l939/hoi-an-transfer-tofrom-hue-by-private-car-via-hai-van-pass-t540183/",
        "https://www.getyourguide.com/da-nang-l939/hoi-an-private-car-to-hue-with-sightseeing-stops-t892424/",
        "https://www.getyourguide.com/hoi-an-l831/hoi-an-to-hue-by-private-car-with-sightseeing-stops-t489402/",
    ],
}

# ---- 5. X / Twitter ----
X_ACTOR = "xquik/x-tweet-scraper"
X_SINCE = "2024-06-01"
X_MAX_ITEMS = 800
X_SEARCHES = [
    '"Hoi An" -filter:retweets',
    '"Da Nang" (trip OR travel OR beach OR hotel OR food) -filter:retweets',
    '("Ba Na Hills" OR "Golden Bridge" OR "Bana Hills") -filter:retweets',
    'Hue Vietnam (citadel OR imperial OR food OR trip) -filter:retweets',
    '"Hai Van Pass" -filter:retweets',
    'Vietnam honeymoon -filter:retweets',
    'Vietnam (trip OR travel OR visa) (India OR Indian OR Indians) -filter:retweets',
    '"Da Nang" (January OR Jan) (weather OR rain OR beach OR cold) -filter:retweets',
]

# ---- Spend caps (USD, per Apify run; Apify's minimum cap is $0.50) ----
CAP_BOOKING_PER_RUN = 0.5
CAP_BOOKING_REVIEWS = 1.0
CAP_GYG = 2.0
CAP_X = 0.5

# ---- 6. YouTube ----
YT_VIDEOS_CSV = "youtube_videos.csv"   # from the earlier YouTube run
YT_MAX_VIDEOS = 120
YT_SLEEP = (6, 12)                     # seconds between videos (keeps YouTube happy)
YT_COOKIES_FILE = ""                   # optional: path to a cookies.txt export if YouTube keeps blocking
YT_RELEVANT = (r"hoi ?an|da ?nang|danang|\bhue\b|ba ?na|bana|golden bridge|hai ?van|marble|my son|son tra|"
               r"lady buddha|an thuong|central vietnam|honeymoon|india|indian|tamil|chennai|kochi|budget|"
               r"cost|january|scam|street food|food tour|cooking|lantern|vietnam (travel|trip|itinerary|guide)")
YT_SKIP = r"sapa|sa pa|ha giang|phu quoc|mekong|cat ba|ninh binh|dalat|da lat|mui ne|saigon|ho chi minh|hcmc|nha trang|halong|ha long"
# ======================================================================


# ---------------------------------------------------------------- utils
class Tee:
    def __init__(self, path):
        self.f = open(path, "a", encoding="utf-8", buffering=1)
        self.out = sys.stdout

    def write(self, s):
        self.out.write(s)
        self.f.write(s)

    def flush(self):
        self.out.flush()
        self.f.flush()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:80]


def cache_get(key):
    p = os.path.join(CACHE, key + ".json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None


def cache_put(key, value):
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, key + ".json"), "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False)


def flatten(d, prefix=""):
    """Turn nested Apify items into flat CSV-friendly dicts."""
    out = {}
    for k, v in (d or {}).items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flatten(v, key + "."))
        elif isinstance(v, list):
            if all(not isinstance(x, (dict, list)) for x in v):
                out[key] = "; ".join(str(x) for x in v)
            else:
                out[key] = json.dumps(v, ensure_ascii=False)
        else:
            out[key] = v
    return out


def write_csv(name, rows, first_cols=()):
    if not rows:
        print(f"   (nothing to write for {name})")
        return
    keys = [c for c in first_cols if any(c in r for r in rows)]
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(name, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"   saved {len(rows):6} rows -> {name}")


def http_json(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "vietnam-trip-research/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            try:
                return json.loads(body)          # Open-Meteo returns {"error": true, "reason": ...}
            except Exception:
                last = f"HTTP {e.code}: {body[:200]}"
        except Exception as e:
            last = str(e)
        time.sleep(2 * (i + 1))
    return {"error": True, "reason": last}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 2) if xs else None


def pct(flags):
    flags = [f for f in flags if f is not None]
    return round(100 * sum(1 for f in flags if f) / len(flags), 1) if flags else None


# ---------------------------------------------------------- 1. WEATHER
ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
MARINE = "https://marine-api.open-meteo.com/v1/marine"
HOURLY = "temperature_2m,relative_humidity_2m,precipitation,cloud_cover,cloud_cover_low,wind_speed_10m,wind_gusts_10m"
DAILY = "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_hours,sunshine_duration,wind_speed_10m_max"


def fetch_land(name, lat, lng, elev, year):
    key = f"wx_{slug(name)}_{year}"
    data = cache_get(key)
    if data is None:
        q = {"latitude": lat, "longitude": lng,
             "start_date": f"{year}-01-{DAY_FROM:02d}", "end_date": f"{year}-01-{DAY_TO:02d}",
             "hourly": HOURLY, "daily": DAILY, "timezone": TZ}
        if elev:
            q["elevation"] = elev
        data = http_json(ARCHIVE + "?" + urllib.parse.urlencode(q))
        if data.get("error"):
            print(f"   !! {name} {year}: {data.get('reason')}")
            return []
        cache_put(key, data)
        time.sleep(0.3)
    H, D = data.get("hourly", {}), data.get("daily", {})
    rows = []
    for i, day in enumerate(D.get("time", [])):
        idx = [j for j, t in enumerate(H.get("time", [])) if t.startswith(day)]
        morning = [j for j in idx if 7 <= int(H["time"][j][11:13]) <= 11]          # 07:00-11:59
        daytime = [j for j in idx if 8 <= int(H["time"][j][11:13]) <= 17]

        def hv(var, js):
            col = H.get(var) or []
            return [col[j] if j < len(col) else None for j in js]

        r = {
            "point": name, "year": year, "date": day, "day": int(day[8:10]),
            "tmax_c": D["temperature_2m_max"][i], "tmin_c": D["temperature_2m_min"][i],
            "rain_mm": D["precipitation_sum"][i], "rain_hours": D["precipitation_hours"][i],
            "sunshine_h": round((D["sunshine_duration"][i] or 0) / 3600, 1),
            "wind_max_kmh": D["wind_speed_10m_max"][i],
            "morning_low_cloud_pct": mean(hv("cloud_cover_low", morning)),
            "morning_total_cloud_pct": mean(hv("cloud_cover", morning)),
            "morning_rh_pct": mean(hv("relative_humidity_2m", morning)),
            "morning_rain_mm": round(sum(x or 0 for x in hv("precipitation", morning)), 1),
            "daytime_rain_mm": round(sum(x or 0 for x in hv("precipitation", daytime)), 1),
            "daytime_gust_max_kmh": max([x for x in hv("wind_gusts_10m", daytime) if x is not None], default=None),
        }
        rain = r["rain_mm"] or 0
        r["rain_day"] = rain >= 1.0
        r["washout"] = rain >= 10 or (r["rain_hours"] or 0) >= 8
        r["good_day"] = rain < 1.0 and r["sunshine_h"] >= 5
        # Ba Na fog proxy: thick low cloud or saturated air or rain in the morning (see notes)
        r["clouded_morning"] = ((r["morning_low_cloud_pct"] or 0) >= 80
                                or ((r["morning_rh_pct"] or 0) >= 95 and (r["morning_total_cloud_pct"] or 0) >= 80)
                                or r["morning_rain_mm"] >= 1.0)
        rows.append(r)
    return rows


def fetch_sea(name, lat, lng, year):
    key = f"sea_{slug(name)}_{year}"
    data = cache_get(key)
    if data is None:
        base = {"start_date": f"{year}-01-{DAY_FROM:02d}", "end_date": f"{year}-01-{DAY_TO:02d}",
                "daily": "wave_height_max,wave_period_max,wave_direction_dominant",
                "hourly": "wave_height", "timezone": TZ}
        data, why = None, ""
        for step in range(4):                     # nudge offshore if the cell is land
            for extra in ({}, {"models": "era5_ocean"}):
                q = dict(base, latitude=lat, longitude=round(lng + 0.08 * step, 3), **extra)
                d = http_json(MARINE + "?" + urllib.parse.urlencode(q))
                if not d.get("error") and any(v is not None for v in d.get("daily", {}).get("wave_height_max", [])):
                    data = d
                    break
                why = d.get("reason") or "no sea data at this point"
            if data:
                break
        if not data:
            print(f"   !! sea {name} {year}: {why}")
            return []
        cache_put(key, data)
        time.sleep(0.3)
    D = data["daily"]
    rows = []
    for i, day in enumerate(D.get("time", [])):
        wh = D["wave_height_max"][i]
        rows.append({"point": name, "year": year, "date": day, "day": int(day[8:10]),
                     "wave_height_max_m": wh, "wave_period_max_s": D.get("wave_period_max", [None] * 99)[i],
                     "wave_dir_deg": D.get("wave_direction_dominant", [None] * 99)[i],
                     "rough_over_1_5m": None if wh is None else wh > 1.5,
                     "calm_under_1m": None if wh is None else wh < 1.0})
    return rows


def run_weather():
    print("\n=== 1/6 WEATHER: 22-28 Jan, " + f"{YEARS[0]}-{YEARS[-1]} ===")
    land, sea = [], []
    for name, (lat, lng, elev) in WEATHER_POINTS.items():
        for y in YEARS:
            land += fetch_land(name, lat, lng, elev, y)
        print(f"   {name}: {sum(1 for r in land if r['point'] == name)} days")
    for name, (lat, lng) in SEA_POINTS.items():
        for y in YEARS:
            sea += fetch_sea(name, lat, lng, y)
        print(f"   {name}: {sum(1 for r in sea if r['point'] == name)} days")

    write_csv("weather_daily.csv", land + sea, first_cols=("point", "year", "date"))

    summary, lines = [], []
    lines.append(f"WEATHER 22-28 JANUARY, {YEARS[0]}-{YEARS[-1]} ({len(YEARS)} years x 7 days per place)")
    lines.append("Source: Open-Meteo historical reanalysis (ERA5 family, ~9-25 km grid). Treat as typical odds, not a forecast.\n")
    for name in WEATHER_POINTS:
        rs = [r for r in land if r["point"] == name]
        if not rs:
            continue
        s = {"point": name, "days": len(rs),
             "avg_max_c": mean([r["tmax_c"] for r in rs]), "avg_min_c": mean([r["tmin_c"] for r in rs]),
             "avg_rain_mm_per_day": mean([r["rain_mm"] for r in rs]),
             "pct_rain_days": pct([r["rain_day"] for r in rs]),
             "pct_washout_days": pct([r["washout"] for r in rs]),
             "pct_good_days": pct([r["good_day"] for r in rs]),
             "avg_sunshine_h": mean([r["sunshine_h"] for r in rs]),
             "pct_clouded_mornings": pct([r["clouded_morning"] for r in rs]),
             "avg_morning_low_cloud_pct": mean([r["morning_low_cloud_pct"] for r in rs])}
        summary.append(s)
        lines.append(f"{name}: max {s['avg_max_c']} C / min {s['avg_min_c']} C | rain on {s['pct_rain_days']}% of days, "
                     f"washouts {s['pct_washout_days']}%, good sunny days {s['pct_good_days']}% | "
                     f"sunshine {s['avg_sunshine_h']} h/day | clouded-in mornings {s['pct_clouded_mornings']}%")

    # --- plan-specific odds ---
    def by_year(point, days):
        out = {}
        for r in land:
            if r["point"] == point and r["day"] in days:
                out.setdefault(r["year"], {})[r["day"]] = r
        return {y: v for y, v in out.items() if all(d in v for d in days)}

    lines.append("\nPLAN-SPECIFIC ODDS")
    hue = by_year("Hue", (24, 25))
    if hue:
        one = pct([v[24]["washout"] or v[25]["washout"] for v in hue.values()])
        both = pct([v[24]["washout"] and v[25]["washout"] for v in hue.values()])
        lines.append(f"Hue 24-25 Jan: at least one washout day in {one}% of years; both days washed out in {both}% of years.")
        lines.append("   -> Keep the indoor Imperial City halls + Royal Antiquities museum as the swap for whichever day the forecast shows wetter.")
    bana = by_year("Ba Na Hills", (26, 27))
    if bana:
        p27 = pct([v[27]["clouded_morning"] for v in bana.values()])
        both = pct([v[26]["clouded_morning"] and v[27]["clouded_morning"] for v in bana.values()])
        clear_any = pct([not (v[26]["clouded_morning"] and v[27]["clouded_morning"]) for v in bana.values()])
        lines.append(f"Ba Na Hills mornings: clouded-in on 27 Jan in {p27}% of years; clear on at least one of 26/27 Jan in {clear_any}% "
                     f"of years (both clouded {both}%).")
        lines.append("   -> Coasters close in rain/fog/cloud. Decide the evening before from the forecast; the 72-hour cable-car ticket gives a second try.")
        trans = [v[27]["clouded_morning"] for v in bana.values() if v[26]["clouded_morning"]]
        if trans:
            lines.append(f"   If 26 Jan morning was clouded, 27 Jan was ALSO clouded in {pct(trans)}% of those years (persistence).")
    sea_s = []
    for name in SEA_POINTS:
        rs = [r for r in sea if r["point"] == name and r["wave_height_max_m"] is not None]
        if not rs:
            continue
        s = {"point": name, "days": len(rs),
             "median_wave_max_m": round(statistics.median([r["wave_height_max_m"] for r in rs]), 2),
             "pct_rough_over_1_5m": pct([r["rough_over_1_5m"] for r in rs]),
             "pct_calm_under_1m": pct([r["calm_under_1m"] for r in rs])}
        sea_s.append(s)
        lines.append(f"{name}: median daily max wave {s['median_wave_max_m']} m | over 1.5 m on {s['pct_rough_over_1_5m']}% of days | "
                     f"under 1 m on {s['pct_calm_under_1m']}% of days.")
    if sea_s:
        lines.append("   -> Over ~1.5 m with a steady onshore swell = red-flag/no-swim on most beaches; under 1 m = usually swimmable.")
    lines.append("\nNOTES: 'clouded-in morning' = 07-12h low cloud >= 80%, or humidity >= 95% with cloud >= 80%, or >= 1 mm rain. "
                 "The grid smooths mountains, so Ba Na figures are a relative guide, not a fog count. "
                 "'washout' = >= 10 mm rain or >= 8 rainy hours. 'good day' = < 1 mm rain and >= 5 h sun.")
    write_csv("weather_summary.csv", summary + sea_s, first_cols=("point",))
    with open("weather_summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n" + "\n".join(lines))
    print("   saved -> weather_summary.txt")


# ------------------------------------------------------------ APIFY
def apify_client():
    try:
        from apify_client import ApifyClient
    except ImportError:
        sys.exit("Run first:  pip install -U apify-client")
    token = os.environ.get("APIFY_TOKEN") or getpass.getpass("Paste your Apify API token (hidden, just paste + Enter): ").strip()
    return ApifyClient(token)


def run_info(run):
    """apify-client v1/v2 return a dict, v3 returns an object - handle both."""
    if run is None:
        return "no run", None
    if isinstance(run, dict):
        return run.get("status"), run.get("defaultDatasetId")
    status = getattr(run, "status", None)
    status = getattr(status, "value", status)
    ds = getattr(run, "default_dataset_id", None) or getattr(run, "defaultDatasetId", None)
    return str(status), ds


def dataset_items(client, ds):
    if not ds:
        return []
    d = client.dataset(ds)
    try:
        return [dict(x) for x in d.iterate_items()]
    except AttributeError:
        return list(d.list_items().items)


def apify_run(client, key, actor, run_input, cap_usd):
    """Run an actor once; cache its items. Reads the dataset even if the run hit the spend cap."""
    cached = cache_get(key)
    if cached is not None:
        print(f"   cached: {key} ({len(cached)} items)")
        return cached
    print(f"   running {actor}  [{key}]  (cap ${max(0.5, cap_usd):.2f}) ...")
    act = client.actor(actor)
    try:
        try:
            run = act.call(run_input=run_input, max_total_charge_usd=max(0.5, cap_usd))
        except TypeError:   # older apify-client without the cap argument
            run = act.call(run_input=run_input)
    except Exception as e:
        print(f"   !! {actor} failed to start: {str(e)[:300]}")
        return []
    status, ds = run_info(run)
    items = dataset_items(client, ds)
    if "SUCCEEDED" not in str(status):
        print(f"   !! run status {status} - keeping the {len(items)} items it produced")
    if items or "SUCCEEDED" in str(status):
        cache_put(key, items)
    print(f"   -> {len(items)} items")
    return items


def norm(s):
    return re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower().replace("&", " and ")).split()


STOP = set("hotel resort spa and the da nang danang hoi an hue beach boutique villas villa vietnam".split())


def name_match(wanted, got):
    w = [t for t in norm(wanted) if t not in STOP] or norm(wanted)
    g = set(norm(got))
    return sum(1 for t in w if t in g) >= max(1, (len(w) + 1) // 2)


# ---------------------------------------------------------- 2. BOOKING
def run_booking(client):
    print("\n=== 2/6 BOOKING.COM prices for your dates ===")
    hotels, rooms, matched = [], [], []

    def collect(block, cin, cout, items, wanted=None):
        nights = (dt.date.fromisoformat(cout) - dt.date.fromisoformat(cin)).days
        picked = items
        if wanted:
            picked = [it for it in items if name_match(wanted, it.get("name"))][:1]
            if not picked:
                print(f"   ?? no Booking match for '{wanted}' (got: {[it.get('name') for it in items][:3]})")
                hotels.append({"block": block, "wanted": wanted, "name": "NOT FOUND", "check_in": cin, "check_out": cout})
                return
        for it in picked:
            rs = it.get("rooms") or []
            sea = [r for r in rs if re.search(SEA_VIEW_WORDS, f"{r.get('roomType', '')} {r.get('features', '')}", re.I)]
            avail = [r for r in rs if r.get("available", True) and isinstance(r.get("price"), (int, float))]
            sea_av = [r for r in sea if r in avail]
            row = {"block": block, "wanted": wanted or "", "name": it.get("name"), "check_in": cin, "check_out": cout,
                   "nights": nights, "booking_rating": it.get("rating"), "booking_reviews": it.get("reviews"),
                   "stars": it.get("stars"), "listed_price": it.get("price"), "currency": it.get("currency"),
                   "cheapest_room_price": min([r["price"] for r in avail], default=None),
                   "cheapest_sea_view_price": min([r["price"] for r in sea_av], default=None),
                   "sea_view_room_types": "; ".join(sorted({str(r.get("roomType")) for r in sea})),
                   "address": (it.get("address") or {}).get("full") if isinstance(it.get("address"), dict) else it.get("address"),
                   "url": it.get("url")}
            row.update({"raw." + k: v for k, v in flatten(it).items() if k not in ("rooms",) and not k.startswith("rooms")})
            hotels.append(row)
            if wanted:
                matched.append({"block": block, "name": it.get("name"), "url": it.get("url")})
            for r in rs:
                rooms.append({"block": block, "hotel": it.get("name"), "check_in": cin, "check_out": cout,
                              "room_type": r.get("roomType"), "bed": r.get("bedType"), "persons": r.get("persons"),
                              "price_as_listed": r.get("price"), "currency": r.get("currency"), "available": r.get("available"),
                              "sea_view": bool(re.search(SEA_VIEW_WORDS, f"{r.get('roomType', '')} {r.get('features', '')}", re.I)),
                              "features": "; ".join(map(str, r.get("features") or [])) if isinstance(r.get("features"), list) else r.get("features")})

    base = {"currency": CURRENCY, "adults": ADULTS, "children": 0, "rooms": 1,
            "minMaxPrice": "0-999999", "extractAdditionalHotelData": True}
    for block, cin, cout, names in STAY_BLOCKS:
        for nm in names:
            items = apify_run(client, f"booking_{slug(nm)}_{cin}", BOOKING_ACTOR,
                              dict(base, search=nm, checkIn=cin, checkOut=cout, maxItems=3), CAP_BOOKING_PER_RUN)
            collect(block, cin, cout, items, wanted=nm)
    for block, city, cin, cout, n, min_score in CITY_SEARCHES:
        items = apify_run(client, f"booking_city_{slug(city)}_{cin}", BOOKING_ACTOR,
                          dict(base, search=city, checkIn=cin, checkOut=cout, maxItems=n, minScore=min_score), CAP_BOOKING_PER_RUN)
        collect(block, cin, cout, items)

    write_csv("booking_hotels.csv", hotels, first_cols=("block", "wanted", "name", "check_in", "check_out", "nights",
                                                         "cheapest_room_price", "cheapest_sea_view_price", "currency",
                                                         "booking_rating", "booking_reviews", "sea_view_room_types", "url"))
    write_csv("booking_rooms.csv", rooms)
    print("\n   Shortlist prices (as listed for the whole stay, in " + CURRENCY + "):")
    for h in hotels:
        if h.get("wanted"):
            print(f"   - {h['block']:<30} {str(h['name'])[:38]:<38} cheapest {h.get('cheapest_room_price')}  "
                  f"sea-view {h.get('cheapest_sea_view_price')}")
    return matched


# --------------------------------------------------- 3. BOOKING REVIEWS
def run_booking_reviews(client, matched):
    print("\n=== 3/6 BOOKING.COM reviews of the shortlist ===")
    urls = [{"url": m["url"].split("?")[0], "userData": {"block": m["block"], "hotel": m["name"]}}
            for m in matched if m.get("url")]
    if not urls:
        print("   (no matched hotel URLs - run the BOOKING part first)")
        return
    items = apify_run(client, "booking_reviews_" + str(len(urls)), BOOKING_REVIEWS_ACTOR,
                      {"startUrls": urls, "maxReviewsPerHotel": BOOKING_REVIEWS_PER_HOTEL,
                       "sortReviewsBy": "f_recent_desc", "cutoffDate": BOOKING_REVIEWS_SINCE, "reviewScores": ["ALL"]},
                      CAP_BOOKING_REVIEWS)
    write_csv("booking_reviews.csv", [flatten(i) for i in items],
              first_cols=("customData.block", "customData.hotel", "rating", "travelerType", "roomInfo",
                          "stayDate", "reviewTitle", "likedText", "dislikedText"))


# ------------------------------------------------------ 4. GETYOURGUIDE
def run_gyg(client):
    print("\n=== 4/6 GETYOURGUIDE reviews of the tours ===")
    cat_of = {}
    urls = []
    for cat, lst in GYG_TOURS.items():
        for u in lst:
            u = u.split("?")[0]
            cat_of[re.search(r"-t(\d+)/?$", u).group(1)] = cat
            urls.append({"url": u})
    items = apify_run(client, f"gyg_{len(urls)}_{GYG_REVIEWS_PER_TOUR}", GYG_ACTOR,
                      {"startUrls": urls, "maxReviewsPerUrl": GYG_REVIEWS_PER_TOUR,
                       "maxItems": GYG_REVIEWS_PER_TOUR * len(urls), "cutoffDate": GYG_REVIEWS_SINCE,
                       "language": "en-US", "allowEmptyResults": True}, CAP_GYG)
    rows = []
    for it in items:
        r = flatten(it)
        tid = str(r.get("activityId") or "")
        if not tid:
            m = re.search(r"-t(\d+)", str(r.get("activityUrl", "")))
            tid = m.group(1) if m else ""
        r["tour_category"] = cat_of.get(tid, "")
        rows.append(r)
    write_csv("gyg_reviews.csv", rows, first_cols=("tour_category", "activityUrl", "rating", "reviewDate",
                                                   "travelerType", "reviewerCountry", "reviewText"))


# ------------------------------------------------------------- 5. X
def run_x(client):
    print("\n=== 5/6 X / TWITTER posts ===")
    items = apify_run(client, f"x_{len(X_SEARCHES)}_{X_MAX_ITEMS}_{X_SINCE}", X_ACTOR,
                      {"searchTerms": X_SEARCHES, "maxItems": X_MAX_ITEMS, "queryType": "Top",
                       "since": X_SINCE, "lang": "en"}, CAP_X)
    rows = []
    for it in items:
        a = it.get("author") or {}
        rows.append({"created": it.get("createdAt"), "likes": it.get("likeCount"), "reposts": it.get("retweetCount"),
                     "replies": it.get("replyCount"), "author": a.get("userName") or a.get("username") or it.get("authorUsername"),
                     "followers": a.get("followers") or it.get("authorFollowers"),
                     "text": (it.get("text") or "").replace("\n", " "), "url": it.get("url"),
                     "search": it.get("searchTerm") or it.get("query") or ""})
    rows.sort(key=lambda r: -(r["likes"] or 0))
    write_csv("x_posts.csv", rows)


# ------------------------------------------------------ 6. YOUTUBE
def pick_videos():
    path = YT_VIDEOS_CSV
    if not os.path.exists(path):
        alt = input(f"   Can't find {YT_VIDEOS_CSV} here. Paste its full path (or Enter to skip YouTube): ").strip().strip('"')
        if not alt or not os.path.exists(alt):
            return []
        path = alt
    with open(path, encoding="utf-8-sig") as f:
        vids = list(csv.DictReader(f))
    scored = []
    for v in vids:
        title = f"{v.get('title', '')} {v.get('description', '')[:300]}".lower()
        t = (v.get("title") or "").lower()
        if re.search(YT_SKIP, t) and not re.search(r"hoi ?an|da ?nang|danang|\bhue\b|ba ?na|hai ?van", t):
            continue
        hits = len(re.findall(YT_RELEVANT, title))
        if not hits:
            continue
        try:
            pop = float(v.get("views") or 0) ** 0.25 + float(v.get("comment_count") or 0) ** 0.5
        except ValueError:
            pop = 0
        scored.append((hits * 10 + pop, v))
    scored.sort(key=lambda x: -x[0])
    return [v for _, v in scored[:YT_MAX_VIDEOS]]


def parse_json3(raw):
    data = json.loads(raw)
    parts = []
    for ev in data.get("events", []):
        for s in ev.get("segs", []) or []:
            t = s.get("utf8", "")
            if t and t != "\n":
                parts.append(t)
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def parse_vtt(raw):
    out, last = [], ""
    for line in raw.splitlines():
        if "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:")) or not line.strip():
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line and line != last:
            out.append(line)
            last = line
    return " ".join(out)


class Blocked(Exception):
    pass


def yt_transcript(ydl, vid):
    try:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
    except Exception as e:
        msg = str(e)
        if re.search(r"429|Too Many|not a bot|Sign in to confirm", msg, re.I):
            raise Blocked(msg[:200])
        return "", f"ERROR {msg[:120]}", ""
    manual, auto = info.get("subtitles") or {}, info.get("automatic_captions") or {}
    orig = info.get("language") or ""
    choices = []
    for k in manual:
        if k.startswith("en"):
            choices.append(("manual", k, manual[k]))
    for k in ("en-orig", "en", "en-US", "en-GB"):
        if k in auto:
            choices.append(("auto" if k == "en-orig" or orig.startswith("en") else "auto-translated", k, auto[k]))
    for kind, lang, fmts in choices:
        fm = next((f for f in fmts if f.get("ext") == "json3"), None) or next((f for f in fmts if f.get("ext") == "vtt"), None)
        if not fm:
            continue
        try:
            raw = ydl.urlopen(fm["url"]).read().decode("utf-8", "ignore")
        except Exception as e:
            if re.search(r"429|Too Many", str(e)):
                raise Blocked(str(e)[:200])
            continue
        text = parse_json3(raw) if fm.get("ext") == "json3" else parse_vtt(raw)
        if text:
            return text, f"{kind}:{lang}", orig
    return "", "none", orig


def run_youtube():
    print("\n=== 6/6 YOUTUBE transcripts (auto-captions) ===")
    try:
        import yt_dlp
    except ImportError:
        print("   !! Run first:  pip install -U yt-dlp   (skipping YouTube)")
        return
    vids = pick_videos()
    if not vids:
        print("   (no videos selected)")
        return
    print(f"   {len(vids)} relevant videos selected (Central Vietnam / India / budget / food / honeymoon).")
    opts = {"skip_download": True, "quiet": True, "no_warnings": True, "noplaylist": True}
    if YT_COOKIES_FILE:
        opts["cookiefile"] = YT_COOKIES_FILE
    rows, blocked_streak, done_new = [], 0, 0
    with yt_dlp.YoutubeDL(opts) as ydl:
        for i, v in enumerate(vids, 1):
            vid = v["video_id"]
            key = f"yt_{vid}"
            c = cache_get(key)
            if c is None:
                text = src = lang = None
                while text is None:
                    try:
                        text, src, lang = yt_transcript(ydl, vid)
                        blocked_streak = 0
                    except Blocked as e:
                        blocked_streak += 1
                        if blocked_streak >= 3:
                            break
                        wait = 90 * blocked_streak
                        print(f"   [{i}/{len(vids)}] YouTube is rate-limiting ({e}). Waiting {wait}s, then retrying ...")
                        time.sleep(wait)
                if text is None:
                    print("   !! Still blocked. Stopping YouTube for now - re-run later (or on a phone hotspot); "
                          "finished videos are cached and won't be fetched again.")
                    break
                c = {"text": text, "source": src, "lang": lang}
                if not src.startswith("ERROR"):
                    cache_put(key, c)
                done_new += 1
                print(f"   [{i}/{len(vids)}] {'OK ' if text else '-- '} {src:<22} {len(text):6} chars  {v.get('title', '')[:60]}")
                time.sleep(random.uniform(*YT_SLEEP))
            rows.append({"video_id": vid, "title": v.get("title"), "channel": v.get("channel"),
                         "upload_date": v.get("upload_date"), "views": v.get("views"), "url": v.get("url"),
                         "caption_source": c["source"], "video_language": c["lang"], "transcript": c["text"]})
    write_csv("youtube_transcripts_v2.csv", rows)
    got = sum(1 for r in rows if r["transcript"])
    print(f"   transcripts: {got} of {len(rows)} processed videos")


# --------------------------------------------------------------- main
def main():
    sys.stdout = Tee("extra_data_log.txt")
    print(f"\n######## Vietnam extra data run - {dt.datetime.now():%Y-%m-%d %H:%M} ########")
    os.makedirs(CACHE, exist_ok=True)

    if RUN_WEATHER:
        try:
            run_weather()
        except Exception as e:
            print(f"   !! weather part failed: {e}")

    need_apify = RUN_BOOKING or RUN_BOOKING_REVIEWS or RUN_GYG or RUN_X
    if need_apify:
        n_hotels = sum(len(b[3]) for b in STAY_BLOCKS)
        n_tours = sum(len(v) for v in GYG_TOURS.values())
        print("\n=== Apify parts ===")
        print(f"   Booking prices : {n_hotels} hotels + {len(CITY_SEARCHES)} city search   (est. $0.3-0.6)")
        print(f"   Booking reviews: up to {BOOKING_REVIEWS_PER_HOTEL}/hotel                    (est. $0.3-0.8, cap ${CAP_BOOKING_REVIEWS})")
        print(f"   GetYourGuide   : {n_tours} tours x {GYG_REVIEWS_PER_TOUR} reviews             (est. $1.0-1.5, cap ${CAP_GYG})")
        print(f"   X / Twitter    : up to {X_MAX_ITEMS} posts                          (est. $0.1-0.3, cap ${CAP_X})")
        print("   Rough total: $2-3. Check your remaining credit at console.apify.com -> Billing first.")
        if input("   Go ahead with the Apify parts? (y/n): ").strip().lower() != "y":
            need_apify = False
            print("   Skipping Apify parts.")
    if need_apify:
        client = apify_client()
        matched = []
        if RUN_BOOKING:
            try:
                matched = run_booking(client)
            except Exception as e:
                print(f"   !! Booking part failed: {e}")
        if RUN_BOOKING_REVIEWS:
            try:
                run_booking_reviews(client, matched)
            except Exception as e:
                print(f"   !! Booking reviews part failed: {e}")
        if RUN_GYG:
            try:
                run_gyg(client)
            except Exception as e:
                print(f"   !! GetYourGuide part failed: {e}")
        if RUN_X:
            try:
                run_x(client)
            except Exception as e:
                print(f"   !! X part failed: {e}")

    if RUN_YOUTUBE:
        try:
            run_youtube()
        except Exception as e:
            print(f"   !! YouTube part failed: {e}")

    print("\nDone. Attach these files in the chat:")
    for f in ("weather_summary.txt", "weather_daily.csv", "booking_hotels.csv", "booking_rooms.csv",
              "booking_reviews.csv", "gyg_reviews.csv", "x_posts.csv", "youtube_transcripts_v2.csv", "extra_data_log.txt"):
        if os.path.exists(f):
            print(f"   - {f}  ({os.path.getsize(f) // 1024} KB)")


if __name__ == "__main__":
    main()
