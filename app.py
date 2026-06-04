import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# تهيئة الـ Session State
if 'lang' not in st.session_state: st.session_state.lang = 'ar'
if 'theme' not in st.session_state: st.session_state.theme = 'dark'
if 'loaded_file_name' not in st.session_state: st.session_state.loaded_file_name = ""
if 'channels' not in st.session_state: st.session_state.channels = []
if 'is_modern' not in st.session_state: st.session_state.is_modern = False
if 'root' not in st.session_state: st.session_state.root = None
if 'broadcast_data' not in st.session_state: st.session_state.broadcast_data = None
if 'file_text_original' not in st.session_state: st.session_state.file_text_original = ""
if 'model_name' not in st.session_state: st.session_state.model_name = ""
if 'legacy_tag' not in st.session_state: st.session_state.legacy_tag = None

# قاموس النصوص
UI_TEXT = {
    'ar': {
        'title': "📺 RAMBO - المُرتب العالمي لشاشات LG",
        'subtitle': "⚡ ترتيب ذكي لملفات قنوات LG",
        'upload_label': "🚀 اختر ملف القنوات (GlobalClone00001.TLL) من الفلاشة:",
        'update_freq_label': "⚛️ تحديث الترددات تلقائياً",
        'add_new_ch_label': "✨ إضافة القنوات الجديدة المتاحة تلقائياً",
        'success_read': "🛸 تم قراءة الملف بنجاح!",
        'system_label': "النظام:",
        'total_label': "إجمالي القنوات:",
        'search_header': "🔍 البحث عن قناة داخل الملف:",
        'search_placeholder': "اكتب اسم القناة هنا...",
        'search_col_num': "الرقم",
        'search_col_name': "اسم القناة",
        'search_col_cat': "الفئة",
        'search_col_freq': "التردد",
        'search_no_results': "⚠️ لا توجد نتائج مطابقة.",
        'config_title': "🎛️ ترتيب الفئات:",
        'multiselect_label': "اختر الفئات بالترتيب المطلوب:",
        'preview_title': "📊 معاينة التوزيع الحالي:",
        'channels_count': "قناة",
        'ready_msg': "✅ تم تجهيز الملف النهائي للتحميل:",
        'btn_download_tll': "📥 تحميل ملف الشاشة النهائي (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 تحميل تقرير الترتيب (Channels_List.txt)",
        'txt_header': "📄 تقرير ترتيب القنوات النهائي",
        'txt_order': "🛠️ ترتيب الفئات المختار: ",
        'lg_trick_title': "💡 ملحوظة فنية:",
        'lg_trick_text': "لو الشاشة لم تُظهر الترتيب كما هو، ادخل Channel Manager ثم Edit All Channels ثم Restore.",
        'no_file': "⬆️ ارفع ملف TLL أولاً لتبدأ العمل."
    },
    'en': {
        'title': "📺 RAMBO - LG Universal Sorter",
        'subtitle': "⚡ Smart LG channel file sorting",
        'upload_label': "🚀 Upload Channel File (GlobalClone00001.TLL) from USB:",
        'update_freq_label': "⚛️ Auto update frequencies",
        'add_new_ch_label': "✨ Auto inject missing channels",
        'success_read': "🛸 File parsed successfully!",
        'system_label': "System:",
        'total_label': "Total channels:",
        'search_header': "🔍 Search inside file:",
        'search_placeholder': "Type channel name...",
        'search_col_num': "No.",
        'search_col_name': "Channel Name",
        'search_col_cat': "Category",
        'search_col_freq': "Frequency",
        'search_no_results': "⚠️ No matching results.",
        'config_title': "🎛️ Category order:",
        'multiselect_label': "Select categories in desired order:",
        'preview_title': "📊 Current distribution preview:",
        'channels_count': "Channels",
        'ready_msg': "✅ Final file ready for download:",
        'btn_download_tll': "📥 Download Final TV File (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 Download Sorting Report (Channels_List.txt)",
        'txt_header': "📄 Final Channel Sorting Report",
        'txt_order': "🛠️ Selected category priority: ",
        'lg_trick_title': "💡 Technical note:",
        'lg_trick_text': "If the TV does not show the exact order, open Channel Manager, then Edit All Channels, then Restore.",
        'no_file': "⬆️ Upload a TLL file to start."
    }
}

t = UI_TEXT[st.session_state.lang]
st.set_page_config(page_title="RAMBO - LG Sorter", page_icon="⚡", layout="wide")

# إعدادات الـ Theme والـ Styling
if st.session_state.theme == 'dark':
    bg_style = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)"
    text_color = "#00f0ff"
    box_bg = "rgba(13, 7, 33, 0.85)"
    box_border = "#00f0ff"
    footer_bg = "#05020d"
    footer_text = "#ffffff"
else:
    bg_style = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
    text_color = "#0d0722"
    box_bg = "#ffffff"
    box_border = "#ff007f"
    footer_bg = "#e4e7eb"
    footer_text = "#000000"

st.markdown(f"""<style>.main {{ background: {bg_style} !important; }}</style>""", unsafe_allow_html=True)

# باقي الكود (وظائف parse_tll و ai_classify كما هي...)
# ... [ضع الدوال الخاصة بك هنا] ...

# تصحيح منطقة عرض الأزرار والفوتر في نهاية الكود:
st.write("---")
st.success(t['ready_msg'])

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.download_button(
        label=t['btn_download_tll'],
        data=final_xml_bytes, # تأكد أن هذا المتغير معرف
        file_name="GlobalClone00001.TLL",
        mime="application/octet-stream"
    )
with col_btn2:
    st.download_button(
        label=t['btn_download_txt'],
        data=text_report, # تأكد أن هذا المتغير معرف
        file_name="Channels_List.txt",
        mime="text/plain; charset=utf-8"
    )

# الملحوظة الفنية
st.markdown(f"""
<div style="background-color: rgba(255, 165, 0, 0.12); border-left: 5px solid #ffa500; padding: 20px; border-radius: 12px; margin-top: 25px;">
    <h4 style="color: #ffa500; margin-top: 0; font-weight: bold;">{t['lg_trick_title']}</h4>
    <p>{t['lg_trick_text']}</p>
</div>
""", unsafe_allow_html=True)

# الفوتر
whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"
st.markdown(f"""
<div style="background:{footer_bg}; border:2px solid #00f0ff; color:{footer_text} !important; padding:35px; text-align:center; border-radius:20px; margin-top:65px;">
    <div style="color:#ff007f; font-size:26px; font-weight:bold;">🛠️ DEVELOPER ENG: RAFIK RAMBO</div>
    <div>📱 <b>MOBILE:</b> +201280339779</div>
    <a href="{whatsapp_url}" target="_blank" style="color:#25d366 !important; margin-top:20px; display:inline-block;">WhatsApp Web</a>
</div>
""", unsafe_allow_html=True)
