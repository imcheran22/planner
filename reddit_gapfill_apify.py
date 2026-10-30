"""
Reddit gap-fill for the Vietnam honeymoon (22-28 Jan 2027) - via Apify, no Reddit login.

Your browser scraper (v5) got 270 threads but:
  * 4 threads FAILED (one is "As an Indian tourist visiting Vietnam for two..." - worth having)
  * it was weighted to Hanoi / Phu Quoc / Saigon; Central-Vietnam and plan-specific questions
    (Ba Na fog & coaster, Han River cruise, Asia Park, our hotels, January sea, Indian food,
    e-visa, flights from South India, honeymoon in Da Nang ...) were thin
  * your Reddit account got banned - so this uses Apify's Reddit scraper (its own proxies,
    nothing touches your account or your IP)

How it works (cheapest first, stops when your Apify credit would run out):
  A. the 4 failed threads, with comments
  B. DISCOVERY: ~30 targeted searches, posts only (cheap) -> drops threads you already have
     (all 270 v5 thread IDs are built in), old ones (< 2023-06) and off-topic ones
  C. COMMENTS for the best new threads - as many as your remaining credit allows

Output (same columns as vietnam_reddit_v5.csv, so the two files can be stacked):
  reddit_v6.csv                 threads + comments
  reddit_v6_discovered.csv      every post found in B, with keep/skip reason
  reddit_v6_log.txt

Setup:  pip install -U apify-client
Run:    python reddit_gapfill_apify.py
Cost:   Apify's Reddit scraper is ~$3.4 per 1,000 items (a post or a comment = 1 item).
        A: ~$1.1   B: ~$1.2   C: whatever credit is left (about $0.17 per thread at 50 comments,
        so roughly 15 new threads on a fresh $5 account).
Safe to re-run: every finished step is cached in reddit_cache/.
"""

import csv
import datetime as dt
import hashlib
import getpass
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# =============================== SETTINGS ===============================
ACTOR = "trudax/reddit-scraper-lite"
CACHE = "reddit_cache"
PRICE_PER_ITEM = 0.0034          # USD, estimate (posts and comments each count)
KEEP_CREDIT_USD = 0.05
MAX_NEW_THREADS = 40             # upper limit for step C (credit decides the real number)
COMMENTS_PER_THREAD = 50
POSTS_PER_SEARCH = 10
MIN_DATE = "2023-06-01"
MIN_COMMENTS = 5
PROXY = {"useApifyProxy": True}  # if Reddit returns nothing, try {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]}

FAILED_THREADS = [  # from your v5 log; most useful first
    "https://www.reddit.com/r/VietNam/comments/1poricr/as_an_indian_tourist_visiting_vietnam_for_two/",
    "https://www.reddit.com/r/Vietnam_Tourism/comments/1un74xs/is_ninh_binh_worth_more_than_a_day_trip_my/",
    "https://www.reddit.com/r/backpacking/comments/95nhmb/completed_the_hai_van_pass_on_a_motorbike_vietnam/",
    "https://www.reddit.com/r/travel/comments/7041xz/seen_while_motorbiking_through_the_hai_van_pass/",
]
FAILED_COMMENTS = 80

