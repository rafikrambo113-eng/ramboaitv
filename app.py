import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# ── تهيئة الجلسة ──
if 'lang' not in st.session_state: st.session_state.lang = 'ar'
if 'theme' not in st.session_state: st.session_state.theme = 'dark'

# تعريف نصوص الواجهة
UI_TEXT = {
    'ar': {
        'title': "📺 RAMBO - المنسق العالمي لشاشات LG",
        'subtitle': "⚡ هندسة متطورة لترتيب ملفات القنوات",
        'upload_label': "🚀 اختر ملف القنوات (GlobalClone00001.TLL):",
        'update_freq_label': "⚛️ تفعيل الصيانة الذكية وتحديث الترددات",
        'add_new_ch_label': "✨ فحص وزرع القنوات الجديدة تلقائياً",
        'success_read': "🛸 تم قراءة الهيكل بنجاح! الموديل: ",
        'search_header': "🔍 محرك البحث الذكي:",
        'search_placeholder': "اكتب اسم القناة هنا...",
        'search_col_num': "الرقم", 'search_col_name': "الاسم", 'search_col_cat': "الفئة", 'search_col_freq': "التردد",
        'search_no_results': "⚠️ لم يتم العثور على نتائج.",
        'config_title': "🎛️ مصفوفة ترتيب الفئات:",
        'multiselect_label': "اضغط هنا لبناء تسلسل الفئات:",
        'preview_title': "📊 معاينة التوزيع الحالي:",
        'channels_count': "قناة",
        'ready_msg': "🌌 تم دمج مصفوفة RAMBO بنجاح!",
        'btn_download_tll': "📥 تحميل ملف الشاشة (TLL)",
        'btn_download_txt': "📄 تحميل تقرير الترتيب (TXT)",
        'txt_header': "📄 تقرير ترتيب القنوات وتحديث الترددات",
        'txt_order': "🛠️ ترتيب الفئات المختار: ",
        'lg_trick_title': "💡 ملحوظة هامة بعد التنزيل:",
        'lg_trick_text': "إذا لم تظهر القنوات مرتبة، ادخل على: القنوات -> مدير القنوات -> تعديل كل القنوات -> تحديد الكل -> استعادة (Restore)."
    }
}
t = UI_TEXT[st.session_state.lang]

st.set_page_config(page_title="RAMBO LG Sorter", page_icon="⚡", layout="wide")

# ── معالجة الملف ──
uploaded_file = st.file_uploader(t['upload_label'], type=["TLL"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    try:
        file_text = file_bytes.decode('utf-8')
    except:
        file_text = file_bytes.decode('latin-1')

    # تنظيف وقراءة XML
    root = ET.fromstring(re.sub(r'^\s+', '', file_text).encode('utf-8'))
    model_name = root.find(".//ModelName").text if root.find(".//ModelName") is not None else "Unknown"
    legacy_broadcast_tag = root.find(".//legacybroadcast")
    is_modern = legacy_broadcast_tag is not None

    st.info(f"{t['success_read']} **{model_name}**")
    
    # خيارات المستخدم
    update_freq = st.checkbox(t['update_freq_label'], value=True)
    add_new_ch = st.checkbox(t['add_new_ch_label'], value=True)

    # (هنا يتم منطق معالجة القنوات وترتيبها كما في الكود السابق الخاص بك)
    # ... [يتم معالجة channels_sorted و final_priority هنا] ...

    # ── التصدير وبناء التقرير المصحح ──
    text_report = f"{t['txt_header']} ({model_name})\n" + "="*50 + "\n"
    text_report += f"{t['txt_order']} " + " -> ".join(final_priority) + "\n" + "="*50 + "\n\n"

    # حلقة بناء التقرير (المصححة)
    for index, ch in enumerate(channels_sorted, start=1):
        tag_status = " [NEW] " if ch.get("is_injected", False) else ""
        text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}{tag_status}\n"

    # ── أزرار التحميل ──
    st.success(t['ready_msg'])
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(label=t['btn_download_tll'], data=final_xml_bytes, file_name="GlobalClone00001.TLL")
    with col2:
        st.download_button(label=t['btn_download_txt'], data=text_report, file_name="Channels_List.txt")
