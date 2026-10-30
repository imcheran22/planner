# Vietnam honeymoon (22–28 Jan 2027): project handoff for Claude Code

This folder continues a long claude.ai session (29–30 Oct 2026) that collected travel data, analysed it, and wrote a first itinerary. That session is closed. **Everything you need is in this file and the files listed below.** Read this file fully, then `plan_current.md`, before doing anything.

---

## 1. The user and the trip

- **User:** Cheran G. Lives and works in Bengaluru. Comfortable running Python in a VS Code terminal and JS in the Chrome console. Writes casually and briefly, with typos; wants depth and real data, not generic advice. Laptop is Windows (Chrome, VS Code); paths like `Downloads\yt_cache` came up.
- **Trip:** honeymoon for two (the wedding is 5–6 Dec 2026). **Fri 22 – Thu 28 Jan 2027**, 6 nights in Vietnam, leaving India on an overnight flight on Thu 21 Jan.
- **Home base:** the Coimbatore area. Departing from Chennai, Bengaluru, Trichy or Kochi is acceptable.

### Hard constraints, as the user stated them
| Constraint | Detail |
|---|---|
| Budget | **₹2,00,000 total for two, all-inclusive** (flights, visa, stays, transport, tickets, food) |
| Food | **Non-veg, but no beef and no pork** (both of them) |
| Beach | **One beach-view room**. Agreed as 2 nights in a beach-view room, the rest in cheaper central hotels. The user has since proposed cutting it to **1 beach night** (see §4). |
| Style | Not a stay-in-the-hotel trip. Wants **classes** (cooking, lantern-making), **nightlife**, **meeting new people**, culture, food, fun. |
| Region | "Decide from Reddit". Settled as **Central Vietnam only** (Hoi An, Hue, Da Nang). |
| Wants from the plan | Where to eat, travel, see and stay; where to book; hacks for the best deals. |

### Working preferences (follow these)
- **Use only real numbers from the data.** If a metric has nothing behind it, leave it out; don't estimate it in prose. Label caps and assumptions clearly as caps you control.
- Use plain dates and month ranges ("Aug–Oct 2026"), never "H1 FY26"-style labels.
- Compute with code (pandas) over the CSVs. Don't eyeball.
- Cite sources: subreddit and thread, Google rating and review count (e.g. "4.9, 2,594"), URLs for web facts.
- The user is price-sensitive and asks "does that make sense?". Give a straight recommendation plus the trade-off.

---

## 2. Current plan (v1, written 30 Oct 2026)

The full text is in **`plan_current.md`**, exported from the claude.ai Doc at https://claude.ai/artifact/PVHk8U5ttv5pPemVNgkBoJ. Claude Code cannot edit that Doc. **Write updates to `plan_v2.md`** in this folder; the user can paste them back.

Route: **Hoi An (2 nights) → Hue (2 nights) → Da Nang beach-view (2 nights)**. Estimated total **₹1,83,878**, leaving a **₹16,122** buffer.

| Day | Date | Sleep | Plan |
|---|---|---|---|
| 0 | Thu 21 Jan | flight | Chennai → Da Nang via Kuala Lumpur (AirAsia, ~9h35m, 1 stop) |
| 1 | Fri 22 | Hoi An, La Siesta | Grab from airport (250k–350k VND); Old Town 16:30 (120k VND); lantern boat 18:00 (150k VND per boat); seafood dinner; cocktail bar |
| 2 | Sat 23 | Hoi An | My Son sunrise (150k VND ticket + tour 400k–600k); cooking class with basket boat at 13:30 (Gioan Cookery School, customisable menu); Old Town after 21:00 |
| 3 | Sun 24 | Hue, Pilgrimage Village | Private car Hoi An → Hue (~$70) via Marble Mountains (40k VND), Hai Van Pass, lunch at Lang Co |
| 4 | Mon 25 | Hue | Imperial City + 2 tombs combo (420k VND); Thien Mu at sunset; Hue food tour (~$35 each) or Moon River Cruises |
| 5 | Tue 26 | Da Nang, Naman Retreat ocean view | Heritage train **HĐ1** 07:05 → 10:10 (330k VND, sit on the left); pool; Lady Buddha on Son Tra at sunset; seafood; An Thuong bars |
| 6 | Wed 27 | Da Nang | Ba Na Hills if clear (1,000,000 VND; cable-car ticket valid 72 h from first use since 2026), else beach and spa; rooftop farewell dinner (Gypsy Rooftop) |
| 7 | Thu 28 | — | Sunrise beach walk, Grab to the airport |

