# Plant NFC Tracker

Lightweight FastAPI + SQLite web app for managing cultivation records tied to physical NFC tags.

## Features

- Mobile-first NFC scan landing pages (`/scan/{nfc_tag_id}` and `/plant/{plant_id}`)
- Quick actions: watering, feeding, pruning/training, stage/pot update, photo capture/upload
- Dashboard with search + filters by stage, strain, and pot size
- Plant detail timeline with metadata editor and gallery
- CSV export endpoint (`/export/csv`) returning ZIP with `plants_export.csv` + `logs_export.csv`
- Local SQLite DB at `./data/app.db`
- Uploaded images stored in `./app/static/uploads/`

## Requirements

- Python 3.11+
- Linux or macOS

## Setup (Bare Metal, No Docker)

```bash
cd /home/runner/work/plant-DB/plant-DB
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run the App

### Option A: `run.sh`

```bash
chmod +x run.sh
./run.sh
```

### Option B: Uvicorn directly

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open:

- `http://127.0.0.1:8000/` dashboard
- `http://127.0.0.1:8000/docs` API docs

The app automatically creates:

- `./data/`
- `./app/static/uploads/`
- SQLite schema (`./data/app.db`)

## Grow Area Schema (Phase 1)

Phase 1 adds schema + migrations for area-aware cultivation tracking. No UI/routes are changed yet.

New tables:

- `grow_areas`: indoor/outdoor area records (type, dimensions, notes)
- `plant_area_assignments`: plant-to-area history with `start_at`/`end_at` (one active area per plant)
- `area_light_schedules`: fixed/sunlight/hybrid schedule settings with optional time-of-day and hour fields
- `area_env_targets`: per-area min/max target ranges for air temp, humidity, vpd, soil temp, water content %, soil ec, co2, ppfd
- `area_readings`: timestamped actual area readings (manual/import/sensor source-ready)
- `area_equipment`: equipment inventory by area (type/name/model/serial/notes)
- `fertilizer_products`: fertilizer catalog (brand/product/formulation/npk)
- `nutrient_applications`: nutrient events linked to area and optionally plant, tied to fertilizer products
- `area_alerts`: out-of-range alert records tied to area and optionally a reading

Migration notes:

- Alembic is now included for deterministic schema migration scripts.
- Phase 1 migration file: `migrations/versions/a288e5a1186c_add_grow_area_phase1_schema.py`
- Apply migrations with: `alembic upgrade head`

## NFC Tools Pro URL Records

Write URLs to chips in NFC Tools Pro using one of these patterns:

- `http://<SERVER_IP>:8000/scan/<NFC_TAG_ID>`
- `http://<SERVER_IP>:8000/plant/<PLANT_ID>`

Examples:

- `http://192.168.1.50:8000/scan/tent-a-plant-004`
- `http://192.168.1.50:8000/plant/12`

When a scan hits `/scan/<NFC_TAG_ID>`:

- If known: quick-action screen opens for that plant
- If unknown: prompt to assign the tag to an existing plant

## systemd Auto-Start (Optional)

1. Copy project to a persistent path (example `/opt/plant-nfc-tracker`).
2. Edit `plant-tracker.service`:
   - `User`, `Group`
   - `WorkingDirectory`
   - `ExecStart`
3. Install and enable:

```bash
sudo cp plant-tracker.service /etc/systemd/system/plant-tracker.service
sudo systemctl daemon-reload
sudo systemctl enable plant-tracker
sudo systemctl start plant-tracker
sudo systemctl status plant-tracker
```

## Project Layout

```text
plant-DB/
├── app/
│   ├── __init__.py
│   ├── init.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── plants.py
│   │   ├── logs.py
│   │   └── export.py
│   ├── static/
│   │   └── uploads/
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── scan.html
│       ├── plant_detail.html
│       └── plant_form.html
├── data/
├── requirements.txt
├── run.sh
├── plant-tracker.service
└── README.md
```
