import streamlit as st
import pandas as pd
from rapidfuzz import process
import pdfplumber
from unidecode import unidecode

st.set_page_config(layout="wide")
st.title("💰 Advanced Payment Matching System")

# ======================
# 🔤 تحويل عربي / إنجليزي
# ======================
def normalize(name):
    name = str(name).strip().lower()
    name = unidecode(name)  # يحول عربي -> قريب للإنجليزي
    return name

# ======================
# 📄 قراءة PDF
# ======================
def extract_pdf(file):
    data = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")

            for line in lines:
                parts = line.split()

                if len(parts) >= 3:
                    name = parts[0]
                    amount = parts[-1]

                    data.append({
                        "Name": name,
                        "Amount": amount
                    })

    return pd.DataFrame(data)

# ======================
# 🔍 مطابقة ذكية
# ======================
def smart_match(name, bank_names):
    match = process.extractOne(name, bank_names)
    if match:
        return match[0], match[1]
    return None, 0

# ======================
# رفع الملفات
# ======================
order_file = st.file_uploader("Upload Orders", type=["xlsx"])
bank_file = st.file_uploader("Upload Bank (Excel or PDF)", type=["xlsx", "pdf"])

if order_file and bank_file:

    orders = pd.read_excel(order_file, engine="openpyxl")

    if bank_file.name.endswith(".pdf"):
        bank = extract_pdf(bank_file)
    else:
        bank = pd.read_excel(bank_file, engine="openpyxl")

    orders.columns = orders.columns.str.strip()
    bank.columns = bank.columns.str.strip()

    # تنظيف
    orders["Name_clean"] = orders["Name"].apply(normalize)
    bank["Name_clean"] = bank["Name"].apply(normalize)

    orders["Amount"] = pd.to_numeric(orders["Amount"], errors="coerce")
    bank["Amount"] = pd.to_numeric(bank["Amount"], errors="coerce")

    bank_names = bank["Name_clean"].tolist()

    matches = []
    scores = []

    for name in orders["Name_clean"]:
        m, s = smart_match(name, bank_names)
        matches.append(m)
        scores.append(s)

    orders["Matched_Name"] = matches
    orders["Match_Score"] = scores

    result = orders.merge(
        bank,
        left_on="Matched_Name",
        right_on="Name_clean",
        how="left"
    )

    # ======================
    # 🧪 تحليل الأخطاء
    # ======================
    def analyze(row):
        if pd.isna(row["Name_clean_y"]):
            return "❌ Not Found"

        if abs(row["Amount_x"] - row["Amount_y"]) > 1:
            return "⚠️ Amount Mismatch"

        if row["Match_Score"] < 80:
            return "⚠️ Name Similar"

        return "✅ Paid"

    result["Status"] = result.apply(analyze, axis=1)

    # ======================
    # 📊 Dashboard
    # ======================
    total = len(result)
    paid = len(result[result["Status"] == "✅ Paid"])
    not_found = len(result[result["Status"] == "❌ Not Found"])
    mismatch = len(result[result["Status"] == "⚠️ Amount Mismatch"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", total)
    col2.metric("Paid", paid)
    col3.metric("Not Found", not_found)
    col4.metric("Mismatch", mismatch)

    st.divider()

    st.dataframe(result)

    # تحميل
    csv = result.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇ Download Report",
        csv,
        "advanced_report.csv",
        "text/csv"
    )