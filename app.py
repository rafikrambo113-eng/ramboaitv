import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# ── تهيئة الجلسة ──
if 'lang' not in st.session_state: st.session_state.lang = 'ar'
if 'theme' not in st.session_state: st.session_state.theme = 'dark'

# (تم اختصار الـ UI_TEXT للتركيز على التصحيح، يمكنك استبداله بالنص الكامل لديك)
# ... [البيانات من المصادر 90-105] ...

# ── منطق معالجة الملفات (الجزء المصحح) ──
# عند التصدير (قبل زر التحميل):
text_report = f"{t['txt_header']} ({model_name})\n" + "="*50 + "\n"
text_report += f"{t['txt_order']} " + " -> ".join(final_priority) + "\n" + "="*50 + "\n\n"

if is_modern:
    final_list_modern = []
    for index, ch in enumerate(channels_sorted, start=1):
        node = ch["node_data"]
        node["majorNumber"] = index
        final_list_modern.append(node)
        
        # تصحيح: بناء التقرير بشكل صحيح داخل حلقة التكرار
        tag_status = " [NEW] " if ch["is_injected"] else ""
        text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}{tag_status}\n"
    
    broadcast_data["channelList"] = final_list_modern
    legacy_broadcast_tag.text = json.dumps(broadcast_data, ensure_ascii=False, separators=(',', ':'))
    final_xml_bytes = ET.tostring(root, encoding="utf-8")

else:
    # معالجة الشاشات القديمة
    item_strings_sorted = []
    for index, ch in enumerate(channels_sorted, start=1):
        raw = ch["raw_str"]
        if "<prNum>" in raw:
            raw = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{index}</prNum>', raw)
        else:
            raw = raw.replace("<ITEM>", f"<ITEM>\r\n<prNum>{index}</prNum>")
        item_strings_sorted.append(raw)
        
        # تصحيح: بناء التقرير للأنظمة القديمة
        tag_status = " [NEW] " if ch["is_injected"] else ""
        text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}{tag_status}\n"

    combined_items_str = "\r\n".join(item_strings_sorted)
    # ... [باقي كود التجميع النصي] ...
    try: final_xml_bytes = final_text_output.encode('utf-8')
    except UnicodeEncodeError: final_xml_bytes = final_text_output.encode('latin-1')
