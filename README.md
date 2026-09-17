# 🐄 Dairy Farm Manager — Dairy Farming Information Management & Alert System

A complete, working farm-management app for Indian dairy farmers, built with
**Python + Streamlit + SQLite + Pandas + Plotly**.

---

## 1. What's included

| Module | What it does |
|---|---|
| 🏠 Dashboard | Live KPI cards, alerts overview, charts |
| 🐄 Animals | Add/Edit/Delete/Search animals, photo upload, full history view |
| 🥛 Milk Production | Daily milk logging, auto totals & income, 5 chart types |
| 🌾 Feed | Daily feeding log + cost reports |
| 💊 Health | Symptoms/diagnosis/treatment log, auto-updates animal health status |
| 💉 Vaccination | Scheduling with 🔴🟠🟡🟢 automatic due-date alerts |
| ❤️ Breeding | Heat → AI → pregnancy → calving workflow with auto reminders |
| 💰 Income | Milk (auto) + animal/calf/manure/other income |
| 💸 Expenses | 10 categories, daily/monthly/yearly reports |
| 📦 Inventory | Feed stock with low-stock alerts |
| ✅ Tasks | Morning/Afternoon/Evening checklist + custom tasks, overdue tracking |
| 🔔 Alerts | Unified, auto-computed alert center + custom reminders |
| 📊 Reports | CSV/Excel/PDF export for every module + Profit & Loss |
| ⚙️ Settings | Language, notification prefs, backup/restore, password change |

The **Alert Engine** (`services/reminder_service.py`) runs every time a page
loads and checks *real dates* in your database — vaccination due dates,
expected calving dates, treatment end dates, feed stock levels, custom
reminders, and task due dates — and classifies each as:

- 🔴 **Urgent** — overdue or due today
- 🟠 **Important** — due within 7 days (configurable in Settings)
- 🟡 **Upcoming** — due within 30 days (configurable in Settings)
- 🟢 **Completed**

No cron job needed for the in-app alerts — they're always fresh because
they're calculated live from `date.today()`.

---

## 2. Project structure

```
dairy_farming_system/
├── app.py                     # Main entry point (login + Dashboard)
├── config.py                  # All constants, dropdown options, paths
├── database.py                # Schema creation + generic DB helpers
├── requirements.txt
│
├── pages/                     # Streamlit auto-discovers these as sidebar pages
│   ├── 1_🐄_Animals.py
│   ├── 2_🥛_Milk_Production.py
│   ├── 3_🌾_Feed.py
│   ├── 4_💊_Health.py
│   ├── 5_💉_Vaccination.py
│   ├── 6_❤️_Breeding.py
│   ├── 7_💰_Income.py
│   ├── 8_💸_Expenses.py
│   ├── 9_📦_Inventory.py
│   ├── 10_✅_Tasks.py
│   ├── 11_🔔_Alerts.py
│   ├── 12_📊_Reports.py
│   └── 13_⚙️_Settings.py
│
├── services/
│   ├── reminder_service.py    # The alert/reminder engine
│   ├── backup_service.py      # Backup / restore the .db file
│   └── report_service.py      # CSV / Excel / PDF export helpers
│
├── database/
│   └── dairy.db                # SQLite database (auto-created, your data lives here)
│
├── assets/
│   └── animal_photos/          # Uploaded animal photos are stored here
└── backups/                    # Backup .db files land here
```

---

## 3. Database schema (13 tables)

`animals`, `milk_production`, `feed_records`, `feed_inventory`,
`health_records`, `vaccinations`, `breeding_records`, `expenses`,
`income`, `tasks`, `alerts`, `users`, `settings`.

All child tables use `animal_id` as a **foreign key** to `animals.id`
with `ON DELETE CASCADE` (deleting an animal cleans up its milk, health,
vaccination, and breeding records — you get a confirmation warning first).
`database.py`'s `init_db()` creates every table with `CREATE TABLE IF NOT
EXISTS`, so **restarting the app never wipes your data**.

---

## 4. Installation

```bash
# 1. Unzip / copy the project, then move into it
cd dairy_farming_system

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 5. Running the app

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

**Default login:**
- Username: `farmer`
- Password: `farmer123`

Change this immediately from **⚙️ Settings → Account → Change Password**.

The database file `database/dairy.db` is created automatically on first
run — nothing else to set up.

---

## 6. Quick start / testing checklist

1. Log in with the default credentials above.
2. Go to **🐄 Animals → Add/Edit Animal** and add your first cow/buffalo.
3. Go to **🥛 Milk Production → Record Milk** and log today's milking.
4. Go to **💉 Vaccination → Schedule Vaccination** and set a next-due date
   a few days in the future — watch it appear as 🟠/🟡 on the Dashboard
   and 🔔 Alerts page automatically.
