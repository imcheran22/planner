"""Budget for the 4 combos. Rates: 29 Oct 2026 (CLAUDE.md): Rs1 = 271.22 VND, $1 = 25,836.19 VND."""
VND = 271.22; USD = 25836.19 / VND
v = lambda x: x / VND; u = lambda x: x * USD
common = [  # (item, basis, inr, kind)
    ('E-visa + SIM', '₹2,846 pp, Reddit traveller actual; visa $25 evisa.gov.vn', 2 * 2846, 'quote'),
    ('Old Town ticket', '120,000 VND × 2', v(240000), 'quote'),
    ('Lantern boat', '150,000 VND per boat', v(150000), 'quote'),
    ('My Son sunrise tour + ticket', '(600,000 + 150,000 VND) × 2', v(1500000), 'quote'),
    ('Marble Mountains', '40,000 VND × 2', v(80000), 'quote'),
    ('Private car Hoi An ↔ Hue via Hai Van', '$70, Reddit couple', u(70), 'quote'),
    ('Heritage train Hue ↔ Da Nang', '330,000 VND × 2', v(660000), 'quote'),
    ('Hue 3-site combo', '420,000 VND × 2', v(840000), 'quote'),
    ('Cooking class + basket boat', '$46 × 2, Cookly', u(92), 'quote'),
    ('Hue food tour', 'about $35 × 2, Reddit', u(70), 'quote'),
    ('Ba Na Hills ticket', '1,000,000 VND × 2 (Oct 2026 review: raised from 900k)', v(2000000), 'quote'),
    ('Ba Na alpine coaster, 3 rides each', '250,000 VND × 2 (Hindi vlog, Feb 2026)', v(500000), 'quote'),
    ('Grab to and from Ba Na', '$15 each way (YouTube Oct 2026: $12–18)', u(30), 'quote'),
    ('Grab airport → first hotel', '350,000 VND (Reddit: Grab 270k–350k)', v(350000), 'quote'),
    ('Other local Grab + airport run', 'Cap', 3000, 'cap'),
    ('Everyday food and coffee, 6.5 days', 'Cap, about ₹2,770/day', 18000, 'cap'),
    ('Farewell dinner', '1,000,000 VND pp, Maps price band', v(2000000), 'quote'),
]
combos = {
 'A': dict(name='Classic route, upgraded (v1 shape)', flights=('Chennai via Kuala Lumpur, ₹22,838 pp return, AirAsia on Kayak (not for your dates)', 45676), hotels=[
    ('Cozy An Boutique Hotel, Hoi An, 22–24', 'Booking, real dates, Superior, breakfast, free cancel', 12778, 'listing'),
    ('Pilgrimage Village, Hue, 24–26', 'Booking, real dates, Superior Double + breakfast, free cancel', 24751, 'listing'),
    ('Golden Lotus Grand, sea view high floor, 26–27', 'Booking, real date 26 Jan, breakfast, free cancel', 12184, 'listing'),
    ('Golden Lotus Grand, same room, 27–28', '26 Jan price reused; 27 Jan not collected', 12184, 'assumed')], extra=[]),
 'B': dict(name='Resort finish (1 central + 1 resort night)', flights=('Chennai via Kuala Lumpur, ₹22,838 pp return, AirAsia on Kayak (not for your dates)', 45676), hotels=[
    ('Cozy An Boutique Hotel, Hoi An, 22–24', 'Booking, real dates', 12778, 'listing'),
    ('White Lotus Hue Hotel, 24–26', 'Booking, real dates, Superior Queen, breakfast, free cancel', 10353, 'listing'),
    ('Golden Lotus Grand, city view, 26–27', 'Booking, real date, free cancel', 6019, 'listing'),
    ('Fusion Resort, Ocean View Suite, spa inclusive, 27–28', 'Booking, real date, breakfast + spa, free cancel', 32326, 'listing')], extra=[]),
 'C': dict(name='Da Nang first (recommended)', flights=('Chennai via Kuala Lumpur, ₹22,838 pp return, AirAsia on Kayak (not for your dates)', 45676), hotels=[
    ('Golden Lotus Grand, sea view high floor, 22–23', '26 Jan price used; 22 Jan not collected', 12184, 'assumed'),
    ('Golden Lotus Grand, same room, 23–24', '26 Jan price used; 23 Jan not collected', 12184, 'assumed'),
    ('White Lotus Hue Hotel, 24–26', 'Booking, real dates, breakfast, free cancel', 10353, 'listing'),
    ('Cozy An Boutique Hotel, Hoi An, 26–28', '22-24 price used; 26-28 not collected', 12778, 'assumed')],
    extra=[('Han River cruise (Poseidon, cruise only), Sat 23, 21:00 fire show', '$21.30 × 2', u(42.6), 'quote')]),
 'D': dict(name='Bengaluru + lean stays', flights=('Bengaluru via Bangkok, ₹33,306 pp return, Thai AirAsia (not for your dates)', 66612), hotels=[
    ('Hoi An TNT Villa, 22–24', 'Booking, real dates, breakfast, free cancel', 8338, 'listing'),
    ('White Lotus Hue Hotel, 24–26', 'Booking, real dates', 10353, 'listing'),
    ('Golden Lotus Grand, city view, 26–27', 'Booking, real date', 6019, 'listing'),
    ('Monarque Hotel, Royal Room Ocean View, 27–28', 'Booking, real date', 10346, 'listing')], extra=[]),
}
for k, c in combos.items():
    rows = [('Flights', c['flights'][0], c['flights'][1], 'listing')] + c['hotels'] + common + c['extra']
    tot = sum(r[2] for r in rows); hot = sum(r[2] for r in c['hotels'])
    print(f"\n## {k} {c['name']}: total Rs{tot:,.0f}  hotels Rs{hot:,.0f}  buffer Rs{200000-tot:,.0f}")
    for r in rows: print(f"  {r[0]:55s} {r[2]:>9,.0f}  [{r[3]}] {r[1]}")
print('\nUSD in INR', round(USD, 2))

# ---- markdown output for plan_v2.md ----
KIND = {'listing': 'Booking listing, real dates', 'assumed': 'proxy price (see note)', 'quote': 'quote', 'cap': '**cap**'}
with open('analysis/budget_tables.md', 'w') as f:
    for k, c in combos.items():
        rows = [('Flights for two', c['flights'][0], c['flights'][1], 'quote')] + c['hotels'] + common + c['extra']
        tot = sum(r[2] for r in rows)
        f.write(f"\n### Combo {k}: {c['name']}\n\n| Item | Basis | Type | ₹ for two |\n|---|---|---|---:|\n")
        for r in rows:
            f.write(f"| {r[0]} | {r[1]} | {KIND[r[3]]} | {r[2]:,.0f} |\n")
        f.write(f"| **Total** | | | **{tot:,.0f}** |\n| **Buffer left of ₹2,00,000** | | | **{200000 - tot:,.0f}** |\n")
