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
    if any(w in n for w in ["CTV","AGHAPY","MESAT","KARMA","ALKARMA","NOURSAT","SAT-7","SAT7","AL HAYAT","HAYAT TV","MIRACLE","COPTIC","CHURCH","LOGOS","ALFADY","SALVATION","LOVEWORLD","KOOGI","NOUR"]):
        return "⛪ مسيحية"
    if any(w in n for w in ["QURAN","RAHMA","MAJD","MAKKA","IQRAA","IQRA","HUDA","WESAL","ISLAM","SUNNAH","AL-MAJD","ALMAJD","PRAYER","AZAN","TARAWEEH"]):
        return "🕌 إسلامية"
    if any(w in n for w in ["MOSALSALAT","DRAMA","SERIES","KHOLASA","MASRAWI","SHAHID","MUSALSAL","AFLAM SERIES"]):
        return "🎬 دراما"
    if any(w in n for w in ["CINEMA","ROTANA","AFLAM","MIX","FOX","MBC2","MBC 2","MBC4","MBC 4","MBC MAX","ACTION","RAMBO","MOVIE","FILM","COMEDY","OSN MOVIES","STAR MOVIES"]):
        return "🍿 أفلام"
    if any(w in n for w in ["SPACE TOON","SPACETOON","CN","CARTOON","MAJID","KIDS","TOM","TOYOR","BABY","JUNIOR","BOOMERANG","DISNEY"]):
        return "👶 أطفال"
    if any(w in n for w in ["SPORT","SPORTS","ONTIME","ON TIME","KASS","AD_SPORTS","AD SPORTS","SSC","BEIN","MATCH","FOOTBALL","SOCCER","GOLF","TENNIS"]):
        return "⚽ رياضة"
    if any(w in n for w in ["NEWS","JAZEERA","ARABIYA","HADATH","CAIRO","SKY NEWS","BBC","CNN","EXTRA NEWS","CBC","ON E","SADA","BALADI","MASR","MBC MASR","NILE NEWS","EGYPT","NILE"]):
        return "📰 أخبار"
    return "📺 عامة"

# Full NileSat channel database with real frequencies
NILESAT_DB = [
    # ─── Christian ───
    {"name": "Al Hayat",                "freq": 11392, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SAT-7 KIDS",              "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SAT-7 ARABIC",            "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Alkarma ME 1",            "freq": 11392, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "AGHAPY TV",               "freq": 11179, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "Almagd TV",               "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MESat",                   "freq": 11096, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "AlKarma Praise",          "freq": 11392, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Karma Family",         "freq": 11392, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Alkarma Discipleship",    "freq": 11392, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Loveworld Arabic",        "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SALVATION TV MENA",       "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Alfady",                  "freq": 11179, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "Al Horreya",              "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Logos TV",                "freq": 11392, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Koogi",                   "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nour Mariam",             "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Noursat",                 "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Noursat AlChabab",        "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "CTV",                     "freq": 12022, "pol": "Vertical",   "sat_id": "3530"},
    # ─── Islamic ───
    {"name": "Iqraa",                   "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Almajd TV",               "freq": 11862, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rahma",                   "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Quran Kareem",            "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Huda TV",                 "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Majd Quran",           "freq": 11862, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Wesal TV",                "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Islam Channel",           "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    # ─── News ───
    {"name": "Al Jazeera HD",           "freq": 10853, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "Al Jazeera Mubasher",     "freq": 10853, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "Al Arabiya",              "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Hadath",               "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Sky News Arabia",         "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "CBC",                     "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Extra News",              "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "ON E",                    "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC Masr",                "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC Masr 2",              "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile News",               "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile Drama",              "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile Cinema",             "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile Comedy",             "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile Sport",              "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile Family",             "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile Life",               "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Egypt TV",                "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Hayat 2",              "freq": 12207, "pol": "Vertical",   "sat_id": "3530"},
    # ─── Movies & Series ───
    {"name": "MBC 2",                   "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC 4",                   "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC Action",              "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rotana Cinema",           "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rotana Aflam",            "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rotana Classic",          "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rotana Drama",            "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "CBC Drama",               "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "ON Drama",                "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Shahid Mix",              "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    # ─── Kids ───
    {"name": "Space Toon",              "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Majid Kids",              "freq": 11862, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Toyor Al Jannah",         "freq": 11179, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "CN Arabic",               "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Baby TV",                 "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Junior",                  "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    # ─── Sports ───
    {"name": "ON Time Sports 1",        "freq": 11861, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "ON Time Sports 2",        "freq": 11861, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "ON Time Sports 3",        "freq": 11861, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SSC 1",                   "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SSC 2",                   "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SSC 3",                   "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SSC Extra 1",             "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SSC Extra 2",             "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "beIN Sports 1 Arabic",    "freq": 10853, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "beIN Sports 2 Arabic",    "freq": 10853, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "beIN Sports 3 Arabic",    "freq": 10853, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "beIN Sports 4 Arabic",    "freq": 10853, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "AD Sports 1",             "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "AD Sports 2",             "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile Sport",              "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    # ─── General ───
    {"name": "MBC 1",                   "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC 3",                   "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Dubai TV",                "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Abu Dhabi TV",            "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Kuwait TV",               "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Saudi 1",                 "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Saudi 2",                 "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Oula Morocco",         "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Jordan TV",               "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "LBC",                     "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Future TV",               "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Mayadeen",             "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
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
