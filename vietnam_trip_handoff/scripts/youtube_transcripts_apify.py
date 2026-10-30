"""
YouTube transcripts via Apify - for when YouTube blocks your own internet connection (HTTP 429).

Apify fetches the captions through its own servers, so your block doesn't matter.
Picks the same ~150 relevant videos as vietnam_extra_data_v2.py from youtube_videos.csv.

  Step 1  Apify's own YouTube Scraper (streamers/youtube-scraper), captions only,
          in the video's own language (Tamil/Hindi/Malayalam videos come back in that language;
          Claude can read them).                                    ~ $0.004 per video  (~$0.60 for 150)
  Step 2  for videos that came back without captions: a second transcript scraper
          (devsef/youtube-transcript-scraper), which only charges when it succeeds. ~ $0.002 per video

Works in batches of 50 and saves after each batch, so a stop costs nothing.
Results also go into extra_cache/, so vietnam_extra_data_v2.py treats these videos as done.

Setup:  pip install -U apify-client
Run:    python youtube_transcripts_apify.py      (in the folder with youtube_videos.csv)
Output: youtube_transcripts_v2.csv
"""

import csv
import getpass
import json
import os
import re
import sys
import urllib.error
import urllib.request

# =============================== SETTINGS ===============================
YT_VIDEOS_CSV = "youtube_videos.csv"
CACHE = "extra_cache"
MAX_VIDEOS = 150
BATCH = 50
STEP1_ACTOR = "streamers/youtube-scraper"
STEP1_PRICE = 0.004
STEP2_ACTOR = "devsef/youtube-transcript-scraper"
STEP2_PRICE = 0.003            # $0.002 + a little platform usage
KEEP_CREDIT_USD = 0.05
YT_RELEVANT = (r"hoi ?an|da ?nang|danang|\bhue\b|ba ?na|bana|golden bridge|hai ?van|marble|my son|son tra|"
               r"lady buddha|an thuong|central vietnam|honeymoon|india|indian|tamil|chennai|kochi|budget|"
               r"cost|january|scam|street food|food tour|cooking|lantern|vietnam (travel|trip|itinerary|guide)")
YT_SKIP = r"sapa|sa pa|ha giang|phu quoc|mekong|cat ba|ninh binh|dalat|da lat|mui ne|saigon|ho chi minh|hcmc|nha trang|halong|ha long"
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


def pick_videos():
    path = YT_VIDEOS_CSV
    if not os.path.exists(path):
        path = input(f"Can't find {YT_VIDEOS_CSV} here. Paste its full path: ").strip().strip('"')
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
    return [v for _, v in scored[:MAX_VIDEOS]]


def strip_timed(text):
    """Turn SRT / VTT into plain text."""
    out, last = [], ""
    for line in str(text).splitlines():
        line = line.strip()
        if not line or line.isdigit() or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:")):
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line and line != last:
            out.append(line)
            last = line
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def video_id(s):
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", str(s or ""))
    return m.group(1) if m else (str(s) if re.fullmatch(r"[A-Za-z0-9_-]{11}", str(s or "")) else "")


OUT_OF_CREDIT = re.compile(r"usage limit|hard limit|monthly usage|not enough|insufficient|credit|payment|exceed|402", re.I)


class Apify:
    def __init__(self, token):
        from apify_client import ApifyClient
        self.token, self.client, self.out, self.reset_at = token, ApifyClient(token), False, ""

    def remaining(self):
        d = http_json("https://api.apify.com/v2/users/me/limits", headers={"Authorization": f"Bearer {self.token}"})
        try:
            d = d["data"]
            self.reset_at = (d.get("monthlyUsageCycle") or {}).get("endAt", "")[:10]
            return round(d["limits"]["maxMonthlyUsageUsd"] - d["current"]["monthlyUsageUsd"], 3)
        except Exception:
            return None

    def run(self, actor, run_input, est_usd, label):
        if self.out:
            return None
        left = self.remaining()
        cap = max(0.5, round(est_usd * 1.8, 2))
        if left is not None:
            print(f"   credit left: ${left:.2f}")
            if left - KEEP_CREDIT_USD < max(est_usd, 0.5):
                print(f"   -- not enough credit for {label} (~${est_usd:.2f}; Apify needs $0.50 headroom per run)")
                self.out = True
                return None
            cap = min(cap, max(0.5, round(left - KEEP_CREDIT_USD, 2)))
        print(f"   running {actor} [{label}] est ${est_usd:.2f}, cap ${cap:.2f} ...")
        act = self.client.actor(actor)
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
        print(f"   -> {len(items)} items")
        return items


def ask_token():
    if os.environ.get("APIFY_TOKEN"):
        print("   (ignoring the APIFY_TOKEN saved on this computer - using the token you paste now)")
    for _ in range(3):
        token = getpass.getpass("Paste the Apify API token to use (hidden, paste + Enter): ").strip()
        if not token:
            return None
        me = http_json("https://api.apify.com/v2/users/me", headers={"Authorization": f"Bearer {token}"})
        user = (me.get("data") or {}).get("username") if isinstance(me, dict) else None
        if not user:
            print("   !! Apify did not accept that token - copy it again from console.apify.com -> Settings -> API & Integrations.")
            continue
        ap = Apify(token)
        left = ap.remaining()
        print(f"   Account: {user} | credit left: " + (f"${left:.2f}" if left is not None else "unknown")
              + f" | resets {ap.reset_at or 'monthly'}")
        return ap
    return None


