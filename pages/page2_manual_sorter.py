import streamlit as st
import xml.etree.ElementTree as ET
import json
import re
import pandas as pd

# ─────────────────────────────────────────────
# 1. تهيئة الجلسة (Session State) بشكل مستقر
# ─────────────────────────────────────────────
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'channels' not in st.session_state:
    st.session_state.channels = []          
if 'ordered_channels' not in st.session_state:
    st.session_state.ordered_channels = []  
if 'is_modern' not in st.session_state:
    st.session_state.is_modern = False
if 'root' not in st.session_state:
    st.session_state.root = None
if 'broadcast_data' not in st.session_state:
    st.session_state.broadcast_data = None
if 'file_text_original' not in st.session_state:
    st.session_state.file_text_original = ""
if 'model_name' not in st.session_state:
    st.session_state.model_name = ""
if 'edit_finished' not in st.session_state:
    st.session_state.edit_finished = False 

# ─────────────────────────────────────────────
# 2. قواميس النصوص (عربي / إنجليزي)
# ─────────────────────────────────────────────
UI = {
    'ar': {
        'title':           "📺 RAMBO — المُرتب اليدوي المطور",
        'subtitle':        "⚡ نظام الترتيب الذكي المستقر: اضغط زرع، عدل أرقامك، ثم اضغط حفظ التعديلات",
        'upload_label':    "🚀 ارفع ملف القنوات (GlobalClone00001.TLL):",
        'success_read':    "🛸 تم قراءة الملف بنجاح! الموديل: ",
        'search_ph':       "🔍 ابحث عن قناة بالاسم في الملف الأصلي...",
        'all_ch_title':    "📋 1. جدول القنوات الكلي المتوفرة",
        'ordered_title':   "📊 2. جدول الترتيب النهائي (اكتب أرقام الترتيب هنا واضغط حفظ بالأسفل)",
        'col_action':      "إجراء",
        'btn_add_to_order': "➕ زرع",
        'auto_features_title': "⚙️ خيارات الفحص الذكي والصيانة الفورية للملف",
        'chk_scan_inject': "📡 تفعيل الفحص التلقائي وزرع القنوات الجديدة المتاحة على القمر فوراً",
        'chk_modern_maint': "🔧 تفعيل الصيانة الحديثة وتحديث الترددات الميتة والقديمة تلقائياً",
        'preview_title':   "🏁 استخراج وتنزيل الملفات النهائية",
        'btn_finish':      "🔒 إنهاء التعديل وتجهيز ملفات التحميل",
        'ready_msg':       "🌌 تم اعتماد الترتيب الجديد وعمل التقرير بنجاح! الملفات جاهزة الآن:",
        'btn_tll':         "📥 تحميل ملف الشاشة المعدل (GlobalClone00001.TLL)",
        'btn_txt':         "📄 تحميل تقرير لستة الترتيب (Channels_List.txt)",
        'txt_header':      "📄 تقرير الترتيب اليدوي المطور — RAMBO Page 2",
        'no_file':         "⬆️ ارفع ملف TLL أولاً لتبدأ العمل.",
    },
    'en': {
        'title':           "📺 RAMBO — Advanced Manual Sorter",
        'subtitle':        "⚡ Stable Smart Sorting System: Inject, edit order numbers, then click Save",
        'upload_label':    "🚀 Upload Channel File (GlobalClone00001.TLL):",
        'success_read':    "🛸 File Parsed Successfully! Model: ",
        'search_ph':       "🔍 Search channel name in original pool...",
        'ordered_title':   "📊 2. Final Custom List (Change numbers then click save below)",
        'col_action':      "Action",
        'btn_add_to_order': "➕ Inject",
        'auto_features_title': "⚙️ Smart Auto-Maintenance & Scanning Options",
        'chk_scan_inject': "📡 Enable Auto-Scan & Inject newly available Satellite Channels",
        'chk_modern_maint': "🔧 Enable Modern Maintenance & Auto-Update dead frequencies",
        'preview_title':   "🏁 Export & Download Final Files",
        'btn_finish':      "🔒 Finish Editing & Generate Download Links",
        'ready_msg':       "🌌 Sorting completed & report generated! Ready for download:",
        'btn_tll':         "📥 Download TV File (GlobalClone00001.TLL)",
        'btn_txt':         "📄 Download Sorted List Report (Channels_List.txt)",
        'txt_header':      "📄 Manual Sorting Advanced Report — RAMBO Page 2",
        'no_file':         "⬆️ Upload a TLL file to start.",
    }
}