5. Go to **📦 Inventory → Add Stock**, set a minimum stock level higher
   than the quantity you enter, and confirm the low-stock warning appears.
6. Go to **✅ Tasks → Today's Checklist** and click "Generate today's
   default checklist" to see the Morning/Afternoon/Evening list.
7. Go to **📊 Reports** and download a CSV/Excel/PDF of any module.
8. Go to **⚙️ Settings → Backup & Restore** and click "Backup Database Now".

---

## 7. Creating backups

- **Manual backup:** Settings → Backup & Restore → "Backup Database Now".
  This copies `database/dairy.db` into `backups/dairy_backup_<timestamp>.db`,
  which you can download from the same page.
- **Automated backup (optional):** schedule a daily OS task that copies
  `database/dairy.db` to a safe folder (or cloud drive), e.g. a cron job:
  ```bash
  0 22 * * * cp /path/to/dairy_farming_system/database/dairy.db /path/to/safe/backup_$(date +\%F).db
  ```
- **Restore:** Settings → Backup & Restore → upload a `.db` file → confirm
  the checkbox → "Restore Now". A safety copy of your *current* data is
  taken automatically before the overwrite, so restoring is never risky.

---

## 8. Adding real email notifications (optional)

The Settings page has toggles for email notifications, and the value is
stored in the `settings` table — but sending real emails needs your own
SMTP credentials. To wire it up:

1. Get SMTP credentials (e.g., a Gmail "App Password", or SendGrid/Mailgun).
2. Add a function to `services/reminder_service.py`:

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alerts(smtp_host, smtp_port, smtp_user, smtp_password, to_email):
    alerts = get_all_alerts()
    if not alerts:
        return
    body = "\n".join(f"[{a['level']}] {a['title']} - {a['detail']}" for a in alerts)
    msg = MIMEText(body)
    msg["Subject"] = "Dairy Farm - Daily Alerts"
    msg["From"] = smtp_user
    msg["To"] = to_email
    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
```

3. Store SMTP credentials in Streamlit `secrets.toml` (never hard-code them).
4. Call `send_email_alerts(...)` once a day using a scheduler (cron / Windows
   Task Scheduler / a small `schedule`-library script) — Streamlit itself
   doesn't run in the background, so the daily trigger must live outside it.

**WhatsApp/SMS** works the same way once you sign up for a gateway like
Twilio or Gupshup — replace the email-sending code with their API call.

---

## 9. Deploying online

**Option A — Streamlit Community Cloud (free, easiest)**
1. Push this project to a GitHub repository.
2. Go to https://share.streamlit.io → "New app" → select your repo → set
   main file to `app.py` → Deploy.
3. Note: Streamlit Cloud's filesystem is ephemeral on redeploy — for a farm
   that needs permanent data, either (a) redeploy rarely and back up often,
   or (b) switch `database.py` to a hosted database (see Option C).

**Option B — Your own VPS (DigitalOcean, AWS EC2, etc.)**
```bash
git clone <your-repo>
cd dairy_farming_system
pip install -r requirements.txt
streamlit run app.py --server.port 80 --server.address 0.0.0.0
```
Run it under `systemd` or `pm2`/`supervisor` so it restarts automatically,
and put it behind Nginx + HTTPS (Let's Encrypt) for a real domain.

**Option C — Upgrading to MySQL for multi-device / production use**
The app was built so only `database.py`'s `get_connection()` needs to
change:
```python
import mysql.connector
def get_connection():
    return mysql.connector.connect(
        host="...", user="...", password="...", database="dairy_farm"
    )
```
You'll also need to change the `?` placeholders to `%s` (MySQL syntax) and
recreate the `CREATE TABLE` statements with MySQL-compatible types
(`AUTO_INCREMENT` instead of `AUTOINCREMENT`, etc.). Because every page
only calls `fetch_df()` / `execute()` from `database.py`, none of the
page code needs to change.

---

## 10. Notes on data safety

- Every delete action (animal, records) asks for explicit confirmation.
- Foreign keys + `ON DELETE CASCADE` keep the database consistent.
- `init_db()` uses `CREATE TABLE IF NOT EXISTS` — restarting the app never
  erases data.
- Take backups regularly (Section 7) — SQLite is a single file, so backups
  are simple and reliable.

---

## 11. Customizing for Marathi-speaking farmers

`config.py` has a `LANG` dictionary with English/Marathi labels for the
main section headings, and the Settings page already lets a user pick
"मराठी" as the language. For a full translation, wrap page headings with
`LANG[selected_language]["key"]` the same way `app.py` does for the
Dashboard title. This was kept lightweight so you can extend it exactly
to the terms your farmers use locally.

---

Enjoy — and happy farming! 🐄🥛