### Budget v1 (₹ for two)
| Item | Basis | ₹ |
|---|---|---|
| Flights Chennai ↔ Da Nang via KUL | ₹22,838 return pp, AirAsia, Kayak | 45,676 |
| E-visa + SIM | ₹2,846 pp (Reddit traveller's actual spend); visa $25 on evisa.gov.vn | 5,692 |
| Hoi An hotel, 2 nights | $65/night, La Siesta Google listing | 12,384 |
| Hue hotel, 2 nights | $85/night, Pilgrimage Village Google listing | 16,194 |
| Da Nang beach-view, 2 nights | **CAP** ₹15,000/night (no live price yet) | 30,000 |
| Grab airport → Hoi An | 350k VND | 1,290 |
| Private car Hoi An → Hue | $70 (Reddit couple) | 6,668 |
| Heritage train | 330k VND × 2 | 2,433 |
| Local Grab, Ba Na transfer, airport | **CAP** | 5,000 |
| Hoi An Old Town | 120k VND × 2 | 885 |
| Lantern boat | 150k VND per boat | 553 |
| My Son tour + ticket | (600k + 150k VND) × 2 | 5,531 |
| Marble Mountains | 40k VND × 2 | 295 |
| Hue 3-site combo | 420k VND × 2 | 3,097 |
| Ba Na Hills (optional) | 1,000,000 VND × 2 | 7,374 |
| Cooking class + basket boat | $46 × 2 (Cookly) | 8,764 |
| Hue food tour | ~$35 × 2 (Reddit) | 6,668 |
| Everyday food, 6.5 days | **CAP** ~₹2,770/day | 18,000 |
| Farewell rooftop dinner | 1,000,000 VND pp | 7,374 |
| **Total** | | **1,83,878** |

The buffer (₹16,122) must also cover travel to Chennai, AirAsia checked bags, insurance, massages, tips and shopping. **Bengaluru instead of Chennai** is ₹33,306 return pp on Thai AirAsia via Bangkok, **+₹20,936**.

**Exchange rates (29 Oct 2026):** ₹1 = 271.22 VND; $1 = 25,836.19 VND ≈ ₹95.26. Refresh these before final numbers.

---

## 3. Facts already verified on the web (30 Oct 2026)
- **Tet 2027 = Sat 6 Feb.** The trip is two weeks before Tet, so everything is open. The Hoi An full-moon lantern night is Thu 21 Jan 2027 (missed by one evening). Computed with a lunar library, and matches Reddit.
- **January climate (long-term):** Da Nang 25.0/19.3 °C, 82 mm, 12 rain days, 132 sun hours. Hue 23.5/17.5 °C, 129 mm, 15.5 rain days, 104 sun hours.
- **The Hoi An beaches (Cua Dai, An Bang, Ha My) have seawall construction.** It appears in Maps reviews from Aug–Oct 2026 ("swimming not possible within 1 km"); the project is due in Dec 2026. Hence beach nights go in **Da Nang**.
- **Hai Van Pass:** the Da Nang side is scarred by a new Vingroup resort build (Reddit thread "destroyed by construction", 851 upvotes).
- **Ba Na Hills alpine coasters:** 3 coasters, **not included** in the entry ticket. 70k VND per ride in happy hours (08:30–09:30 and 16:30–17:30), otherwise 100k; 3 rides cost 180k or 250k. They **close in rain, fog or cloud**. Reddit: "go early, after 12 it's mostly cloudy" and "the alpine coaster alone was worth the trip". (hoiandaytrip.com)
- **Asia Park / Sun World Danang Wonders:** opens 15:00–22:00, free entry. Sun Wheel 140k–150k VND; all-rides wristband ~200k. The rides are a modest carnival with a small roller coaster.
- **Han River cruise:** ~45 min, boats at 18:00, 19:00 and 20:00. **The Dragon Bridge fire show is Fri, Sat and Sun at 21:00 only**, so not on the Tue/Wed Da Nang nights. Poseidon cruise only $21.30 pp; Vietnamese dinner set $50.35 pp; chicken/salmon set $58.09 pp. Ask for no pork or beef.
- **VinWonders Nam Hoi An:** 15 km from Hoi An, 650k VND (450k after 14:00), needs 6–8 hours. Its site recommends Feb–Apr. Judged not worth a day here.
- **Sa Pa** was asked about and rejected: 5–6 h from Hanoi, needs 2–3 nights, breaks the beach requirement and the budget, and January is 7–15 °C with bare terraces. The user's real wish was a **coaster ride**, which **Ba Na Hills** covers.
- **Apify terms (section 4.3) forbid one person holding multiple personal accounts.** The earlier session declined to build automatic multi-key rotation and told the user about the suspension risk. Keep the scripts single-token.

---

## 4. Open decisions and pending changes (not yet applied to the plan)
1. **The user proposed one beach-view night instead of two**, freeing money and time for a cruise and theme park plus the coaster. The proposed (not confirmed) rework:
   - **Tue 26:** central/An Thuong hotel (~₹5,500, an estimate). Train arrives 10:10. Lady Buddha. Evening at Asia Park (Sun Wheel) + Han River cruise + An Thuong bars.
   - **Wed 27:** Ba Na Hills at opening, coasters at happy-hour prices, then move to the beach-view room. Farewell dinner, sunrise walk on Thu.
   - Budget effect (v1 caps): saves ~₹9,500. Adds coasters ₹1,844 (3 rides × 2, midday price), Asia Park wristbands ₹1,475, Poseidon cruise-only ₹4,058. Buffer becomes ~₹18,200, or ~₹12,700 with the dinner cruise (₹9,593).
   - **Redo this with the real Booking.com prices** (§5) and the Ba Na fog odds (weather_summary.txt) before recommending.
2. **The partner's passport status is unknown.** The e-visa needs the passport number, and passports need 6 months' validity. This is the most urgent item.
3. Flights: no live fares for the actual dates yet; set alerts.
4. Ba Na Hills go/no-go and which morning, using the weather odds plus the fog/coaster reviews.
5. Which cooking class, My Son operator, Hue food tour and cruise to book, using the GetYourGuide reviews.

---

## 5. Data files (in this folder on the user's laptop)

### Round 1 (29–30 Oct): already analysed for plan v1
| File | Rows | What |
|---|---|---|
| `vietnam_reddit_v5.csv` | 13,934 rows, 270 threads | Columns: `thread_no, found_via, subreddit, thread_title, thread_date, thread_score, num_comments, type(post/comment), depth, author, score, date, text, thread_url`. Skewed toward Hanoi, Phu Quoc and Saigon; Central threads are fewer. |
| `youtube_videos.csv` | 399 | `video_id, title, channel, upload_date, views, likes, comment_count, minutes, language, description, url, found_via, transcript_lang, translated_to_en` |
| `youtube_comments.csv` | 21,722 | Mostly chatter; useful for Indian-traveller tips |
| `youtube_transcripts.csv` | 399 rows, **only 13 with text** | YouTube blocked the rest (see `youtube_transcripts_v2.csv` below) |
| `gmaps_places.csv` | 383 places (332 in the 3 cities) | Rating, reviews, price band, hotel stars, lat/lng, `hotel_prices_seen`, `amenities_and_info`, `hotel_review_summary`, `popular_times`, `place_id`; `group` = stays/food/experiences/nightlife |
| `gmaps_reviews.csv` | 3,555 | ~20 newest reviews per place, with `reviewContext` (trip type, e.g. couple) |
| `gmaps_review_tags.csv` | 2,987 | Google's review keyword chips with counts (e.g. "sea view 26") |
| `gmaps_qna.csv` | 443 | Q&A |
| `gmaps_raw.jsonl` | — | Raw Apify output |

### Round 2 (30 Oct, `vietnam_extra_data_v2.py`): NOT YET ANALYSED, start here
| File | What | Use it for |
|---|---|---|
| `weather_summary.txt`, `weather_summary.csv`, `weather_daily.csv` | Open-Meteo reanalysis, 22–28 Jan for each year 2015–2026, at Hoi An, Hue, Da Nang beach, Ba Na (1,400 m) and Hai Van, plus wave height off Da Nang and Hoi An. Flags: `clouded_morning`, `washout`, `good_day`, `dry_evening`, `rough_over_1_5m`, `calm_under_1m`. | Ba Na go/no-go odds, swim odds, Hue rain swap, lantern-boat evenings. `clouded_morning` is a **proxy** for summit fog, because the grid smooths mountains. |
| `booking_hotels.csv` (slim) / `booking_hotels_full.csv` | Booking.com for the **real dates**: 13 shortlisted hotels plus city discovery searches (Hoi An 22–24, Hue 24–26, Da Nang central 26–27, Da Nang sea-view finder 27–28). Columns include `cheapest_room_price`, `cheapest_sea_view_price` (INR, **for the whole stay as listed**), `sea_view_room_types`, `booking_rating`. | Replace the ₹15,000 cap and the other hotel lines with real prices. Check whether "price" is for the whole stay or per night by comparing nights=1 and nights=2 blocks. |
| `booking_rooms.csv` | Every room type with price, availability and a `sea_view` flag | Find the cheapest **true** ocean-view room at Naman, Pullman, Furama, TMS, Chicland, etc. |
| `booking_sea_view_options.csv` | **Was NOT written in the user's run.** The filter is: Da Nang block + rating ≥ 8.5 + a sea-view room with a price. | Check why (empty `rooms`? ratings on a different scale? `sea_view` regex misses?). Rebuild it from `booking_rooms.csv`. |
| `booking_reviews.csv` | Newest ~50 Booking reviews per shortlisted hotel since 2025-01-01 (`customData.hotel`, rating, traveller type, room info, liked/disliked) | Couple-specific pros and cons; whether "ocean view" rooms really face the sea |
| `gmaps_deep_reviews.csv` | Google reviews since 2025-06-01: 42 plan places (`dig = plan places`, `plan_name`), 10 big sights by search, and **keyword digs**: Ba Na "fog", "coaster" and "cloud"; Naman "ocean view"; Hoi An Old Town "January" (`keyword` column) | Ba Na fog/coaster experience by month posted; restaurant pork/beef issues; recent quality changes |
| `gyg_reviews.csv` | GetYourGuide reviews for 35 tours (`tour_category`: cooking class, lantern class, Hoi An food tour, My Son sunrise, Ba Na tour/ticket, Han River cruise, Marble + Lady Buddha, Hue food tour, Hue Imperial City + tombs, Hai Van private car) with `travelerType` | Pick operators: menu flexibility for chicken/seafood, pickup reliability, weather cancellations |
| `x_posts.csv` | Up to 1,000 X posts since Jun 2024 | Low weight; scan for recent closures, scams, events |
| `extra_data_log.txt` | Run log | Check what was skipped or failed |

### Round 3: scripts given to the user, may or may not have been run yet
| File | What |
|---|---|
| `youtube_transcripts_v2.csv` | From `youtube_transcripts_apify.py`: captions for the 150 most relevant videos via Apify. **Tamil, Hindi, Malayalam and Telugu videos come back in the original language**, so translate them while analysing. `caption_source` shows the track. |
| `vietnam_reddit_v6.csv` | From the console script `reddit_vietnam_v6_console.js`: 4 failed threads + ~50 new Central/plan-specific threads. `thread_no` starts at 1001, so stack it with v5 directly. |
| `reddit_v6.csv`, `reddit_v6_discovered.csv` | From `reddit_gapfill_apify.py` (the Apify alternative), same columns |

---

## 6. Scripts (in `scripts/`) and their status
| Script | Status / notes |
|---|---|
| `reddit_vietnam_v5.js` | Done (270 threads). **The user's Reddit account was then banned** (2 s delay was too fast). |
| `reddit_vietnam_v6_console.js` | New. Slow (6–9 s), stops after 3 refusals and saves; `saveV6()` saves early. All 270 v5 thread IDs are built in. |
| `reddit_gapfill_apify.py` | New, Apify alternative (no Reddit account or IP). ~$1.1 failed threads + ~$1.2 discovery + rest of credit for comments. |
| `youtube_vietnam.py` | Done (399 videos). Transcripts blocked after ~12. |
| `youtube_transcripts_apify.py` | New. `streamers/youtube-scraper` with `transcriptionAndSubtitle: ALWAYS_SUBTITLES`, `subtitlesLanguage: any`, `subtitlesFormat: plaintext`; falls back to `devsef/youtube-transcript-scraper`. ~$0.004/video. |
| `gmaps_vietnam_full.py` | Done (lite mode). Has the apify-client v3 fixes. |
| `vietnam_extra_data.py` | v1, superseded by v2. |
| `vietnam_extra_data_v2.py` | Ran: weather, Booking, Google Maps deep, Booking reviews, GetYourGuide, X all done. YouTube part hit **HTTP 429 on the first video** (YouTube is blocking the user's IP), so use the Apify YouTube script instead. Asks for the token every run and shows account and credit; checks remaining credit before every job; caches everything in `extra_cache/`. |
| `tripadvisor_vietnam.py`, `maps_tripadvisor_vietnam.py` | Never run; the user said to leave TripAdvisor out. |
| `helpers/area.py` | `area(lat, lng)` → named zone (Hue, Son Tra, My Khe/An Thuong, city centre, Non Nuoc, An Bang/Ha My, Cua Dai, Hoi An old town, Ba Na, My Son, ...) |
| `helpers/rshow.py` | `python rshow.py 12,45 10`: prints the top comments of Reddit thread numbers |
| `helpers/ytshow.py` | `python ytshow.py "ba na" 8`: top YouTube comments for videos whose title matches |
| `notes/v1_findings.md` | Early Reddit findings (21 threads), with thread references T1–T21 |
| `notes/known_reddit_ids.txt` | The 270 v5 thread IDs |

### Apify gotchas learned the hard way
- `apify-client` v3 returns a **Run object, not a dict**. Use the `run_info()` / `dataset_items()` helpers in the scripts. The first paid Maps run was lost to this bug and recovered via run id `Hudc9Pl9HbDkfFldI`.
- The **minimum `max_total_charge_usd` per run is $0.50**. A job can't start with less than $0.50 of credit left.
- Credit: the user's current account had used ~$1.25 of $5 by the end of round 2 (≈$3.75 left before the YouTube/Reddit Apify scripts). One account's cycle **resets on 2026-11-29**.
- **Apify tokens were pasted into logs twice. Remind the user to regenerate them.** Never print or store tokens; the scripts use `getpass`.
- Don't build multi-account key rotation (Apify ToS 4.3).

---

## 7. What to do next (suggested order)
1. **Inventory:** list which round-2/3 files exist in this folder, with row counts. Read `extra_data_log.txt` for skips and failures.
2. **Weather** → `weather_summary.txt`:
   - Ba Na clouded-morning odds for 26/27 Jan, and persistence (if the 26th is clouded, how likely is the 27th).
   - Wave odds over 1.5 m (swim or not).
   - Hue washout odds.
   - Hoi An dry-evening odds.
   - Hai Van on the 24th.
3. **Hotels** → Booking files:
   - Real prices for La Siesta (22–24), Pilgrimage Village (24–26) and the Da Nang beach-view options (27–28).
   - The cheapest well-rated **true sea-view** rooms; rebuild the missing `booking_sea_view_options.csv`.
   - A central/An Thuong hotel for 26–27.
   - Decide 1 vs 2 beach nights with real numbers.
   - Cross-check with `booking_reviews.csv` (couples, room-view complaints).
4. **Ba Na decision** → `gmaps_deep_reviews.csv` keyword digs (fog/coaster/cloud by month) + weather odds + GetYourGuide Ba Na reviews → go/no-go rule and which morning.
5. **Activities** → `gyg_reviews.csv`: pick the cooking class (evidence of a chicken/seafood-only menu), lantern class, My Son sunrise operator, Han River cruise (food content, karaoke noise, which boat for river views), Hue food tour, and Hai Van car. Note pickup reliability and weather cancellations.
6. **Restaurants** → `gmaps_deep_reviews.csv` (plan places): recent ratings, any decline, pork/beef/halal mentions, prices.
7. **YouTube transcripts / Reddit v6** (if present): extract prices, routes and January experiences; translate non-English transcripts; stack Reddit v6 under v5.
8. **Write `plan_v2.md`:**
   - Same structure as `plan_current.md`, with the Day 5–7 rework if the data supports it.
   - Recompute the budget with real prices, refreshed exchange rates and caps labelled.
   - Keep the "Eating without pork or beef" section.
   - Update the checklist (passport first).
   - Put a short "What changed from v1 and why" at the top.
9. Keep chat replies short; the plan file is the deliverable.

## 8. Style for plan_v2.md
- Plain English, second person ("you"), short sentences, tables for comparisons and the budget.
- Every price says its source and whether it is a quote, a listing for the real dates, or a cap.
- Ratings in brackets as Google stars and review count, e.g. "(4.9, 2,594)".
- No invented numbers. If the data doesn't cover something, say "not collected" and give the action (e.g. "ask for a quote on WhatsApp").