SUBS_VN = "VietNam+Vietnam_Tourism+VietnamTravelAdvice+DaNang+HoiAn+travel+solotravel+honeymoon+backpacking"
SUBS_IN = "india+IndiaTravel+SoloTravel_India+indiasocial+TravelHacksIndia+Chennai+bangalore+Kerala"
SEARCHES = [  # (query, subreddits)
    ("Da Nang January weather", SUBS_VN), ("Hoi An January", SUBS_VN), ("Hue rain January", SUBS_VN),
    ("Da Nang beach swim waves", SUBS_VN), ("Ba Na Hills fog", SUBS_VN), ("Ba Na Hills worth it", SUBS_VN),
    ("Ba Na alpine coaster", SUBS_VN), ("Golden Bridge cloudy", SUBS_VN),
    ("Han River cruise", SUBS_VN), ("Dragon Bridge fire show", SUBS_VN), ("Asia Park Sun Wheel", SUBS_VN),
    ("Naman Retreat", SUBS_VN), ("Pilgrimage Village Hue", SUBS_VN), ("La Siesta Hoi An", SUBS_VN),
    ("Da Nang ocean view hotel", SUBS_VN), ("An Thuong bars", SUBS_VN), ("Da Nang nightlife couple", SUBS_VN),
    ("Hoi An cooking class", SUBS_VN), ("Hoi An lantern making", SUBS_VN), ("Hue food tour", SUBS_VN),
    ("My Son sunrise", SUBS_VN), ("Hai Van Pass private car", SUBS_VN), ("Hue Da Nang heritage train", SUBS_VN),
    ("Marble Mountains Lady Buddha", SUBS_VN), ("Da Nang honeymoon", SUBS_VN), ("Hoi An honeymoon", SUBS_VN),
    ("Vietnam no pork", SUBS_VN), ("Indian food Da Nang", SUBS_VN), ("halal Da Nang", SUBS_VN),
    ("Vietnam honeymoon", SUBS_IN), ("Da Nang", SUBS_IN), ("Vietnam e-visa", SUBS_IN),
    ("Vietnam trip cost", SUBS_IN), ("Vietnam flight Chennai", SUBS_IN), ("Vietnam food non veg", SUBS_IN),
]
CENTRAL = re.compile(r"hoi ?an|da ?nang|danang|\bhue\b|ba ?na|golden bridge|hai ?van|marble|my son|son tra|an thuong|"
                     r"han river|dragon bridge|asia park|central vietnam|lang co|naman|pilgrimage|la siesta", re.I)
VIETNAM = re.compile(r"vietnam|viet nam|hoi ?an|da ?nang|danang|\bhue\b|hanoi|saigon|ho chi minh|ba ?na|hai ?van", re.I)
PLAN_WORDS = re.compile(r"january|\bjan\b|honeymoon|couple|wife|husband|india|indian|pork|beef|halal|vegetarian|"
                        r"cooking|lantern|coaster|fog|cruise|ocean view|sea view|swim|waves|budget|cost|visa|flight|scam", re.I)

