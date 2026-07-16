# Moon Calendar

A Django-based web application for tracking and managing calendar events with lunar phase information.

It also includes **Daily Signal**, a mobile-first PWA daily-horoscope dashboard
(see [Daily Signal](#daily-signal) below).

## Prerequisites

- Python 3.x
- pip (Python package manager)
- PostgreSQL 17+ or Docker
- Git

## Setting Up the Development Environment

1. **Clone the Repository**
   ```bash
   git clone https://github.com/tajahreynolds/moon-cal
   cd moon-cal
   ```

2. **Python Environment Setup**
- *(Optional)* Create and activate a Python virtual environment (to install required dependencies locally):
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows use `venv\Scripts\activate`
  ```
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Environment Configuration**
   - Copy the `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Update the following variables in `.env`:
     - `PG_USERNAME`: PostgreSQL username
     - `PG_PASSWORD`: PostgreSQL password
     - `PG_DATABASE`: Database name

4. **Database Setup**
   
   Choose one of the following options:

   **Option A: Using Docker**
   - Ensure Docker and Docker Compose are installed
   - Run the database container:
     ```bash
     docker compose up -d
     ```

   **Option B: Local PostgreSQL**
   - Install PostgreSQL 17 or higher
   - Create a database and user with appropriate permissions
   - Update the `.env` file with your database credentials

5. **Database Migration**
   ```bash
   python manage.py migrate
   ```

6. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```
   The application will be available at:
   - **Daily Signal** (horoscope PWA): `http://127.0.0.1:8000/`
   - **Moon Calendar** (events): `http://127.0.0.1:8000/mooncal/`

## Daily Signal

A no-BS daily transit dashboard that feels like a weather/fitness tracker, not a
mystical portal. Three screens:

- **Today** (`/`) — Energy / Focus / Friction status bars plus three one-line
  directives, and a live countdown to the next major transit shift.
- **Forecast** (`/forecast/`) — a 7-day "Friction vs. Flow" trend line; tap any
  day for the raw transit math (applying/separating aspects, orbs, time-to-exact).
- **Blueprint** (`/blueprint/`) — your natal placements table with retrograde
  (℞) markers, Ascendant and Sun highlighted.

It installs as a PWA (manifest + service worker) and works offline against the
last cached reading. No account is required — a profile is keyed to your browser
session; visiting `/` for the first time starts onboarding.

### Transparency / methodology

The product separates **computed astronomy (fact)** from **our heuristic
interpretation (read)** — see `/methodology/` in the app:

- **Ephemeris:** Swiss Ephemeris via [`pyswisseph`], using the built-in
  **Moshier** analytical model (`swe.FLG_MOSEPH`). No data files and no network
  are required at runtime.
- **Zodiac:** tropical. **Houses:** whole-sign by default (Placidus optional).
- **Retrograde:** shown when apparent longitudinal speed is negative.
- **Aspects:** standard orbs, each labelled applying/separating with an estimated
  time to exact. "Exact" is reserved for orbs under 0.1°.
- **Energy / Focus / Friction** and the flow score are opinionated heuristics
  layered on top of the computed positions.

The daily directive text is produced by a pluggable text engine
(`HOROSCOPE_TEXT_ENGINE` setting). The default `RuleBasedEngine` is deterministic;
a `ClaudeEngine` stub documents where an LLM generator can drop in later.

### Licensing note

`pyswisseph` (Swiss Ephemeris) is licensed **AGPL-3.0**. This is acceptable for a
self-hosted deployment; review the license before distributing a hosted service.

### Running the tests

```bash
python manage.py test          # runs both the mooncalendar and horoscope suites
```

[`pyswisseph`]: https://pypi.org/project/pyswisseph/

## Development

- To create a superuser account:
  ```bash
  python manage.py createsuperuser
  ```
- Access the admin interface at `http://127.0.0.1:8000/admin/`

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

