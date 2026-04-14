import streamlit as st
import pandas as pd
from rapidfuzz import process
import pdfplumber
from unidecode import unidecode
import re

# ======================
# Settings
# ======================
st.set_page_config(
    page_title="PayMatch Pro",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================
# CSS
# ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #F7F8FC;
    --surface: #FFFFFF;
    --border: #E4E7F0;
    --text-primary: #0F1628;
    --text-secondary: #6B7A99;
    --accent: #2563EB;
    --accent-light: #EEF3FF;
    --green: #059669;
    --green-light: #ECFDF5;
    --red: #DC2626;
    --red-light: #FEF2F2;
    --amber: #D97706;
    --amber-light: #FFFBEB;
    --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 24px rgba(0,0,0,0.08);
    --radius: 14px;
}

* { font-family: 'Sora', sans-serif !important; }

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text-primary) !important;
}

.paymatch-header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px 36px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 18px;
    box-shadow: var(--shadow);
}
.paymatch-logo {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #2563EB, #7C3AED);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
}
.paymatch-title { font-size: 22px; font-weight: 700; color: var(--text-primary); margin: 0; }
.paymatch-sub { font-size: 13px; color: var(--text-secondary); margin: 2px 0 0; }
.paymatch-badge {
    margin-left: auto;
    background: var(--accent-light);
    color: var(--accent);
    font-size: 12px; font-weight: 600;
    padding: 6px 14px; border-radius: 20px;
    letter-spacing: 0.3px;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 6px !important;
    gap: 4px !important;
    box-shadow: var(--shadow) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 10px 22px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    box-shadow: var(--shadow);
    margin-bottom: 16px;
}
.card-title {
    font-size: 13px; font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase; letter-spacing: 0.8px;
    margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
}

