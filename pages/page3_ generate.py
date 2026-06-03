import streamlit as st
import xml.etree.ElementTree as ET
import json

def apply_egypt_config(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # 1. تحديث الـ ModelInfo الرئيسي (XML)
    model_info = root.find(".//ModelInfo")
    model_info.find("BroadcastCountrySetting").text = "EGY"
    model_info.find("country").text = "EGY"

    # 2. تحديث الـ iepg والـ legacybroadcast (JSON المدمج)
    # هذا الجزء هو السبب الرئيسي لرفض الملفات
    for tag in ["iepg", "legacybroadcast"]:
        element = root.find(f".//{tag}")
        if element is not None and element.text:
            data = json.loads(element.text)
            # تحديث كود الدولة داخل الـ JSON
            if 'modelInfo' in data:
                data['modelInfo']['country'] = "Egypt"
            element.text = json.dumps(data)
    
    return ET.tostring(root, encoding='utf-8', method='xml')

# في واجهة الاستخدام:
# عند اختيار "مصر"، استدعِ هذه الدالة وقم بتنزيل الملف الناتج باسم GlobalClone00001.TLL
