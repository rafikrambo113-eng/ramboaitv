import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# 1. التعريفات الأساسية (يجب أن تكون في الأعلى)
NILESAT_LIVE_DB = {
    "AL HAYAT": {"frequency": 12207, "polarization": "Vertical"},
    "AL HAYAT 2": {"frequency": 12207, "polarization": "Vertical"},
    "SAT-7 KIDS": {"frequency": 11353, "polarization": "Vertical"},
    "SAT-7 ARABIC": {"frequency": 11353, "polarization": "Vertical"},
    "CTV": {"frequency": 12022, "polarization": "Vertical"},
    "AGHAPY TV": {"frequency": 11179, "polarization": "Horizontal"},
    "MESAT": {"frequency": 11096, "polarization": "Horizontal"},
    "IQRAA": {"frequency": 11938, "polarization": "Vertical"},
    "MAJD": {"frequency": 11862, "polarization": "Vertical"},
    "RAHMA": {"frequency": 11938, "polarization": "Vertical"},
    "QURAN KAREEM": {"frequency": 11727, "polarization": "Vertical"},
    "AL JAZEERA HD": {"frequency": 10853, "polarization": "Vertical"},
    "AL ARABIYA": {"frequency": 11938, "polarization": "Vertical"},
    "AL HADATH": {"frequency": 11938, "polarization": "Vertical"},
    "CBC": {"frequency": 12092, "polarization": "Vertical"},
    "EXTRA NEWS": {"frequency": 12092, "polarization": "Vertical"},
    "ON E": {"frequency": 12092, "polarization": "Vertical"},
    "MBC 2": {"frequency": 11938, "polarization": "Vertical"},
    "MBC 4": {"frequency": 11938, "polarization": "Vertical"},
    "ROTANA CINEMA": {"frequency": 11938, "polarization": "Vertical"},
    "ON TIME SPORTS 1": {"frequency": 11861, "polarization": "Vertical"},
    "ON TIME SPORTS 2": {"frequency": 11861, "polarization": "Vertical"},
    "SPACE TOON": {"frequency": 11727, "polarization": "Vertical"},
    "MAJID": {"frequency": 11862, "polarization": "Vertical"},
    "TOYOR ALJANNAH": {"frequency": 11179, "polarization": "Horizontal"}
}

ALL_AVAILABLE_CATEGORIES = ["⛪ قنوات مسيحية", "🕌 قنوات إسلامية", "🎬 مسلسلات ودراما", "🍿 أفلام عربية وأجنبية", "👶 أطفال وكرتون", "⚽ رياضة", "📰 أخبار وسياسة", "📺 قنوات عامة ومنوعات"]

def ai_classify(channel_name):
    # (دالة التصنيف الخاصة بك هنا)
    return ALL_AVAILABLE_CATEGORIES[-1]

# ── رفع الملف والمعالجة ──
uploaded_file = st.file_uploader("🚀 اختر ملف القنوات (GlobalClone00001.TLL) من الفلاشة:", type=["TLL"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_text = file_bytes.decode('latin-1', errors='ignore')
    
    is_modern = 'legacybroadcast' in file_text
    st.info("✅ تم قراءة الملف بنجاح.")

    update_freq = st.checkbox("⚛️ تفعيل الصيانة الذكية وتحديث الترددات", value=True)
    
    channels_to_sort = []
    
    # 🔧 معالجة الشاشات القديمة <ITEM>
    item_blocks = re.findall(r'<ITEM>.*?</ITEM>', file_text, re.DOTALL | re.IGNORECASE)

    for item_str in item_blocks:
        name_match = re.search(r'<vchName>(.*?)</vchName>', item_str, re.IGNORECASE)
        freq_match = re.search(r'<frequency>(.*?)</frequency>', item_str, re.IGNORECASE)
        ch_name = name_match.group(1).strip() if name_match else "Unknown"
        old_freq = freq_match.group(1).strip() if freq_match else "N/A"
        name_up = ch_name.upper()

        updated_item_str = item_str
        # التعديل هنا: التأكد من وجود NILESAT_LIVE_DB وتحديث التردد
        if update_freq and name_up in NILESAT_LIVE_DB:
            live_freq = str(NILESAT_LIVE_DB[name_up]["frequency"])
            updated_item_str = re.sub(r'<frequency>\d+</frequency>', f'<frequency>{live_freq}</frequency>', updated_item_str, flags=re.IGNORECASE)
        
        channels_to_sort.append({"name": ch_name, "raw_str": updated_item_str})

    # الترتيب (اختياري حسب منطقك)
    channels_sorted = sorted(channels_to_sort, key=lambda x: ALL_AVAILABLE_CATEGORIES.index(ai_classify(x["name"])))

    # إعادة البناء
    final_items_list = []
    for index, ch in enumerate(channels_sorted, start=1):
        raw = ch["raw_str"]
        raw = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{index}</prNum>', raw, flags=re.IGNORECASE)
        final_items_list.append(raw)
    
    combined_items_str = "\r\n".join(final_items_list)
    final_text_output = re.sub(r'(<ITEM>.*</ITEM>)', combined_items_str, file_text, flags=re.DOTALL | re.IGNORECASE)
    final_xml_bytes = final_text_output.encode('utf-8')

    st.download_button(label="📥 تحميل الملف النهائي", data=final_xml_bytes, file_name="GlobalClone00001.TLL")
