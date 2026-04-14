import streamlit as st
import pandas as pd
import pdfplumber
from fuzzywuzzy import fuzz
import io

# إعدادات الصفحة
st.set_page_config(page_title="مطابق البنك الذكي", layout="wide")

st.title("🏦 نظام مطابقة كشوفات بنك فلسطين")
st.markdown("قم برفع ملف البنك (PDF) وملف العملاء (Excel) للمطابقة التلقائية.")

# --- وظائف المعالجة ---
def extract_bank_received(pdf_file):
    """استخراج المبالغ المستلمة من كشف بنك فلسطين"""
    data = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table[1:]:
                    # بناءً على الكشف: العمود 1 للمستلم، 4 للتفاصيل، 5 للتاريخ
                    if row[1] and row[1].strip(): 
                        try:
                            data.append({
                                "amount": float(row[1].replace(',', '')),
                                "details": row[4],
                                "date": row[5]
                            })
                        except: continue
    return data

# --- واجهة الرفع ---
col1, col2 = st.columns(2)

with col1:
    bank_file = st.file_uploader("ارفع كشف البنك (PDF)", type=["pdf"])

with col2:
    excel_file = st.file_uploader("ارفع ملف الإكسل (Excel)", type=["xlsx"])

if bank_file and excel_file:
    if st.button("بدء عملية المطابقة"):
        # 1. معالجة البيانات
        bank_data = extract_bank_received(bank_file)
        df_excel = pd.read_excel(excel_file)
        
        results = []
        
        # 2. منطق المطابقة الذكي
        for _, ex_row in df_excel.iterrows():
            name = str(ex_row['الاسم'])
            amount = float(ex_row['المبلغ'])
            
            status = "❌"
            note = "لم يتم العثور على اسم مطابق"
            date_found = "-"
            
            best_score = 0
            for b_row in bank_data:
                # فحص التشابه بين العربي والإنجليزي
                score = fuzz.token_sort_ratio(name.lower(), b_row['details'].lower())
                
                if score > 70: # عتبة التشابه
                    if score > best_score:
                        best_score = score
                        date_found = b_row['date']
                        
                        if b_row['amount'] == amount:
                            status = "✅"
                            note = "تطابق تام في الاسم والمبلغ"
                        else:
                            status = "⚠️"
                            note = f"الاسم موجود لكن المبلغ بالبنك {b_row['amount']}"

            results.append({
                "الاسم (Excel)": name,
                "المبلغ المطلوب": amount,
                "الحالة": status,
                "التاريخ بالبنك": date_found,
                "ملاحظات": note
            })

        # 3. عرض النتائج
        df_final = pd.DataFrame(results)
        st.subheader("📊 نتائج المطابقة")
        
        # تلوين الجدول بناءً على الحالة
        def color_status(val):
            if val == "✅": return 'background-color: #d4edda'
            if val == "⚠️": return 'background-color: #fff3cd'
            if val == "❌": return 'background-color: #f8d7da'
            return ''

        st.table(df_final.style.applymap(color_status, subset=['الحالة']))

        # 4. تحميل النتيجة
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 تحميل تقرير المطابقة (Excel)",
            data=output.getvalue(),
            file_name="Matching_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
