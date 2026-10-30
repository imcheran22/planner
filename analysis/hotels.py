import sys, numpy as np, pandas as pd
sys.path.insert(0, 'vietnam_trip_handoff')
from helpers.area import area
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_colwidth', 50); pd.set_option('display.max_rows', 500)
d = pd.read_csv('analysis/booking_room_options.csv')
d = d[(d.persons >= 2) & (d.persons <= 3)].copy()
def km(lat, lng, la2, ln2):
    return np.round(6371 * 2 * np.arcsin(np.sqrt(np.sin(np.radians(la2 - lat) / 2) ** 2 + np.cos(np.radians(lat)) * np.cos(np.radians(la2)) * np.sin(np.radians(ln2 - lng) / 2) ** 2)), 2)
d['area'] = [area(a, b) for a, b in zip(d.lat, d.lng)]
d['km_hoian_bridge'] = km(d.lat, d.lng, 15.8771, 108.3262)
d['km_hue_citadel'] = km(d.lat, d.lng, 16.4698, 107.5786)
d['km_an_thuong'] = km(d.lat, d.lng, 16.0490, 108.2470)
d['km_beach_line'] = km(d.lat, d.lng, d.lat, 108.2475 + (16.06 - d.lat) * 0.0)  # rough: My Khe shore ~108.2475
d.to_csv('analysis/booking_room_options_geo.csv', index=False)
good = d[(d.rating >= 8.8) & (d.reviews >= 150)]
def best(block, extra=None, n=25, col=None):
    s = good[good.cache.str.contains(block)]
    if extra is not None: s = s[extra(s)]
    # cheapest refundable option per hotel, plus cheapest any
    a = s.sort_values('pay_inr').groupby('hotel').head(1).copy()
    fc = s[s.free_cancel].sort_values('pay_inr').groupby('hotel').pay_inr.first()
    a['cheapest_refundable'] = a.hotel.map(fc)
    cols = ['hotel', 'stars', 'rating', 'reviews', 'area', 'room', 'pay_inr', 'pay_per_night', 'cheapest_refundable', 'free_cancel', 'breakfast_incl'] + ([col] if col else [])
    print(a.sort_values('pay_inr')[cols].head(n).to_string())
print('\n=== HOI AN 22-24 (2 nights, total) ==='); best('hoi_an|la_siesta|cozy|moire|little_hoi', col='km_hoian_bridge')
print('\n=== HUE 24-26 (2 nights, total) ==='); best('hue', col='km_hue_citadel')
print('\n=== DA NANG CENTRAL 26-27 (1 night) ==='); best('central', col='km_an_thuong')
print('\n=== DA NANG 27-28 SEA-VIEW ROOMS (1 night) ===')
best('sea_view_finder|naman|fusion|pullman|furama|tms|chicland', extra=lambda s: s.sea_view, n=40, col='km_an_thuong')
