import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# تهيئة الجلسة
if 'lang' not in st.session_state: st.session_state.lang = 'ar'
if 'theme' not in st.session_state: st.session_state.theme = 'dark'

# نصوص الواجهة (كما هي في ملفك)
UI_TEXT = {
    'ar': {'title': "📺 RAMBO - المنسق العالمي لشاشات LG", 'subtitle': "⚡ هندسة متطورة لترتيب ملفات القنوات", 'upload_label': "🚀 اختر ملف القنوات (GlobalClone00001.TLL):", 'success_read': "🛸 تم قراءة الهيكل بنجاح! الموديل:", 'search_header': "🔍 محرك البحث:", 'search_placeholder': "ابحث هنا...", 'config_title': "🎛️ مصفوفة ترتيب الفئات:", 'multiselect_label': "رتب الفئات حسب الأولوية:", 'preview_title': "📊 معاينة حية:", 'channels_count': "قناة", 'ready_msg': "🌌 تم الدمج بنجاح! جاهز للتحميل.", 'btn_download_tll': "📥 تحميل ملف الشاشة النهائي", 'btn_download_txt': "📄 تحميل تقرير الترتيب"},
    'en': {'title': "📺 RAMBO - LG Universal AI Channel Sorter", 'subtitle': "⚡ Next-Gen Cyber-Engineered Architecture", 'upload_label': "🚀 Upload Channel File (GlobalClone00001.TLL):", 'success_read': "🛸 Matrix Structure Decoded! Model:", 'search_header': "🔍 Search Engine:", 'search_placeholder': "Type channel name...", 'config_title': "🎛️ Custom Category Priority Matrix:", 'multiselect_label': "Select categories order:", 'preview_title': "📊 Channel Grid Preview:", 'channels_count': "Channels", 'ready_msg': "🌌 Quantum Matrix Deployment Successful!", 'btn_download_tll': "📥 Download Final TV Configuration", 'btn_download_txt': "📄 Download Sorting Diagnostics"}
}
t = UI_TEXT[st.session_state.lang]

# تعريف قاعدة البيانات والوظائف (ai_classify, NILESAT_LIVE_DB) - [ضعها هنا كما في كودك الأصلي]
# (تأكد من إبقاء دوال ai_classify و قاعدة بيانات الأقمار كما هي)

st.title(t['title'])
uploaded_file = st.file_uploader(t['upload_label'], type=["TLL"])

if uploaded_file is not None:
    file_text = uploaded_file.read().decode('utf-8', errors='ignore')
    
    # تحديد النوع (Modern vs Legacy)
    is_modern = "<legacybroadcast>" in file_text
    
    # المعالجة والترتيب (المنطق البرمجي)
    # ... [هنا يوضع منطق معالجة القنوات الذي قمت ببرمجته] ...
    
    # ── التعديل الجوهري للترتيب في الملفات القديمة ──
    if not is_modern:
        # تأكد هنا أنك تقوم بفرز مصفوفة النصوص (raw_str) بناءً على الترتيب الجديد
        # وهذا هو الكود المحدث لضمان استجابة الشاشة:
        
        item_strings_sorted = []
        for index, ch in enumerate(channels_sorted, start=1):
            raw = ch["raw_str"]
            # 1. تحديث رقم القناة في الـ XML
            if "<prNum>" in raw:
                raw = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{index}</prNum>', raw)
            else:
                raw = raw.replace("<ITEM>", f"<ITEM>\r\n<prNum>{index}</prNum>")
            
            # 2. إضافة النص المرتب للمصفوفة
            item_strings_sorted.append(raw)

        # 3. دمج المصفوفة بالترتيب الجديد تماماً
        combined_items_str = "\r\n".join(item_strings_sorted)
        
        # 4. إعادة بناء الملف
        start_idx = file_text.find("<ITEM>")
        end_idx = file_text.rfind("</ITEM>") + len("</ITEM>")
        if start_idx != -1:
            final_text_output = file_text[:start_idx] + combined_items_str + file_text[end_idx:]
            final_xml_bytes = final_text_output.encode('utf-8')
    else:
        # [منطق الـ Modern JSON هنا كما كان]
        pass

    # زر التحميل
    st.download_button(t['btn_download_tll'], data=final_xml_bytes, file_name="GlobalClone00001.TLL")
