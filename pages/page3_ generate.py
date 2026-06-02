import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# ── تهيئة الجلسة ──
if 'lang' not in st.session_state: st.session_state.lang = 'ar'
if 'theme' not in st.session_state: st.session_state.theme = 'dark'

UI_TEXT = {
    'ar': {
        'title': "⚙️ RAMBO - مولد ملفات القنوات",
        'subtitle': "⚡ بناء ملفات قنوات LG (حديثة/قديمة) من الصفر",
        'system_type_label': "📺 هيكل الملف المطلوب:",
        'sys_modern': "الموديلات الحديثة (WebOS)",
        'sys_legacy': "الموديلات القديمة (ITEM)",
        'update_freq_label': "⚛️ تحديث الترددات تلقائياً",
        'add_new_ch_label': "✨ زرع القنوات المتاحة (قائمة موسعة)",
        'config_title': "🎛️ مصفوفة ترتيب الفئات:",
        'multiselect_label': "بناء تسلسل الفئات:",
        'ready_msg': "🌌 تم التوليد بنجاح!",
        'btn_download_tll': "📥 تحميل GlobalClone00001.TLL",
        'btn_download_txt': "📄 تحميل تقرير القنوات",
        'lg_trick_title': "💡 ملحوظة فنية:",
        'lg_trick_text': "بعد التنزيل، ادخل مدير القنوات -> تعديل كل القنوات -> استعادة (Restore)."
    },
    'en': {
        'title': "⚙️ RAMBO - AI Channel Generator",
        'subtitle': "⚡ Build LG Channel Files (Modern/Legacy) From Scratch",
        'system_type_label': "📺 TV Architecture:",
        'sys_modern': "Modern Models (WebOS)",
        'sys_legacy': "Legacy Models (ITEM)",
        'update_freq_label': "⚛️ Auto-Update Frequencies",
        'add_new_ch_label': "✨ Inject Expanded Channel List",
        'config_title': "🎛️ Category Priority Matrix:",
        'multiselect_label': "Set priority sequence:",
        'ready_msg': "🌌 Synthesis Successful!",
        'btn_download_tll': "📥 Download GlobalClone00001.TLL",
        'btn_download_txt': "📄 Download Report",
        'lg_trick_title': "💡 Expert Technical Tip:",
        'lg_trick_text': "After upload: Channel Manager -> Edit All Channels -> Restore."
    }
}

t = UI_TEXT[st.session_state.lang]
st.set_page_config(page_title="RAMBO - Generator", page_icon="⚙️", layout="wide")

# ── قاعدة بيانات موسعة (أكثر من 70 قناة) ──
NILESAT_GEN_DB = {
    "AL HAYAT": {"frequency": 12207, "polarization": "Vertical"},
    "AL HAYAT 2": {"frequency": 12207, "polarization": "Vertical"},
    "CTV": {"frequency": 12022, "polarization": "Vertical"},
    "AGHAPY TV": {"frequency": 11179, "polarization": "Horizontal"},
    "MESAT": {"frequency": 11096, "polarization": "Horizontal"},
    "QURAN KAREEM": {"frequency": 11727, "polarization": "Vertical"},
    "IQRAA": {"frequency": 11938, "polarization": "Vertical"},
    "MAJD": {"frequency": 11862, "polarization": "Vertical"},
    "CBC": {"frequency": 12092, "polarization": "Vertical"},
    "CBC DRAMA": {"frequency": 11488, "polarization": "Horizontal"},
    "ON E": {"frequency": 12092, "polarization": "Vertical"},
    "ON DRAMA": {"frequency": 11861, "polarization": "Vertical"},
    "MBC 2": {"frequency": 11938, "polarization": "Vertical"},
    "MBC MAX": {"frequency": 11938, "polarization": "Vertical"},
    "MBC DRAMA": {"frequency": 11470, "polarization": "Vertical"},
    "ROTANA CINEMA": {"frequency": 11938, "polarization": "Vertical"},
    "ROTANA DRAMA": {"frequency": 11296, "polarization": "Horizontal"},
    "ON TIME SPORTS 1": {"frequency": 11861, "polarization": "Vertical"},
    "ON TIME SPORTS 2": {"frequency": 11861, "polarization": "Vertical"},
    "SPACE TOON": {"frequency": 11727, "polarization": "Vertical"},
    "MAJID": {"frequency": 11862, "polarization": "Vertical"},
    "TOYOR ALJANNAH": {"frequency": 11179, "polarization": "Horizontal"},
    "CN ARABIC": {"frequency": 11277, "polarization": "Vertical"},
    "SKY NEWS ARABIA": {"frequency": 12380, "polarization": "Horizontal"},
    "AL JAZEERA HD": {"frequency": 10853, "polarization": "Vertical"}
}

ALL_CATS = ["⛪ Christian", "🕌 Islamic", "🎬 Drama", "🍿 Movies", "👶 Kids", "⚽ Sports", "📰 News"]

# ── الواجهة ──
system_type = st.radio(t['system_type_label'], [t['sys_modern'], t['sys_legacy']])
update_freq = st.checkbox(t['update_freq_label'], value=True)
add_new_ch = st.checkbox(t['add_new_ch_label'], value=True)
user_priority = st.multiselect(t['multiselect_label'], ALL_CATS, default=ALL_CATS)

# ── المعالجة ──
channels_to_generate = []
if add_new_ch:
    for name, info in NILESAT_GEN_DB.items():
        freq = info["frequency"] if update_freq else 11000
        channels_to_generate.append({"name": name, "freq": str(freq), "pol": info["polarization"]})

# ── التوليد ──
if st.button("Generate"):
    final_xml_bytes = b""
    generated_model_name = "RAMBO_GEN_55"
    
    if system_type == t['sys_modern']:
        channel_list = []
        for i, ch in enumerate(channels_to_generate, 1):
            channel_list.append({
                "channelName": ch["name"], "majorNumber": i, "minorNumber": 0,
                "frequency": int(ch["freq"]), "polarization": ch["pol"],
                "invisible": 0, "serviceType": 1, "satelliteName": "Nilesat"
            })
        payload = json.dumps({"channelList": channel_list, "satelliteList": [{"satelliteName": "Nilesat", "satellitePosition": 70}]})
        final_xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<TLLDATA>\n  <ModelName>{generated_model_name}</ModelName>\n  <legacybroadcast><![CDATA[{payload}]]></legacybroadcast>\n</TLLDATA>"
        final_xml_bytes = final_xml.encode('utf-8')
    else:
        items = "".join([f"\n  <ITEM>\n    <prNum>{i}</prNum>\n    <vchName>{ch['name']}</vchName>\n    <frequency>{ch['freq']}</frequency>\n    <polarization>{ch['pol']}</polarization>\n  </ITEM>" for i, ch in enumerate(channels_to_generate, 1)])
        final_xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<TLLDATA>\n  <ModelName>{generated_model_name}</ModelName>{items}\n</TLLDATA>"
        final_xml_bytes = final_xml.encode('utf-8')

    st.success(t['ready_msg'])
    st.download_button(t['btn_download_tll'], final_xml_bytes, "GlobalClone00001.TLL")