def step1_text(item):
    subs = item.get("subtitles") or []
    if isinstance(subs, dict):
        subs = [subs]
    best = None
    for s in subs:
        if not isinstance(s, dict):
            continue
        raw = s.get("plaintext") or s.get("text") or s.get("srt") or s.get("vtt") or s.get("xml") or ""
        text = strip_timed(re.sub(r"<[^>]+>", " ", raw)) if raw else ""
        if text:
            cand = (text, f"{s.get('type') or 'subtitles'}:{s.get('language') or '?'}", s.get("language") or "")
            if best is None or (str(cand[2]).startswith("en") and not str(best[2]).startswith("en")):
                best = cand
    return best


def main():
    sys.stdout = Tee("youtube_apify_log.txt")
    print("\n######## YouTube transcripts via Apify ########")
    try:
        import apify_client  # noqa: F401
    except ImportError:
        sys.exit("Run first:  pip install -U apify-client")
    vids = pick_videos()
    todo = [v for v in vids if not (cache_get(f"yt_{v['video_id']}") or {}).get("text")]
    print(f"   {len(vids)} relevant videos; {len(vids) - len(todo)} already have a transcript; {len(todo)} to fetch.")
    print(f"   Estimated cost: step 1 ~${len(todo) * STEP1_PRICE:.2f}, step 2 (only misses) up to ~${len(todo) * STEP2_PRICE:.2f}")
    ap = ask_token() if todo else None
    if todo and not ap:
        print("   No usable token - nothing fetched.")
    if ap and input("   Go ahead? (y/n): ").strip().lower() != "y":
        ap = None

    if ap:
        print("\n=== Step 1: Apify YouTube Scraper (captions only) ===")
        for b in range(0, len(todo), BATCH):
            batch = [v for v in todo[b:b + BATCH] if not (cache_get(f"yt_{v['video_id']}") or {}).get("text")]
            if not batch:
                continue
            items = ap.run(STEP1_ACTOR, {
                "startUrls": [{"url": f"https://www.youtube.com/watch?v={v['video_id']}"} for v in batch],
                "maxResults": 1, "maxResultsShorts": 0, "maxResultStreams": 0,
                "transcriptionAndSubtitle": "ALWAYS_SUBTITLES", "subtitlesLanguage": "any",
                "subtitlesFormat": "plaintext", "preferAutoGeneratedSubtitles": False, "saveSubsToKVS": False,
            }, len(batch) * STEP1_PRICE, f"videos {b + 1}-{b + len(batch)}")
            if items is None:
                break
            got = 0
            for it in items:
                vid = video_id(it.get("id")) or video_id(it.get("url"))
                best = step1_text(it)
                if vid and best:
                    cache_put(f"yt_{vid}", {"text": best[0], "source": "apify-yt:" + best[1], "lang": best[2]})
                    got += 1
            print(f"   transcripts saved from this batch: {got} of {len(batch)}")

        miss = [v for v in todo if not (cache_get(f"yt_{v['video_id']}") or {}).get("text")]
        if miss and not ap.out:
            print(f"\n=== Step 2: second transcript scraper for {len(miss)} videos without captions ===")
            for b in range(0, len(miss), BATCH):
                batch = miss[b:b + BATCH]
                items = ap.run(STEP2_ACTOR, {
                    "videoUrls": [f"https://www.youtube.com/watch?v={v['video_id']}" for v in batch],
                    "language": "en", "includeSegments": False,
                }, len(batch) * STEP2_PRICE, f"misses {b + 1}-{b + len(batch)}")
                if items is None:
                    break
                got = 0
                for it in items:
                    vid = video_id(it.get("videoId")) or video_id(it.get("url"))
                    text = (it.get("text") or "").strip()
                    if vid and text and str(it.get("status", "ok")).lower() == "ok":
                        kind = "auto" if it.get("isAutoGenerated") else "manual"
                        cache_put(f"yt_{vid}", {"text": text, "source": f"apify-ts:{kind}:{it.get('language') or '?'}",
                                                "lang": it.get("language") or ""})
                        got += 1
                print(f"   transcripts saved from this batch: {got} of {len(batch)}")

    rows = []
    for v in vids:
        c = cache_get(f"yt_{v['video_id']}") or {}
        rows.append({"video_id": v["video_id"], "title": v.get("title"), "channel": v.get("channel"),
                     "upload_date": v.get("upload_date"), "views": v.get("views"), "url": v.get("url"),
                     "caption_source": c.get("source", "none"), "video_language": c.get("lang", ""),
                     "transcript": c.get("text", "")})
    with open("youtube_transcripts_v2.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    have = sum(1 for r in rows if r["transcript"])
    print(f"\nSaved youtube_transcripts_v2.csv: {have} of {len(rows)} videos have a transcript.")
    if ap and ap.out and have < len(rows):
        print(f"Credit ran short - re-run after it resets ({ap.reset_at or 'next month'}); finished videos are kept.")
    print("Attach youtube_transcripts_v2.csv (and youtube_apify_log.txt if anything failed).")


if __name__ == "__main__":
    main()
