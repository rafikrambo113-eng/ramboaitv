import streamlit as st
import xml.etree.ElementTree as ET
import json
import re
from collections import OrderedDict

# ─────────────────────────────
# Session
# ─────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "ar"

t = {
    "ar": {
        "title": "🤖 RAMBO AI - مولد ملف القنوات الذكي",
        "sat": "📡 القمر الصناعي (إجباري)",
        "country": "🌍 بلد البث (إجباري)",
        "model": "📺 الموديل (اختياري)",
        "year": "📅 سنة الصنع (إجباري)",
        "inch": "📏 البوصة (اختياري)",
        "btn": "🚀 توليد الملف الذكي",
        "missing": "⚠️ أكمل البيانات الإلزامية",
        "done": "✅ تم توليد الملف بنجاح",
        "type_new": "🆕 ملف حديث",
        "type_old": "📼 ملف قديم"
    }
}

UI = t["ar"]

st.set_page_config(page_title="RAMBO AI Generator", layout="centered")

st.title(UI["title"])

# ─────────────────────────────
# Inputs
# ─────────────────────────────
satellite = st.selectbox(UI["sat"], ["Nilesat 7W", "Arabsat 26E", "Hotbird 13E"])
country = st.text_input(UI["country"])
model = st.text_input(UI["model"])
inch = st.text_input(UI["inch"])
year = st.number_input(UI["year"], 1990, 2026, 2024)

# ─────────────────────────────
# AI Categories Engine
# ─────────────────────────────
CATEGORY_ORDER = [
    "News",
    "Sports",
    "Movies",
    "Drama",
    "Kids",
    "Religious",
    "General"
]

def ai_classify(name):
    n = name.upper()

    if any(x in n for x in ["NEWS", "BBC", "CNN", "CBC", "JAZEERA"]):
        return "News"
    if any(x in n for x in ["SPORT", "ON TIME", "SSC", "BEIN"]):
        return "Sports"
    if any(x in n for x in ["MOVIE", "CINEMA", "ROTANA", "MBC2"]):
        return "Movies"
    if any(x in n for x in ["DRAMA", "SERIES"]):
        return "Drama"
    if any(x in n for x in ["CARTOON", "KIDS", "CN", "TOYOR"]):
        return "Kids"
    if any(x in n for x in ["QURAN", "ISLAM", "MOSQUE", "MAKKA"]):
        return "Religious"

    return "General"

# ─────────────────────────────
# AI Channel DB (Example)
# ─────────────────────────────
CHANNEL_DB = [
    "MBC 2",
    "MBC 4",
    "AL JAZEERA",
    "BBC NEWS",
    "ON TIME SPORTS",
    "ROTANA CINEMA",
    "CARTOON NETWORK",
    "IQRAA",
    "CBC",
    "FOX MOVIES",
    "SSC SPORTS",
    "TOYOR ALJANNAH"
]

# ─────────────────────────────
# Generate Logic
# ─────────────────────────────
if st.button(UI["btn"]):

    if not satellite or not country or not year:
        st.warning(UI["missing"])
        st.stop()

    file_type = "MODERN" if year >= 2020 else "LEGACY"

    if file_type == "MODERN":
        st.info(UI["type_new"])
    else:
        st.info(UI["type_old"])

    # ────────────────
    # AI SORT
    # ────────────────
    categorized = {}

    for ch in CHANNEL_DB:
        cat = ai_classify(ch)
        categorized.setdefault(cat, []).append(ch)

    sorted_channels = []
    for cat in CATEGORY_ORDER:
        if cat in categorized:
            sorted_channels += categorized[cat]

    # ────────────────
    # Build TLL
    # ────────────────
    root = ET.Element("ChannelList")

    for i, name in enumerate(sorted_channels, 1):

        if file_type == "MODERN":
            node = ET.SubElement(root, "channel")
            ET.SubElement(node, "channelName").text = name
            ET.SubElement(node, "majorNumber").text = str(i)
            ET.SubElement(node, "category").text = ai_classify(name)

        else:
            item = ET.SubElement(root, "ITEM")
            ET.SubElement(item, "prNum").text = str(i)
            ET.SubElement(item, "vchName").text = name
            ET.SubElement(item, "frequency").text = "0000"

    xml_data = ET.tostring(root, encoding="utf-8")

    # ────────────────
    # Report
    # ────────────────
    report = f"""
RAMBO AI GENERATED FILE
========================
Satellite: {satellite}
Country: {country}
Year: {year}
Model: {model}
Type: {file_type}

ORDER:
{CATEGORY_ORDER}
"""

    st.success(UI["done"])

    st.download_button(
        "📥 تحميل ملف القنوات",
        data=xml_data,
        file_name="GlobalClone00001.TLL",
        mime="application/octet-stream"
    )

    st.download_button(
        "📄 تقرير التوليد",
        data=report,
        file_name="AI_Report.txt",
        mime="text/plain"
    )
