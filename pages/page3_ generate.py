import streamlit as st
import xml.etree.ElementTree as ET
import json

# دالة لاختيار التمبلت بناءً على الاختيارات
def select_template(year, inch):
    # إذا كانت حديثة (55 بوصة وما فوق) نستخدم ملف الـ 55
    if "2020" in year:
        return "GlobalClone_55_Template.TLL" 
    # إذا كانت قديمة (أو 32 بوصة) نستخدم ملف الـ 32
    else:
        return "GlobalClone_32_Template.TLL"

# دالة التوليد الكاملة (Master Generator)
def generate_final_file(template_path, country_code, country_name):
    tree = ET.parse(template_path)
    root = tree.getroot()
    
    # 1. تحديث الترويسة (Header)
    model_info = root.find(".//ModelInfo")
    model_info.find("BroadcastCountrySetting").text = country_code
    model_info.find("country").text = country_code
    
    # 2. تحديث هيكل الـ JSON المدمج (لتفادي مشكلة "الملف لا يعمل")
    for tag in ["iepg", "legacybroadcast"]:
        element = root.find(f".//{tag}")
        if element is not None and element.text:
            data = json.loads(element.text)
            if 'modelInfo' in data:
                data['modelInfo']['country'] = country_name
            element.text = json.dumps(data)
            
    return ET.tostring(root, encoding='utf-8', method='xml')

# --- واجهة المستخدم في صفحة التوليد ---
st.title("🚀 RAMBO - المولد الذكي المتكامل")

# الاختيارات الإجبارية التي طلبتها
with st.form("generator_form"):
    country = st.selectbox("🌍 بلد البث (إجباري):", ["مصر", "السعودية"])
    year = st.selectbox("📅 سنة الصنع (إجباري):", ["قديم (قبل 2020)", "حديث (2020-2026)"])
    inch = st.selectbox("📏 البوصة (اختياري):", ["32", "55", "أخرى"])
    satellite = st.selectbox("🛰️ القمر الصناعي (إجباري):", ["نايل سات"])
    
    submit = st.form_submit_button("توليد ملف القنوات")

if submit:
    # 1. اختيار التمبلت الأساسي (المخزن عندك في السيرفر)
    template = select_template(year, inch)
    
    # 2. تحضير كود البلد
    country_map = {"مصر": ("EGY", "Egypt"), "السعودية": ("SAU", "Saudi Arabia")}
    code, name = country_map[country]
    
    # 3. التوليد
    final_data = generate_final_file(template, code, name)
    
    st.success(f"✅ تم توليد الملف بنجاح باستخدام تمبلت: {template}")
    st.download_button("📥 تحميل الملف النهائي", data=final_data, file_name="GlobalClone00001.TLL")
