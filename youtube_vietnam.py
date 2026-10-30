"""
Vietnam trip research: YouTube videos -> 3 CSV files (no API key needed).

  youtube_videos.csv       one row per video: title, channel, date, views, likes, duration, description
  youtube_transcripts.csv  one row per video: full spoken transcript (translated to English if needed)
  youtube_comments.csv     top comments + replies for every video

How to run (VS Code terminal, Windows):
    pip install -U yt-dlp youtube-transcript-api
    python youtube_vietnam.py

Safe to stop and re-run: finished videos are cached in the yt_cache folder and skipped.
Takes roughly 20-40 minutes for ~150 videos. Leave it running.
"""

import csv
import json
import os
import random
import re
import sys
import time
from datetime import datetime

try:
    import yt_dlp
except ImportError:
    sys.exit("Run first:  pip install -U yt-dlp youtube-transcript-api")
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    sys.exit("Run first:  pip install -U yt-dlp youtube-transcript-api")

# ---------------- Settings ----------------
MAX_COMMENTS = 300            # top comments per video (plus some replies)
SEARCH_RESULTS_PER_QUERY = 12 # extra videos found per search below
MIN_UPLOAD = "20240101"       # skip searched videos older than this (yyyymmdd)
MIN_MINUTES, MAX_MINUTES = 4, 75
CACHE = "yt_cache"