FAILED_IDS = {re.search(r"/comments/([a-z0-9]+)", u).group(1) for u in FAILED_THREADS}
KNOWN_IDS = set("""
10biddl 11tho2h 11xbc4s 13agplc 13h3x8g 13pma5f 13wbr01 14mr1h4 15i60zg 15jaaqe 165wegz 166tort
16877gc 17pxd64 17rzwke 17wbwm9 17yhz1z 18gawes 18hplr5 18hxesa 193vmix 198qdz0 19bzozv 19dltlu
1ahylts 1atn11t 1bgrb4b 1bvpmj5 1cxqb36 1dst0ft 1f4v7ps 1fu4dp0 1gbtw6z 1gonwvj 1gqwy1p 1grpxpg
1h7johm 1hg7k14 1hjemha 1hpquuw 1hxbds2 1i1qypz 1i4b5mi 1id1tl5 1if1esx 1ilf8kn 1iqnldt 1isdr37
1j3qlnb 1j6e3w9 1jbx8p4 1jn3fzc 1jorkpy 1jp9cpu 1k12fe6 1k9xtme 1khnqma 1kl7izs 1kvhre4 1kytbcs
1kz16i6 1l1n75f 1l3c895 1lcxjq3 1le7jm4 1lf4n3o 1lgt26d 1ll5xdj 1loy6fx 1lwc7ly 1lzh5qx 1m6f7x5
1meq56r 1mmgpsd 1mo27a1 1mo5bu3 1mp16b7 1n7rhye 1nikzxm 1np8a73 1nyicwa 1o55ocb 1o76p3p 1o9xcig
1obgl0a 1oc77qk 1oct2w9 1ofpada 1og9i2e 1on7tz3 1or3ca9 1osjngq 1oxwd88 1p1ivbi 1p2ip0o 1p4byyw
1pblkfs 1pc6tuk 1pdxke0 1pjih8v 1plm9wz 1py5ph7 1q01g1s 1q30rnb 1q4an6d 1q8iemm 1q9hroj 1qbpz0v
1qfmq10 1qgzqrq 1qn62a0 1qnll0c 1qqzdht 1qscb1h 1qsuyus 1qtumnc 1qwqqup 1qzkutj 1r0nuhl 1r2hykj
1r5rr3c 1ra0uhj 1ra974f 1rc1vpr 1rdbpvi 1rgpoi0 1rgy6b7 1rjlexs 1rklyr9 1rld765 1rm3t5i 1rm3zfg
1roxda9 1rrdfh4 1rrnbs2 1rw1wk5 1s1lynd 1s5lrh5 1s5rj05 1s770rx 1s8kzj8 1sabk0k 1sam5p3 1sh9r85
1sj20pl 1sjxrfe 1snc7b2 1sqem1x 1srtnig 1sxwvv4 1t0mu25 1t2fn36 1t2fuip 1t62ffb 1t8hd3h 1tdapli
1tfrgca 1tfuz4s 1tfy2u0 1tkbg8a 1tlbik8 1tldn6y 1tnzvfr 1tukbdh 1tuvgor 1tvh0sd 1tzt333 1u4vxh9
1uayeel 1ud9aws 1ugzpas 1upqsq4 1upskea 1usfazk 1ushjii 1uuvee1 1uwiq69 1uyrkjj 1uzvf3k 1v1r99a
1v4y4u6 1v619ou 1v6x8sk 1v7mlfg 1v9qof2 1vaesl5 1vfynu5 1vh3pnk 1vivw68 1vklueu 1vm9452 1vn013m
1vph5o1 1vqg9jm 1vti9us 1vv7sol 1vw7q1c 1vww0cg 1vxzvlg 1vyth14 1vzso1b 1w2dyxq 1w2gzte 1w2h1kt
1w5uedt 1w5vjqf 1w6cceb 1wc1wgo 1wdskpx 1wfjtiy 1wgte7g 1wgwtbq 1wh76hk 1whkfwr 1wi36yu 1wjljgf
1wjlw4a 1wm7q0q 1wmaqjs 1wmdcci 1wn44qn 1wnavh9 1wo03ng 1wo0okv 1wrnw9i 1wrpkqx 1wrpm4z 1ws08s8
1wt5sb5 1wtqid4 1wu87d9 1wvz4wv 1wwclmx 1wx75ol 1wxdn4f 1wymhem 1wzkkmo 1x01ed4 1x1izgs 1x2u5ti
1x3mbuc 1x4jb3c 1x4lc5e 1x5l762 1x5l7tf 1x5m8p0 1x6flch 1x6knoq 1x7dsp4 1x7gjyc 1x7mejp 1x7yrl9
1x84kzs 1x86l1n 1x894j2 1xai2gk 1xanxkj 1xbr8pk 1xcmw3s 1xcsaiq 1xd5jnk 1xdobko 1xe352r 1xex6ii
1xeyyih 1xg2hmx 1xgl9xe 1xgrm85 1xhtbvu 1xix5xc
""".split())
# ======================================================================


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
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def cache_put(key, value):
    os.makedirs(CACHE, exist_ok=True)
    json.dump(value, open(os.path.join(CACHE, key + ".json"), "w", encoding="utf-8"), ensure_ascii=False)


def http_json(url, headers=None):
    try:
        req = urllib.request.Request(url, headers=dict({"User-Agent": "trip-research"}, **(headers or {})))
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8", "ignore"))
        except Exception:
            return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


OUT_OF_CREDIT = re.compile(r"usage limit|hard limit|monthly usage|not enough|insufficient|credit|payment|exceed|402", re.I)


