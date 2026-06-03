import streamlit as st
import xml.etree.ElementTree as ET
import json

# تعريف إعدادات الدول (كود XML, اسم في JSON)
COUNTRY_CONFIG = {
    "مصر": {"xml_code": "EGY", "json_name": "Egypt"},
    "السعودية": {"xml_code": "SAU", "json_name": "Saudi Arabia"}
}

def generate_custom_tll(template_file, country_key):
    # تحميل ملف التمبلت الأصلي
    tree = ET.parse(template_file)
    root = tree.getroot()
    
    config = COUNTRY_CONFIG[country_key]
    
    # 1. تحديث الترويسة (XML) - الجزء الحساس للشاشة
    model_info = root.find(".//ModelInfo")
    if model_info is not None:
        model_info.find("BroadcastCountrySetting").text = config["xml_code"]
        model_info.find("country").text = config["xml_code"]
    
    # 2. تحديث الـ JSON المدمج (للموديلات الحديثة)
    for tag in ["iepg", "legacybroadcast"]:
        element = root.find(f".//{tag}")
        if element is not None and element.text:
            data = json.loads(element.text)
            if 'modelInfo' in data:
                data['modelInfo']['country'] = config["json_name"]
            element.text = json.dumps(data)
            
    return ET.tostring(root, encoding='utf-8', method='xml')

# واجهة المستخدم
st.title("🚀 RAMBO - المولد الذكي للقنوات")
uploaded_file = st.file_uploader("ارفع ملف القنوات الأصلي (التمبلت)", type=['TLL', 'bak'])
selected_country = st.selectbox("اختر بلد البث:", list(COUNTRY_CONFIG.keys()))

if uploaded_file and st.button("توليد الملف النهائي"):
    final_data = generate_custom_tll(uploaded_file, selected_country)
    st.download_button("📥 تحميل الملف المعدل", data=final_data, file_name="GlobalClone00001.TLL")
