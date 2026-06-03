import streamlit as st
import xml.etree.ElementTree as ET
import json
import os

# --- إعدادات القوالب (يجب وضع ملفاتك في مجلد باسم templates) ---
TEMPLATES = {
    "32_inch": "templates/GlobalClone_32.TLL",
    "55_inch": "templates/GlobalClone_55.TLL"
}

def generate_tll(template_path, country_code, country_name):
    # تحميل الملف من المسار
    tree = ET.parse(template_path)
    root = tree.getroot()
    
    # 1. تحديث XML Header
    model_info = root.find(".//ModelInfo")
    if model_info is not None:
        model_info.find("BroadcastCountrySetting").text = country_code
        model_info.find("country").text = country_code
    
    # 2. تحديث JSON المدمج (للموديلات الحديثة)
    for tag in ["iepg", "legacybroadcast"]:
        element = root.find(f".//{tag}")
        if element is not None and element.text:
            data = json.loads(element.text)
            if 'modelInfo' in data:
                data['modelInfo']['country'] = country_name
            element.text = json.dumps(data)
            
    return ET.tostring(root, encoding='utf-8', method='xml')

# --- واجهة المولد ---
st.title("⚙️ RAMBO - المولد التلقائي")

with st.form("generator_form"):
    country = st.selectbox("🌍 بلد البث:", ["مصر", "السعودية"])
    inch = st.selectbox("📏 حجم الشاشة:", ["32_inch", "55_inch"])
    submit = st.form_submit_button("توليد الملف")

if submit:
    # اختيار القالب بناءً على اختيار المستخدم
    template_file = TEMPLATES[inch]
    
    if os.path.exists(template_file):
        country_map = {"مصر": ("EGY", "Egypt"), "السعودية": ("SAU", "Saudi Arabia")}
        code, name = country_map[country]
        
        # التوليد
        final_data = generate_tll(template_file, code, name)
        
        st.success(f"تم التوليد بنجاح باستخدام قالب: {inch}")
        st.download_button("📥 تحميل الملف النهائي", data=final_data, file_name="GlobalClone00001.TLL")
    else:
        st.error(f"خطأ: الملف {template_file} غير موجود في المجلد. يرجى التأكد من رفع ملفات التمبلت.")
