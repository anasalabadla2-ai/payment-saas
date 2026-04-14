import streamlit as st
import pandas as pd
import pdfplumber
from fuzzywuzzy import fuzz
import io

# إعدادات الصفحة
st.set_page_config(page_title="مطابق البنك الذكي", layout="wide")

st.title("🏦 نظام مطابقة كشوفات بنك فلسطين")
st.markdown("قم برفع ملف البنك (PDF) وملف العملاء (Excel) للمطابقة التلقائية.")

# 1. وظيفة استخراج البيانات من ملف البنك
def extract_bank_received(pdf_file):
    data = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table[1:]:
                    if len(row) > 5 and row[1] and row[1].strip(): 
                        try:
                            data.append({
                                "amount": float(row[1].replace(',', '')),
                                "details": str(row[4]),
                                "date": str(row[5])
                            })
                        except: continue
    return data

# 2. واجهة رفع الملفات
col1, col2 = st.columns(2)
with col1:
    bank_file = st.file_uploader("ارفع كشف البنك (PDF)", type=["pdf"])
with col2:
    excel_file = st.file_uploader("ارفع ملف الإكسل (Excel)", type=["xlsx"])

# 3. منطق المعالجة والمطابقة
if bank_file and excel_file:
    if st.button("بدء عملية المطابقة"):
        bank_data = extract_bank_received(bank_file)
        df_excel = pd.read_excel(excel_file)
        
        name_col = next((c for c in df_excel.columns if 'اسم' in str(c) or 'name' in str(c).lower()), None)
        amount_col = next((c for c in df_excel.columns if 'مبلغ' in str(c) or 'amount' in str(c).lower()), None)

        if not name_col or not amount_col:
            st.error(f"❌ لم يتم العثور على أعمدة 'الاسم' و 'المبلغ'. الأعمدة الموجودة في ملفك هي: {list(df_excel.columns)}")
        else:
            results = []
            for _, ex_row in df_excel.iterrows():
                name = str(ex_row[name_col]).strip()
                try:
                    amount = float(ex_row[amount_col])
                except:
                    amount = 0
                
                status = "❌"
                note = "لم يتم العثور على سجل مطابق"
                date_found = "-"
                
                best_score = 0
                for b_row in bank_data:
                    score = fuzz.token_sort_ratio(name.lower(), b_row['details'].lower())
                    if score > 70: 
                        if score > best_score:
                            best_score = score
                            date_found = b_row['date']
                            if abs(b_row['amount'] - amount) < 0.1:
                                status = "✅"
                                note = "تطابق تام"
                            else:
                                status = "⚠️"
                                note = f"الاسم مطابق لكن المبلغ بالبنك {b_row['amount']}"

                results.append({
                    "الاسم المطلوب": name,
                    "المبلغ المطلوب": amount,
                    "الحالة": status,
                    "التاريخ بالبنك": date_found,
                    "ملاحظات": note
                })
            
            df_final = pd.DataFrame(results)
            st.subheader("📊 نتائج المطابقة")
            
            def color_status(val):
                if val == "✅": return 'background-color: #d4edda'
                if val == "⚠️": return 'background-color: #fff3cd'
                if val == "❌": return 'background-color: #f8d7da'
                return ''

            # تم تحديث الدالة هنا من applymap إلى map لتجنب الخطأ
            st.table(df_final.style.map(color_status, subset=['الحالة']))

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 تحميل تقرير المطابقة (Excel)",
                data=output.getvalue(),
                file_name="Matching_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