# Your links
LINKS = """
https://youtu.be/KuKHih_QwhM
https://youtu.be/6496pZT94_k
https://youtu.be/owZaKB_cf98
https://youtu.be/-xQrA0RaAvA
https://youtu.be/HjNyj2q_FVU
https://www.youtube.com/watch?v=TJIrdahQJ6s
https://www.youtube.com/watch?v=ZDdzNZnSBoM
https://www.youtube.com/watch?v=2hkYu5EQ8t8
https://www.youtube.com/watch?v=IQANyRw3wq0
https://www.youtube.com/watch?v=cmLx-bNeySs
https://www.youtube.com/watch?v=3UXnhiGbnh0
https://www.youtube.com/watch?v=MzXydAHhO3w
https://www.youtube.com/watch?v=6pM1DWpRBSM
https://www.youtube.com/watch?v=Hfe4SFTM7K8
https://www.youtube.com/watch?v=Wllog2Wmeu0
https://www.youtube.com/watch?v=jsMr3tclN60
https://www.youtube.com/watch?v=sOq6NOTKEOQ
https://www.youtube.com/watch?v=RpPJru6vFCk
https://www.youtube.com/watch?v=th_eS7Xub-s
https://www.youtube.com/watch?v=fpb65B-89yQ
https://www.youtube.com/watch?v=nBQ-Q6F9I8M
https://www.youtube.com/watch?v=hGBsgkQlJL4
https://www.youtube.com/watch?v=bYzFgfuyZ7s
https://www.youtube.com/watch?v=Rd-iJYyYQv8
https://www.youtube.com/watch?v=828isg9kL4o
https://www.youtube.com/watch?v=Fum7CNbaXa8
https://www.youtube.com/watch?v=hlOSSy9hhgs
https://www.youtube.com/watch?v=AXVYSL9mjyw
https://www.youtube.com/watch?v=e-wXB9uuEYY
https://www.youtube.com/watch?v=9b90vmWLls0
https://www.youtube.com/watch?v=O5TvCD7capI
https://www.youtube.com/watch?v=RP3i48A5Z2I
https://www.youtube.com/watch?v=vb93PCX9rZk
https://www.youtube.com/watch?v=VqqIKvgFCSI
https://www.youtube.com/watch?v=Z6dJHYC0jbg
https://www.youtube.com/watch?v=ubO8bQGd2YA
https://www.youtube.com/watch?v=H6WU9E5MQAs
https://www.youtube.com/watch?v=Txafsp1ebos
https://www.youtube.com/watch?v=KZ_9uMC5ueM
https://www.youtube.com/watch?v=7vdmzzDr-88
https://www.youtube.com/watch?v=sXP090OGA2Q
https://www.youtube.com/watch?v=6JqFb69I-2Q
https://www.youtube.com/watch?v=DkF4ON_F_xo
https://www.youtube.com/watch?v=srrvyT_IKvQ
https://www.youtube.com/watch?v=qfp51wVghEo
https://www.youtube.com/watch?v=1fQx9bKYHI8
https://www.youtube.com/watch?v=waqiOfMlwKY
https://www.youtube.com/watch?v=F2hYr47RRI8
https://www.youtube.com/watch?v=c8IoyMNy624
https://www.youtube.com/watch?v=aqdQYeqN_Os
https://www.youtube.com/watch?v=s7BAF-x9OCg
https://www.youtube.com/watch?v=xJc4PeR5Zdg
https://www.youtube.com/watch?v=ndETf3JuLcA
https://www.youtube.com/watch?v=WI6Z676BL00
https://www.youtube.com/watch?v=TMjaPAwaY6o
https://www.youtube.com/watch?v=P4aTv994wxI
https://www.youtube.com/watch?v=LyZiCa7LBmA
https://www.youtube.com/watch?v=1W63cN9TYxg
https://www.youtube.com/watch?v=lisg09Tb2IM
https://www.youtube.com/watch?v=M48WoJNPH0s
https://www.youtube.com/watch?v=j9ku_T-lwhc
https://www.youtube.com/watch?v=OfLWoRJ9pBo
https://www.youtube.com/watch?v=nKdMZ7jcYV4
https://www.youtube.com/watch?v=0vpEWnroJRc
https://www.youtube.com/watch?v=zi8eOw77TDw
https://www.youtube.com/watch?v=aHFiHD3Ij84
https://www.youtube.com/watch?v=__labQD_JM4
https://www.youtube.com/watch?v=FoqRiJuiglU
https://www.youtube.com/watch?v=S7CwSY1Kf_k
https://www.youtube.com/watch?v=Ke8ESh2XCgw
https://www.youtube.com/watch?v=5UuF-K3s4vY
https://www.youtube.com/watch?v=R9K1XpWZ98o
https://www.youtube.com/watch?v=7M2K5Xq8P1A
https://www.youtube.com/watch?v=3N5K8Wl9Q2Z
https://www.youtube.com/watch?v=8P2L4Mv7X0Y
https://www.youtube.com/watch?v=9X3K7Np1V4M
https://www.youtube.com/watch?v=1W8M5Kl2Z6X
https://www.youtube.com/watch?v=4Q7N9Xp3L2V
https://www.youtube.com/watch?v=6K2P1Lm8X5Y
https://www.youtube.com/watch?v=2V5X8Nt4M1Q
https://www.youtube.com/watch?v=7L9M3Kp2X6W
https://www.youtube.com/watch?v=3X4N6Vl1P8Y
https://www.youtube.com/watch?v=5K8P2Lm7X9Z
https://www.youtube.com/watch?v=1Q3M7Xv4N2K
https://www.youtube.com/watch?v=9V2L5Kp8X6W
https://www.youtube.com/watch?v=4X6N1Lm3P7Y
https://www.youtube.com/watch?v=8K3P9Vv2X4M
https://www.youtube.com/watch?v=2M5X7Kt1L9Q
https://www.youtube.com/watch?v=6L1P8Vv3X2W
https://www.youtube.com/watch?v=3V4M6Kp9X5Y
https://www.youtube.com/watch?v=7X2N1Lm4P8Z
https://www.youtube.com/watch?v=5Q3P8Vv2X6K
https://www.youtube.com/watch?v=1K9M4Kp7X3W
https://www.youtube.com/watch?v=9X2N6Lm1P5Y
https://www.youtube.com/watch?v=4V3P8Vv7X2M
https://www.youtube.com/watch?v=8M1X5Kp9L6Q
https://www.youtube.com/watch?v=2K7N3Lm4P1W
https://www.youtube.com/watch?v=6X4P9Vv8X2Y
https://www.youtube.com/watch?v=3L5M2Kp1X7Z
https://www.youtube.com/watch?v=7V8N4Lm6P3K
https://www.youtube.com/watch?v=1X3P9Vv5X4W
https://www.youtube.com/watch?v=5M2X7Kp8L9Y
https://www.youtube.com/watch?v=9K4N1Lm3P2Q
https://www.youtube.com/watch?v=4X5P8Vv6X1Z
https://www.youtube.com/watch?v=8L3M2Kp7X5W
https://www.youtube.com/watch?v=2V9N6Lm4P1Y
https://www.youtube.com/watch?v=6K1P3Vv8X7M
https://www.youtube.com/watch?v=3X8M5Kp2L4Q
https://www.youtube.com/watch?v=7Y2N4Lm1P9Z
https://www.youtube.com/watch?v=5V6P9Vv3X2K
"""

