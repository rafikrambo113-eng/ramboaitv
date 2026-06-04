import streamlit as st
import xml.etree.ElementTree as ET
import json
import re
import copy
from datetime import datetime

# ──────────────────────────────────────────────────────
# 1. SESSION STATE
# ──────────────────────────────────────────────────────
for key, val in {
    'lang': 'ar',
    'theme': 'dark',
    'p3_step': 1,          # 1=form, 2=preview, 3=done
    'p3_answers': {},
    'p3_output_bytes': None,
    'p3_report_txt': None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ──────────────────────────────────────────────────────
# 2. UI TEXT
# ──────────────────────────────────────────────────────
UI = {
    'ar': {
        'title':        "📺 RAMBO — مولّد ملفات القنوات",
        'subtitle':     "⚡ أجب على الأسئلة وسيتم توليد ملف TLL مخصص لشاشتك",
        'step1_header': "🛰️ الخطوة 1: معلومات الإعداد",
        'q_sat':        "القمر الصناعي *",
        'q_country':    "بلد البث *",
        'q_inch':       "حجم الشاشة (بوصة)",
        'q_model':      "موديل الشاشة (اختياري)",
        'q_year':       "سنة الصنع *",
        'sat_opts':     ["🛰️ نايل سات 7°W", "🛰️ عرب سات / بدر 26°E", "🛰️ هوت بيرد 13°E", "🛰️ يوتلسات 8°W"],
        'country_opts': ["🇪🇬 مصر", "🇸🇦 السعودية", "🇦🇪 الإمارات", "🇯🇴 الأردن", "🇱🇧 لبنان", "🇸🇩 السودان", "🇩🇿 الجزائر", "🇲🇦 المغرب", "🇹🇳 تونس", "🇱🇾 ليبيا", "🇮🇶 العراق", "🇸🇾 سوريا", "🇾🇪 اليمن", "🇰🇼 الكويت", "🇶🇦 قطر", "🇧🇭 البحرين", "🇴🇲 عُمان"],
        'inch_opts':    ["32", "43", "49", "50", "55", "65", "75", "86"],
        'year_opts':    ["2024 / 2025 (جديد)", "2022 / 2023", "2020 / 2021", "2018 / 2019", "2016 / 2017 (قديم)"],
        'btn_next':     "▶️ توليد الملف",
        'step2_header': "📊 الخطوة 2: معاينة الملف المولَّد",
        'info_modern':  "✅ نوع الملف: **حديث (Modern JSON)** — مناسب لشاشات 2020+",
        'info_legacy':  "✅ نوع الملف: **قديم (Legacy XML)** — مناسب لشاشات ما قبل 2020",
        'preview_ch':   "📋 عينة من القنوات المضمنة:",
        'btn_download': "📥 تحميل ملف الشاشة (GlobalClone00001.TLL)",
        'btn_report':   "📄 تحميل تقرير القنوات (Channels_List.txt)",
        'btn_back':     "🔄 إنشاء ملف جديد",
        'success_msg':  "🎉 تم توليد الملف بنجاح! جاهز للتحميل.",
        'warn_sat':     "⚠️ اختر القمر الصناعي.",
        'warn_country': "⚠️ اختر بلد البث.",
        'warn_year':    "⚠️ اختر سنة الصنع.",
        'col_num':      "الرقم",
        'col_name':     "اسم القناة",
        'col_freq':     "التردد",
        'col_cat':      "الفئة",
        'file_type_lbl':"نوع الملف المولَّد:",
        'ch_count_lbl': "إجمالي القنوات:",
        'sat_lbl':      "القمر الصناعي:",
        'country_lbl':  "بلد البث:",
    },
    'en': {
        'title':        "📺 RAMBO — Channel File Generator",
        'subtitle':     "⚡ Answer the questions and get a custom TLL file for your TV",
        'step1_header': "🛰️ Step 1: Setup Information",
        'q_sat':        "Satellite *",
        'q_country':    "Broadcast Country *",
        'q_inch':       "Screen Size (inch)",
        'q_model':      "TV Model (optional)",
        'q_year':       "Year of Manufacture *",
        'sat_opts':     ["🛰️ NileSat 7°W", "🛰️ ArabSat / Badr 26°E", "🛰️ HotBird 13°E", "🛰️ Eutelsat 8°W"],
        'country_opts': ["🇪🇬 Egypt", "🇸🇦 Saudi Arabia", "🇦🇪 UAE", "🇯🇴 Jordan", "🇱🇧 Lebanon", "🇸🇩 Sudan", "🇩🇿 Algeria", "🇲🇦 Morocco", "🇹🇳 Tunisia", "🇱🇾 Libya", "🇮🇶 Iraq", "🇸🇾 Syria", "🇾🇪 Yemen", "🇰🇼 Kuwait", "🇶🇦 Qatar", "🇧🇭 Bahrain", "🇴🇲 Oman"],
        'inch_opts':    ["32", "43", "49", "50", "55", "65", "75", "86"],
        'year_opts':    ["2024 / 2025 (New)", "2022 / 2023", "2020 / 2021", "2018 / 2019", "2016 / 2017 (Old)"],
        'btn_next':     "▶️ Generate File",
        'step2_header': "📊 Step 2: Preview Generated File",
        'info_modern':  "✅ File Type: **Modern (JSON)** — for 2020+ TVs",
        'info_legacy':  "✅ File Type: **Legacy (XML)** — for pre-2020 TVs",
        'preview_ch':   "📋 Sample of included channels:",
        'btn_download': "📥 Download TV File (GlobalClone00001.TLL)",
        'btn_report':   "📄 Download Channel Report (Channels_List.txt)",
        'btn_back':     "🔄 Generate New File",
        'success_msg':  "🎉 File generated successfully! Ready to download.",
        'warn_sat':     "⚠️ Please select a satellite.",
        'warn_country': "⚠️ Please select a broadcast country.",
        'warn_year':    "⚠️ Please select manufacture year.",
        'col_num':      "No.",
        'col_name':     "Channel Name",
        'col_freq':     "Frequency",
        'col_cat':      "Category",
        'file_type_lbl':"Generated file type:",
        'ch_count_lbl': "Total channels:",
        'sat_lbl':      "Satellite:",
        'country_lbl':  "Country:",
    }
}

# ──────────────────────────────────────────────────────
# 3. CHANNEL DATABASE (NileSat 7°W — comprehensive)
# ──────────────────────────────────────────────────────

# Categories keywords
def ai_classify(name):
    n = name.upper().strip()
    if any(w in n for w in ["CTV","AGHAPY","MESAT","KARMA","ALKARMA","NOURSAT","SAT-7","SAT7","AL HAYAT","HAYAT TV","MIRACLE","COPTIC","CHURCH","LOGOS","ALFADY","SALVATION","LOVEWORLD","KOOGI","NOUR MARIAM","EL HAYAT TV"]):
        return "⛪ مسيحية"
    if any(w in n for w in ["QURAN","RAHMA","MAJD","MAKKA","IQRAA","IQRA","HUDA","WESAL","ISLAM","SUNNAH","AL-MAJD","ALMAJD","PRAYER","AZAN","TARAWEEH","MEKKA","ALMAJD","AL QURAN","AL-QURAN","KAREM","KORAN"]):
        return "🕌 إسلامية"
    if any(w in n for w in ["MOSALSALAT","DRAMA","SERIES","KHOLASA","MASRAWI","SHAHID","MUSALSAL","SERIE","MUSALSALAT"]):
        return "🎬 دراما"
    if any(w in n for w in ["CINEMA","ROTANA","AFLAM","MIX","FOX","MBC2","MBC 2","MBC4","MBC 4","MBC MAX","ACTION","RAMBO","MOVIE","FILM","COMEDY","OSN MOVIES","STAR MOVIES"]):
        return "🍿 أفلام"
    if any(w in n for w in ["SPACE TOON","SPACETOON","CARTOON","MAJID","KIDS","TOYOR","BABY","JUNIOR","BOOMERANG","DISNEY","BARAEM","TOM AND JERRY","NICKELODEON"]):
        return "👶 أطفال"
    if any(w in n for w in ["SPORT","SPORTS","ONTIME","ON TIME","KASS","AD_SPORTS","AD SPORTS","SSC","BEIN","MATCH","FOOTBALL","SOCCER","GOLF","TENNIS","OLYMPIC","STADIUM"]):
        return "⚽ رياضة"
    if any(w in n for w in ["NEWS","JAZEERA","ARABIYA","HADATH","SKY NEWS","BBC","CNN","EXTRA NEWS","CBC","SADA","BALADI","NILE NEWS","AL GHAD","ALARABY","MAYADEEN","MASR","EGYPT","AL HURRA","FRANCE 24","RT ARABIC"]):
        return "📰 أخبار"
    return "📺 عامة"

# Full NileSat channel database with real frequencies
NILESAT_DB = [
    # ─── ⛪ Christian ───
    {"name": "AGHAPY TV", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Hayat", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Karma Family", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alfady", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alkarma Discipleship", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alkarma ME 1", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alkarma New Generation", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlKarma Praise", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CTV EGYPT", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Hayat TV Algerie", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Koogi", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Logos TV", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Loveworld Arabic", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MESat", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nour Mariam", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Noursat", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Noursat AlChabab", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SALVATION TV MENA", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SAT-7 ARABIC", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SAT-7 KIDS", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    # ─── 🕌 Islamic ───
    {"name": "Africa TV 1 Quran", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Quran", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al QURAN-SYR", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL RAHMA", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Majd3", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-Quran AL_Karem", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Almajd General", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALRAHMAN", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alwadi quran", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Holly Quran", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Holy Quran Radio", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Huda TV", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait Holy Quran", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya Radio Quran Karem", "freq": 12303, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Majd Kids TV HD", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Makkah TV", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Misr Quran Kareem", "freq": 11861, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nedaa El Islam", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oman HolyQuran Radio", "freq": 12130, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Qatar R Quran", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Qatar R Quran 2", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Qatar TV Quran", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Quran Kareem", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Quran Kareem Ajloun", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Quran Kareem Al-Balqa", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Quran Kareem Aqaba", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Quran Kareem Jordan", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Quran Kareem Karak", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Quran Kareem ma\'an", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Quran Karem", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Saudi CH For Quran", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SAUDI CH For Quran HD", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Saudi CH For Sunnah", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SAUDI CH For Sunnah HD", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sharjah Quran", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sharjah Quran TV", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sout Al-Islam Doha", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Zayed Quran", "freq": 12322, "pol": "Vertical", "sat_id": "3530"},
    # ─── 🎬 Drama ───
    {"name": "1 IRAQ Drama", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Shams Drama", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SHASHA  DRAMA", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Nahar Drama", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alatwla Drama", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALFA DRAMA", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alhwanem Drama", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alking Drama TV", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Beirut Drama", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Beit ElDrama", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Cairo Plus Drama", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CBC Drama", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dahab drama tv", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DAHAB MOSALSALAT", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "dmc drama", "freq": 12091, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dolly Drama", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dolly Mosalsalat", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Drama Alyoom", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Drama Be Alaraby", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Drama khaligia TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Drama Live", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Omda Drama", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "EL WAHA DRAMA", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Elfadjer drama Dz", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Elkholasa mosalsalat", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Elkhoulasa Drama", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Elzaeem Drama", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Fox Drama", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "HADRAMAUT TV", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraqi Drama", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Light Drama", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MAJESTIC DRAMA", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MAJESTIC MOSALSALAT", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC Drama", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC MASR DRAMA HD", "freq": 11219, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Melody Drama", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Moga Drama", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "New Drama", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nile Drama", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ON Drama", "freq": 11861, "pol": "Vertical", "sat_id": "3530"},
    {"name": "One Drama", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Panorama Drama", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Panorama Drama 2", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "PLAY DRAMA", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rotana Drama", "freq": 12226, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sa3a Drama", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sa3a Mosalsalat", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SHABABIK DRAMA", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sukariya drama", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Top Drama", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "West Elbalad Drama", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    # ─── 🍿 Movies ───
    {"name": "5 Movies 1", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "5 Movies 2", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Aflam 1", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Aflam 2", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AFLAM TV", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SHASHA  FILM", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SHASHA CINEMA", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alatawla Cinema", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALFA CINEMA", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alking Aflam", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Beirut Aflam", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Beirut Cinema", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Cairo Plus Cinema", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Cinema 1", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "comedy 1", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "comedy 3", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dolly cinema", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dolly movies", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Khoulasa Cinema", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Omda Aflam", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Elzaeem Cinema", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Fox Be Elaraby TV", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "I Film Arabic", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MAJESTIC AFLAM", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MAJESTIC CINEMA", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC 2", "freq": 11219, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC 4", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC Action", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Melody Aflam", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mix", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mix Bel Araby", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mix One", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Moga Cinema", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Moga Comedy", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Movies 1", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nile Cinema", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nile Comedy", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "NOVA CINEMA", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "One Movies", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "One Movies HD", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Panorama Film", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "PLAY AFLAM", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "PLAY CINEMA", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rotana Cinema EGY", "freq": 12226, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rotana Cinema EGY HD", "freq": 12226, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rotana Cinema KSA", "freq": 12226, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rotana Classic", "freq": 12226, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rotana Clip", "freq": 12226, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rotana FM KSA", "freq": 12226, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rotana Khalijia", "freq": 12226, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rotana Music", "freq": 12226, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rotana Radio Jordan", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rotana Tarab Jordan", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sa3a Cinema", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SHABABIK CINEMA", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sukariya cinema", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Zee Aflam", "freq": 12322, "pol": "Vertical", "sat_id": "3530"},
    # ─── 👶 Kids ───
    {"name": "5 KIDS", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Algerian 4Kids", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BATOOT KIDS TV", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Cartoon 2", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Cartoon Network", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Cookies Kids HD", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Cookies Kids TV", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kids 3", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kidsy", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SPACETOON ARABIC", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Toyor Aljanah", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Wanasat Baby", "freq": 11430, "pol": "Vertical", "sat_id": "3530"},
    {"name": "YAMAN KIDS", "freq": 11430, "pol": "Vertical", "sat_id": "3530"},
    # ─── ⚽ Sports ───
    {"name": "AD Sport 1 HD", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AD Sport 2 HD", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlHayat Sport", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alkass four HD", "freq": 11919, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alkass one HD", "freq": 11919, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alkass seven HD", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alkass three HD", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alkass two HD", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN 4K", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS 2 AFC", "freq": 12245, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS 4 AFC", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS 5", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS MAX 1", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS MAX 2", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS MAX 3", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS MAX 4", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS MAX 5", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS MAX 6", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS NEWS", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS XTRA 6", "freq": 12245, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS XTRA 7", "freq": 12245, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS XTRA 8", "freq": 12245, "pol": "Vertical", "sat_id": "3530"},
    {"name": "beIN SPORTS XTRA 9", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DUBAI SPORTS 1 HD", "freq": 12418, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DUBAI SPORTS 2 HD", "freq": 12418, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraqia Sport HD", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Jordan Sport", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Jordan Sport HD", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kassala TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KSA SPORT1 HD", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KSA SPORT2 HD", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KSA SPORTS 1", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KSA SPORTS 2", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KSA SPORTS 3", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KSA SPORTS 3 HD", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KSA SPORTS 4 HD", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait Sport plus", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait Sports", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Learning passport SD1", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Learning passport SD2", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "LIBYA SPORT 1 HD", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya Sport 2 HD", "freq": 12303, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nile Sport", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oman TV Sport HD", "freq": 12130, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ON SPORT", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ON SPORT HD", "freq": 11977, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ON SPORT MAX", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ON SPORT PLUS", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Palestine Sport", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sharjah Sport 2 HD", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sharjah Sport HD", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sharjah Sport SD", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SPORT PLUS HD", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sports First", "freq": 11296, "pol": "Vertical", "sat_id": "3530"},
    {"name": "YAS Sports HD", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Zamalek Sports", "freq": 12091, "pol": "Vertical", "sat_id": "3530"},
    # ─── 📰 News ───
    {"name": "Al Arabiya", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Arabiya Business", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Arabiya FM", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Ghad HD", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Ghadeer", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Hadath", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL HADATH HD", "freq": 12322, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera 2", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera 2 HD", "freq": 12521, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera Documentary", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera Documentary HD", "freq": 12521, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera English", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera English HD", "freq": 12521, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera HD", "freq": 12521, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera Mubasher", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera Mubasher 2", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera Mubasher 2 HD", "freq": 12521, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Jazeera Mubasher HD", "freq": 12521, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Karama News", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Masryia HD", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL Masryia SD", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Mayadeen HD", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL MAYADEEN TV", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Qahera News", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Qahera News SD", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SHARQIYA NEWS HD", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Arabiya Alhadath", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL24 News", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALAHWAZ ALARABIYA", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alaraby HD TV", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlAraby2", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlHadath Alyoum", "freq": 11823, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Almasrawya TV", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALMAYADEEN PLUS", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Asharq News  Channel", "freq": 12360, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Asharq News Channel HD", "freq": 12360, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BBC (A)", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BBC (E)", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BBC Arabic", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BBC Horn of Africa", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BBC News TV", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CBC", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CBC HD", "freq": 12091, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CBC Sofra", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CNBC ARABIYA", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CNN", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DamasRadio FM", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "dmc masraheyat", "freq": 12091, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Echorouk News", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Egyptian TV HD", "freq": 11823, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Extra News", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Extra News HD", "freq": 12303, "pol": "Vertical", "sat_id": "3530"},
    {"name": "GB News", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "i24 News Arabic", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "INEWS TV HD", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraq Al Hadath HD", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraqia News HD", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kurdsat News", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "LIBYA ALHADATH HD", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC MASR", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC MASR 2", "freq": 11219, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC MASR 2 HD", "freq": 11219, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC MASR HD", "freq": 11219, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nile News", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nile News HD", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "One America News Network", "freq": 11296, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Palestine News", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Palestine News HD", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Masr", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sada El Balad", "freq": 11823, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sada El Balad 2", "freq": 11823, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sada ElBalad 3", "freq": 11823, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sky News Arabia", "freq": 11976, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sky News Arabia HD", "freq": 11976, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SSBC (News   MEDIA)", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SSBC (News &amp; MEDIA)", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Syria News HD", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Syria News SD", "freq": 12303, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ZEE ALWAN Egypt", "freq": 11277, "pol": "Vertical", "sat_id": "3530"},
    # ─── 📺 General ───
    {"name": "1 Baghdad", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "1 IRAQ TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "2M Maroc", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "2M MAROC HD", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "3yoon TV", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "a Konoz Alhayat", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "A TV", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "A Wealth of Entertainment", "freq": 11296, "pol": "Vertical", "sat_id": "3530"},
    {"name": "A3 HD", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ABC-ALKhalijia TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Abu Dhabi FM", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Abu Dhabi TV HD", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AD Nat Geo HD", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Aden", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Aden Almustakilla", "freq": 11334, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Aden TV", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ADM R1", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ADM R2", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ADM R3", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ADM R4", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AFAQ TV", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Africa TV 1", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Aghwar Shamaliah", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Ahwas State TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AJMAN HD", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL AHAD HD", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL AHAD VOICE", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Ahly HD", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Ahly SD", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Alam HD", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Alam Syria", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL AMAL", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Aoula inter", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Araby 2 HD", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Araby 2 SD", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL ARABY TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL ARABY TV HD", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL AYAM HD", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL BACHAEER RADIO", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL BAHRANY TV", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Basira", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Basra", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL DAFRA HD", "freq": 12322, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Dawaar", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Ekhbaria", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Ekhbaria HD", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Eman", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Emarat TV HD", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL ESHRAQ TV", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Etejah TV", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Fath Al3amh", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Fath Sonnah TV", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Forat", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Forat HD", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL HAQEQA AL DAWLIAH", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Hiwar TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Horreya", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Huriya Yamin TV", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al joumhouriya", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "al kafeel", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Kahera Wal Nas", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Kahera Wal Nas +2", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Kawthar HD", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL KERAZA TV", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Khartoum Radio", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Kout TV", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL MALAKOOT SAT  THE KINGDOM SAT", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL MALAKOOT SATTHE KINGDOM SAT", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Mashhad", "freq": 12322, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Mawsleya HD", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL NADA TV", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL NAHRAIN TV", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Nas", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL NOJABA TV", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Ons TV", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Ostoura", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL oula", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL Oula HD", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Qamar HD", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Quds Al Yawm", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Rabiaa TV", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL RASHEED RADIO", "freq": 11315, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL RASHEED TV HD", "freq": 11315, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Rayyan Al Qadeem HD", "freq": 12521, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Rayyan HD", "freq": 12521, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL Resala", "freq": 12226, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SABAH", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Sahat", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SALAM TV", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SAYEDAH TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL Shams", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SHARQIYA HD", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SHASHA  ALWAN", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SHASHA  HEKAYAT", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SHASHA MOSLSLAT", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al shirazioun", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SIRAT TV", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Sukariya Classic", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL SUMARIA HD", "freq": 11315, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al TALEAA HD", "freq": 11334, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Thania", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Thaqafiya HD", "freq": 11219, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL THAQALAYN TV", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Watania 24", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Wathaeqya", "freq": 12303, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al Wousta from Al Dhaid HD", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-adhamiya Iraq", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-Aghani", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Ahvaz", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-AKHBAR", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-Anbar", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Ansar TV", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Aqila TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-askari TV", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Awhad TV", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Bawadi", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-bernameg AL-aam", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-Bernameg AL-moussekey", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-bernameg AL-orobi", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Burhan Rukia TV", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Etejah TV", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Falloja", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Ganob", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-GEZIRA TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Jawad TV", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-Kahera Al-Kobra", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "al-khaleej alyoum", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Mahdi", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Marjaeyoun TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-Menia", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-MUSTAKILA", "freq": 11430, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Nahar Life", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Nahar Nour", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Nahar One", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Sabah TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Shaaer TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-shabab W Al-reyadah", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al-Shahed TV HD", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AL-Sharg AL-awsat", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Al3ylh TV", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALAAN TV HD", "freq": 11277, "pol": "Vertical", "sat_id": "3530"},
    {"name": "alafasy", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALAMAL TV", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alanwar TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALASKANDRIA", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALASSEMA", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alatawla Hekayat", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alawla Iraq TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Albaghdadiya", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Albalad TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALBASRA 1 TV", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Aldawla TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALDELTA", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALEGHATHIAH TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alerth-Alnbawi", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALFA HEKAYAT", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALFATH TV", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALHAQIQA", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alhara", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALHAWYAH TV", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALhayah ALaan", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALhayat", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alhayat 2", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlHayat 3", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlHayat HD", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alhayat Muslsalat", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alhayat We Alnas", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALHIJAZ TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALHOUDA", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alhour", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alhujja TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alhurra HD", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alhuseinya Radio", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Ali Gate TV", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Aliman TV", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALISTIQAMA TV", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Aljanub TV", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALJAWADAIN", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALKAHERA", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alkalema", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALKANAL", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALKARBALAEIA TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alkawther", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alkhaleej 24", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALKOFIYA HD", "freq": 11334, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALLAHDAH TV", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALLIBIYA TV", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Almaaref TV HD", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Almagd TV", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Almahriah HD", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Almamlaka TV", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Almasalah", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Almasirah HD", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Almasirah Mubashar", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALMASIRAH TV", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALMAWQEF TV", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALMERGAB TV", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALNAEEM TV", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alnajaf Alashraf tv", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "alnassr 24 tv", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlNassr media", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALNOJABA TV", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alqamar HD TV", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlQanat9", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alrabaa SD Radio", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alrai TV", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALS3YDA MADEEH", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALSA3EED", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlSaeedah", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALSahraa HD", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alsay3da", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALSHABAB", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlShaoub TV", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALSHOOR TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alsouriya tv", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alsouriya TV-HD", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlSudania 2 Radio", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Altaghier HD", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Altahoona", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Altamselia", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Althanya", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AlThaqafeya HD", "freq": 12322, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALWAAI ALSHIRAZI", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALWadi ALGaded", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alwadi TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALWAQIE TV HD", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALWATAN TV", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ALWESAM  TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alwilayah TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alyaum TV", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Alzrga", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AmharaSat TV", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Amman TV", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Amozhgary TV", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ANA DEJLAH", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Ana Sooria", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Anewz", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Angel TV", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AnwarTV2", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Arara TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ARIRANG", "freq": 11277, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Arirang HD", "freq": 12322, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ARTA Radio", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ARZKR!", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Asharq Discovery", "freq": 12360, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Asharq Discovery HD", "freq": 12360, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Asharq Documentary", "freq": 12360, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Asharq Documentary HD", "freq": 12360, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Asil TV", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Aswan", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Atfal Mawaheb", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Athan Tulkarem", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ATV Kurd", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "atv-ALADALAH", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "AVA TV", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Awazna1", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Awdeh", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Awdeh HD", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Ayozat TV", "freq": 11296, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Azhari", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "B4U PLUS", "freq": 11277, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Baghdad TV", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Bahia TV", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Bahrain International HD", "freq": 12728, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Bahrain TV HD", "freq": 12728, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Bakous Alexandaria", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Bangali", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BANGAWAZ TV", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Basma Radio", "freq": 11262, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Baynounah TV", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Beirut Alyoom", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Beity TV", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Beladi FM", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BELQEES", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BELQEES HD", "freq": 11334, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Bengali", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BERBERE TV", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BIN OTHAIMEEN", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "BN TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Cairo Plus Alyoum", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Calssic", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Canal algerie HD", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Canal Radio", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CAR TV", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CATV", "freq": 11277, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CGTN", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CGTN-Arabic", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CHADA TV", "freq": 11315, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CHAINE 1", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CHAINE 2", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CHAINE 3", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Channel 8 ARA", "freq": 11334, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Channel 8 KUR", "freq": 11334, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CHANNEL8", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Chebab TV", "freq": 11488, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Cima", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CIRA TV", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Cleopatra TV", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CN ARABIA", "freq": 11277, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CNB", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "CSAT", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dabanga TV", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DAEWA TV", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Damascus-Radio", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dar Alshefa", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Daystar", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dijlah TV HD", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dijlah Zaman TV HD", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Diwan", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "dmc", "freq": 12091, "pol": "Vertical", "sat_id": "3530"},
    {"name": "dmc HD", "freq": 12091, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dolly Alyoom", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dolly Classic", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dongola Radio", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DRN Radio", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DUA CHANNEL", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Duaa 1", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dubai One HD", "freq": 12418, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DUBAI RACING 1 HD", "freq": 12418, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DUBAI RACING 2 HD", "freq": 12418, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dubai Radio", "freq": 12418, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Dubai TV HD", "freq": 12418, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DW Arabia HD", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DW-A2", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "DW05", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Echorouk TV", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "EDUC 1", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Eductional channel", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "EI JUMHURIA TV", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Ekhbaria", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Adjwaa TV", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El barlamaniya", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Bilad TV", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Heddaf TV", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Khoulasa Classic", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Madah", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "EL MAHROUSA TV", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Omda Al yom", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Sharq TV", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "El Watania TV", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Eldjazair N1", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ELILHEM TV", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ELMEHWAR", "freq": 11823, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ELMEHWAR-HD", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ELMOLED", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ELRADIO 9090", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Emarat FM", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Energy FM", "freq": 12091, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Ennahar rokia", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Ennahar TV Algerie", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ERI Radio 2", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ERI Radio 3", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ERI Radio 4", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ERI Radio1", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ERIPM", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ERISAT", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ERISAT RADIO", "freq": 12686, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Eriteria TV", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ESAN TV", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ETIHAD TV", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "European Radio", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Eurpean Radio", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Eutelsat Data 1", "freq": 11488, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Extra Live SD", "freq": 12091, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Faith TV", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Falastini.tv", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "falestinona TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Febrauary TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "FILE 1", "freq": 11315, "pol": "Vertical", "sat_id": "3530"},
    {"name": "FR HD", "freq": 11334, "pol": "Vertical", "sat_id": "3530"},
    {"name": "France 24", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "France 24 (in Arabic)", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "France 24 Eng", "freq": 11976, "pol": "Vertical", "sat_id": "3530"},
    {"name": "France 24 English", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "French", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Fujairah FM", "freq": 12322, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Fujairah TV HD", "freq": 12322, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Fursan Aliraq TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Gali Kurdistan HD", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Global Biz TV", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Gulfsat", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hadramout TV", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hala Arabia", "freq": 12728, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hala Baghdad TV", "freq": 11553, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hala mosr3a", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Halab today", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hamiltan TV", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "HAQ TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hawa Baghdad", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hawa Dijlah Radio", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hayat FM", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Healing Streams", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hebron.Sat TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hikayh TV", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "HodHod  TV", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hogan TV", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hola Qatar", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Home TV", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Hona AlAzim", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Houna alazm", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Humax PVR - Live OTA", "freq": 12072, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Humax Retail OTA", "freq": 12072, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Humax WIFI HEVC PVR - Live OTA", "freq": 12072, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Huna Aliraq", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "HYA", "freq": 11785, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Ifrikya FM", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "iKA TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "IMAM ALI RADIO", "freq": 11334, "pol": "Vertical", "sat_id": "3530"},
    {"name": "IMAM ALI TV", "freq": 11334, "pol": "Vertical", "sat_id": "3530"},
    {"name": "IMAM HUSSEIN TV 2", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ins", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "IRAQ 24", "freq": 11315, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraq EDU 1", "freq": 10853, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraq EDU 2", "freq": 10853, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraq EDU 3", "freq": 10853, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraq EDU 4", "freq": 10853, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraq EDU 5", "freq": 10853, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraq EDU 6", "freq": 10853, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraq EDU 7", "freq": 10853, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraq Future", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraq Now", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraqi interior radio", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraqia Ent HD", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraqia Kurd", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraqia Syriac HD", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Iraqia Turkuman", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Jedda Radio", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "JIN TV HD", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Jordan", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Jordan Amen", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Jordan HD", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Jordan Radio", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "JORDAN SAMA", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "K24 HD", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kadak", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KAHRAMANA TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kaifa", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kalimat TV", "freq": 11334, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kan88", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kanon TV Sudan", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kan_Bet", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kan_Gimel", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kan_Homusica", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kan_Makan", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kan_Moreshet", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kan_Reka", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kan_Tarbut", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Karameesh TV", "freq": 11430, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Karbala Documentary HD", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Karbala TV HD", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kartoon channel", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KBS WORLD", "freq": 11277, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Khartoum-TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Khozama", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "kirkuk alan", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kirkuk TV HD", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KNN TV", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KSA1727", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KTO", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kunuz Al-Jannah", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KURDISTAN TV", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "KURDMAX", "freq": 12728, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kurdsat HD", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait Al-Thikr Al-Hakeem", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait Dana", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait Dar Al-Ethaa", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait Easy", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait FM", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait Main Program", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait Old Arabic", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait Second Program", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait Super Station", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait TV 1", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Kuwait TV 2", "freq": 11054, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Layali Zaman", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "LBC SAT", "freq": 12226, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Lebanon TV", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "LIBYA ABU SURRA", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya al Ahrar HD", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya Al Hedaya TV", "freq": 12303, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya Al-Youm", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya Al-Youm HD", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "LIBYA ALMASAR TV", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "LIBYA ALMOKHTAR", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya Almustaqbal", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya Almustaqbal TV", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya Alrasmia", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya Alwataniya", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya BN TV", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya G+", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya Government TV", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "LIBYA IFTA RADIO", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "LIBYA IFTA TV", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "LIBYA LEBDA TV", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Libya WTV HD", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "LJBC TV", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Loud FM", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "LTV", "freq": 11277, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Lualua TV", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "M24 MAROC", "freq": 11430, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Maan TV", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Madah", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Madh Elnabi", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Madrastna 1", "freq": 12303, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Madrastna 2", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Madrastna 3", "freq": 12206, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mahdawioun TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mahdi has appeared TV", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MAJESTIC CLASSIC", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MAKAN", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MANU CHAT", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Marah TV", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Marina TV HD", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MarjaeyatTV 2 HD", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Maspero FM   Thakafy", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Maspero Zaman", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MASSAYA TV", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Matrouh", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mazzika", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC 1", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC 3", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC Bollywood", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC FM", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC IRAQ", "freq": 11219, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBC IRAQ HD", "freq": 11219, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBCA+ TV", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBCam alshifaa", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBCFM SPLIT1", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MBCFM SPLIT2", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MCD Radio", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MDEEH", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Med Music", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Medan TV", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Medi1 TV Arabic", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MEDI1RADIO AFRIQUE", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mega FM", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mekameleen TV", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Menelik Satellite Television", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Menhag Alnabowe", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mereja TV", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Misk Syria", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Misr Al Zera3eya", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Misr ElBald", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Modern Mti", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Moga Today", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MOH", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mowagahat-1", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mowagahat-2", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mowagahat-8", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mowajahat", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Mowajhat", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MTA3", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MUSAWA", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Musawa HD", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Music 1", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Music India", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "MUSIC IRAQ", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "N Africa", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "NABA TV", "freq": 11641, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nablus Radio", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nagham FM", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nawader TV", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nesiha TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Neu TV", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "NEW LIBYA", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "NHK World Japan", "freq": 11976, "pol": "Vertical", "sat_id": "3530"},
    {"name": "NHK World-Japan", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nile Culture", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nile Family", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nile FM", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nile Life", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nile TV", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nilesat Feed", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nilesat PROMO", "freq": 12728, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nilesat Promo HD", "freq": 11804, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nogoum FM", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nogoum FM TV", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Noor Dubai Radio", "freq": 12418, "pol": "Vertical", "sat_id": "3530"},
    {"name": "North Africa", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "North Sinai", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nour Koddass", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nour TV", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "NRT 2 HD", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "NRT HD", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "NRT4", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Nu TV", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "OM-AlBaneen TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oman Classic Radio", "freq": 12130, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oman English Radio", "freq": 12130, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oman General Radio", "freq": 12130, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oman Shabab Radio", "freq": 12130, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oman TV Culture HD", "freq": 12130, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oman TV General HD", "freq": 12130, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oman TV General SD", "freq": 12130, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oman TV Live HD", "freq": 12130, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ON  E", "freq": 11861, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ON E HD", "freq": 11861, "pol": "Vertical", "sat_id": "3530"},
    {"name": "One TV", "freq": 11488, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oscar TV", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "OSN", "freq": 12072, "pol": "Vertical", "sat_id": "3530"},
    {"name": "OSN Test", "freq": 12072, "pol": "Vertical", "sat_id": "3530"},
    {"name": "OTA", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "OTA 1", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "OTA 2", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Outdoor Channel", "freq": 11296, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Oyoun AlWatan", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Pal Quraan 2", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Palestine", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Palestine EDU", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Palestine HD", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Palestine Live", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Palestine Live HD", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Palestine Quraan", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Palestine Radio", "freq": 11823, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Palestine Today", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Panorama FM", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Panorama Food", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Parole Di Vita", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "PAYAM TV HD", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "PDL Lite- Kaon Box OTA", "freq": 12072, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Pishto", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "PLAY HEKAYAT", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "PLAY TODAY", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "praisefm Global", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Press TV HD", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Prime TV", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Pulse95 SHJ", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Qatar 2", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Qatar Oryx Radio", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Qatar QBS Radio", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Qatar Radio", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Qatar TV HD", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Qatar Urdu", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "QBC  HD", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "QBC 4K", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RADI0_CHAINE 3", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio 03 World Service", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio 1", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio 2", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio 21 September", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio AI-Forqan", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio AL Wasat", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio AL-Iraqia", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio alomma", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Althora", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RADIO ANTINEA", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Baghdad", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RADIO BERBERE", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RADIO CORAN", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RADIO CULTURE", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Damascus", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RADIO DECROCHAGE", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Erena", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Erena (new)", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Fann Jordan", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Hits", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RADIO INTERNATIONALE", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RADIO JEUNESSE", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RADIO MARIAM ARABIC", "freq": 11430, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Miraya", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Salam", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Samar Sudan", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Sawa VOA Sudan", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Sawt El Shaa", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Sawt El Shaab", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Talavat", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio WAL", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Radio Yaqeen Jordan", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RDK", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RED SEA TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Reef Alyemen", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Revival TV", "freq": 11430, "pol": "Vertical", "sat_id": "3530"},
    {"name": "REVOLUTION-SYR", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "River Nile TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Riyad Al Salihin", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Riyad Radio", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Riyadh FM Split", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ROGHAYAH TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ROJAVA FM", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rojava HD", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Ronahi TV", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Rosheta", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ROYA HD", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RT ARABIC HD", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RT ARABIC SD", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RT English", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RUDAW", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "RUDAW TV", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sa3a Hekayat", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SABA HD", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Saba World Promo", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sahar Kurdi", "freq": 12015, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sahiroon Radio", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Salahden TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SALAM", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SAMA DUBAI HD", "freq": 12418, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Samarra tv", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Samira TV", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Saout alaqila", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SAT.TV", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sat.tv demo loop", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Saudi Radio 1", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Saudi Radio 2", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Saudi TV", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SAUDI TV HD", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Saudia Alaan TV", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Saudia Alaan TV HD", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sawt Al-alam", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sawt Alitra", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sawt Alitra TV", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sawtoman Raido", "freq": 12130, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SBC", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SBC HD", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SBN Global", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Segenet TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sha3by FM", "freq": 12053, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SHABABIK HEKAYAT", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SHABABIK MOSLSLAT", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SHAM TV", "freq": 11553, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Shamalia TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Shams TV", "freq": 11976, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sharjah HD", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sharjah Radio", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sharjah SD", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sharqiya from Kalba HD", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SHASHAT AL-IRAQ TV", "freq": 11553, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sheba", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SHEHAB TV HD", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Shopping 3", "freq": 11471, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SHOW TV", "freq": 12728, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Skyworth OTA", "freq": 12072, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SMTV", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sniper Fm Radio", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SOAL 24", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sout Al Rayyan", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sout AL-arab", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sout Alkhaleej 2", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sout Alkhaleej 3", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sout Alkhaleej 4", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sout Alkhaleej Europe", "freq": 10834, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SOUT MASER", "freq": 12604, "pol": "Vertical", "sat_id": "3530"},
    {"name": "South Sinai", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Spare", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Spare 2009", "freq": 11976, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Spare 2013", "freq": 11976, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Spare 2014", "freq": 11976, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Speda TV HD", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Star FM", "freq": 11411, "pol": "Vertical", "sat_id": "3530"},
    {"name": "STERK TV HD", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Strongman Champions League", "freq": 11296, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SUBORO TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sudan TV", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SUHAIL TV", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sukariya hekayat", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Sukariya zaman", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SUMER FM", "freq": 11315, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Suroyo FM", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Suroyo TV", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Syria 2 HD", "freq": 12034, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Syria One TV", "freq": 11554, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Syria TV", "freq": 10971, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Syria TV 01", "freq": 11938, "pol": "Vertical", "sat_id": "3530"},
    {"name": "SYRIA TV HD", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Tafilah Radio", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TAHA", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TANASUH EDUCATION TV", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TANASUH RADIO", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TANASUH TV", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TAYBA TV", "freq": 12728, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TCHAD Radio", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TCHAD TV HD", "freq": 11602, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TCTT", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TEBA", "freq": 11178, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TEHRAN ONE", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Tele Lumiere", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TeN TV", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test", "freq": 11842, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test 1", "freq": 11219, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test 2", "freq": 11219, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test 3", "freq": 11957, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test 4", "freq": 11219, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test HD", "freq": 11804, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test HD 2", "freq": 12729, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test HD 3", "freq": 12729, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test-3", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test1", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test123", "freq": 12729, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test2", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test4", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test5", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test6", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test7", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TEST_CB", "freq": 11315, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Test_ip", "freq": 12729, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Tets3", "freq": 12187, "pol": "Vertical", "sat_id": "3530"},
    {"name": "The Grace TV", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Thikrayat HD", "freq": 12284, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Thikrayatt", "freq": 12149, "pol": "Vertical", "sat_id": "3530"},
    {"name": "thmanyah.1", "freq": 12360, "pol": "Vertical", "sat_id": "3530"},
    {"name": "thmanyah.2", "freq": 12360, "pol": "Vertical", "sat_id": "3530"},
    {"name": "thmanyah.3", "freq": 12360, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Time Zaman TV", "freq": 12562, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TOP Zaman", "freq": 10815, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TRT Arabi", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TRT Arabi HD", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TRT KURDI", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TRT World HD", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Tunisia Nat1 HD", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Tunisia Nat2 HD", "freq": 10873, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TUNISIA SHOP", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TURKMENELI HD", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TURKMENELI Radio", "freq": 11373, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TV 4", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TV 5", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TV ISLAAMA", "freq": 11637, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TV5", "freq": 11900, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TV6 HD", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TV7 ELMAARIFA", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TV8 EDHAKIRA", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TVRI", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "TWR Arabic Ø¥Ø°Ø§Ø¹Ø© Ø­ÙÙ Ø§ÙØ¹Ø§Ã", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Umdorman Radio", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "UTV Iraq", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "UTV Iraq HD", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Vatican Radio", "freq": 10892, "pol": "Vertical", "sat_id": "3530"},
    {"name": "VOA 24", "freq": 12399, "pol": "Vertical", "sat_id": "3530"},
    {"name": "VOA Iraq", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "VOA Libya", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Voice of Palestine", "freq": 12646, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Voice of Palestine HD", "freq": 11564, "pol": "Vertical", "sat_id": "3530"},
    {"name": "WAAR HD", "freq": 10727, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Wadi Al-Neil   Palestine", "freq": 11766, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Watan Palestine Radio", "freq": 11177, "pol": "Vertical", "sat_id": "3530"},
    {"name": "WATAN TV", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "WATAR SHJ", "freq": 11013, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Wedo TV", "freq": 11296, "pol": "Vertical", "sat_id": "3530"},
    {"name": "West Elbalad Zaman", "freq": 11678, "pol": "Vertical", "sat_id": "3530"},
    {"name": "White Nile State Radio", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Wild TV", "freq": 11296, "pol": "Vertical", "sat_id": "3530"},
    {"name": "WION HD", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "World Fashion Channel", "freq": 11449, "pol": "Vertical", "sat_id": "3530"},
    {"name": "World Fishing Network", "freq": 11296, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Yemen", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Yemen Documentary", "freq": 11137, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Yemen Education", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Yemen Radio", "freq": 12687, "pol": "Vertical", "sat_id": "3530"},
    {"name": "YEMEN SHABAB", "freq": 11392, "pol": "Vertical", "sat_id": "3530"},
    {"name": "YEMEN SHABAB HD", "freq": 11258, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Yemen Today", "freq": 11747, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Yemen Today TV", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Yemen TV HD", "freq": 11096, "pol": "Vertical", "sat_id": "3530"},
    {"name": "YEMENIA TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Z24", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ZAD TV", "freq": 11277, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Zagros 24", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ZAGROS TV HD", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Zahra TV", "freq": 10921, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ZAMEN FM", "freq": 11680, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ZAROK TV HD", "freq": 11354, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ZAYTOONA", "freq": 11430, "pol": "Vertical", "sat_id": "3530"},
    {"name": "ZEE ALWAN.", "freq": 11277, "pol": "Vertical", "sat_id": "3530"},
    {"name": "Zoom TV", "freq": 12688, "pol": "Vertical", "sat_id": "3530"},
]


# ArabSat channels (subset)
ARABSAT_DB = [
    {"name": "MBC 1 HD",       "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "MBC 2 HD",       "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "MBC 3 HD",       "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "MBC 4 HD",       "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "MBC Action HD",  "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "MBC Masr HD",    "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "beIN Sports 1",  "freq": 12245, "pol": "Vertical",   "sat_id": "2600"},
    {"name": "beIN Sports 2",  "freq": 12245, "pol": "Vertical",   "sat_id": "2600"},
    {"name": "beIN Sports 3",  "freq": 12245, "pol": "Vertical",   "sat_id": "2600"},
    {"name": "Dubai TV HD",    "freq": 12092, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "Abu Dhabi TV HD","freq": 12092, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "Saudi 1 HD",     "freq": 12149, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "Saudi 2 HD",     "freq": 12149, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "Rotana Cinema HD","freq": 12034,"pol": "Horizontal", "sat_id": "2600"},
    {"name": "Al Arabiya HD",  "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "Al Jazeera HD",  "freq": 12245, "pol": "Vertical",   "sat_id": "2600"},
]

# Country → ISO code map
COUNTRY_CODE_MAP = {
    "🇪🇬 مصر": "EGY",        "🇸🇦 السعودية": "SAU",
    "🇦🇪 الإمارات": "ARE",   "🇯🇴 الأردن": "JOR",
    "🇱🇧 لبنان": "LBN",       "🇸🇩 السودان": "SDN",
    "🇩🇿 الجزائر": "DZA",    "🇲🇦 المغرب": "MAR",
    "🇹🇳 تونس": "TUN",        "🇱🇾 ليبيا": "LBY",
    "🇮🇶 العراق": "IRQ",      "🇸🇾 سوريا": "SYR",
    "🇾🇪 اليمن": "YEM",       "🇰🇼 الكويت": "KWT",
    "🇶🇦 قطر": "QAT",          "🇧🇭 البحرين": "BHR",
    "🇴🇲 عُمان": "OMN",
    "🇪🇬 Egypt": "EGY",        "🇸🇦 Saudi Arabia": "SAU",
    "🇦🇪 UAE": "ARE",           "🇯🇴 Jordan": "JOR",
    "🇱🇧 Lebanon": "LBN",       "🇸🇩 Sudan": "SDN",
    "🇩🇿 Algeria": "DZA",       "🇲🇦 Morocco": "MAR",
    "🇹🇳 Tunisia": "TUN",       "🇱🇾 Libya": "LBY",
    "🇮🇶 Iraq": "IRQ",          "🇸🇾 Syria": "SYR",
    "🇾🇪 Yemen": "YEM",         "🇰🇼 Kuwait": "KWT",
    "🇶🇦 Qatar": "QAT",          "🇧🇭 Bahrain": "BHR",
    "🇴🇲 Oman": "OMN",
}

# Is file modern or legacy based on year?
def is_modern_year(year_str):
    return "2024" in year_str or "2022" in year_str or "2020" in year_str

# ──────────────────────────────────────────────────────
# 4. FILE GENERATORS
# ──────────────────────────────────────────────────────

def get_channel_db(sat_choice):
    if "عرب سات" in sat_choice or "ArabSat" in sat_choice or "Badr" in sat_choice:
        return ARABSAT_DB
    return NILESAT_DB  # NileSat / HotBird / Eutelsat fallback


def generate_legacy_xml(channels, country_code, model_name, sat_choice):
    """Generate Legacy XML TLL file (pre-2020 style) — exact LG structure."""
    sat_handle = "4" if ("عرب" in sat_choice or "ArabSat" in sat_choice or "Badr" in sat_choice) else "5"

    # ── ModelInfo ──────────────────────────────────────────────
    xml_header = (
        '<?xml version="1.0" encoding="UTF-8"?>\r\n\r\n'
        '<TLLDATA>\r\n'
        '<ModelInfo>\r\n'
        f'<ModelName type="0">{model_name}</ModelName>\r\n'
        '<CloneVersion type="1">\r\n'
        '<MajorVersion>100</MajorVersion>\r\n'
        '<MinorVersion>000</MinorVersion>\r\n'
        '<SatelliteDBVersion>400</SatelliteDBVersion>\r\n'
        '</CloneVersion>\r\n'
        '<DTVInfo type="0">DTV_DVB</DTVInfo>\r\n'
        f'<BroadcastCountrySetting type="0">{country_code}</BroadcastCountrySetting>\r\n'
        '<country type="0">JA</country>\r\n'
        '</ModelInfo>\r\n'
    )

    # ── Minimal SatelliteDB (required by LG parser) ────────────
    sat_db = (
        '<SatelliteDB>\r\n'
        '<SATDBInfo>\r\n'
        '<SatHdrInfo>\r\n'
        '<MagicNo type="0">0</MagicNo>\r\n'
        '<SatSlotStatusTable>\r\n'
        '<slot0 type="0">255</slot0>\r\n'
        '<slot1 type="0">255</slot1>\r\n'
        '<slot2 type="0">255</slot2>\r\n'
        '<slot3 type="0">255</slot3>\r\n'
        '<slot4 type="0">255</slot4>\r\n'
        '<slot5 type="0">255</slot5>\r\n'
        '<slot6 type="0">0</slot6>\r\n'
        '<slot7 type="0">0</slot7>\r\n'
        '</SatSlotStatusTable>\r\n'
        '<Reserved type="0">0</Reserved>\r\n'
        '<CurrEndIndex type="0">0</CurrEndIndex>\r\n'
        '</SatHdrInfo>\r\n'
        '</SATDBInfo>\r\n'
        '<SettingIDDBInfo>\r\n'
        '<SettingIDInfo>\r\n'
        '<tbl1>\r\n'
        '<TPList>\r\n'
        '</TPList>\r\n'
        '</tbl1>\r\n'
        '</SettingIDInfo>\r\n'
        '</SettingIDDBInfo>\r\n'
        '</SatelliteDB>\r\n'
    )

    # ── CHANNEL wrapper — exact LG structure ──────────────────
    channel_open = '<CHANNEL>\r\n<ATV>\r\n</ATV>\r\n<DTV>\r\n'
    channel_close = '\r\n</DTV>\r\n</CHANNEL>\r\n</TLLDATA>'

    # ── Build ITEM blocks ──────────────────────────────────────
    items_parts = []
    for idx, ch in enumerate(channels, start=1):
        name_str = ch["name"]
        name_hex = name_str.encode("utf-8").hex()
        name_len = len(name_str)
        service_id = 7000 + idx
        item = (
            '<ITEM>\r\n'
            f'<prNum>{idx}</prNum>\r\n'
            '<minorNum>0</minorNum>\r\n'
            '<original_network_id>110</original_network_id>\r\n'
            '<transport_id>23</transport_id>\r\n'
            '<network_id>110</network_id>\r\n'
            f'<service_id>{service_id}</service_id>\r\n'
            '<physicalNum>135</physicalNum>\r\n'
            '<sourceIndex>7</sourceIndex>\r\n'
            '<serviceType>1</serviceType>\r\n'
            '<special_data>81188906</special_data>\r\n'
            f'<frequency>{ch["freq"]}</frequency>\r\n'
            '<nitVersion>2</nitVersion>\r\n'
            '<mapType>1</mapType>\r\n'
            '<mapAttr>0</mapAttr>\r\n'
            f'<programNo>{service_id}</programNo>\r\n'
            '<favoriteIdxA>250</favoriteIdxA>\r\n'
            '<favoriteIdxB>250</favoriteIdxB>\r\n'
            '<favoriteIdxC>250</favoriteIdxC>\r\n'
            '<favoriteIdxD>250</favoriteIdxD>\r\n'
            '<favoriteIdxE>250</favoriteIdxE>\r\n'
            '<favoriteIdxF>250</favoriteIdxF>\r\n'
            '<favoriteIdxG>250</favoriteIdxG>\r\n'
            '<favoriteIdxH>250</favoriteIdxH>\r\n'
            '<isInvisable>0</isInvisable>\r\n'
            '<isBlocked>0</isBlocked>\r\n'
            '<isSkipped>0</isSkipped>\r\n'
            '<isNumUnSel>0</isNumUnSel>\r\n'
            '<isDeleted>0</isDeleted>\r\n'
            '<chNameByte>0</chNameByte>\r\n'
            '<isDisabled>0</isDisabled>\r\n'
            f'<hexVchName>{name_hex}</hexVchName>\r\n'
            f'<notConvertedLengthOfVchName>{name_len}</notConvertedLengthOfVchName>\r\n'
            f'<vchName>{name_str}</vchName>\r\n'
            f'<lengthOfVchName>{name_len}</lengthOfVchName>\r\n'
            '<hSettingIDHandle>1</hSettingIDHandle>\r\n'
            f'<usSatelliteHandle>{sat_handle}</usSatelliteHandle>\r\n'
            '<isUserSelCHNo>1</isUserSelCHNo>\r\n'
            '<videoStreamType>2</videoStreamType>\r\n'
            '</ITEM>'
        )
        items_parts.append(item)

    items_xml = '\r\n'.join(items_parts)

    full_content = xml_header + sat_db + channel_open + items_xml + channel_close
    return full_content.encode("utf-8")


def generate_modern_json(channels, country_code, model_name, country_full, sat_info):
    """Generate Modern JSON TLL file (2020+ style)."""
    sat_name = sat_info.get("name", "NILESAT 7.0W")
    sat_id = channels[0]["sat_id"] if channels else "3530"
    sat_location = sat_info.get("loc", "7.0W")

    channel_list = []
    import base64
    for idx, ch in enumerate(channels, start=1):
        name_b64 = base64.b64encode(ch["name"].ljust(40, '\x00').encode("utf-8")).decode()
        channel_list.append({
            "disabled": False,
            "cellID": 0,
            "videoStreamType": 27,
            "specialData": 1154931754,
            "pcrPid": 8191,
            "sourceIndex": "SATELLITE DIGITAL",
            "regionId": 0,
            "audioDesc": False,
            "signalLossDay": 0,
            "homeTP": False,
            "primaryCh": False,
            "userSelCHNo": True,
            "altPhysicalNum": 0,
            "isDVBI": False,
            "userSubtitleLangCode": 0,
            "virtualChannel": False,
            "majorNumber": idx,
            "physicalNumber": 50,
            "skipped": False,
            "minorNumber": 0,
            "videoPid": 8191,
            "transSystem": "DVBS",
            "deleted": False,
            "validLCN": False,
            "isFVP": False,
            "conflict": False,
            "setIdHandle": 1,
            "astraMfCh": False,
            "optrBlocked": False,
            "factoryDefault": False,
            "Invisible": False,
            "networkId": 1918,
            "locked": False,
            "satelliteId": sat_id,
            "hdStatus": 1,
            "coderate": 1,
            "serviceIdentifier": 0,
            "dvbss2": 1,
            "chNameByte": False,
            "solveNeed": False,
            "prev_tsId": 1,
            "LCNPriority": 0,
            "userDualmonoType": 0,
            "audioPid": 8191,
            "chNameBase64": name_b64,
            "nitVersion": 2,
            "ipChannel": False,
            "userCustomize": True,
            "frequency": ch["freq"],
            "channelName": ch["name"],
            "discarded": False,
            "orgPhysicalNum": 0,
            "disableUpdate": False,
            "prev_onId": 1,
            "adultChannel": 0,
            "mapType": "CUSTOMIZED",
            "audioSetbyUser": False,
            "fineTuned": False,
            "conflictNumber": 0,
            "programNum": idx,
            "subtitleSetbyUser": False,
            "userEditChNumber": True,
            "bandwidth": "BW_8M",
            "rfIpChannel": False,
            "userAudio": 8191,
            "SVCID": idx,
            "TSID": 23,
            "isMultipleLCN": False,
            "numUnSel": False,
            "scrambled": False,
            "stillPicture": False,
            "tpId": f"{sat_id}{ch['freq']}0",
            "usedChName": False,
            "altChannel": False,
            "serviceType": 1,
            "ac3AudioType": False,
            "isOtherBroadcast": False,
            "ONID": 110,
            "userSubtitle": 8191,
            "profileV2": 0
        })

    broadcast_data = {
        "modelInfo": {"country": country_full},
        "bouquetList": [],
        "settingIdList": [{"satelliteId": sat_id, "Selected": True}],
        "channelList": channel_list,
        "motorPositionObj": {},
        "operatorConfigObj": {},
        "lcnStoreObj": {},
        "currActvStatObj": {},
        "satelliteList": [{
            "tpListLoad": True,
            "angleToGo": "65.65E",
            "TransponderList": [],
            "satelliteName": sat_name,
            "factoryDefault": False,
            "deleteFlag": False,
            "satelliteId": sat_id,
            "satLocation": sat_location
        }],
        "positionConfigObj": {},
        "homeTpList": [],
        "tkgsConfigObj": {}
    }

    tll_content = f"""<?xml version="1.0" encoding="UTF-8"?>\n<TLLDATA>\n<ModelInfo>\n<ModelName type="0">{model_name}</ModelName>\n<CloneVersion type="1">\n<MajorVersion>100</MajorVersion>\n<MinorVersion>000</MinorVersion>\n<SatelliteDBVersion>400</SatelliteDBVersion>\n</CloneVersion>\n<DTVInfo type="0">DTV_DVB</DTVInfo>\n<BroadcastCountrySetting type="0">{country_code}</BroadcastCountrySetting>\n</ModelInfo>\n<legacybroadcast>{json.dumps(broadcast_data, ensure_ascii=False, separators=(',', ':'))}</legacybroadcast>\n</TLLDATA>"""
    return tll_content.encode("utf-8")


def generate_report(channels, answers, file_type, lang):
    t = UI[lang]
    lines = []
    lines.append("=" * 60)
    lines.append("  RAMBO — Channel File Generator Report")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)
    lines.append(f"  {t['sat_lbl']}      {answers.get('sat','')}")
    lines.append(f"  {t['country_lbl']}  {answers.get('country','')}")
    lines.append(f"  {t['file_type_lbl']} {file_type}")
    lines.append(f"  {t['ch_count_lbl']}  {len(channels)}")
    lines.append("=" * 60)
    lines.append("")
    for idx, ch in enumerate(channels, start=1):
        cat = ai_classify(ch["name"])
        lines.append(f"  {idx:03d}. {ch['name']:<35} | {ch['freq']} | {cat}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────
# 5. PAGE CONFIG & THEME
# ──────────────────────────────────────────────────────
t = UI[st.session_state.lang]
st.set_page_config(page_title="RAMBO P3 — Generator", page_icon="📡", layout="wide")

col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("🌐 English" if st.session_state.lang == 'ar' else "🌐 العربية"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
        st.rerun()
with col_theme:
    if st.button("☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

# CSS
if st.session_state.theme == 'dark':
    bg = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)"
    tc, bb, bord = "#00f0ff", "rgba(13,7,33,0.85)", "#00f0ff"
    bsh, tsh = "rgba(0,240,255,0.35)", "0 0 5px rgba(0,240,255,0.4)"
else:
    bg = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
    tc, bb, bord = "#0d0722", "#ffffff", "#ff007f"
    bsh, tsh = "rgba(255,0,127,0.15)", "none"

ff = "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
.main {{ background: {bg} !important; color: {tc} !important; font-family: {ff}; }}
h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.4) !important; text-align: center; font-weight: 900; margin-top: 5px; }}
h3, p, label, .stMarkdown {{ color: {tc} !important; text-shadow: {tsh}; }}
.stSelectbox > div > div, .stTextInput > div > div > input {{
    background-color: {bb} !important; color: {tc} !important;
    border: 2px solid {bord} !important; border-radius: 10px !important;
}}
.rambo-card {{
    background: {bb}; border: 2px solid {bord};
    box-shadow: 0 5px 15px {bsh}; border-radius: 14px;
    padding: 22px; margin-bottom: 18px;
}}
.stButton > button {{
    background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
    color: #ffffff !important; border: 2px solid #ff007f !important;
    border-radius: 12px !important; font-weight: bold; width: 100%;
    font-size: 1.05rem; padding: 0.6rem;
}}
.stDownloadButton > button {{
    background: linear-gradient(135deg, #00b894 0%, #00695c 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; font-weight: bold; width: 100%;
}}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 6. TITLE
# ──────────────────────────────────────────────────────
st.title(t['title'])
st.markdown(f"<h3 style='text-align:center;'>{t['subtitle']}</h3>", unsafe_allow_html=True)
st.write("---")

# ──────────────────────────────────────────────────────
# 7. STEP 1 — FORM
# ──────────────────────────────────────────────────────
if st.session_state.p3_step == 1:
    st.markdown(f"### {t['step1_header']}")

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="rambo-card">', unsafe_allow_html=True)

            sat_choice = st.selectbox(
                t['q_sat'],
                options=[""] + t['sat_opts'],
                key="p3_sat"
            )

            country_choice = st.selectbox(
                t['q_country'],
                options=[""] + t['country_opts'],
                key="p3_country"
            )

            year_choice = st.selectbox(
                t['q_year'],
                options=[""] + t['year_opts'],
                key="p3_year"
            )

            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="rambo-card">', unsafe_allow_html=True)

            inch_choice = st.selectbox(
                t['q_inch'],
                options=[""] + t['inch_opts'],
                key="p3_inch"
            )

            model_choice = st.text_input(
                t['q_model'],
                placeholder="مثال: 55UN7340PVA" if st.session_state.lang == 'ar' else "e.g. 55UN7340PVA",
                key="p3_model"
            )

            # Live preview of file type
            if year_choice:
                is_mod = is_modern_year(year_choice)
                if is_mod:
                    st.info(t['info_modern'])
                else:
                    st.info(t['info_legacy'])

            st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    col_btn, _, _ = st.columns([2, 1, 1])
    with col_btn:
        if st.button(t['btn_next'], use_container_width=True):
            # Validate
            errors = []
            if not sat_choice:
                errors.append(t['warn_sat'])
            if not country_choice:
                errors.append(t['warn_country'])
            if not year_choice:
                errors.append(t['warn_year'])

            if errors:
                for e in errors:
                    st.warning(e)
            else:
                # Build model name
                inch_str = inch_choice if inch_choice else "55"
                model_name = model_choice.strip() if model_choice.strip() else f"LG{inch_str}XXXXX"
                country_code = COUNTRY_CODE_MAP.get(country_choice, "EGY")
                is_mod = is_modern_year(year_choice)

                # Get channel DB
                ch_db = get_channel_db(sat_choice)

                # Determine sat info for modern file
                if "نايل" in sat_choice or "Nile" in sat_choice:
                    sat_info = {"name": "NILESAT 7.0W", "loc": "7.0W"}
                elif "عرب" in sat_choice or "Arab" in sat_choice or "Badr" in sat_choice:
                    sat_info = {"name": "ARABSAT 26.0E", "loc": "26.0E"}
                elif "هوت" in sat_choice or "HotBird" in sat_choice:
                    sat_info = {"name": "HOTBIRD 13.0E", "loc": "13.0E"}
                else:
                    sat_info = {"name": "EUTELSAT 8.0W", "loc": "8.0W"}

                country_full_map = {
                    "EGY": "Egypt", "SAU": "Saudi Arabia", "ARE": "United Arab Emirates",
                    "JOR": "Jordan", "LBN": "Lebanon", "SDN": "Sudan", "DZA": "Algeria",
                    "MAR": "Morocco", "TUN": "Tunisia", "LBY": "Libya", "IRQ": "Iraq",
                    "SYR": "Syria", "YEM": "Yemen", "KWT": "Kuwait", "QAT": "Qatar",
                    "BHR": "Bahrain", "OMN": "Oman"
                }
                country_full = country_full_map.get(country_code, "Egypt")

                # Generate file
                if is_mod:
                    out_bytes = generate_modern_json(ch_db, country_code, model_name, country_full, sat_info)
                    file_type_label = "Modern JSON (2020+)"
                else:
                    out_bytes = generate_legacy_xml(ch_db, country_code, model_name, sat_choice)
                    file_type_label = "Legacy XML (pre-2020)"

                report_txt = generate_report(ch_db, {
                    "sat": sat_choice, "country": country_choice
                }, file_type_label, st.session_state.lang)

                st.session_state.p3_answers = {
                    "sat": sat_choice,
                    "country": country_choice,
                    "inch": inch_str,
                    "model": model_name,
                    "year": year_choice,
                    "file_type": file_type_label,
                    "ch_count": len(ch_db),
                    "is_modern": is_mod,
                }
                st.session_state.p3_output_bytes = out_bytes
                st.session_state.p3_report_txt = report_txt
                st.session_state.p3_channels_preview = ch_db
                st.session_state.p3_step = 2
                st.rerun()

# ──────────────────────────────────────────────────────
# 8. STEP 2 — PREVIEW & DOWNLOAD
# ──────────────────────────────────────────────────────
elif st.session_state.p3_step == 2:
    ans = st.session_state.p3_answers
    t = UI[st.session_state.lang]

    st.success(t['success_msg'])
    st.markdown(f"### {t['step2_header']}")

    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t['sat_lbl'], ans.get('sat', '')[:20])
    with col2:
        st.metric(t['country_lbl'], ans.get('country', '')[:15])
    with col3:
        st.metric(t['file_type_lbl'], "Modern JSON" if ans.get('is_modern') else "Legacy XML")
    with col4:
        st.metric(t['ch_count_lbl'], ans.get('ch_count', 0))

    st.write("---")

    # Preview table (first 30 channels)
    st.markdown(f"#### {t['preview_ch']}")
    preview_data = []
    for idx, ch in enumerate(st.session_state.p3_channels_preview[:30], start=1):
        preview_data.append({
            t['col_num']: idx,
            t['col_name']: ch['name'],
            t['col_freq']: ch['freq'],
            t['col_cat']: ai_classify(ch['name']),
        })
    st.table(preview_data)

    if len(st.session_state.p3_channels_preview) > 30:
        remaining = len(st.session_state.p3_channels_preview) - 30
        st.caption(f"... و {remaining} قناة أخرى في الملف الكامل." if st.session_state.lang == 'ar' else f"... and {remaining} more channels in the full file.")

    st.write("---")

    # Download buttons
    col_d1, col_d2, col_d3 = st.columns([2, 2, 1])
    with col_d1:
        st.download_button(
            label=t['btn_download'],
            data=st.session_state.p3_output_bytes,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream",
            use_container_width=True,
        )
    with col_d2:
        st.download_button(
            label=t['btn_report'],
            data=st.session_state.p3_report_txt,
            file_name="Channels_List.txt",
            mime="text/plain; charset=utf-8",
            use_container_width=True,
        )
    with col_d3:
        if st.button(t['btn_back'], use_container_width=True):
            st.session_state.p3_step = 1
            st.session_state.p3_output_bytes = None
            st.session_state.p3_report_txt = None
            st.session_state.p3_channels_preview = []
            st.rerun()
# ─────────────────────────────────────────────
# 10. الفوتر السيبراني (FIXED)
# ─────────────────────────────────────────────

whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"

footer_bg = "#0f172a"
footer_text = "#ffffff"

st.markdown(f"""
<div style="
background:{footer_bg};
border:2px solid #00f0ff;
color:{footer_text};
padding:35px;
text-align:center;
border-radius:20px;
margin-top:65px;
font-family:Arial;
">

<div style="color:#ff007f;font-size:26px;font-weight:bold;">
🛠️ DEVELOPER ENG: RAFIK NATHAN
</div>

<div style="margin-top:10px;">
📱 <b>MOBILE / الموبايل:</b> +201280339779
</div>

<div style="margin-top:10px;">
✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com
</div>

<a href="{whatsapp_url}" target="_blank"
style="
color:#25d366;
padding:14px 35px;
border-radius:35px;
display:inline-block;
font-weight:bold;
border:2px solid #25d366;
text-decoration:none;
margin-top:20px;
">
WhatsApp
</a>

</div>
""", unsafe_allow_html=True)
