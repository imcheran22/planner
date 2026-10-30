# Analysis scripts for plan v2 (run from the repo root)

| Script | What it does |
|---|---|
| `parse_booking.py` | Rebuilds room-level Booking prices from `extra_cache/booking_*.json` → `booking_room_options.csv` (pay = displayedPrice + excludedTaxesPrice, whole stay) |
| `hotels.py` | Adds area and distances, ranks options per city → `booking_room_options_geo.csv` |
| `budget.py` | The four combo budgets → `budget_tables.md` (pasted into `plan_v2.md`) |
| `rs.py` | `python analysis/rs.py 1015,1028 8` — top comments of Reddit threads (v5 + v6 stacked) |
| `rgrep.py` | `python analysis/rgrep.py 'ba ?na' 'fog' 10` — keyword search across Reddit v5 + v6 |
| `ytgrep.py` | `python analysis/ytgrep.py 'coaster' 10` — keyword windows in YouTube transcripts v2 |

`booking_sea_view_options.csv` in the repo root is rebuilt from these (it failed in the original run).
