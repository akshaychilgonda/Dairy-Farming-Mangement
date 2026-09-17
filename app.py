"""
app.py
-------
Main entry point of the Dairy Farm Manager.
Run with:   streamlit run app.py

This file:
 1. Initializes the database (creates tables the first time it runs)
 2. Shows a simple login screen
 3. Renders the DASHBOARD (home page) with all key farm metrics
Other modules live in pages/ and appear automatically in Streamlit's
sidebar navigation.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta

from config import APP_TITLE, APP_ICON, CURRENCY
from database import init_db, fetch_df, verify_user, get_setting
from services.reminder_service import get_all_alerts, alert_counts

# ---------------------------------------------------------------
# PAGE CONFIG (must be the first Streamlit command)
# ---------------------------------------------------------------
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

# Make sure the database & tables exist before anything else runs
init_db()

# ---------------------------------------------------------------
# SIMPLE LOGIN GATE
# ---------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.caption("दुग्ध व्यवसाय व्यवस्थापन प्रणाली — Dairy Farming Information Management System")
    st.write("### 🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username / वापरकर्ता नाव", value="farmer")
        password = st.text_input("Password / पासवर्ड", type="password", value="")
        submitted = st.form_submit_button("Login")
        if submitted:
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")
    st.info("Default login → **username:** farmer | **password:** farmer123  \n"
            "(You can change this later from the Settings page.)")
    st.stop()

# ---------------------------------------------------------------
# SIDEBAR — farm name + logout
# ---------------------------------------------------------------
farm_name = get_setting("farm_name", "My Dairy Farm")
st.sidebar.title(f"{APP_ICON} {farm_name}")
st.sidebar.caption(f"Logged in as **{st.session_state.get('username','farmer')}**")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()
st.sidebar.markdown("---")
st.sidebar.caption("Use the menu above to navigate: Animals, Milk, Feed, Health, "
                    "Vaccination, Breeding, Income, Expenses, Inventory, Tasks, "
                    "Alerts, Reports, Settings.")

# ---------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------
st.title(f"🏠 Dashboard — {farm_name}")
st.caption(f"Today: {date.today().strftime('%d %B %Y')}")

today = date.today()
month_start = today.replace(day=1)

animals_df = fetch_df("SELECT * FROM animals WHERE is_active = 1")
milk_df = fetch_df("SELECT * FROM milk_production")
expenses_df = fetch_df("SELECT * FROM expenses")
income_df = fetch_df("SELECT * FROM income")
tasks_df = fetch_df("SELECT * FROM tasks")
vacc_df = fetch_df("SELECT * FROM vaccinations WHERE status != 'Completed'")
breeding_df = fetch_df("SELECT * FROM breeding_records")

# ---- Basic calculations -----------------------------------------------
total_animals = len(animals_df)
healthy_animals = len(animals_df[animals_df["health_status"] == "Healthy"]) if total_animals else 0
attention_animals = total_animals - healthy_animals

if not milk_df.empty:
    milk_df["date"] = pd.to_datetime(milk_df["date"])
    today_milk = milk_df[milk_df["date"].dt.date == today]["total_milk"].sum()
    month_milk = milk_df[(milk_df["date"].dt.date >= month_start)]["total_milk"].sum()
else:
    today_milk, month_milk = 0, 0

if not expenses_df.empty:
    expenses_df["date"] = pd.to_datetime(expenses_df["date"])
    today_expense = expenses_df[expenses_df["date"].dt.date == today]["amount"].sum()
    month_expense = expenses_df[(expenses_df["date"].dt.date >= month_start)]["amount"].sum()
else:
    today_expense, month_expense = 0, 0

if not income_df.empty:
    income_df["date"] = pd.to_datetime(income_df["date"])
    month_income = income_df[(income_df["date"].dt.date >= month_start)]["amount"].sum()
else:
    month_income = 0

# Add milk income (auto-recorded from milk_production) to monthly income total
month_income_total = month_income + (milk_df[(milk_df["date"].dt.date >= month_start)]["total_income"].sum() if not milk_df.empty else 0)
net_profit = month_income_total - month_expense

alerts = get_all_alerts()
counts = alert_counts(alerts)
vacc_upcoming = len(vacc_df)
breeding_upcoming = len([b for b in breeding_df.itertuples()
                          if b.expected_calving_date not in (None, "", "None")
                          and (b.actual_calving_date in (None, "", "None"))])

today_tasks = tasks_df[tasks_df["due_date"] == str(today)] if not tasks_df.empty else pd.DataFrame()
today_tasks_pending = len(today_tasks[today_tasks["status"] == "Pending"]) if not today_tasks.empty else 0
overdue_tasks = tasks_df[(tasks_df["due_date"] < str(today)) & (tasks_df["status"] == "Pending")] if not tasks_df.empty else pd.DataFrame()

# ---- KPI Cards ----------------------------------------------------------
st.markdown("### 📌 Farm Snapshot")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🐄 Total Animals", total_animals)
c2.metric("✅ Healthy", healthy_animals)
c3.metric("⚠️ Need Attention", attention_animals)
c4.metric("🥛 Today's Milk (L)", f"{today_milk:.1f}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("🥛 Month Milk (L)", f"{month_milk:.1f}")
c6.metric("💸 Today's Expense", f"{CURRENCY}{today_expense:,.0f}")
c7.metric("💰 Month Income", f"{CURRENCY}{month_income_total:,.0f}")
c8.metric("📈 Net Profit (Month)", f"{CURRENCY}{net_profit:,.0f}",
          delta=f"{CURRENCY}{net_profit:,.0f}")

st.markdown("### 🔔 Alerts Overview")
a1, a2, a3, a4 = st.columns(4)
a1.metric("🔴 Urgent Alerts", counts["Urgent"])
a2.metric("🟠 Important Alerts", counts["Important"])
a3.metric("💉 Upcoming Vaccinations", vacc_upcoming)
a4.metric("❤️ Upcoming Calvings", breeding_upcoming)

t1, t2 = st.columns(2)
t1.metric("✅ Today's Tasks Pending", today_tasks_pending)
t2.metric("⏰ Overdue Tasks", len(overdue_tasks))

st.markdown("---")

# ---- Alerts preview -------------------------------------------------
st.markdown("### 🚨 Top Alerts (see full list on the Alerts page)")
if alerts:
    top_alerts = alerts[:8]
    for al in top_alerts:
        emoji = {"Urgent": "🔴", "Important": "🟠", "Upcoming": "🟡", "Completed": "🟢"}.get(al["level"], "⚪")
        st.write(f"{emoji} **[{al['type']}]** {al['title']} — {al['detail']}")
else:
    st.success("🎉 No pending alerts right now. Everything looks good!")

st.markdown("---")

# ---- Charts -----------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🥛 Milk Production — Last 14 Days")
    if not milk_df.empty:
        last14 = milk_df[milk_df["date"] >= pd.Timestamp(today - timedelta(days=13))]
        daily = last14.groupby(last14["date"].dt.date)["total_milk"].sum().reset_index()
        if not daily.empty:
            fig = px.bar(daily, x="date", y="total_milk", labels={"date": "Date", "total_milk": "Liters"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No milk records in the last 14 days yet.")
    else:
        st.info("No milk production records yet. Add some from the Milk Production page.")

with col2:
    st.markdown("#### 💰 Income vs Expense — This Month")
    labels = ["Income", "Expense"]
    values = [month_income_total, month_expense]
    if sum(values) > 0:
        fig2 = px.pie(names=labels, values=values, color=labels,
                       color_discrete_map={"Income": "#33cc66", "Expense": "#ff4d4d"})
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No income/expense records for this month yet.")

st.markdown("#### 🐄 Herd Composition")
col3, col4 = st.columns(2)
with col3:
    if not animals_df.empty:
        fig3 = px.pie(animals_df, names="animal_type", title="Cow vs Buffalo")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No animals added yet. Go to the Animals page to add your first animal.")
with col4:
    if not animals_df.empty:
        fig4 = px.pie(animals_df, names="health_status", title="Health Status")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info(" ")

st.caption("Tip: Use the sidebar to manage Animals, record Milk, track Feed/Health/"
           "Vaccination/Breeding, log Income & Expenses, and view full Reports.")