class Apify:
    def __init__(self, token):
        from apify_client import ApifyClient
        self.token, self.client = token, ApifyClient(token)
        self.out, self.reset_at = False, ""

    def remaining(self):
        d = http_json("https://api.apify.com/v2/users/me/limits", headers={"Authorization": f"Bearer {self.token}"})
        try:
            d = d["data"]
            self.reset_at = (d.get("monthlyUsageCycle") or {}).get("endAt", "")[:10]
            return round(d["limits"]["maxMonthlyUsageUsd"] - d["current"]["monthlyUsageUsd"], 3)
        except Exception:
            return None

    def run(self, key, run_input, est_usd, label):
        cached = cache_get(key)
        if cached is not None:
            print(f"   cached: {label} ({len(cached)} items)")
            return cached
        if self.out:
            return None
        left = self.remaining()
        cap = max(0.5, round(est_usd * 1.6, 2))
        if left is not None:
            print(f"   credit left: ${left:.2f}")
            if left - KEEP_CREDIT_USD < max(est_usd, 0.5):
                print(f"   -- not enough credit for '{label}' (~${est_usd:.2f})")
                self.out = True
                return None
            cap = min(cap, max(0.5, round(left - KEEP_CREDIT_USD, 2)))
        print(f"   running {ACTOR} [{label}] est ${est_usd:.2f}, cap ${cap:.2f} ...")
        act = self.client.actor(ACTOR)
        try:
            try:
                run = act.call(run_input=run_input, max_total_charge_usd=cap)
            except TypeError:
                run = act.call(run_input=run_input)
        except Exception as e:
            print(f"   !! {str(e)[:300]}")
            if OUT_OF_CREDIT.search(str(e)):
                self.out = True
            return None
        if isinstance(run, dict):
            status, ds = run.get("status"), run.get("defaultDatasetId")
        else:
            status = getattr(getattr(run, "status", None), "value", getattr(run, "status", None))
            ds = getattr(run, "default_dataset_id", None) or getattr(run, "defaultDatasetId", None)
        items = []
        if ds:
            d = self.client.dataset(ds)
            try:
                items = [dict(x) for x in d.iterate_items()]
            except AttributeError:
                items = list(d.list_items().items)
        if "SUCCEEDED" not in str(status):
            print(f"   !! run status {status} - keeping {len(items)} items")
        if items or "SUCCEEDED" in str(status):
            cache_put(key, items)
        print(f"   -> {len(items)} items")
        return items


def thread_id(url_or_id):
    m = re.search(r"/comments/([a-z0-9]+)", str(url_or_id or ""))
    if m:
        return m.group(1)
    s = str(url_or_id or "")
    return s[3:] if s.startswith("t3_") else s


def plain_id(x):
    s = str(x or "")
    return s.split("_", 1)[1] if re.match(r"^t\d_", s) else s


def date10(x):
    return str(x or "")[:10]


def thread_rows(items, found_via, start_no):
    """Convert actor items (posts + comments) into v5-style rows."""
    posts = {thread_id(i.get("url") or i.get("id")): i for i in items if i.get("dataType") == "post"}
    comments = [i for i in items if i.get("dataType") == "comment"]
    by_id = {plain_id(c.get("id") or c.get("parsedId")): c for c in comments}

    def depth(c):
        d, p, seen = 0, c.get("parentId"), set()
        while p and str(p).startswith("t1_") and plain_id(p) in by_id and p not in seen:
            seen.add(p)
            d += 1
            p = by_id[plain_id(p)].get("parentId")
        return d

    rows, no = [], start_no
    for tid, p in posts.items():
        no += 1
        base = {"thread_no": no, "found_via": found_via, "subreddit": p.get("communityName", "").replace("r/", ""),
                "thread_title": p.get("title"), "thread_date": date10(p.get("createdAt")),
                "thread_score": p.get("upVotes"), "num_comments": p.get("numberOfComments"),
                "thread_url": (p.get("url") or "").split("?")[0]}
        rows.append(dict(base, type="post", depth=0, author=p.get("username"), score=p.get("upVotes"),
                         date=date10(p.get("createdAt")), text=(p.get("body") or "").strip()))
        for c in comments:
            if thread_id(c.get("postId") or c.get("url")) != tid and not str(c.get("url", "")).count(tid):
                continue
            rows.append(dict(base, type="comment", depth=depth(c) + 1, author=c.get("username"), score=c.get("upVotes"),
                             date=date10(c.get("createdAt")), text=(c.get("body") or "").strip()))
    return rows, no


