"""
Vietnam trip research: DETAILED Google Maps extraction (Da Nang, Hoi An, Hue) via Apify.
One run collects everything needed for the itinerary, so you shouldn't have to repeat it.

What you get
  gmaps_places.csv       every place: rating, review count, star split (1-5), price level, hotel stars,
                         category, address, lat/lng, opening hours, amenities, phone, website, map link
  gmaps_reviews.csv      reviews with stars, date, likes, owner reply, AND trip context
                         (e.g. "Travel group: Couple", "Trip type: Vacation") + sub-ratings (Rooms/Service/Location)
  gmaps_review_tags.csv  Google's review keywords per place with counts (e.g. "beach 210", "breakfast 95")
  gmaps_qna.csv          questions & answers on each place
  gmaps_raw.jsonl        every field Apify returned (backup, so nothing is lost)

Groups searched in each city: STAYS, FOOD, EXPERIENCES, NIGHTLIFE (lists below).

Setup:  pip install -U apify-client      then:  python gmaps_vietnam_full.py
It shows an estimated cost and asks before spending anything.
Safe to stop/re-run: each finished (group, city) is cached in gmaps_cache/ and skipped.
"""

import csv
import json
import os
import sys

try:
    from apify_client import ApifyClient
except ImportError:
    sys.exit("Run first:  pip install -U apify-client")

# ------------------------------------------------------------------
# MODE: "lite" fits inside Apify's free monthly credit (~$5).
#       "full" is about 2-3x deeper (more places, more reviews), ~$13, needs more than the free credit.
MODE = "lite"
# ------------------------------------------------------------------

CITIES = ["Da Nang, Vietnam", "Hoi An, Vietnam", "Hue, Vietnam"]

GROUPS = {
    "stays": {
        "searches": {
            "Da Nang, Vietnam": ["beachfront resort", "beach resort", "resort with ocean view room",
                                 "5 star hotel", "boutique hotel", "honeymoon resort", "villa with private pool"],
            "Hoi An, Vietnam": ["beachfront resort", "beach resort An Bang", "resort Cua Dai beach",
                                "boutique hotel", "honeymoon resort", "villa with private pool"],
            "Hue, Vietnam": ["riverside resort", "boutique hotel", "5 star hotel"],
        },
        "lite": (6, 25), "full": (12, 50),      # (places per search, reviews per place)
        "sort": "newest", "since": "2025-01-01",
    },
    "food": {
        "searches": ["seafood restaurant", "Vietnamese restaurant", "street food", "banh mi",
                     "chicken rice", "Indian restaurant", "halal restaurant", "fine dining",
                     "romantic dinner restaurant", "cafe with view", "coffee shop", "dessert"],
        "lite": (4, 8), "full": (8, 15),
        "sort": "mostRelevant", "since": None,
    },
    "experiences": {
        "searches": ["cooking class", "food tour", "lantern making workshop", "spa massage",
                     "jeep tour", "motorbike tour", "boat tour", "tourist attraction",
                     "museum", "pagoda", "viewpoint", "beach"],
        "lite": (3, 8), "full": (6, 12),
        "sort": "mostRelevant", "since": None,
    },
    "nightlife": {
        "searches": ["rooftop bar", "beach bar", "cocktail bar", "live music bar",
                     "night market", "nightclub"],
        "lite": (3, 6), "full": (5, 10),
        "sort": "mostRelevant", "since": None,
    },
}

QUESTIONS_PER_PLACE = 5
CACHE = "gmaps_cache"
ACTOR = "compass/crawler-google-places"

# Apify prices for this actor (free plan, per item) - used only for the estimate
PRICE_PLACE, PRICE_DETAILS, PRICE_REVIEW = 0.004, 0.002, 0.0005


def searches_for(group, city):
    s = GROUPS[group]["searches"]
    return s.get(city, []) if isinstance(s, dict) else s


