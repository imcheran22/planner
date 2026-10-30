"""Rebuild Booking.com room-level prices from the raw Apify cache (extra_cache/booking_*.json).

Why: booking_rooms.csv has price_as_listed = NaN for every room (the v2 script read the wrong
field), which is why booking_sea_view_options.csv was never written. The real price sits in
rooms[].options[]: pay = displayedPrice + excludedTaxesPrice (= discount.discountedPrice when a
discount applies). 'price' on its own is the pre-discount figure.
"""
import json, glob, re, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, '..', 'extra_cache')
rows = []
for f in sorted(glob.glob(os.path.join(CACHE, 'booking_*.json'))):
    tag = os.path.basename(f)
    if 'reviews' in tag:
        continue
    for it in json.load(open(f)):
        cin, cout = it.get('checkInDate'), it.get('checkOutDate')
        nights = (pd.Timestamp(cout) - pd.Timestamp(cin)).days if cin and cout else None
        loc = it.get('location') or {}
        for r in it.get('rooms') or []:
            fac = [x for x in (r.get('facilities') or []) if x]
            sea = any(re.search(r'sea view|ocean view|beach ?front', x, re.I) for x in fac) or \
                  bool(re.search(r'sea|ocean|beach ?front', r.get('roomType') or '', re.I))
            for o in r.get('options') or []:
                if o.get('displayedPrice') is None:
                    continue
                pay = o['displayedPrice'] + (o.get('excludedTaxesPrice') or 0)
                ch = o.get('yourChoices') or []
                rows.append(dict(
                    cache=tag, query=it.get('startUrlOrQuery'), hotel=it.get('name'), type=it.get('type'),
                    stars=it.get('stars'), rating=it.get('rating'), reviews=it.get('reviews'),
                    lat=float(loc.get('lat')) if loc.get('lat') else None,
                    lng=float(loc.get('lng')) if loc.get('lng') else None,
                    check_in=cin, nights=nights, room=r.get('roomType'), rooms_left=r.get('roomsLeft'),
                    sea_view=sea, room_type_says_sea=bool(re.search(r'sea|ocean|beach ?front', r.get('roomType') or '', re.I)),
                    partial='partial' in (r.get('roomType') or '').lower(),
                    persons=o.get('persons'), pay_inr=round(pay), pay_per_night=round(pay / nights) if nights else None,
                    free_cancel=bool(o.get('freeCancellation')),
                    breakfast_incl=any(re.search(r'breakfast included|breakfast & dinner|all-inclusive', c, re.I) for c in ch),
                    choices=' | '.join(ch), facilities=', '.join(fac), url=(it.get('url') or '').split('?')[0]))
df = pd.DataFrame(rows)
out = os.path.join(HERE, 'booking_room_options.csv')
df.to_csv(out, index=False)
print(len(df), 'room options ->', out)
