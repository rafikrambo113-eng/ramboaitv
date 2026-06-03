import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# ── تهيئة الجلسة ──
if 'lang' not in st.session_state: st.session_state.lang = 'ar'
if 'theme' not in st.session_state: st.session_state.theme = 'dark'

# (تم اختصار UI_TEXT و CSS و NILESAT_LIVE_DB لتوفير المساحة، يمكنك الاحتفاظ بالتي لديك)
# تأكد من وضع القواميس والدوال التي كتبتها سابقاً في مكانها الصحيح قبل الكود أدناه.

# ── رفع الملف والمعالجة ──
uploaded_file = st.file_uploader("🚀 اختر ملف القنوات (GlobalClone00001.TLL) من الفلاشة:", type=["TLL"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    try:
        file_text = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        file_text = file_bytes.decode('latin-1')

    # محاولة كشف نوع النظام
    is_modern = 'legacybroadcast' in file_text

    st.info("✅ تم قراءة الملف بنجاح.")

    update_freq = st.checkbox("⚛️ تفعيل الصيانة الذكية وتحديث الترددات", value=True)
    add_new_ch = st.checkbox("✨ فحص وزرع القنوات الجديدة", value=True)

    channels_to_sort = []
    report_changes = []
    existing_names_upper = set()

    if is_modern:
        # معالجة JSON (كما كانت سابقاً)
        # ... (نفس منطقك السابق للـ JSON) ...
        pass
    else:
        # 🔧 معالجة الشاشات القديمة <ITEM> - (الكود المُعدل)
        item_blocks = re.findall(r'<ITEM>.*?</ITEM>', file_text, re.DOTALL | re.IGNORECASE)

        for item_str in item_blocks:
            name_match = re.search(r'<vchName>(.*?)</vchName>', item_str, re.IGNORECASE)
            freq_match = re.search(r'<frequency>(.*?)</frequency>', item_str, re.IGNORECASE)
            ch_name = name_match.group(1).strip() if name_match else "Unknown"
            old_freq = freq_match.group(1).strip() if freq_match else "N/A"
            name_up = ch_name.upper()
            existing_names_upper.add(name_up)

            updated_item_str = item_str
            # تحديث التردد
            if update_freq and name_up in NILESAT_LIVE_DB:
                live_freq = str(NILESAT_LIVE_DB[name_up]["frequency"])
                if old_freq != live_freq:
                    updated_item_str = re.sub(r'<frequency>\d+</frequency>', f'<frequency>{live_freq}</frequency>', updated_item_str, flags=re.IGNORECASE)
            
            channels_to_sort.append({"name": ch_name, "raw_str": updated_item_str})

        # الترتيب
        channels_sorted = sorted(channels_to_sort, key=lambda x: ALL_AVAILABLE_CATEGORIES.index(ai_classify(x["name"])))

        # إعادة البناء
        final_items_list = []
        for index, ch in enumerate(channels_sorted, start=1):
            raw = ch["raw_str"]
            # تحديث prNum بالرقم الجديد
            raw = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{index}</prNum>', raw, flags=re.IGNORECASE)
            final_items_list.append(raw)
        
        combined_items_str = "\r\n".join(final_items_list)

        # استبدال منطقة القنوات بالكامل في الملف باستخدام Regex دقيق
        # النمط يبحث من أول <ITEM> حتى آخر </ITEM>
        final_text_output = re.sub(r'(<ITEM>.*</ITEM>)', combined_items_str, file_text, flags=re.DOTALL | re.IGNORECASE)
        final_xml_bytes = final_text_output.encode('utf-8')

    # ── التصدير ──
    st.success("🌌 تم معالجة الملف بنجاح!")
    st.download_button(label="📥 تحميل الملف النهائي", data=final_xml_bytes, file_name="GlobalClone00001.TLL")
