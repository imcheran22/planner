"""
Vietnam trip research: Google Maps + TripAdvisor -> CSV files, via Apify (free plan works).

Output files:
  gmaps_places.csv        hotels / restaurants / attractions: rating, review count, price level, address, map link
  gmaps_reviews.csv       recent Google reviews for every place (text, stars, date, likes)
  tripadvisor_places.csv  TripAdvisor hotels / restaurants / things to do: rating, ranking, review count
  tripadvisor_reviews.csv TripAdvisor reviews for the top places (includes trip type e.g. COUPLES)

Setup (one time, ~5 min):
  1. Sign up free at https://apify.com
  2. Console -> Settings -> API & Integrations -> copy your Personal API token
  3. VS Code terminal:   pip install -U apify-client
  4. python maps_tripadvisor_vietnam.py      (it asks for the token)

Cost: Apify bills per result from your monthly free credit. The settings below are kept small.
Run it once, then check Console -> Billing/Usage before raising any numbers.
Safe to re-run: finished parts are cached in apify_cache/ and skipped.
"""

import csv
import json
import os
import sys

try:
    from apify_client import ApifyClient
except ImportError:
    sys.exit("Run first:  pip install -U apify-client")

# ---------------- Settings ----------------
CITIES = ["Da Nang, Vietnam", "Hoi An, Vietnam", "Hue, Vietnam"]

# What to look for on Google Maps in EVERY city above
GMAPS_SEARCHES = [
    "beachfront resort",
    "beach hotel with sea view",
    "seafood restaurant",
    "Vietnamese restaurant",
    "Indian restaurant",
    "chicken rice",
    "cafe",
    "cooking class",
    "food tour",
    "rooftop bar",
    "night market",
    "spa",
    "tourist attraction",
]
GMAPS_PLACES_PER_SEARCH = 8      # places per search per city
GMAPS_REVIEWS_PER_PLACE = 30     # newest reviews per place
GMAPS_REVIEWS_SINCE = "2024-06-01"

TRIPADVISOR_QUERIES = ["Da Nang", "Hoi An", "Hue"]
TA_PLACES_PER_QUERY = 30         # hotels + restaurants + attractions per city
TA_REVIEW_PLACES = 25            # how many top places (per city) to pull reviews for
TA_REVIEWS_PER_PLACE = 20

RUN_GMAPS = False   # Google Maps now has its own detailed script: gmaps_vietnam_full.py
CACHE = "apify_cache"
# -------------------------------------------

GMAPS_ACTOR = "compass/crawler-google-places"
TA_ACTOR = "maxcopell/tripadvisor"
TA_REVIEWS_ACTOR = "maxcopell/tripadvisor-reviews"


def cached_run(client, key, actor, run_input):
    path = os.path.join(CACHE, key + ".json")
    if os.path.exists(path):
        print(f"  cached: {key}")
        return json.load(open(path, encoding="utf-8"))
    print(f"  running {actor} ... ({key})")
    run = client.actor(actor).call(run_input=run_input)
    if not run or run.get("status") != "SUCCEEDED":
        print(f"  !! run did not succeed: {run.get('status') if run else 'no run'}")
        return []
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    json.dump(items, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"  -> {len(items)} items")
    return items


def write(name, rows):
    if not rows:
        print(f"(nothing for {name})")
        return
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(name, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"Saved {len(rows):6} rows -> {name}")


def slug(s):
    return "".join(ch if ch.isalnum() else "_" for ch in s).strip("_").lower()


