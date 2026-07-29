# Sales Analytics Dashboard

An interactive Streamlit dashboard for visualizing sales KPIs, backed by a
MySQL database, with Plotly charts and an automated weekly reporting script.

## Stack
Python · Streamlit · Pandas · Plotly · MySQL

## Project structure
```
dashboard_project/
├── schema.sql            # MySQL table definitions
├── generate_data.py      # Seeds the DB with synthetic sales data
├── db_config.py          # Shared MySQL connection helper
├── app.py                # Main Streamlit dashboard
├── automated_report.py   # Scheduled weekly summary report generator
├── requirements.txt
└── .env.example           # Template for DB credentials
```

## Quickstart (Docker — recommended, zero manual setup)

If you have [Docker](https://www.docker.com/products/docker-desktop/) installed,
this is the easiest way to run the whole thing — MySQL, sample data, and the
dashboard — with one command:

```bash
docker-compose up --build
```

Then open **http://localhost:8501**. That's it — no manual DB install, no
`.env` file, no seeding step. The app container waits for MySQL to be ready,
seeds it with sample data automatically on first run, and launches the
dashboard. Restarting (`docker-compose up`) reuses the existing data instead
of reseeding.

To stop: `Ctrl+C`, then `docker-compose down` (add `-v` to also wipe the
database volume and start fresh next time).

---

## Manual Setup (no Docker)

### 1. Install MySQL and create the database
Install MySQL locally (or use a free cloud instance, e.g. PlanetScale, Railway,
or AWS RDS free tier). Then run:
```bash
mysql -u root -p < schema.sql
```

### 2. Configure credentials
```bash
cp .env.example .env
# edit .env with your actual DB_USER / DB_PASSWORD
```

### 3. Install Python dependencies
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Seed the database with sample data
```bash
python generate_data.py
```
This creates ~300 customers, 20 products across 4 categories, and 4,000
orders (~10,000 line items) spread across the last 2 years — enough volume
for the trend charts and filters to look realistic.

### 5. Run the dashboard
```bash
streamlit run app.py
```<img width="1920" height="993" alt="image" src="https://github.com/user-attachments/assets/7a139ddb-8e66-44c7-aafd-c7aab36acf77" />

Open the URL Streamlit prints (usually http://localhost:8501).

### 6. (Optional) Run the automated report
```bash
python automated_report.py
```
Generates a weekly text summary + CSV export in `reports/`. See the bottom
of `automated_report.py` for how to schedule it with cron.

## Customizing for your own data
- Swap the schema in `schema.sql` for your actual business entities.
- Update the SQL query in `load_data()` inside `app.py` to match your schema.
- Add/remove filters in the sidebar section of `app.py` to match your dimensions.

## Pushing to GitHub

Your `.env` (real DB credentials) is already excluded via `.gitignore` —
only `.env.example` gets committed. Double-check `.env` is never staged
before your first push.

```bash
cd dashboard_project
git init
git add .
git status          # confirm .env is NOT listed here
git commit -m "Initial commit: sales analytics dashboard"
```

Create a new empty repo on GitHub (no README/license, since you already
have them), then:

```bash
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

### Making the repo portfolio-ready
- Update the `[Your Name]` placeholder in `LICENSE`.
- Add a screenshot or GIF of the running dashboard to the top of this
  README (drag an image into the GitHub README editor, or reference
  `![dashboard](docs/screenshot.png)` after adding one to a `docs/` folder).
- Consider deploying it live via [Streamlit Community Cloud](https://streamlit.io/cloud)
  (free) so the GitHub repo links to a working demo, not just code — this
  matters a lot for a "personal project" resume line since reviewers can
  click through and actually use it.
- Pin the repo on your GitHub profile once it's live.

## Ideas to extend this project
- Add a login/auth layer (`streamlit-authenticator`)
- Deploy to Streamlit Community Cloud or a small VPS
- Add anomaly detection (e.g. flag weeks with revenue >2 std dev from mean)
- Swap MySQL for a cloud warehouse (BigQuery/Snowflake) to show scale
- Add caching benchmarks (before/after `@st.cache_data`) to quantify performance