.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 22px;
    box-shadow: var(--shadow);
    position: relative; overflow: hidden;
}
.metric-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
}
.metric-card.blue::before { background: linear-gradient(90deg, #2563EB, #7C3AED); }
.metric-card.green::before { background: linear-gradient(90deg, #059669, #10B981); }
.metric-card.red::before { background: linear-gradient(90deg, #DC2626, #F87171); }
.metric-card.amber::before { background: linear-gradient(90deg, #D97706, #F59E0B); }
.metric-icon { font-size: 28px; margin-bottom: 10px; }
.metric-value { font-size: 32px; font-weight: 700; color: var(--text-primary); line-height: 1; }
.metric-label { font-size: 12px; color: var(--text-secondary); font-weight: 500; margin-top: 6px; }

.stFileUploader > div {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
    transition: all 0.2s !important;
}
.stFileUploader > div:hover {
    border-color: var(--accent) !important;
    background: var(--accent-light) !important;
}

.stDataFrame { border-radius: var(--radius) !important; overflow: hidden !important; }
[data-testid="stDataFrameResizable"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow) !important;
}

.stDownloadButton button, .stButton button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
    transition: all 0.2s !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.35) !important;
}

.status-paid { color: var(--green); background: var(--green-light); padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.status-notfound { color: var(--red); background: var(--red-light); padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.status-mismatch { color: var(--amber); background: var(--amber-light); padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }

.summary-bar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 24px;
    display: flex; gap: 32px; align-items: center;
    box-shadow: var(--shadow);
    margin-bottom: 20px;
}
.summary-item { text-align: center; }
.summary-value { font-size: 20px; font-weight: 700; }
.summary-label { font-size: 11px; color: var(--text-secondary); font-weight: 500; margin-top: 2px; }

.section-divider { border: none; border-top: 1px solid var(--border); margin: 24px 0; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 20px !important; max-width: 1400px; }
</style>
""", unsafe_allow_html=True)

# ======================
# Helper Functions
# ======================
def normalize(name):
    name = str(name).strip().lower()
    name = unidecode(name)
    name = re.sub(r'[^\w\s]', '', name)
    return name

def parse_amount(val):
    if pd.isna(val):
        return None
    val = str(val).replace(',', '').replace(' ', '')
    val = re.sub(r'[^\d.-]', '', val)
    try:
        return float(val)
    except:
        return None

def extract_pdf_transactions(file):
    data = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        if row and len(row) >= 2:
                            row = [str(c).strip() if c else '' for c in row]
                            data.append(row)
            else:
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        parts = line.split()
                        if len(parts) >= 3:
                            data.append(parts)
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df.columns = [f"Col_{i}" for i in range(len(df.columns))]
    return df

def extract_bank_statement(file):
    if file.name.endswith('.pdf'):
        raw = extract_pdf_transactions(file)
        if raw.empty:
            return pd.DataFrame()
        df = raw.copy()
        df.columns = [f"Field_{i}" for i in range(len(df.columns))]
        return df
    else:
        df = pd.read_excel(file, engine='openpyxl')
        df.columns = df.columns.str.strip()
        return df

def detect_transaction_type(row, debit_col, credit_col):
    try:
        debit = parse_amount(row.get(debit_col, 0)) or 0
        credit = parse_amount(row.get(credit_col, 0)) or 0
        if credit > 0:
            return "💚 إيداع", credit
        elif debit > 0:
            return "🔴 سحب/مدفوع", debit
        else:
            return "➖ غير محدد", 0
    except:
        return "➖ غير محدد", 0

def smart_match(name, bank_names, threshold=60):
    match = process.extractOne(name, bank_names)
    if match and match[1] >= threshold:
        return match[0], match[1]
    return None, 0

def analyze_match(row):
    if pd.isna(row.get("Name_clean_y", None)) or row.get("Name_clean_y") is None:
        return "❌ غير موجود"
    amt_x = parse_amount(row.get("Amount_x", 0)) or 0
    amt_y = parse_amount(row.get("Amount_y", 0)) or 0
    if abs(amt_x - amt_y) > 1:
        return "⚠️ فرق في المبلغ"
    if row.get("Match_Score", 0) < 80:
        return "⚠️ اسم مشابه"
    return "✅ مدفوع"

# ======================
# HEADER
# ======================
st.markdown("""
<div class="paymatch-header">
    <div class="paymatch-logo">💳</div>
    <div>
        <div class="paymatch-title">PayMatch Pro</div>
        <div class="paymatch-sub">نظام مطابقة المدفوعات الذكي</div>
    </div>
    <div class="paymatch-badge">✦ Smart Matching</div>
</div>
""", unsafe_allow_html=True)

# ======================
# TABS
# ======================
tab1, tab2 = st.tabs(["💳 مطابقة المدفوعات", "🏦 تحليل كشف الحساب"])

# ==================================================
# TAB 1
# ==================================================
with tab1:
    col_upload1, col_upload2 = st.columns(2)
    with col_upload1:
        st.markdown('<div class="card-title">📋 ملف الطلبات</div>', unsafe_allow_html=True)
        order_file = st.file_uploader("Orders File", type=["xlsx"], key="orders", label_visibility="collapsed")

    with col_upload2:
        st.markdown('<div class="card-title">🏦 كشف البنك</div>', unsafe_allow_html=True)
        bank_file = st.file_uploader("Bank File", type=["xlsx", "pdf"], key="bank", label_visibility="collapsed")

    if order_file and bank_file:
        with st.spinner("جاري المعالجة..."):
            orders = pd.read_excel(order_file, engine="openpyxl")
            orders.columns = orders.columns.str.strip()

            if bank_file.name.endswith(".pdf"):
                bank = extract_pdf_transactions(bank_file)
            else:
                bank = pd.read_excel(bank_file, engine="openpyxl")
                bank.columns = bank.columns.str.strip()

            if "Name" in orders.columns:
                orders["Name_clean"] = orders["Name"].apply(normalize)
            if "Name" in bank.columns:
                bank["Name_clean"] = bank["Name"].apply(normalize)

            if "Amount" in orders.columns:
                orders["Amount"] = orders["Amount"].apply(parse_amount)
            if "Amount" in bank.columns:
                bank["Amount"] = bank["Amount"].apply(parse_amount)

            if "Name_clean" in bank.columns and "Name_clean" in orders.columns:
                bank_names = bank["Name_clean"].tolist()
                matches, scores = [], []
                for name in orders["Name_clean"]:
                    m, s = smart_match(name, bank_names)
                    matches.append(m)
                    scores.append(s)
                orders["Matched_Name"] = matches
                orders["Match_Score"] = scores

                result = orders.merge(
                    bank, left_on="Matched_Name",
                    right_on="Name_clean", how="left",
                    suffixes=("_x", "_y")
                )
                result["Status"] = result.apply(analyze_match, axis=1)
            else:
                result = orders.copy()
                result["Status"] = "⚠️ تحقق من أسماء الأعمدة"

        total = len(result)
        paid = len(result[result["Status"] == "✅ مدفوع"]) if "Status" in result.columns else 0
        not_found = len(result[result["Status"] == "❌ غير موجود"]) if "Status" in result.columns else 0
        mismatch = len(result[result["Status"].str.contains("فرق|مشابه", na=False)]) if "Status" in result.columns else 0

        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card blue">
                <div class="metric-icon">📊</div>
                <div class="metric-value">{total}</div>
                <div class="metric-label">إجمالي السجلات</div>
            </div>
            <div class="metric-card green">
                <div class="metric-icon">✅</div>
                <div class="metric-value">{paid}</div>
                <div class="metric-label">مدفوع</div>
            </div>
            <div class="metric-card red">
                <div class="metric-icon">❌</div>
                <div class="metric-value">{not_found}</div>
                <div class="metric-label">غير موجود</div>
            </div>
            <div class="metric-card amber">
                <div class="metric-icon">⚠️</div>
                <div class="metric-value">{mismatch}</div>
                <div class="metric-label">يحتاج مراجعة</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="card-title">🔍 فلترة النتائج</div>', unsafe_allow_html=True)
        status_filter = st.multiselect(
            "اختر الحالة",
            result["Status"].unique().tolist() if "Status" in result.columns else [],
            default=result["Status"].unique().tolist() if "Status" in result.columns else [],
            label_visibility="collapsed"
        )
        filtered = result[result["Status"].isin(status_filter)] if status_filter else result

        st.dataframe(filtered, use_container_width=True, height=420)

        csv = result.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ تحميل التقرير الكامل", csv, "payment_report.csv", "text/csv")

    else:
        st.markdown("""
        <div class="card" style="text-align:center; padding: 48px; color: var(--text-secondary);">
            <div style="font-size: 48px; margin-bottom: 12px;">📂</div>
            <div style="font-size: 16px; font-weight: 600; margin-bottom: 6px;">ارفع الملفين للبدء</div>
            <div style="font-size: 13px;">ملف الطلبات + كشف البنك</div>
        </div>
        """, unsafe_allow_html=True)

# ==================================================
# TAB 2
# ==================================================
with tab2:
    st.markdown('<div class="card-title">🏦 رفع كشف الحساب البنكي</div>', unsafe_allow_html=True)
    stmt_file = st.file_uploader("Bank Statement", type=["xlsx", "pdf"], key="statement", label_visibility="collapsed")

    if stmt_file:
        with st.spinner("جاري قراءة الكشف..."):
            df_raw = extract_bank_statement(stmt_file)

        if df_raw.empty:
            st.error("تعذر قراءة الملف. تأكد من صحة التنسيق.")
        else:
            st.markdown(f'<div class="card-title">📋 معاينة البيانات — {len(df_raw)} سجل</div>', unsafe_allow_html=True)
            st.dataframe(df_raw.head(10), use_container_width=True)

            st.markdown("---")
            st.markdown('<div class="card-title">⚙️ حدد الأعمدة</div>', unsafe_allow_html=True)

            cols = df_raw.columns.tolist()
            col_a, col_b, col_c, col_d = st.columns(4)

            with col_a:
                date_col = st.selectbox("📅 التاريخ", ["—"] + cols)
            with col_b:
                desc_col = st.selectbox("📝 الوصف / الاسم", ["—"] + cols)
            with col_c:
                debit_col = st.selectbox("🔴 المدين (سحب)", ["—"] + cols)
            with col_d:
                credit_col = st.selectbox("💚 الدائن (إيداع)", ["—"] + cols)

            if st.button("🔍 تحليل الكشف"):
                df = df_raw.copy()

                if debit_col != "—" and credit_col != "—":
                    types, amounts = [], []
                    for _, row in df.iterrows():
                        t, a = detect_transaction_type(row, debit_col, credit_col)
                        types.append(t)
                        amounts.append(a)
                    df["نوع الحركة"] = types
                    df["المبلغ"] = amounts
                elif debit_col != "—":
                    df["نوع الحركة"] = "🔴 سحب/مدفوع"
                    df["المبلغ"] = df[debit_col].apply(parse_amount)
                elif credit_col != "—":
                    df["نوع الحركة"] = "💚 إيداع"
                    df["المبلغ"] = df[credit_col].apply(parse_amount)

                rename = {}
                if date_col != "—":
                    rename[date_col] = "التاريخ"
                if desc_col != "—":
                    rename[desc_col] = "الوصف"
                df = df.rename(columns=rename)

                total_in = df[df["نوع الحركة"] == "💚 إيداع"]["المبلغ"].sum() if "نوع الحركة" in df.columns else 0
                total_out = df[df["نوع الحركة"] == "🔴 سحب/مدفوع"]["المبلغ"].sum() if "نوع الحركة" in df.columns else 0
                net = total_in - total_out
                count_in = len(df[df["نوع الحركة"] == "💚 إيداع"]) if "نوع الحركة" in df.columns else 0
                count_out = len(df[df["نوع الحركة"] == "🔴 سحب/مدفوع"]) if "نوع الحركة" in df.columns else 0

                st.markdown(f"""
                <div class="metric-grid">
                    <div class="metric-card green">
                        <div class="metric-icon">💚</div>
                        <div class="metric-value">{total_in:,.0f}</div>
                        <div class="metric-label">إجمالي الإيداعات ({count_in} حركة)</div>
                    </div>
                    <div class="metric-card red">
                        <div class="metric-icon">🔴</div>
                        <div class="metric-value">{total_out:,.0f}</div>
                        <div class="metric-label">إجمالي المسحوبات ({count_out} حركة)</div>
                    </div>
                    <div class="metric-card blue">
                        <div class="metric-icon">💰</div>
                        <div class="metric-value">{net:,.0f}</div>
                        <div class="metric-label">صافي الرصيد</div>
                    </div>
                    <div class="metric-card amber">
                        <div class="metric-icon">📊</div>
                        <div class="metric-value">{len(df)}</div>
                        <div class="metric-label">إجمالي الحركات</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="card-title">🔍 فلتر حسب النوع</div>', unsafe_allow_html=True)
                if "نوع الحركة" in df.columns:
                    type_filter = st.multiselect(
                        "نوع الحركة",
                        df["نوع الحركة"].unique().tolist(),
                        default=df["نوع الحركة"].unique().tolist(),
                        label_visibility="collapsed"
                    )
                    df_show = df[df["نوع الحركة"].isin(type_filter)]
                else:
                    df_show = df

                st.dataframe(df_show, use_container_width=True, height=500)

                csv2 = df.to_csv(index=False).encode("utf-8-sig")
                st.download_button("⬇️ تحميل كشف الحساب المحلل", csv2, "bank_statement_analyzed.csv", "text/csv")

    else:
        st.markdown("""
        <div class="card" style="text-align:center; padding: 48px; color: var(--text-secondary);">
            <div style="font-size: 48px; margin-bottom: 12px;">🏦</div>
            <div style="font-size: 16px; font-weight: 600; margin-bottom: 6px;">ارفع كشف الحساب البنكي</div>
            <div style="font-size: 13px;">Excel أو PDF — سيتم تحليل كل حركة تلقائياً</div>
        </div>
        """, unsafe_allow_html=True)