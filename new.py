import pandas as pd
import pdfplumber
import re
from fuzzywuzzy import fuzz

def extract_bank_data(pdf_path):
    """استخراج الحركات المالية (المبالغ المستلمة) من ملف البنك PDF"""
    bank_records = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue
            
            # تحديد أعمدة الكشف (تختلف حسب التصميم، هنا بناءً على ملفك)
            # الرصيد، المبالغ المستلمة، المبالغ المدفوعة، التاريخ، التفاصيل...
            for row in table[1:]:  # تخطي العنوان
                if row[1]:  # إذا كان هناك مبلغ في خانة "المبالغ المستلمة"
                    try:
                        amount = float(row[1].replace(',', ''))
                        details = row[4] if row[4] else ""
                        date = row[5] if row[5] else ""
                        bank_records.append({
                            "amount": amount,
                            "details": details,
                            "date": date
                        })
                    except:
                        continue
    return bank_records

def match_data(excel_path, bank_records):
    """مطابقة ملف Excel مع بيانات البنك"""
    df_excel = pd.read_excel(excel_path)
    results = []

    for index, row in df_excel.iterrows():
        excel_name = str(row['الاسم']).strip()
        excel_amount = float(row['المبلغ'])
        
        status = "❌ غير موجود"
        note = ""
        
        for record in bank_records:
            # تنظيف النصوص للمقارنة (إزالة المسافات والرموز)
            clean_details = record['details'].replace('\n', ' ')
            
            # حساب نسبة التشابه بين الاسم في اكسل والتفاصيل في البنك
            name_similarity = fuzz.partial_ratio(excel_name.lower(), clean_details.lower())
            
            # 1. تطابق تام (الاسم موجود والمبلغ متطابق)
            if name_similarity > 80 and excel_amount == record['amount']:
                status = "✅"
                note = f"تم التأكيد في تاريخ {record['date']}"
                break
            
            # 2. حالة الشك (الاسم موجود لكن المبلغ مختلف)
            elif name_similarity > 80 and excel_amount != record['amount']:
                status = "⚠️"
                note = f"الاسم مطابق لكن المبلغ بالبنك هو {record['amount']}"
                break
            
            # 3. حالة شك (تشابه متوسط في الاسم)
            elif 50 < name_similarity <= 80:
                status = "❓"
                note = "تشابه جزئي في الاسم، يرجى المراجعة"

        results.append({
            "الاسم": excel_name,
            "المبلغ المطلوب": excel_amount,
            "الحالة": status,
            "ملاحظات": note
        })

    return pd.DataFrame(results)

# --- التشغيل التجريبي ---
# pdf_file = "Account_Statement.pdf"
# excel_file = "clients.xlsx"
# bank_data = extract_bank_data(pdf_file)
# final_report = match_data(excel_file, bank_data)
# final_report.to_excel("Matching_Report.xlsx", index=False)
