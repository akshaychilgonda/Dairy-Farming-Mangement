"""
config.py
----------
Central configuration for the Dairy Farm Manager application.
Keeping all constants in one place makes the app easy to customize.
"""

import os

# ---------------------------------------------------------------
# FOLDER PATHS (all relative to this file, so app works from any cwd)
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "dairy.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PHOTOS_DIR = os.path.join(ASSETS_DIR, "animal_photos")

# Create folders if they don't already exist
for _folder in (DB_DIR, BACKUP_DIR, ASSETS_DIR, PHOTOS_DIR):
    os.makedirs(_folder, exist_ok=True)

# ---------------------------------------------------------------
# APP INFO
# ---------------------------------------------------------------
APP_TITLE = "Dairy Farm Manager"
APP_ICON = "🐄"
CURRENCY = "₹"

# ---------------------------------------------------------------
# DROPDOWN OPTIONS (used across many forms)
# ---------------------------------------------------------------
ANIMAL_TYPES = ["Cow", "Buffalo"]
GENDERS = ["Female", "Male"]
HEALTH_STATUSES = ["Healthy", "Sick", "Under Treatment", "Weak", "Recovering", "Dry"]
PREGNANCY_STATUSES = ["Not Pregnant", "Pregnant", "Unknown"]

FEED_TYPES = ["Green Fodder", "Dry Fodder", "Silage", "Concentrate", "Mineral Mixture", "Other"]
FEED_UNITS = ["kg", "liters", "bags", "bundles"]
FEEDING_TIMES = ["Morning", "Afternoon", "Evening", "Night"]

EXPENSE_CATEGORIES = [
    "Feed", "Medicine", "Veterinary", "Electricity", "Water", "Labour",
    "Animal Purchase", "Equipment", "Transportation", "Other"
]
PAYMENT_METHODS = ["Cash", "UPI", "Bank Transfer", "Cheque", "Credit", "Other"]

INCOME_TYPES = ["Milk Sales", "Animal Sales", "Calf Sales", "Manure Sales", "Other Income"]

ALERT_TYPES = [
    "Vaccination", "Medicine", "Feeding", "Veterinary Appointment", "Pregnancy Check",
    "Expected Calving", "Heat Detection", "AI Reminder", "Milk Collection",
    "Insurance Renewal", "Health Check", "Equipment Maintenance", "Feed Stock Low",
    "Payment Due", "Other Task"
]

# Alert levels mapped to an emoji + a sort priority (lower number = shown first)
ALERT_LEVELS = {
    "Urgent":    {"emoji": "🔴", "priority": 0, "color": "#ff4d4d"},
    "Important": {"emoji": "🟠", "priority": 1, "color": "#ff9900"},
    "Upcoming":  {"emoji": "🟡", "priority": 2, "color": "#ffd633"},
    "Completed": {"emoji": "🟢", "priority": 3, "color": "#33cc66"},
}

TASK_CATEGORIES = ["Morning", "Afternoon", "Evening", "Custom"]

DEFAULT_MORNING_TASKS = ["Feed animals", "Check animal health", "Milk animals", "Check water", "Record milk production"]
DEFAULT_AFTERNOON_TASKS = ["Feed animals", "Check sick animals", "Record expenses"]
DEFAULT_EVENING_TASKS = ["Feed animals", "Milk animals", "Record milk production", "Check tomorrow's reminders"]

# ---------------------------------------------------------------
# SIMPLE BILINGUAL LABELS (English / Marathi) — used for headings
# ---------------------------------------------------------------
LANG = {
    "English": {
        "dashboard": "Dashboard", "animals": "Animals", "milk": "Milk Production",
        "feed": "Feed", "health": "Health", "vaccination": "Vaccination",
        "breeding": "Breeding", "income": "Income", "expenses": "Expenses",
        "inventory": "Inventory", "tasks": "Tasks", "alerts": "Alerts",
        "reports": "Reports", "settings": "Settings",
    },
    "मराठी": {
        "dashboard": "डॅशबोर्ड", "animals": "जनावरे", "milk": "दूध उत्पादन",
        "feed": "चारा", "health": "आरोग्य", "vaccination": "लसीकरण",
        "breeding": "प्रजनन", "income": "उत्पन्न", "expenses": "खर्च",
        "inventory": "साठा", "tasks": "कामे", "alerts": "सूचना",
        "reports": "अहवाल", "settings": "सेटिंग्ज",
    },
}