# Extra searches: the script finds the best recent videos for each and adds them
SEARCHES = [
    "Vietnam honeymoon itinerary from India",
    "Vietnam trip from India budget 2026",
    "Da Nang Hoi An Hue itinerary 7 days",
    "Central Vietnam itinerary couple",
    "Da Nang in January weather",
    "Hoi An in January",
    "Da Nang beachfront resort review",
    "Hoi An beach resort review",
    "Hoi An cooking class",
    "Hoi An lantern night boat",
    "Ba Na Hills Golden Bridge worth it",
    "My Son Sanctuary Hoi An",
    "Hue Imperial City tour",
    "Hai Van Pass jeep or motorbike tour",
    "Hue to Da Nang train",
    "Marble Mountains Da Nang",
    "Son Tra peninsula Lady Buddha",
    "Da Nang nightlife",
    "Da Nang seafood restaurant",
    "Hoi An food tour",
    "Vietnam food for Indians",
    "Indian food in Da Nang",
    "Vietnam scams tourists 2026",
    "Vietnam travel tips first time Indian",
    "Vietnam e-visa for Indians",
    "Vietnam vlog Tamil",
    "Vietnam vlog Malayalam",
    "Vietnam honeymoon vlog Hindi",
]
# -------------------------------------------


def video_id(url):
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None


def cache_path(vid):
    return os.path.join(CACHE, vid + ".json")


