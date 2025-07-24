import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ============================
# GOOGLE SHEET CONNECTION
# ============================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open your Google Sheet by NAME
sheet = client.open("MRS_Billing")  # <-- your sheet name here
worksheet = sheet.sheet1

# Get all data from sheet
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# ============================
# STREAMLIT UI
# ============================
st.title("📊 MRS Billing Dashboard")

if not df.empty:

    expected_cols = {"Date", "Customer", "Amount", "Employee"}
    if not expected_cols.issubset(df.columns):
        st.error(f"❌ Your Google Sheet must have headers: {expected_cols}")
    else:
        # Ensure Date column is string
        df["Date"] = df["Date"].astype(str)

        # ---- Extract day, month, year from Date (assuming format dd.mm.yyyy)
        date_parts = df["Date"].str.split(".", expand=True)
        df["Day"] = date_parts[0]
        df["Month"] = date_parts[1]
        df["Year"] = date_parts[2]

        # Show all data
        st.subheader("🔹 All Records")
        st.dataframe(df)

        # -----------------------------
        # Today Filter
        # -----------------------------
        today = datetime.now().strftime("%d.%m.%Y")
        today_df = df[df["Date"] == today]

        st.subheader(f"📅 Today ({today})")
        st.write(today_df)

        st.write("✅ Total customers today:", today_df["Customer"].count())
        st.write("✅ Total sales today:", today_df["Amount"].sum())

        # -----------------------------
        # This Month Filter
        # -----------------------------
        this_month = datetime.now().strftime("%m")
        this_year = datetime.now().strftime("%Y")
        month_df = df[(df["Month"] == this_month) & (df["Year"] == this_year)]

        st.subheader(f"📅 This Month ({this_month}.{this_year})")
        st.write(month_df)

        st.write("✅ Total customers this month:", month_df["Customer"].count())
        st.write("✅ Total sales this month:", month_df["Amount"].sum())

        # -----------------------------
        # This Year Filter
        # -----------------------------
        this_year_df = df[df["Year"] == this_year]

        st.subheader(f"📅 This Year ({this_year})")
        st.write(this_year_df)

        st.write("✅ Total customers this year:", this_year_df["Customer"].count())
        st.write("✅ Total sales this year:", this_year_df["Amount"].sum())

        # -----------------------------
        # Top Employees by Sales (Descending)
        # -----------------------------
        st.subheader("🏆 Top Employees by Sales (Descending)")
        sorted_sales = (
            df.groupby("Employee", as_index=False)["Amount"]
            .sum()
            .sort_values(by="Amount", ascending=False)
        )
        st.dataframe(sorted_sales)
        st.bar_chart(sorted_sales.set_index("Employee"))

        # -----------------------------
        # Top Employees by Customer Count (Descending)
        # -----------------------------
        st.subheader("👥 Top Employees by Customer Count (Descending)")
        customer_count = (
            df.groupby("Employee", as_index=False)["Customer"]
            .count()
            .sort_values(by="Customer", ascending=False)
        )
        customer_count.rename(columns={"Customer": "Customer_Count"}, inplace=True)
        st.dataframe(customer_count)
        st.bar_chart(customer_count.set_index("Employee"))

        # -----------------------------
        # Normal Line Graph of Sales
        # -----------------------------
        st.subheader("📈 Line Graph of Sales by Employee")
        st.line_chart(sorted_sales.set_index("Employee"))

else:
    st.warning("No data found in Google Sheet yet!")
