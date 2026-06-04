import streamlit as st
import xml.etree.ElementTree as ET
import json
import re
import pandas as pd

# ─────────────────────────────────────────────
# 1. Session State
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
if 'last_file_name' not in st.session_state:
    st.session_state.last_file_name = None

# ─────────────────────────────────────────────
# 2. UI Text
# ─────────────────────────────────────────────
UI = {
    'ar': {
        'title': "📺 RAMBO — المُرتب اليدوي المطور",
        'subtitle': "⚡ نظام الترتيب الذكي المستقر",
        'upload_label': "🚀 ارفع ملف القنوات (TLL):",
        'success_read': "🛸 تم قراءة الملف بنجاح! الموديل: ",
        'search_ph': "🔍 ابحث عن قناة...",
        'all_ch_title': "📋 القنوات",
        'ordered_title': "📊 الترتيب النهائي",
        'col_action': "إجراء",
        'btn_add_to_order': "➕ زرع",
        'preview_title': "🏁 التحميل النهائي",
        'btn_finish': "🔒 إنهاء",
        'ready_msg': "🌌 تم تجهيز الملفات!",
        'btn_tll': "📥 تحميل TLL",
        'btn_txt': "📄 تحميل تقرير",
        'no_file': "⬆️ ارفع ملف أولاً",
    },
    'en': {
        'title': "📺 RAMBO Sorter",
        'subtitle': "⚡ Smart Sorting System",
        'upload_label': "🚀 Upload TLL File:",
        'success_read': "🛸 File Loaded: ",
        'search_ph': "🔍 Search...",
        'all_ch_title': "📋 Channels",
        'ordered_title': "📊 Final Order",
        'col_action': "Action",
        'btn_add_to_order': "➕ Add",
        'preview_title': "🏁 Download",
        'btn_finish': "🔒 Finish",
        'ready_msg': "🌌 Ready!",
        'btn_tll': "📥 Download TLL",
        'btn_txt': "📄 Download TXT",
        'no_file': "⬆️ Upload file first",
    }
}

t = UI[st.session_state.lang]

# ─────────────────────────────────────────────
# 3. Page setup
# ─────────────────────────────────────────────
st.set_page_config(page_title="RAMBO", layout="wide")

st.title(t['title'])
st.markdown(t['subtitle'])

# ─────────────────────────────────────────────
# 4. Parse TLL
# ─────────────────────────────────────────────
def parse_tll(file_bytes):
    try:
        file_text = file_bytes.decode('utf-8')
    except:
        file_text = file_bytes.decode('latin-1')

    root = ET.fromstring(file_text.encode('utf-8'))
    legacy_tag = root.find(".//legacybroadcast")

    channels = []
    is_modern = legacy_tag is not None and legacy_tag.text

    if is_modern:
        data = json.loads(legacy_tag.text)
        for i, ch in enumerate(data.get("channelList", [])):
            channels.append({
                "id": i,
                "name": ch.get("channelName"),
                "freq": ch.get("frequency"),
                "raw_node": ch
            })
        return channels, True, root, data, file_text, legacy_tag

    else:
        items = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)
        for i, item in enumerate(items):
            name = re.search(r'<vchName>(.*?)</vchName>', item)
            freq = re.search(r'<frequency>(.*?)</frequency>', item)
            channels.append({
                "id": i,
                "name": name.group(1) if name else "Unknown",
                "freq": freq.group(1) if freq else "N/A",
                "raw_str": item
            })
        return channels, False, root, None, file_text, None

# ─────────────────────────────────────────────
# 5. Upload
# ─────────────────────────────────────────────
uploaded = st.file_uploader(t['upload_label'], type=["TLL"])

if uploaded is not None:

    if st.session_state.last_file_name != uploaded.name:
        st.session_state.channels = []
        st.session_state.ordered_channels = []
        st.session_state.edit_finished = False
        st.session_state.last_file_name = uploaded.name

    if not st.session_state.channels:
        file_bytes = uploaded.read()

        (st.session_state.channels,
         st.session_state.is_modern,
         st.session_state.root,
         st.session_state.broadcast_data,
         st.session_state.file_text_original,
         st.session_state.legacy_tag) = parse_tll(file_bytes)

        st.session_state.model_name = "TV Model Loaded"

# ─────────────────────────────────────────────
# 6. لو مفيش ملف
# ─────────────────────────────────────────────
if not st.session_state.channels:
    st.info(t['no_file'])
    st.stop()

# ─────────────────────────────────────────────
# 7. نجاح القراءة
# ─────────────────────────────────────────────
st.success(f"{t['success_read']} {st.session_state.model_name}")

# ─────────────────────────────────────────────
# 8. جدول بسيط
# ─────────────────────────────────────────────
st.write("### " + t['all_ch_title'])

for ch in st.session_state.channels[:20]:
    st.write(f"{ch['name']} - {ch['freq']}")

# ─────────────────────────────────────────────
# 9. Download (مبسّط)
# ─────────────────────────────────────────────
if st.session_state.channels:
    if st.button(t['btn_finish']):
        st.session_state.edit_finished = True

if st.session_state.edit_finished:
    st.success(t['ready_msg'])

    txt = "\n".join([f"{c['name']} - {c['freq']}" for c in st.session_state.channels])

    st.download_button(t['btn_txt'], txt, file_name="channels.txt")

# ─────────────────────────────────────────────
# 10. 🔥 FOOTER (يظهر دائمًا)
# ─────────────────────────────────────────────
whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779"

st.markdown(f"""
<div style="
background:#0f172a;
border:2px solid #00f0ff;
color:white;
padding:30px;
text-align:center;
border-radius:15px;
margin-top:50px;
">
<b>🛠️ DEVELOPER ENG: RAFIK RAMBO</b><br><br>
📱 +201280339779<br>
✉️ rafikrambo113@gmail.com<br><br>

<a href="{whatsapp_url}" style="color:#25d366;">WhatsApp</a>
</div>
""", unsafe_allow_html=True)
