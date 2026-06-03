import xml.etree.ElementTree as ET
import json

def fix_tll_file(file_content, target_code, target_name):
    # تحميل الملف
    root = ET.fromstring(file_content)
    
    # 1. تعديل الترويسة الرئيسية (XML)
    model_info = root.find(".//ModelInfo")
    if model_info is not None:
        model_info.find("BroadcastCountrySetting").text = target_code
        model_info.find("country").text = target_code # كود الدولة البرمجي

    # 2. تعديل الـ JSON المدمج (هنا تقع المشكلة غالباً)
    for tag_name in ["iepg", "legacybroadcast"]:
        element = root.find(f".//{tag_name}")
        if element is not None and element.text:
            data = json.loads(element.text)
            if 'modelInfo' in data:
                data['modelInfo']['country'] = target_name # اسم الدولة الصريح
            element.text = json.dumps(data)
            
    return ET.tostring(root, encoding='utf-8')