def search_url(q, subs):
    return (f"https://www.reddit.com/r/{subs}/search/?q={urllib.parse.quote(q)}"
            f"&restrict_sr=1&sort=relevance&t=all")


def main():
    sys.stdout = Tee("reddit_v6_log.txt")
    print(f"\n######## Reddit gap-fill via Apify - {dt.datetime.now():%Y-%m-%d %H:%M} ########")
    print(f"   Already have {len(KNOWN_IDS)} threads from v5 - those are skipped.")
    try:
        import apify_client  # noqa: F401
    except ImportError:
        sys.exit("Run first:  pip install -U apify-client")
    token = os.environ.get("APIFY_TOKEN") or getpass.getpass("Paste your Apify API token (hidden, paste + Enter): ").strip()
    ap = Apify(token)
    left = ap.remaining()
    if left is not None:
        print(f"   Credit left on this account: ${left:.2f} (resets {ap.reset_at or 'monthly'})")
    est_a = len(FAILED_THREADS) * (1 + FAILED_COMMENTS) * PRICE_PER_ITEM
    est_b = len(SEARCHES) * POSTS_PER_SEARCH * PRICE_PER_ITEM
    print(f"   Plan: A failed threads ~${est_a:.2f} | B discovery ~${est_b:.2f} | C comments: rest of credit "
          f"(~${(1 + COMMENTS_PER_THREAD) * PRICE_PER_ITEM:.2f} per thread, max {MAX_NEW_THREADS})")
    if input("   Go ahead? (y/n): ").strip().lower() != "y":
        return

    all_rows, no = [], 1000   # thread_no starts at 1001 so it never clashes with v5 numbering

    # ---- A. failed threads
    print("\n=== A. The 4 threads that failed in v5 ===")
    items = ap.run("A_failed", {"startUrls": [{"url": u} for u in FAILED_THREADS], "maxComments": FAILED_COMMENTS,
                                "maxItems": len(FAILED_THREADS) * (1 + FAILED_COMMENTS), "includeNSFW": False,
                                "includeMediaLinks": True, "proxy": PROXY}, est_a, "failed threads")
    if items:
        rows, no = thread_rows(items, "v5 failed link", no)
        all_rows += rows
        print(f"   {len(rows)} rows")

    # ---- B. discovery (posts only)
    print("\n=== B. Discovery searches (posts only) ===")
    items = ap.run(f"B_discovery_{len(SEARCHES)}_{POSTS_PER_SEARCH}",
                   {"startUrls": [{"url": search_url(q, s)} for q, s in SEARCHES], "skipComments": True,
                    "maxPostCount": POSTS_PER_SEARCH, "maxItems": len(SEARCHES) * POSTS_PER_SEARCH,
                    "includeNSFW": False, "includeMediaLinks": True, "proxy": PROXY}, est_b, "discovery (search URLs)")
    if items is not None and not [i for i in items if i.get("dataType") == "post"]:
        print("   search URLs returned no posts - trying plain search terms instead")
        items = ap.run(f"B_discovery_terms_{len(SEARCHES)}_{POSTS_PER_SEARCH}",
                       {"searches": [q for q, _ in SEARCHES], "searchPosts": True, "searchComments": False,
                        "searchCommunities": False, "searchUsers": False, "sort": "relevance", "time": "all",
                        "skipComments": True, "maxPostCount": POSTS_PER_SEARCH,
                        "maxItems": len(SEARCHES) * POSTS_PER_SEARCH, "includeNSFW": False,
                        "includeMediaLinks": True, "proxy": PROXY}, est_b, "discovery (search terms)")
    found, seen = [], set()
    for p in [i for i in (items or []) if i.get("dataType") == "post"]:
        tid = thread_id(p.get("url") or p.get("id"))
        if not tid or tid in seen:
            continue
        seen.add(tid)
        text = f"{p.get('title', '')} {p.get('body', '')} {p.get('communityName', '')}"
        n = p.get("numberOfComments")
        reason = ""
        if tid in KNOWN_IDS or tid in FAILED_IDS:
            reason = "already in v5" if tid in KNOWN_IDS else "fetched in step A"
        elif date10(p.get("createdAt")) and date10(p.get("createdAt")) < MIN_DATE:
            reason = "older than " + MIN_DATE
        elif isinstance(n, int) and n < MIN_COMMENTS:
            reason = f"only {n} comments"
        elif not VIETNAM.search(text):
            reason = "not about Vietnam"
        score = (3 if CENTRAL.search(text) else 0) + len(set(m.lower() for m in PLAN_WORDS.findall(text))) \
            + min(3, (n or 0) // 20)
        found.append({"keep": not reason, "reason": reason, "relevance": score, "thread_id": tid,
                      "subreddit": p.get("communityName"), "title": p.get("title"), "date": date10(p.get("createdAt")),
                      "num_comments": n, "url": (p.get("url") or "").split("?")[0]})
    found.sort(key=lambda r: (not r["keep"], -r["relevance"]))
    if found:
        with open("reddit_v6_discovered.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(found[0]))
            w.writeheader()
            w.writerows(found)
    keep = [r for r in found if r["keep"]]
    print(f"   found {len(found)} posts -> {len(keep)} new & relevant (saved reddit_v6_discovered.csv)")

    # ---- C. comments for the best new threads, as many as credit allows
    print("\n=== C. Comments for the best new threads ===")
    per = (1 + COMMENTS_PER_THREAD) * PRICE_PER_ITEM
    left = ap.remaining()
    n_fit = MAX_NEW_THREADS if left is None else int(max(0, left - KEEP_CREDIT_USD) / (per * 1.15))
    take = keep[:min(MAX_NEW_THREADS, n_fit, len(keep))]
    if take and (left is None or left - KEEP_CREDIT_USD >= 0.5):
        print(f"   credit allows ~{n_fit} threads; taking the top {len(take)} by relevance")
        ids = ",".join(t["thread_id"] for t in take)
        items = ap.run(f"C_comments_{hashlib.md5(ids.encode()).hexdigest()[:10]}_{COMMENTS_PER_THREAD}",
                       {"startUrls": [{"url": t["url"]} for t in take], "maxComments": COMMENTS_PER_THREAD,
                        "maxItems": len(take) * (1 + COMMENTS_PER_THREAD), "includeNSFW": False,
                        "includeMediaLinks": True, "proxy": PROXY}, len(take) * per, f"{len(take)} threads")
        if items:
            rows, no = thread_rows(items, "v6 discovery", no)
            all_rows += rows
            print(f"   {len(rows)} rows")
    elif keep:
        print("   no credit left for comments now - re-run after your credit resets; discovery is cached.")

    if all_rows:
        cols = ["thread_no", "found_via", "subreddit", "thread_title", "thread_date", "thread_score", "num_comments",
                "type", "depth", "author", "score", "date", "text", "thread_url"]
        with open("reddit_v6.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(all_rows)
        print(f"\nSaved {len(all_rows)} rows from {no - 1000} threads -> reddit_v6.csv")
    rest = len(keep) - len(take) if keep else 0
    if rest > 0:
        print(f"{rest} more relevant threads are waiting; re-run after the credit resets ({ap.reset_at or 'next month'}).")
    print("Attach reddit_v6.csv, reddit_v6_discovered.csv and reddit_v6_log.txt in the chat.")


if __name__ == "__main__":
    main()