t = UI[st.session_state.lang]

# ─────────────────────────────────────────────
# 3. إعداد الصفحة والـ CSS السيبراني
# ─────────────────────────────────────────────
st.set_page_config(page_title="RAMBO P2 — Advanced Sorter", page_icon="🎛️", layout="wide")

col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("🌐 English" if st.session_state.lang == 'ar' else "🌐 العربية"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
        st.rerun()
with col_theme:
    if st.button("☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

if st.session_state.theme == 'dark':
    bg_style, text_color, box_bg, box_border = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)", "#00f0ff", "rgba(13, 7, 33, 0.85)", "#00f0ff"
    box_shadow, text_shadow, footer_bg, footer_text = "rgba(0, 240, 255, 0.35)", "0 0 5px rgba(0, 240, 255, 0.4)", "#080314", "#ffffff"
    table_head_bg, table_row_bg, table_row_alt, table_border = "#0d0722", "rgba(0,240,255,0.04)", "rgba(255,0,127,0.05)", "#00f0ff33"
else:
    bg_style, text_color, box_bg, box_border = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)", "#0d0722", "#ffffff", "#ff007f"
    box_shadow, text_shadow, footer_bg, footer_text = "rgba(255, 0, 127, 0.15)", "none", "#110926", "#ffffff"
    table_head_bg, table_row_bg, table_row_alt, table_border = "#0d0722", "#f9f9ff", "#fff0f7", "#ff007f33"

font_family = "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
    .main {{ background: {bg_style} !important; color: {text_color} !important; font-family: {font_family}; }}
    h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.4) !important; text-align: center; font-weight: 900; margin-top: 5px; }}
    h3, p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] p {{ color: {text_color} !important; text-shadow: {text_shadow}; }}
    .stTextInput>div>div>input, .stNumberInput>div>div>input {{ background-color: {box_bg} !important; color: {text_color} !important; border: 2px solid {box_border} !important; border-radius: 10px !important; }}
    div[data-testid="stFileUploader"], .rambo-box {{ background: {box_bg} !important; border: 2px solid {box_border} !important; box-shadow: 0px 5px 15px {box_shadow} !important; border-radius: 14px !important; padding: 18px !important; margin-bottom: 20px !important; }}
    .stButton>button {{ background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important; color: #ffffff !important; border: 2px solid #ff007f !important; border-radius: 12px !important; font-weight: bold; width: 100%; }}
    </style>
""", unsafe_allow_html=True)

st.title(t['title'])
st.markdown(f"<h3>{t['subtitle']}</h3>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4. دالة قراءة وتفكيك ملف الـ TLL
# ─────────────────────────────────────────────
def parse_tll(file_bytes):
    try: file_text = file_bytes.decode('utf-8')
    except UnicodeDecodeError: file_text = file_bytes.decode('latin-1')

    # تنظيف مسبق لأي مسافات غريبة تمنع الـ XML Parser من العمل
    file_text_cleaned = re.sub(r'^\s+', '', file_text)
    root = ET.fromstring(file_text_cleaned.encode('utf-8'))
    
    legacy_tag = root.find(".//legacybroadcast")
    is_modern = legacy_tag is not None and legacy_tag.text

    channels = []
    if is_modern:
        bdata = json.loads(legacy_tag.text)
        for idx, ch in enumerate(bdata.get("channelList", [])):
            channels.append({
                "id": idx,
                "name": ch.get("channelName", "Unknown"),
                "freq": str(ch.get("frequency", "N/A")),
                "pol": ch.get("polarization", "Vertical"),
                "raw_node": ch
            })
        return channels, True, root, bdata, file_text, legacy_tag
    else:
        items = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)
        for idx, item_str in enumerate(items):
            nm = re.search(r'<vchName>(.*?)</vchName>', item_str)
            fq = re.search(r'<frequency>(.*?)</frequency>', item_str)
            channels.append({
                "id": idx,
                "name": nm.group(1) if nm else "Unknown",
                "freq": fq.group(1) if fq else "N/A",
                "pol": "Vertical",
                "raw_str": item_str
            })
        return channels, False, root, None, file_text, None

# ─────────────────────────────────────────────
# 5. رفع ومعالجة الملف الأصلي
# ─────────────────────────────────────────────
uploaded = st.file_uploader(t['upload_label'], type=["TLL"], key="tll_uploader_p
