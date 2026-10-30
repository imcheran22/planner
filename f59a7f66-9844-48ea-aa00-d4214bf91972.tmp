"""
Vietnam honeymoon (22-28 Jan 2027) - EXTRA DATA v2 (deeper), one run.

Parts, in the order they run (Apify parts run by priority and only while credit lasts):
  1. WEATHER   12 Januaries (2015-2026), 22-28 Jan: Hoi An, Hue, Da Nang beach, Ba Na Hills, Hai Van Pass
               + sea wave height + Hoi An evening rain (lantern-boat hours).            FREE
  2. BOOKING   prices for YOUR dates: 13 shortlisted hotels + city discovery searches
               (Hoi An, Hue, Da Nang central, Da Nang sea-view finder).                 Apify  ~$0.8
  3. GMAPS     deep Google reviews: every place named in the plan (33 places + 9 hotels),
               the big sights (Ba Na, Asia Park, Marble Mountains, My Son, Imperial City, ...),
               and keyword digs: Ba Na "fog" / "coaster" / "cloud", Naman "ocean view".  Apify  ~$1.0
  4. BOOKING REVIEWS   newest 50 reviews per shortlisted hotel (couple / room type).    Apify  ~$0.8
  5. GETYOURGUIDE      reviews of 35 tours (cooking, lantern, food tours, My Son,
               Ba Na tickets + tours, Han River cruise, Marble/Son Tra, Hue tours, Hai Van car). Apify ~$1.5
  6. X / TWITTER       up to 1,000 posts since mid-2024.                                 Apify  ~$0.2
  7. YOUTUBE   auto-captions for the 150 most relevant videos in youtube_videos.csv.    FREE

Before every Apify job the script checks your account's remaining monthly credit and
skips a job that would not fit. Anything skipped is listed at the end; re-run the script
after your credit resets (date shown) and it continues - finished jobs are cached.

Setup:   pip install -U apify-client yt-dlp
Run:     python vietnam_extra_data_v2.py      (in the folder with youtube_videos.csv)
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
RUN = {"weather": True, "booking": True, "gmaps": True, "booking_reviews": True,
       "gyg": True, "x": True, "youtube": True}
CACHE = "extra_cache"            # same cache folder as v1, so anything v1 finished is reused
KEEP_CREDIT_USD = 0.05           # leave this much unspent

# ---- 1. Weather ----
YEARS = list(range(2015, 2027))
DAY_FROM, DAY_TO = 22, 28
TZ = "Asia/Ho_Chi_Minh"
WEATHER_POINTS = {
    "Hoi An":        (15.8801, 108.3380, None),
    "Hue":           (16.4637, 107.5909, None),
    "Da Nang beach": (15.9767, 108.2810, None),
    "Ba Na Hills":   (15.9977, 107.9881, 1400),
    "Hai Van Pass":  (16.1925, 108.1300, 496),
}
SEA_POINTS = {"Da Nang beach sea": (15.98, 108.31), "Hoi An beach sea": (15.90, 108.38)}

# ---- 2/4. Booking.com ----
BOOKING_ACTOR = "voyager/booking-scraper"
BOOKING_REVIEWS_ACTOR = "voyager/booking-reviews-scraper"
CURRENCY, ADULTS = "INR", 2
STAY_BLOCKS = [
    ("Hoi An", "2027-01-22", "2027-01-24", [
        "La Siesta Hoi An Resort & Spa", "Little Hoi An Boutique Hotel & Spa",
        "Cozy An Boutique Hotel Hoi An", "Moire Hoi An"]),
    ("Hue", "2027-01-24", "2027-01-26", [
        "Pilgrimage Village Hue", "Azerai La Residence Hue", "Melia Vinpearl Hue"]),
    ("Da Nang beach-view (1 night)", "2027-01-27", "2027-01-28", [
        "Naman Retreat Da Nang", "Fusion Resort & Villas Da Nang", "Pullman Danang Beach Resort",
        "Furama Resort Danang", "TMS Hotel Da Nang Beach", "Chicland Hotel Danang Beach"]),
]
# (label, search text, check-in, check-out, max results, min Booking score)
CITY_SEARCHES = [
    ("Da Nang sea-view finder (1 night)", "Da Nang", "2027-01-27", "2027-01-28", 100, "8.5"),
    ("Da Nang central (1 night)",         "Da Nang", "2027-01-26", "2027-01-27", 50,  "8.5"),
    ("Hoi An discovery",                  "Hoi An",  "2027-01-22", "2027-01-24", 50,  "8.8"),
    ("Hue discovery",                     "Hue",     "2027-01-24", "2027-01-26", 40,  "8.8"),
]
BOOKING_REVIEWS_PER_HOTEL = 50
BOOKING_REVIEWS_SINCE = "2025-01-01"
SEA_VIEW_WORDS = r"ocean|sea ?view|sea-view|seaview|beach ?front|beachfront|bay view|beach view|partial sea|panoramic sea"

# ---- 3. Google Maps deep reviews ----
GMAPS_REVIEWS_ACTOR = "compass/google-maps-reviews-scraper"
GMAPS_REVIEWS_PER_PLACE = 30
GMAPS_SINCE = "2025-06-01"
PLAN_PLACES = {   # place_id: name   (everything named in the itinerary doc)
    "ChIJ_QtJ_CAPQjERbHE4Q_g5lvM": "La Siesta Hoi An Resort & Spa",
    "ChIJraVA3dcNQjERBm8W-fXdvus": "Little Hoi An Boutique Hotel & Spa",
    "ChIJufFtyc0NQjERrjIT-l5Jyg8": "Cozy An Boutique Hotel",
    "ChIJs1rqfRcPQjERepQmvJmfOYM": "Moire Hoi An",
    "ChIJhUeXYPejQTERwnlay35p5Sc": "Pilgrimage Village",
    "ChIJY41oHTqhQTERRathFhKld9A": "Azerai La Residence Hue",
    "ChIJzYZQjj6hQTERUZt1NuNxsCk": "Melia Vinpearl Hue",
    "ChIJg75J__8QQjERpbr4bqBkwk0": "Naman Retreat",
    "ChIJz-LSXAARQjERhdvmlZnPs_Y": "Fusion Resort & Villas Da Nang",
    "ChIJb_HrObEPQjER6_deT8uf0sY": "Me Hoi An Rooftop",
    "ChIJ-X4wFk4PQjER18KAjNp-Ki4": "Mr Dung Seafood",
    "ChIJtboLbQTdaTERuTF42OTqnwQ": "White Sails Fresh Sea Food",
    "ChIJ2TFW-vcPQjER-Snza-H03as": "Dhaba 21 Hoi An",
    "ChIJ3QWhbqoPQjERv2jqQ9fMnLo": "Mezcal Cocteleria",
    "ChIJX1eOf-EPQjER8zeFj6VoNUY": "Deli Sky Bar",
    "ChIJ0bxaw3sOQjER5fdobwBPLrs": "Hoi An Food Tour",
    "ChIJkdc0Zn4OQjERxxjRVWCr2qo": "Gioan Cookery School",
    "ChIJT-XT3K4NQjERyy-Cx8BV-iE": "Coconut Fragrance Cooking Class",
    "ChIJx0dBXWYNQjERQzQO18QYhas": "Mimi Cooking Class",
    "ChIJPXH2hcYPQjER4lmqua1LH1s": "Lantern Making Class With Lynn",
    "ChIJ9a55ExMPQjERXQ2tNz2vd1M": "Hair of the dog bar Hoi An",
    "ChIJ-y_MQy2hQTERPMRWdy0GIzE": "Le Family Riders",
    "ChIJ5ywgMK-hQTER2RIw263YYmA": "Vi Hue Restaurant",
    "ChIJ-Z5gqD6hQTERrkINf3vLTnU": "Nina's Cafe",
    "ChIJF1qQD5-hQTERqOywxDGd1v0": "Imperial Craft Bia Brewpub",
    "ChIJQXphoyKhQTERPVM4I-KFgow": "Secret Lounge Hue",
    "ChIJ0wVgLJemQTERunn1THqLJvc": "Thien Mu Pagoda",
    "ChIJ-YyC-IGhQTERbuDyZ_KNcOI": "Moon River Cruises",
    "ChIJ7ZePIy6hQTERHP94LYVfeAI": "Hue Museum of Royal Antiquities",
    "ChIJEwAAALAZQjERyXCN5eSBt1Q": "Jang Mi Spa & Massage",
    "ChIJeTslKdkXQjERPFZeN_Ta-Ek": "Quan Hai San Be Nu",
    "ChIJqaQoXYMZQjERX_QzVEAZr_Q": "MAAZI Da Nang",
    "ChIJnzvzZGwXQjERm0FP3YQ1yoM": "MANVAR Rasoi",
    "ChIJYTdcRmIZQjERpxIQp-G8HQ4": "Van Cocktail Bar",
    "ChIJP0--pEAXQjERoheJMf24gHA": "Lounge Beach Bar",
    "ChIJ76XtSwwZQjERJapWgs-OVhQ": "Gypsy Rooftop",
    "ChIJu6Pkk2YZQjER6ID6f0tNyJI": "Riverside Terrace",
    "ChIJ88PbSosZQjERkKfKhJFEnZY": "Com Ga WOW",
    "ChIJL1i0GEQXQjERoeh37CnOT6Q": "India0Miles",
    "ChIJ3V2QSAAXQjERMEzpT0QM5Yk": "Kababish Halal",
    "ChIJr_sj6oMPQjERAF3tT5yKABE": "Spice Route Hoi An",
    "ChIJkw-cwoQPQjERTFcDJHYsmbc": "Rasoi Pure Vegetarian Hoi An",
    "ChIJLWoAs80ZQjERLKHDYD-ZymI": "Museum of Cham Sculpture",
}
SIGHTS_PER_PLACE = 50
SIGHTS = [   # not in the earlier Maps data, so found by search
    "Sun World Ba Na Hills", "Golden Bridge Ba Na Hills", "Sun World Danang Wonders Asia Park",
    "Marble Mountains Da Nang", "Linh Ung Pagoda Son Tra", "My Son Sanctuary",
    "Hue Imperial City", "Khai Dinh Tomb", "Hoi An Ancient Town", "Han River Dragon Bridge Da Nang",
]
KEYWORD_DIGS = [   # (place search, keyword, max reviews) - reviews that mention the word
    ("Sun World Ba Na Hills", "fog", 80),
    ("Sun World Ba Na Hills", "coaster", 80),
    ("Sun World Ba Na Hills", "cloud", 60),
    ("Naman Retreat Da Nang", "ocean view", 60),
    ("Hoi An Ancient Town", "January", 40),
]

# ---- 5. GetYourGuide ----
GYG_ACTOR = "automation-lab/getyourguide-reviews-scraper"
GYG_REVIEWS_PER_TOUR = 10
GYG_REVIEWS_SINCE = "2024-06-01"
G = "https://www.getyourguide.com/"
GYG_TOURS = {
    "Cooking class + basket boat": [
        G + "hoi-an-l831/hoi-an-basket-boat-with-lantern-making-cooking-class-tour-t540267/",
        G + "hoi-an-l831/hoi-anvisit-local-marketbasket-boat-ride-and-cooking-class-t133461/",
        G + "hoi-an-l831/hoiandanang-eco-cooking-class-cruise-trip-basket-boat-t218388/",
        G + "hoi-an-l831/hoi-an-cooking-class-market-visit-coconut-basket-boat-t135501/",
        G + "hoi-an-l831/hoi-an-bay-mau-cooking-class-w-market-basket-boat-trip-t486228/"],
    "Lantern making class": [
        G + "hoi-an-l831/hoi-an-vietnamese-foldable-lantern-making-class-t388285/",
        G + "hoi-an-l831/lantern-making-class-with-lynn-t547348/",
        G + "hoi-an-l831/hoi-an-old-town-lantern-making-workshop-t561926/"],
    "Hoi An food tour": [
        G + "hoi-an-l831/hoi-an-street-food-tour-with-billy-t526655/",
        G + "hoi-an-l831/hoi-an-authentic-exotic-evening-food-culture-tour-t485866/",
        G + "hoi-an-l831/hoi-an-food-tour-boat-trip-and-foot-massage-by-night-t219078/"],
    "My Son sunrise": [
        G + "hoi-an-l831/hoi-an-my-son-sanctuary-sunrise-tour-t724941/",
        G + "hoi-an-l831/sunrise-tour-to-my-son-sanctuary-from-hoi-an-t131565/",
        G + "hoi-an-l831/4-hour-my-son-valley-sunrise-tour-t125945/"],
    "Ba Na Hills tour": [
        G + "da-nang-l939/ba-na-hills-golden-bridge-small-group-tour-t466388/",
        G + "da-nang-l939/from-da-nang-ba-na-hills-and-golden-bridge-tour-options-t469551/",
        G + "da-nang-l939/from-da-nang-or-hoi-an-ba-na-hills-golden-bridge-tour-t532798/"],
    "Ba Na Hills ticket": [
        G + "hoi-an-l831/ba-na-hills-admission-with-cable-car-and-optional-lunch-t763730/",
        G + "da-nang-l939/da-nang-ba-na-hills-entry-with-cable-car-and-lunch-option-t649730/"],
    "Han River cruise": [
        G + "da-nang-l939/da-nang-han-river-cruise-and-champa-dance-t469912/",
        G + "da-nang-l939/da-nang-poseidon-cruise-with-dinner-and-dragon-bridge-show-t887190/",
        G + "da-nang-l939/da-nang-han-river-dinner-cruise-with-tien-sa-show-t1061177/",
        G + "da-nang-l939/da-nang-by-night-han-river-dragon-cruise-with-a-local-food-t686658/"],
    "Marble Mountains + Lady Buddha": [
        G + "hoi-an-l831/hoi-an-secrets-of-the-marble-mountains-linh-ung-pagoda-t36985/",
        G + "ngu-hanh-son-l190191/explore-lady-buddha-marble-mountains-and-am-phu-cave-t869046/",
        G + "da-nang-l939/da-nanghoi-an-marble-mountainsam-phu-cave-monkey-mountain-t880461/"],
    "Hue food tour": [
        G + "hue-vietnam-l833/hue-street-walking-food-tour-t572715/",
        G + "hue-vietnam-l833/hue-night-street-food-safari-by-cyclo-t444748/",
        G + "hue-vietnam-l833/hue-food-tour-by-walking-or-cyclo-or-motorbike-with-driver-t543404/"],
    "Hue Imperial City + tombs": [
        G + "hue-vietnam-l833/hue-imperial-city-royal-tombs-with-perfume-river-cruise-t1063006/",
        G + "hue-vietnam-l833/hue-imperial-city-royal-tombs-pagoda-dragon-boat-tour-t696554/",
        G + "hue-vietnam-l833/hue-dragon-boat-perfume-river-hue-imperial-city-t677558/"],
    "Hoi An -> Hue private car via Hai Van": [
        G + "da-nang-l939/hoi-an-transfer-tofrom-hue-by-private-car-via-hai-van-pass-t540183/",
        G + "da-nang-l939/hoi-an-private-car-to-hue-with-sightseeing-stops-t892424/",
        G + "hoi-an-l831/hoi-an-to-hue-by-private-car-with-sightseeing-stops-t489402/"],
}

# ---- 6. X / Twitter ----
X_ACTOR = "xquik/x-tweet-scraper"
X_SINCE, X_MAX_ITEMS = "2024-06-01", 1000
X_SEARCHES = [
    '"Hoi An" -filter:retweets',
    '"Da Nang" (trip OR travel OR beach OR hotel OR food) -filter:retweets',
    '("Ba Na Hills" OR "Golden Bridge" OR "Bana Hills") -filter:retweets',
    '"Ba Na" (fog OR foggy OR cloud OR coaster) -filter:retweets',
    'Hue Vietnam (citadel OR imperial OR food OR trip) -filter:retweets',
    '"Hai Van Pass" -filter:retweets',
    '"Han River" (cruise OR "Dragon Bridge") -filter:retweets',
    'Vietnam honeymoon -filter:retweets',
    'Vietnam (trip OR travel OR visa) (India OR Indian OR Indians) -filter:retweets',
    '"Da Nang" (January OR Jan) (weather OR rain OR beach OR cold) -filter:retweets',
    '"Hoi An" (cooking class OR lantern) -filter:retweets',
    'Vietnam (scam OR scammed) (Da Nang OR "Hoi An" OR Hue) -filter:retweets',
]

# ---- Estimated prices (USD per item, free-plan level; real caps protect you) ----
PRICE = {"booking": 0.0025, "booking_review": 0.0012, "gmaps_review": 0.0006,
         "gyg_review": 0.0044, "x_post": 0.0002}

# ---- 7. YouTube ----
YT_VIDEOS_CSV = "youtube_videos.csv"
YT_MAX_VIDEOS = 150
YT_SLEEP = (6, 12)
YT_COOKIES_FILE = ""
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


def http_json(url, headers=None, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=dict({"User-Agent": "vietnam-trip-research/2.0"}, **(headers or {})))
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            try:
                return json.loads(body)
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

        def hours(a, b):
            return [j for j in idx if a <= int(H["time"][j][11:13]) <= b]

        def hv(var, js):
            col = H.get(var) or []
            return [col[j] if j < len(col) else None for j in js]

        morning, daytime, evening = hours(7, 11), hours(8, 17), hours(18, 21)
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
            "evening_rain_mm": round(sum(x or 0 for x in hv("precipitation", evening)), 1),
            "evening_temp_c": mean(hv("temperature_2m", evening)),
            "daytime_gust_max_kmh": max([x for x in hv("wind_gusts_10m", daytime) if x is not None], default=None),
        }
        rain = r["rain_mm"] or 0
        r["rain_day"] = rain >= 1.0
        r["washout"] = rain >= 10 or (r["rain_hours"] or 0) >= 8
        r["good_day"] = rain < 1.0 and r["sunshine_h"] >= 5
        r["dry_evening"] = r["evening_rain_mm"] < 0.5
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
                "daily": "wave_height_max,wave_period_max,wave_direction_dominant", "timezone": TZ}
        why = ""
        for step in range(4):
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
                     "wave_height_max_m": wh, "wave_period_max_s": (D.get("wave_period_max") or [None] * 99)[i],
                     "wave_dir_deg": (D.get("wave_direction_dominant") or [None] * 99)[i],
                     "rough_over_1_5m": None if wh is None else wh > 1.5,
                     "calm_under_1m": None if wh is None else wh < 1.0})
    return rows


def run_weather():
    print(f"\n=== WEATHER: 22-28 Jan, {YEARS[0]}-{YEARS[-1]} ===")
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
    lines.append("Source: Open-Meteo historical reanalysis (ERA5 family, ~9-25 km grid). Typical odds, not a forecast.\n")
    for name in WEATHER_POINTS:
        rs = [r for r in land if r["point"] == name]
        if not rs:
            continue
        s = {"point": name, "days": len(rs),
             "avg_max_c": mean([r["tmax_c"] for r in rs]), "avg_min_c": mean([r["tmin_c"] for r in rs]),
             "avg_rain_mm_per_day": mean([r["rain_mm"] for r in rs]),
             "pct_rain_days": pct([r["rain_day"] for r in rs]), "pct_washout_days": pct([r["washout"] for r in rs]),
             "pct_good_days": pct([r["good_day"] for r in rs]), "avg_sunshine_h": mean([r["sunshine_h"] for r in rs]),
             "pct_clouded_mornings": pct([r["clouded_morning"] for r in rs]),
             "pct_dry_evenings": pct([r["dry_evening"] for r in rs]),
             "avg_evening_temp_c": mean([r["evening_temp_c"] for r in rs])}
        summary.append(s)
        lines.append(f"{name}: max {s['avg_max_c']} C / min {s['avg_min_c']} C | rain on {s['pct_rain_days']}% of days, "
                     f"washouts {s['pct_washout_days']}%, good sunny days {s['pct_good_days']}% | sun {s['avg_sunshine_h']} h/day | "
                     f"clouded-in mornings {s['pct_clouded_mornings']}% | dry evenings (18-22h) {s['pct_dry_evenings']}%, "
                     f"evening temp {s['avg_evening_temp_c']} C")

    def by_year(point, days):
        out = {}
        for r in land:
            if r["point"] == point and r["day"] in days:
                out.setdefault(r["year"], {})[r["day"]] = r
        return {y: v for y, v in out.items() if all(d in v for d in days)}

    lines.append("\nPLAN-SPECIFIC ODDS")
    ha = by_year("Hoi An", (22, 23))
    if ha:
        lines.append(f"Hoi An evenings 22-23 Jan (lantern boat): at least one dry evening in "
                     f"{pct([v[22]['dry_evening'] or v[23]['dry_evening'] for v in ha.values()])}% of years.")
    hue = by_year("Hue", (24, 25))
    if hue:
        lines.append(f"Hue 24-25 Jan: at least one washout day in {pct([v[24]['washout'] or v[25]['washout'] for v in hue.values()])}% "
                     f"of years; both washed out in {pct([v[24]['washout'] and v[25]['washout'] for v in hue.values()])}%.")
    hv_ = by_year("Hai Van Pass", (24,))
    if hv_:
        lines.append(f"Hai Van Pass 24 Jan (drive day): clouded-in morning in {pct([v[24]['clouded_morning'] for v in hv_.values()])}% "
                     f"of years, washout in {pct([v[24]['washout'] for v in hv_.values()])}%.")
    bana = by_year("Ba Na Hills", (26, 27))
    if bana:
        lines.append(f"Ba Na Hills mornings: clouded-in on 27 Jan in {pct([v[27]['clouded_morning'] for v in bana.values()])}% of years; "
                     f"clear on at least one of 26/27 Jan in {pct([not (v[26]['clouded_morning'] and v[27]['clouded_morning']) for v in bana.values()])}%.")
        trans = [v[27]["clouded_morning"] for v in bana.values() if v[26]["clouded_morning"]]
        if trans:
            lines.append(f"   If 26 Jan was clouded, 27 Jan was also clouded in {pct(trans)}% of those years.")
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
                     f"under 1 m on {s['pct_calm_under_1m']}%.")
    lines.append("\nNOTES: 'clouded-in morning' = 07-12h low cloud >= 80%, or humidity >= 95% with cloud >= 80%, or >= 1 mm rain "
                 "(the grid smooths mountains, so Ba Na is a relative guide, not a fog count). 'washout' = >= 10 mm or >= 8 rainy hours. "
                 "'good day' = < 1 mm and >= 5 h sun. 'dry evening' = < 0.5 mm between 18:00 and 21:59.")
    write_csv("weather_summary.csv", summary + sea_s, first_cols=("point",))
    with open("weather_summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n" + "\n".join(lines))


# ------------------------------------------------------------ APIFY
OUT_OF_CREDIT = re.compile(r"usage limit|hard limit|monthly usage|not enough|insufficient|credit|payment|exceed|402", re.I)


class Apify:
    """One account. Checks remaining credit before every job and stops cleanly when it runs out."""

    def __init__(self, token):
        from apify_client import ApifyClient
        self.token = token
        self.client = ApifyClient(token)
        self.out = False
        self.skipped = []
        self.reset_at = ""

    def remaining(self):
        d = http_json("https://api.apify.com/v2/users/me/limits", headers={"Authorization": f"Bearer {self.token}"})
        try:
            d = d["data"]
            self.reset_at = (d.get("monthlyUsageCycle") or {}).get("endAt", "")[:10]
            return round(d["limits"]["maxMonthlyUsageUsd"] - d["current"]["monthlyUsageUsd"], 3)
        except Exception:
            return None          # unknown - the per-run cap still protects you

    def run(self, key, actor, run_input, est_usd, label=""):
        cached = cache_get(key)
        if cached is not None:
            print(f"   cached: {label or key} ({len(cached)} items)")
            return cached
        if self.out:
            self.skipped.append(label or key)
            return []
        left = self.remaining()
        cap = max(0.5, round(est_usd * 1.6, 2))
        if left is not None:
            print(f"   credit left: ${left:.2f}")
            if left - KEEP_CREDIT_USD < max(est_usd, 0.5):
                print(f"   -- skipping '{label or key}' (needs ~${est_usd:.2f}, Apify needs >= $0.50 headroom per run)")
                self.skipped.append(label or key)
                return []
            cap = min(cap, max(0.5, round(left - KEEP_CREDIT_USD, 2)))
        print(f"   running {actor}  [{label or key}]  est ${est_usd:.2f}, cap ${cap:.2f} ...")
        act = self.client.actor(actor)
        try:
            try:
                run = act.call(run_input=run_input, max_total_charge_usd=cap)
            except TypeError:
                run = act.call(run_input=run_input)
        except Exception as e:
            msg = str(e)
            print(f"   !! {actor}: {msg[:300]}")
            if OUT_OF_CREDIT.search(msg):
                self.out = True
                self.skipped.append(label or key)
            return []
        status, ds = run_info(run)
        items = dataset_items(self.client, ds)
        if "SUCCEEDED" not in str(status):
            msg = getattr(run, "status_message", None) or (run.get("statusMessage") if isinstance(run, dict) else "") or ""
            print(f"   !! run status {status} {msg[:150]} - keeping the {len(items)} items it produced")
            if OUT_OF_CREDIT.search(str(msg)):
                self.out = True
        if items or "SUCCEEDED" in str(status):
            cache_put(key, items)
        print(f"   -> {len(items)} items")
        return items


def run_info(run):
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


def norm(s):
    return re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower().replace("&", " and ")).split()


STOP = set("hotel resort spa and the da nang danang hoi an hue beach boutique villas villa vietnam".split())


def name_match(wanted, got):
    w = [t for t in norm(wanted) if t not in STOP] or norm(wanted)
    g = set(norm(got))
    return sum(1 for t in w if t in g) >= max(1, (len(w) + 1) // 2)


def is_sea(room):
    return bool(re.search(SEA_VIEW_WORDS, f"{room.get('roomType', '')} {room.get('features', '')}", re.I))


# ---------------------------------------------------------- 2. BOOKING
def run_booking(ap):
    print("\n=== BOOKING.COM prices for your dates ===")
    hotels, rooms, matched = [], [], []
    base = {"currency": CURRENCY, "adults": ADULTS, "children": 0, "rooms": 1,
            "minMaxPrice": "0-999999", "extractAdditionalHotelData": True}

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
            avail = [r for r in rs if r.get("available", True) and isinstance(r.get("price"), (int, float))]
            sea_av = [r for r in avail if is_sea(r)]
            row = {"block": block, "wanted": wanted or "", "name": it.get("name"), "check_in": cin, "check_out": cout,
                   "nights": nights, "booking_rating": it.get("rating"), "booking_reviews": it.get("reviews"),
                   "stars": it.get("stars"), "listed_price": it.get("price"), "currency": it.get("currency"),
                   "cheapest_room_price": min([r["price"] for r in avail], default=None),
                   "cheapest_sea_view_price": min([r["price"] for r in sea_av], default=None),
                   "sea_view_room_types": "; ".join(sorted({str(r.get("roomType")) for r in rs if is_sea(r)})),
                   "address": (it.get("address") or {}).get("full") if isinstance(it.get("address"), dict) else it.get("address"),
                   "url": it.get("url")}
            row.update({"raw." + k: v for k, v in flatten(it).items() if not k.startswith("rooms")})
            hotels.append(row)
            if wanted:
                matched.append({"block": block, "name": it.get("name"), "url": it.get("url")})
            for r in rs:
                rooms.append({"block": block, "hotel": it.get("name"), "check_in": cin, "check_out": cout,
                              "room_type": r.get("roomType"), "bed": r.get("bedType"), "persons": r.get("persons"),
                              "price_as_listed": r.get("price"), "currency": r.get("currency"), "available": r.get("available"),
                              "sea_view": is_sea(r),
                              "features": "; ".join(map(str, r.get("features") or [])) if isinstance(r.get("features"), list) else r.get("features")})

    for block, cin, cout, names in STAY_BLOCKS:
        for nm in names:
            items = ap.run(f"booking_{slug(nm)}_{cin}", BOOKING_ACTOR,
                           dict(base, search=nm, checkIn=cin, checkOut=cout, maxItems=3), 3 * PRICE["booking"], nm)
            collect(block, cin, cout, items, wanted=nm)
    for block, city, cin, cout, n, min_score in CITY_SEARCHES:
        items = ap.run(f"booking_city_{slug(block)}_{cin}", BOOKING_ACTOR,
                       dict(base, search=city, checkIn=cin, checkOut=cout, maxItems=n, minScore=min_score),
                       n * PRICE["booking"], block)
        collect(block, cin, cout, items)

    main_cols = ("block", "wanted", "name", "check_in", "check_out", "nights", "cheapest_room_price",
                 "cheapest_sea_view_price", "currency", "booking_rating", "booking_reviews", "stars", "listed_price",
                 "sea_view_room_types", "address", "url")
    # slim file to attach in the chat (the full one with every raw Booking field is very large)
    write_csv("booking_hotels.csv", [{k: h.get(k) for k in main_cols} for h in hotels], first_cols=main_cols)
    write_csv("booking_hotels_full.csv", hotels, first_cols=main_cols)
    write_csv("booking_rooms.csv", rooms)
    sea = [h for h in hotels if h.get("cheapest_sea_view_price") and "Da Nang" in h["block"]
           and (h.get("booking_rating") or 0) >= 8.5]
    sea.sort(key=lambda h: h["cheapest_sea_view_price"])
    write_csv("booking_sea_view_options.csv",
              [{k: h.get(k) for k in ("block", "name", "cheapest_sea_view_price", "currency", "nights", "booking_rating",
                                      "booking_reviews", "sea_view_room_types", "address", "url")} for h in sea])
    print("\n   Shortlist (price as listed for the whole stay, " + CURRENCY + "):")
    for h in hotels:
        if h.get("wanted"):
            print(f"   - {h['block']:<30} {str(h['name'])[:36]:<36} cheapest {h.get('cheapest_room_price')}  "
                  f"sea-view {h.get('cheapest_sea_view_price')}")
    if sea:
        print("   Cheapest well-rated Da Nang sea-view rooms:")
        for h in sea[:8]:
            print(f"   - {str(h['name'])[:40]:<40} {h['cheapest_sea_view_price']} {h.get('currency') or ''}  "
                  f"({h.get('booking_rating')}, {h.get('booking_reviews')} reviews)")
    return matched


# ------------------------------------------------- 3. GOOGLE MAPS DEEP
def run_gmaps(ap):
    print("\n=== GOOGLE MAPS deep reviews ===")
    rows = []

    def add(items, source, keyword=""):
        for it in items:
            r = flatten(it)
            r["dig"] = source
            r["keyword"] = keyword
            r["plan_name"] = PLAN_PLACES.get(r.get("placeId"), "")
            rows.append(r)

    ids = list(PLAN_PLACES)
    items = ap.run(f"gmaps_plan_{len(ids)}_{GMAPS_REVIEWS_PER_PLACE}_{GMAPS_SINCE}", GMAPS_REVIEWS_ACTOR,
                   {"placeIds": ids, "maxReviews": GMAPS_REVIEWS_PER_PLACE, "reviewsSort": "newest",
                    "reviewsStartDate": GMAPS_SINCE, "language": "en", "reviewsOrigin": "google", "personalData": False},
                   len(ids) * GMAPS_REVIEWS_PER_PLACE * PRICE["gmaps_review"], "plan places")
    add(items, "plan places")

    urls = [{"url": "https://www.google.com/maps/search/" + urllib.parse.quote_plus(s)} for s in SIGHTS]
    items = ap.run(f"gmaps_sights_{len(SIGHTS)}_{SIGHTS_PER_PLACE}_{GMAPS_SINCE}", GMAPS_REVIEWS_ACTOR,
                   {"startUrls": urls, "maxReviews": SIGHTS_PER_PLACE, "reviewsSort": "newest",
                    "reviewsStartDate": GMAPS_SINCE, "language": "en", "personalData": False},
                   len(SIGHTS) * SIGHTS_PER_PLACE * PRICE["gmaps_review"], "big sights")
    add(items, "big sights")

    for place, word, n in KEYWORD_DIGS:
        items = ap.run(f"gmaps_kw_{slug(place)}_{slug(word)}_{n}", GMAPS_REVIEWS_ACTOR,
                       {"startUrls": [{"url": "https://www.google.com/maps/search/" + urllib.parse.quote_plus(place)}],
                        "maxReviews": n, "reviewsSort": "newest", "reviewsFilterString": word,
                        "language": "en", "personalData": False},
                       n * PRICE["gmaps_review"], f"{place} / '{word}'")
        add(items, f"keyword: {place}", word)

    write_csv("gmaps_deep_reviews.csv", rows, first_cols=("dig", "keyword", "plan_name", "title", "stars", "publishedAtDate",
                                                          "text", "textTranslated", "reviewContext", "likesCount", "placeId"))
    for place, word, _ in KEYWORD_DIGS:
        rs = [r for r in rows if r["keyword"] == word and r["dig"].endswith(place)]
        if rs:
            months = {}
            for r in rs:
                m = str(r.get("publishedAtDate", ""))[5:7]
                if m:
                    months[m] = months.get(m, 0) + 1
            print(f"   '{word}' at {place}: {len(rs)} reviews; by month posted: {dict(sorted(months.items()))}")


# --------------------------------------------------- 4. BOOKING REVIEWS
def run_booking_reviews(ap, matched):
    print("\n=== BOOKING.COM reviews of the shortlist ===")
    if not matched:      # Booking part skipped this time - rebuild from cache if it ran before
        for block, cin, _, names in STAY_BLOCKS:
            for nm in names:
                for it in (cache_get(f"booking_{slug(nm)}_{cin}") or []):
                    if name_match(nm, it.get("name")):
                        matched.append({"block": block, "name": it.get("name"), "url": it.get("url")})
                        break
    urls = [{"url": m["url"].split("?")[0], "userData": {"block": m["block"], "hotel": m["name"]}} for m in matched if m.get("url")]
    if not urls:
        print("   (no hotel URLs yet - needs the Booking prices part)")
        return
    items = ap.run(f"booking_reviews_{len(urls)}_{BOOKING_REVIEWS_PER_HOTEL}", BOOKING_REVIEWS_ACTOR,
                   {"startUrls": urls, "maxReviewsPerHotel": BOOKING_REVIEWS_PER_HOTEL, "sortReviewsBy": "f_recent_desc",
                    "cutoffDate": BOOKING_REVIEWS_SINCE, "reviewScores": ["ALL"]},
                   len(urls) * BOOKING_REVIEWS_PER_HOTEL * PRICE["booking_review"], "Booking reviews")
    write_csv("booking_reviews.csv", [flatten(i) for i in items],
              first_cols=("customData.block", "customData.hotel", "rating", "travelerType", "roomInfo",
                          "stayDate", "reviewTitle", "likedText", "dislikedText"))


# ------------------------------------------------------ 5. GETYOURGUIDE
def run_gyg(ap):
    print("\n=== GETYOURGUIDE reviews ===")
    cat_of, urls = {}, []
    for cat, lst in GYG_TOURS.items():
        for u in lst:
            u = u.split("?")[0]
            cat_of[re.search(r"-t(\d+)/?$", u).group(1)] = cat
            urls.append({"url": u})
    items = ap.run(f"gyg_{len(urls)}_{GYG_REVIEWS_PER_TOUR}", GYG_ACTOR,
                   {"startUrls": urls, "maxReviewsPerUrl": GYG_REVIEWS_PER_TOUR,
                    "maxItems": GYG_REVIEWS_PER_TOUR * len(urls), "cutoffDate": GYG_REVIEWS_SINCE,
                    "language": "en-US", "allowEmptyResults": True},
                   len(urls) * GYG_REVIEWS_PER_TOUR * PRICE["gyg_review"], "GetYourGuide")
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


# ------------------------------------------------------------- 6. X
def run_x(ap):
    print("\n=== X / TWITTER ===")
    items = ap.run(f"x_{len(X_SEARCHES)}_{X_MAX_ITEMS}_{X_SINCE}", X_ACTOR,
                   {"searchTerms": X_SEARCHES, "maxItems": X_MAX_ITEMS, "queryType": "Top", "since": X_SINCE, "lang": "en"},
                   X_MAX_ITEMS * PRICE["x_post"], "X / Twitter")
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


# ------------------------------------------------------ 7. YOUTUBE
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
        t = (v.get("title") or "").lower()
        text = f"{t} {(v.get('description') or '')[:300].lower()}"
        if re.search(YT_SKIP, t) and not re.search(r"hoi ?an|da ?nang|danang|\bhue\b|ba ?na|hai ?van", t):
            continue
        hits = len(re.findall(YT_RELEVANT, text))
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
    parts = [s.get("utf8", "") for ev in data.get("events", []) for s in (ev.get("segs") or [])]
    return re.sub(r"\s+", " ", "".join(p for p in parts if p != "\n")).strip()


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
    choices = [("manual", k, manual[k]) for k in manual if k.startswith("en")]
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
    print("\n=== YOUTUBE transcripts (auto-captions) ===")
    try:
        import yt_dlp
    except ImportError:
        print("   !! Run first:  pip install -U yt-dlp   (skipping YouTube)")
        return
    vids = pick_videos()
    if not vids:
        print("   (no videos selected)")
        return
    print(f"   {len(vids)} relevant videos selected.")
    opts = {"skip_download": True, "quiet": True, "no_warnings": True, "noplaylist": True}
    if YT_COOKIES_FILE:
        opts["cookiefile"] = YT_COOKIES_FILE
    rows, streak = [], 0
    with yt_dlp.YoutubeDL(opts) as ydl:
        for i, v in enumerate(vids, 1):
            vid = v["video_id"]
            c = cache_get(f"yt_{vid}")
            if c is None:
                text = src = lang = None
                while text is None:
                    try:
                        text, src, lang = yt_transcript(ydl, vid)
                        streak = 0
                    except Blocked as e:
                        streak += 1
                        if streak >= 3:
                            break
                        print(f"   [{i}/{len(vids)}] YouTube is rate-limiting ({e}). Waiting {90 * streak}s ...")
                        time.sleep(90 * streak)
                if text is None:
                    print("   !! Still blocked. Stopping YouTube for now - re-run later (or on a phone hotspot).")
                    break
                c = {"text": text, "source": src, "lang": lang}
                if not src.startswith("ERROR"):
                    cache_put(f"yt_{vid}", c)
                print(f"   [{i}/{len(vids)}] {'OK ' if text else '-- '} {src:<22} {len(text):6} chars  {v.get('title', '')[:60]}")
                time.sleep(random.uniform(*YT_SLEEP))
            rows.append({"video_id": vid, "title": v.get("title"), "channel": v.get("channel"),
                         "upload_date": v.get("upload_date"), "views": v.get("views"), "url": v.get("url"),
                         "caption_source": c["source"], "video_language": c["lang"], "transcript": c["text"]})
    write_csv("youtube_transcripts_v2.csv", rows)
    print(f"   transcripts: {sum(1 for r in rows if r['transcript'])} of {len(rows)} processed videos")


# --------------------------------------------------------------- main
def ask_token():
    """Always asks for the token (ignores any saved APIFY_TOKEN), checks it, and shows which account it is."""
    if os.environ.get("APIFY_TOKEN"):
        print("   (ignoring the APIFY_TOKEN saved on this computer - using the token you paste now)")
    for _ in range(3):
        token = getpass.getpass("   Paste the Apify API token to use for this run (hidden, paste + Enter; "
                                "Enter alone = skip Apify parts): ").strip()
        if not token:
            return None
        me = http_json("https://api.apify.com/v2/users/me", headers={"Authorization": f"Bearer {token}"})
        user = (me.get("data") or {}).get("username") if isinstance(me, dict) else None
        if not user:
            print("   !! Apify did not accept that token. Copy it again from console.apify.com -> Settings -> "
                  "API & Integrations, and paste it.")
            continue
        ap = Apify(token)
        left = ap.remaining()
        print(f"   Account: {user} | credit left: " + (f"${left:.2f}" if left is not None else "unknown")
              + f" | resets {ap.reset_at or 'monthly'}")
        if left is not None and left - KEEP_CREDIT_USD < 0.5:
            print("   This account has under $0.50 left, which is too little to start an Apify run.")
            if input("   Paste a different token? (y/n): ").strip().lower() == "y":
                continue
        return ap
    print("   No usable token - skipping the Apify parts.")
    return None


def estimate():
    n_h = sum(len(b[3]) for b in STAY_BLOCKS)
    n_t = sum(len(v) for v in GYG_TOURS.values())
    return [
        ("booking", "Booking prices", (n_h * 3 + sum(c[4] for c in CITY_SEARCHES)) * PRICE["booking"]),
        ("gmaps", "Google Maps deep reviews", (len(PLAN_PLACES) * GMAPS_REVIEWS_PER_PLACE + len(SIGHTS) * SIGHTS_PER_PLACE
                                               + sum(k[2] for k in KEYWORD_DIGS)) * PRICE["gmaps_review"]),
        ("booking_reviews", "Booking reviews", n_h * BOOKING_REVIEWS_PER_HOTEL * PRICE["booking_review"]),
        ("gyg", "GetYourGuide reviews", n_t * GYG_REVIEWS_PER_TOUR * PRICE["gyg_review"]),
        ("x", "X / Twitter", X_MAX_ITEMS * PRICE["x_post"]),
    ]


def main():
    sys.stdout = Tee("extra_data_log.txt")
    print(f"\n######## Vietnam extra data v2 - {dt.datetime.now():%Y-%m-%d %H:%M} ########")
    os.makedirs(CACHE, exist_ok=True)

    if RUN["weather"]:
        try:
            run_weather()
        except Exception as e:
            print(f"   !! weather part failed: {e}")

    plan = [p for p in estimate() if RUN[p[0]]]
    ap = None
    if plan:
        print("\n=== Apify parts (run in this order while credit lasts) ===")
        for _, label, usd in plan:
            print(f"   {label:<28} est. ${usd:.2f}")
        print(f"   {'TOTAL':<28} est. ${sum(p[2] for p in plan):.2f}   (estimates; each run also has a hard cap)")
        try:
            from apify_client import ApifyClient  # noqa: F401
        except ImportError:
            sys.exit("Run first:  pip install -U apify-client")
        ap = ask_token()
        if ap and input("   Go ahead? (y/n): ").strip().lower() != "y":
            ap, plan = None, []
    if ap:
        matched = []
        steps = {"booking": lambda: matched.extend(run_booking(ap) or []),
                 "gmaps": lambda: run_gmaps(ap),
                 "booking_reviews": lambda: run_booking_reviews(ap, matched),
                 "gyg": lambda: run_gyg(ap),
                 "x": lambda: run_x(ap)}
        for k, label, _ in plan:
            try:
                steps[k]()
            except Exception as e:
                print(f"   !! {label} failed: {e}")

    if RUN["youtube"]:
        try:
            run_youtube()
        except Exception as e:
            print(f"   !! YouTube part failed: {e}")

    print("\n================ DONE ================")
    if ap and ap.skipped:
        print("Not run this time (credit): " + ", ".join(ap.skipped))
        print(f"Re-run this script after your Apify credit resets ({ap.reset_at or 'next month'}); finished parts are cached.")
    print("Attach these files in the chat:")
    for f in ("weather_summary.txt", "weather_daily.csv", "booking_hotels.csv", "booking_sea_view_options.csv",
              "booking_rooms.csv", "gmaps_deep_reviews.csv", "booking_reviews.csv", "gyg_reviews.csv", "x_posts.csv",
              "youtube_transcripts_v2.csv", "extra_data_log.txt"):
        if os.path.exists(f):
            print(f"   - {f}  ({os.path.getsize(f) // 1024} KB)")


if __name__ == "__main__":
    main()