def estimate():
    total_places = total_reviews = 0
    for g, cfg in GROUPS.items():
        per, revs = cfg[MODE]
        for city in CITIES:
            n = len(searches_for(g, city)) * per
            total_places += n
            total_reviews += n * revs
    cost = total_places * (PRICE_PLACE + PRICE_DETAILS) + total_reviews * PRICE_REVIEW
    return total_places, total_reviews, cost


def slug(s):
    return "".join(ch if ch.isalnum() else "_" for ch in s).strip("_").lower()


def run_actor(client, run_input, budget):
    actor = client.actor(ACTOR)
    try:
        return actor.call(run_input=run_input, max_total_charge_usd=budget)
    except TypeError:  # older apify-client without budget cap
        return actor.call(run_input=run_input)


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


# Runs that already finished (and were paid for) but weren't saved because of the earlier bug
RECOVER = {"stays_da_nang__vietnam_lite": "Hudc9Pl9HbDkfFldI"}


def j(v):
    return json.dumps(v, ensure_ascii=False) if v not in (None, "", [], {}) else ""


def main():
    places_n, reviews_n, cost = estimate()
    print(f"MODE = {MODE}")
    print(f"Up to ~{places_n} places and ~{reviews_n} reviews (fewer in practice, duplicates overlap).")
    print(f"Estimated maximum cost: ~${cost:.2f}  (Apify free plan includes ~$5 credit per month)")
    if input("Continue? (y/n): ").strip().lower() != "y":
        return

    import getpass
    token = os.environ.get("APIFY_TOKEN") or getpass.getpass("Paste your Apify API token (hidden, just paste + Enter): ").strip()
    client = ApifyClient(token)
    os.makedirs(CACHE, exist_ok=True)

    all_items = []
    for g, cfg in GROUPS.items():                    # stays first = most important
        per, revs = cfg[MODE]
        for city in CITIES:
            searches = searches_for(g, city)
            if not searches:
                continue
            key = f"{g}_{slug(city)}_{MODE}"
            path = os.path.join(CACHE, key + ".json")
            if not os.path.exists(path) and key in RECOVER:
                try:
                    _, ds = run_info(client.run(RECOVER[key]).get())
                    items = dataset_items(client, ds)
                    if items:
                        json.dump(items, open(path, "w", encoding="utf-8"), ensure_ascii=False)
                        print(f"recovered {key}: {len(items)} places from earlier run (no extra cost)")
                except Exception as e:
                    print(f"could not recover earlier run ({e}); will run again")
            if os.path.exists(path):
                items = json.load(open(path, encoding="utf-8"))
                print(f"cached   {key}: {len(items)} places")
            else:
                run_input = {
                    "searchStringsArray": searches,
                    "locationQuery": city,
                    "maxCrawledPlacesPerSearch": per,
                    "language": "en",
                    "scrapePlaceDetailPage": True,
                    "maxReviews": revs,
                    "reviewsSort": cfg["sort"],
                    "maxQuestions": QUESTIONS_PER_PLACE,
                    "scrapeReviewsPersonalData": False,
                }
                if cfg["since"]:
                    run_input["reviewsStartDate"] = cfg["since"]
                budget = max(0.5, round(len(searches) * per * (PRICE_PLACE + PRICE_DETAILS + revs * PRICE_REVIEW) * 1.3 + 0.05, 2))  # Apify minimum cap is $0.50
                print(f"running  {key}: {len(searches)} searches x {per} places, {revs} reviews each (cap ${budget})")
                run = run_actor(client, run_input, budget)
                status, ds = run_info(run)
                items = dataset_items(client, ds)
                if "SUCCEEDED" in status or items:
                    json.dump(items, open(path, "w", encoding="utf-8"), ensure_ascii=False)
                print(f"         -> {status}, {len(items)} places")
                if "SUCCEEDED" not in status and not items:
                    print("         !! Stopped. Probably out of credit - re-run later; finished parts are kept.")
                    break
            for it in items:
                it["_group"], it["_city"] = g, city.split(",")[0]
            all_items += items

    # ---------- Build output files ----------
    places, reviews, tags, qna, seen = [], [], [], [], {}
    with open("gmaps_raw.jsonl", "w", encoding="utf-8") as raw:
        for p in all_items:
            raw.write(json.dumps(p, ensure_ascii=False) + "\n")
            pid = p.get("placeId") or p.get("url")
            if pid in seen:                          # same place found by several searches
                seen[pid]["found_by"] += f" | {p.get('_group')}: {p.get('searchString')}"
                continue
            loc = p.get("location") or {}
            dist = p.get("reviewsDistribution") or {}
            hours = p.get("openingHours") or []
            row = {
                "group": p.get("_group"), "city": p.get("_city"),
                "found_by": f"{p.get('_group')}: {p.get('searchString')}",
                "name": p.get("title"), "category": p.get("categoryName"),
                "all_categories": ", ".join(p.get("categories") or []),
                "rating": p.get("totalScore"), "reviews_count": p.get("reviewsCount"),
                "five_star": dist.get("fiveStar"), "four_star": dist.get("fourStar"),
                "three_star": dist.get("threeStar"), "two_star": dist.get("twoStar"),
                "one_star": dist.get("oneStar"),
                "price": p.get("price"), "hotel_stars": p.get("hotelStars"),
                "neighborhood": p.get("neighborhood"), "street": p.get("street"),
                "address": p.get("address"), "lat": loc.get("lat"), "lng": loc.get("lng"),
                "opening_hours": "; ".join(f"{h.get('day')}: {h.get('hours')}" for h in hours if isinstance(h, dict)),
                "temporarily_closed": p.get("temporarilyClosed"),
                "permanently_closed": p.get("permanentlyClosed"),
                "phone": p.get("phone"), "website": p.get("website"),
                "description": p.get("description") or p.get("hotelDescription"),
                "amenities_and_info": j(p.get("additionalInfo")),
                "hotel_review_summary": j(p.get("hotelReviewSummary")),
                "hotel_prices_seen": j(p.get("hotelAds")),
                "popular_times": j(p.get("popularTimesHistogram")),
                "images_count": p.get("imagesCount"),
                "maps_url": p.get("url"), "place_id": p.get("placeId"),
            }
            seen[pid] = row
            places.append(row)

            for t in p.get("reviewsTags") or []:
                tags.append({"city": row["city"], "place": row["name"], "group": row["group"],
                             "tag": t.get("title"), "count": t.get("count")})
            for q in p.get("questionsAndAnswers") or []:
                answers = q.get("answer") or q.get("answers") or ""
                qna.append({"city": row["city"], "place": row["name"],
                            "question": q.get("question"), "answer": j(answers) if not isinstance(answers, str) else answers})
            for r in p.get("reviews") or []:
                text = (r.get("textTranslated") or r.get("text") or "").strip()
                ctx = r.get("reviewContext") or {}
                if not text and not ctx:
                    continue
                reviews.append({
                    "city": row["city"], "group": row["group"], "place": row["name"],
                    "category": row["category"], "place_rating": row["rating"],
                    "stars": r.get("stars"), "date": (r.get("publishedAtDate") or "")[:10],
                    "likes": r.get("likesCount"),
                    "reviewer_total_reviews": r.get("reviewerNumberOfReviews"),
                    "local_guide": r.get("isLocalGuide"),
                    "trip_context": j(ctx),
                    "sub_ratings": j(r.get("reviewDetailedRating")),
                    "photos": len(r.get("reviewImageUrls") or []),
                    "text": text,
                    "owner_reply": (r.get("responseFromOwnerText") or "").strip(),
                    "place_id": row["place_id"],
                })

    def write(name, rows):
        if not rows:
            print(f"(nothing for {name})")
            return
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with open(name, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
        print(f"Saved {len(rows):6} rows -> {name}")

    print()
    write("gmaps_places.csv", places)
    write("gmaps_reviews.csv", reviews)
    write("gmaps_review_tags.csv", tags)
    write("gmaps_qna.csv", qna)
    print("Saved gmaps_raw.jsonl (all fields)")
    print("\nDone. Attach the 4 CSV files (and gmaps_raw.jsonl if it is under ~30 MB) in the chat.")


if __name__ == "__main__":
    main()