def search_more(seen):
    found = []
    opts = {"quiet": True, "skip_download": True, "extract_flat": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        for q in SEARCHES:
            try:
                res = ydl.extract_info(f"ytsearch{SEARCH_RESULTS_PER_QUERY * 2}:{q}", download=False)
            except Exception as e:
                print(f"  search failed: {q} ({e})")
                continue
            added = 0
            for e in res.get("entries") or []:
                vid = e.get("id")
                dur = (e.get("duration") or 0) / 60
                if not vid or vid in seen:
                    continue
                if dur and not (MIN_MINUTES <= dur <= MAX_MINUTES):
                    continue
                seen.add(vid)
                found.append((vid, "search: " + q))
                added += 1
                if added >= SEARCH_RESULTS_PER_QUERY:
                    break
            print(f"  '{q}': +{added}")
            time.sleep(1)
    return found


def get_transcript(vid):
    langs = ["en", "en-IN", "en-US", "en-GB"]
    try:
        if hasattr(YouTubeTranscriptApi, "fetch") and not hasattr(YouTubeTranscriptApi, "get_transcript"):
            api = YouTubeTranscriptApi()
            tlist = api.list(vid)
        else:  # older library versions
            tlist = YouTubeTranscriptApi.list_transcripts(vid)
        tr, lang, translated = None, "", False
        try:
            tr = tlist.find_transcript(langs)
        except Exception:
            for t in tlist:  # any language, translate to English if possible
                tr = t
                if t.is_translatable:
                    tr = t.translate("en")
                    translated = True
                break
        if tr is None:
            return "", "", False
        lang = getattr(tr, "language_code", "")
        data = tr.fetch()
        parts = [getattr(s, "text", None) or (s.get("text") if isinstance(s, dict) else "") for s in data]
        text = " ".join(p.replace("\n", " ") for p in parts if p)
        return text, lang, translated
    except Exception as e:
        return "", "ERROR: " + type(e).__name__, False


def get_video(vid):
    opts = {
        "quiet": True, "no_warnings": True, "skip_download": True, "getcomments": True,
        "extractor_args": {"youtube": {"max_comments": [str(MAX_COMMENTS), "all", "5", "3"],
                                       "comment_sort": ["top"]}},
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
    comments = [{
        "comment_id": c.get("id"), "parent": c.get("parent"), "author": c.get("author"),
        "likes": c.get("like_count") or 0,
        "date": datetime.fromtimestamp(c["timestamp"]).strftime("%Y-%m-%d") if c.get("timestamp") else "",
        "text": (c.get("text") or "").strip(),
    } for c in (info.get("comments") or [])]
    up = info.get("upload_date") or ""
    meta = {
        "video_id": vid, "title": info.get("title"), "channel": info.get("channel") or info.get("uploader"),
        "upload_date": f"{up[:4]}-{up[4:6]}-{up[6:]}" if up else "",
        "views": info.get("view_count"), "likes": info.get("like_count"),
        "comment_count": info.get("comment_count"),
        "minutes": round((info.get("duration") or 0) / 60, 1),
        "language": info.get("language"),
        "description": (info.get("description") or "").strip(),
        "url": f"https://www.youtube.com/watch?v={vid}",
    }
    return meta, comments


def main():
    os.makedirs(CACHE, exist_ok=True)
    queue, seen = [], set()
    for line in LINKS.split():
        vid = video_id(line.strip())
        if vid and vid not in seen:
            seen.add(vid)
            queue.append((vid, "your link"))
    print(f"{len(queue)} unique links from your list")

    print("Searching for more videos...")
    queue += search_more(seen)
    print(f"Total videos to process: {len(queue)}\n")

    unavailable = []
    for i, (vid, via) in enumerate(queue, 1):
        if os.path.exists(cache_path(vid)):
            d = json.load(open(cache_path(vid), encoding="utf-8"))
            # retry only the transcript if it was blocked last time
            if not d.get("unavailable") and str(d["meta"].get("transcript_lang", "")).startswith("ERROR"):
                text, lang, translated = get_transcript(vid)
                d["transcript"] = text
                d["meta"].update({"transcript_lang": lang, "translated_to_en": translated})
                json.dump(d, open(cache_path(vid), "w", encoding="utf-8"), ensure_ascii=False)
                print(f"[{i}/{len(queue)}] cached, transcript retry: {'yes' if text else lang}")
                time.sleep(random.uniform(2, 4))
            else:
                print(f"[{i}/{len(queue)}] cached  {vid}")
            continue
        try:
            meta, comments = get_video(vid)
        except Exception as e:
            msg = str(e).splitlines()[0][:120]
            print(f"[{i}/{len(queue)}] UNAVAILABLE {vid}  ({msg})")
            unavailable.append(vid)
            json.dump({"unavailable": True, "via": via, "error": msg}, open(cache_path(vid), "w", encoding="utf-8"))
            continue
        text, lang, translated = get_transcript(vid)
        meta.update({"found_via": via, "transcript_lang": lang, "translated_to_en": translated})
        json.dump({"meta": meta, "comments": comments, "transcript": text},
                  open(cache_path(vid), "w", encoding="utf-8"), ensure_ascii=False)
        print(f"[{i}/{len(queue)}] OK  {len(comments):4} comments  transcript {'yes' if text else 'no '}  "
              f"{(meta['title'] or '')[:55]}")
        time.sleep(random.uniform(2, 4))

    # ---- Write CSVs from cache ----
    vids, trans, coms = [], [], []
    for fn in os.listdir(CACHE):
        d = json.load(open(os.path.join(CACHE, fn), encoding="utf-8"))
        if d.get("unavailable"):
            continue
        m = d["meta"]
        vids.append({k: v for k, v in m.items()})
        trans.append({"video_id": m["video_id"], "title": m["title"], "channel": m["channel"],
                      "upload_date": m["upload_date"], "transcript_lang": m["transcript_lang"],
                      "translated_to_en": m["translated_to_en"], "transcript": d["transcript"]})
        for c in d["comments"]:
            coms.append({"video_id": m["video_id"], "video_title": m["title"], **c})

    def write(name, rows):
        if not rows:
            return
        with open(name, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"Saved {len(rows):6} rows -> {name}")

    print()
    write("youtube_videos.csv", vids)
    write("youtube_transcripts.csv", trans)
    write("youtube_comments.csv", coms)
    no_tr = sum(1 for t in trans if not t["transcript"])
    print(f"\nVideos OK: {len(vids)} | no transcript: {no_tr} | unavailable this run: {len(unavailable)}")
    if no_tr:
        print("If many say 'ERROR: IpBlocked' / 'RequestBlocked', wait an hour and re-run (cached videos are skipped),")
        print("or switch to phone hotspot and re-run.")


if __name__ == "__main__":
    main()