def main():
    token = os.environ.get("APIFY_TOKEN") or input("Paste your Apify API token: ").strip()
    client = ApifyClient(token)
    os.makedirs(CACHE, exist_ok=True)

    # ---------- 1. Google Maps ----------
    print("\n1/3 Google Maps" + ("" if RUN_GMAPS else " (skipped - use gmaps_vietnam_full.py)"))
    g_places, g_reviews, seen = [], [], set()
    for city in (CITIES if RUN_GMAPS else []):
        items = cached_run(client, "gmaps_" + slug(city), GMAPS_ACTOR, {
            "searchStringsArray": GMAPS_SEARCHES,
            "locationQuery": city,
            "maxCrawledPlacesPerSearch": GMAPS_PLACES_PER_SEARCH,
            "maxReviews": GMAPS_REVIEWS_PER_PLACE,
            "reviewsSort": "newest",
            "reviewsStartDate": GMAPS_REVIEWS_SINCE,
            "language": "en",
            "scrapeReviewsPersonalData": False,
        })
        for p in items:
            pid = p.get("placeId") or p.get("url")
            if pid in seen:
                continue
            seen.add(pid)
            loc = p.get("location") or {}
            g_places.append({
                "city": city.split(",")[0],
                "search": p.get("searchString"),
                "name": p.get("title"),
                "category": p.get("categoryName"),
                "rating": p.get("totalScore"),
                "reviews_count": p.get("reviewsCount"),
                "price": p.get("price"),
                "hotel_stars": p.get("hotelStars"),
                "address": p.get("address"),
                "lat": loc.get("lat"), "lng": loc.get("lng"),
                "website": p.get("website"),
                "phone": p.get("phone"),
                "permanently_closed": p.get("permanentlyClosed"),
                "maps_url": p.get("url"),
                "place_id": p.get("placeId"),
            })
            for r in p.get("reviews") or []:
                text = r.get("textTranslated") or r.get("text") or ""
                if not text.strip():
                    continue
                g_reviews.append({
                    "city": city.split(",")[0],
                    "place": p.get("title"),
                    "category": p.get("categoryName"),
                    "stars": r.get("stars"),
                    "date": (r.get("publishedAtDate") or "")[:10],
                    "likes": r.get("likesCount"),
                    "text": text.strip(),
                    "owner_reply": (r.get("responseFromOwnerText") or "").strip(),
                    "place_id": p.get("placeId"),
                })
    write("gmaps_places.csv", g_places)
    write("gmaps_reviews.csv", g_reviews)

    # ---------- 2. TripAdvisor places ----------
    print("\n2/3 TripAdvisor places")
    ta_places = []
    for q in TRIPADVISOR_QUERIES:
        items = cached_run(client, "ta_" + slug(q), TA_ACTOR, {
            "query": q,
            "maxItemsPerQuery": TA_PLACES_PER_QUERY,
            "includeHotels": True,
            "includeRestaurants": True,
            "includeAttractions": True,
            "includeTags": True,
            "includeNearbyResults": False,
            "language": "en",
            "currency": "INR",
        })
        for p in items:
            ta_places.append({
                "city": q,
                "type": p.get("type"),
                "name": p.get("name"),
                "rating": p.get("rating"),
                "reviews_count": p.get("numberOfReviews"),
                "ranking": p.get("rankingString") or p.get("rankingPosition"),
                "price_level": p.get("priceLevel"),
                "price_range": p.get("priceRange"),
                "category": p.get("category") or p.get("subcategories"),
                "cuisines": ", ".join(p.get("cuisines") or []) if isinstance(p.get("cuisines"), list) else p.get("cuisines"),
                "address": p.get("address"),
                "url": p.get("webUrl") or p.get("url"),
            })
    write("tripadvisor_places.csv", ta_places)

    # ---------- 3. TripAdvisor reviews for top places ----------
    print("\n3/3 TripAdvisor reviews")
    ta_reviews = []
    for q in TRIPADVISOR_QUERIES:
        city_places = [p for p in ta_places if p["city"] == q and p.get("url")]
        city_places.sort(key=lambda p: (p.get("reviews_count") or 0), reverse=True)
        urls = [{"url": p["url"]} for p in city_places[:TA_REVIEW_PLACES]]
        if not urls:
            continue
        items = cached_run(client, "ta_reviews_" + slug(q), TA_REVIEWS_ACTOR, {
            "startUrls": urls,
            "maxItemsPerQuery": TA_REVIEWS_PER_PLACE,
            "reviewRatings": ["ALL_REVIEW_RATINGS"],
            "reviewsLanguages": ["en"],
        })
        for r in items:
            info = r.get("placeInfo") or {}
            ta_reviews.append({
                "city": q,
                "place": info.get("name"),
                "rating": r.get("rating"),
                "title": r.get("title"),
                "text": (r.get("text") or "").strip(),
                "trip_type": r.get("tripType"),
                "travel_date": r.get("travelDate"),
                "published": (r.get("publishedDate") or "")[:10],
                "helpful_votes": r.get("helpfulVotes"),
                "url": r.get("url"),
            })
    write("tripadvisor_reviews.csv", ta_reviews)

    print("\nDone. Attach the 4 CSV files in the chat.")


if __name__ == "__main__":
    main()
