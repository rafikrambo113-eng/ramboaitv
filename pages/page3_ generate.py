import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# ─────────────────────────────
# Session State
# ─────────────────────────────
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'

UI = {
    'ar': {
        'title': "📡 RAMBO - توليد ملف قنوات LG الذكي",
        'subtitle': "⚡ إدخال بيانات الجهاز لإنشاء ملف مخصص",
        'satellite': "📡 اختر القمر الصناعي (إجباري)",
        'country': "🌍 بلد البث (إجباري)",
        'inch': "📏 البوصة (اختياري)",
        'model': "📺 الموديل (اختياري)",
        'year': "📅 سنة الصنع (إجباري)",
        'btn_generate': "🚀 توليد الملف",
        'missing': "⚠️ لازم تكمل البيانات الإلزامية",
        'result': "✅ تم تحديد نوع الملف:",
        'new': "🆕 ملف حديث",
        'old': "📼 ملف قديم"
    }
}

t = UI[st.session_state.lang]

st.set_page_config(page_title="RAMBO Page 3", layout="centered")

st.title(t['title'])
st.subheader(t['subtitle'])

# ─────────────────────────────
# Inputs
# ─────────────────────────────
satellite = st.selectbox(
    t['satellite'],
    ["Nilesat 7W", "Arabsat 26E", "Hotbird 13E", "Other"]
)

country = st.text_input(t['country'])

inch = st.text_input(t['inch'])

model = st.text_input(t['model'])

year = st.number_input(
    t['year'],
    min_value=1990,
    max_value=2026,
    value=2024
)

# ─────────────────────────────
# Generate Logic
# ─────────────────────────────
if st.button(t['btn_generate']):

    if not satellite or not country or not year:
        st.warning(t['missing'])
        st.stop()

    # تحديد نوع الملف
    file_type = "NEW" if year >= 2020 else "OLD"

    st.success(t['result'])

    if file_type == "NEW":
        st.info(f"🆕 {t['new']}")
    else:
        st.info(f"📼 {t['old']}")

    # ─────────────────────────────
    # هنا نجهز "Metadata" للصفحات 1 و 2
    # ─────────────────────────────
    metadata = {
        "satellite": satellite,
        "country": country,
        "inch": inch,
        "model": model,
        "year": year,
        "file_type": file_type
    }

    st.session_state["page3_metadata"] = metadata

    # عرض البيانات
    st.json(metadata)

    # ─────────────────────────────
    # مثال: توليد ملف إعداد
    # ─────────────────────────────
    config_text = f"""
RAMBO LG CHANNEL CONFIG
========================
Satellite: {satellite}
Country: {country}
Screen Size: {inch}
Model: {model}
Year: {year}
File Type: {file_type}
"""

    st.download_button(
        "📥 تحميل ملف الإعداد",
        data=config_text,
        file_name="RAMBO_CONFIG.txt",
        mime="text/plain"
    )
