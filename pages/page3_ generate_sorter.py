import streamlit as st
import xml.etree.ElementTree as ET
import json
import re
import copy
import requests
from datetime import datetime

# ──────────────────────────────────────────────────────
# 1. SESSION STATE
# ──────────────────────────────────────────────────────
for key, val in {
    'p3_step': 1,
    'p3_answers': {},
    'p3_output_bytes': None,
    'p3_report_txt': None,
    'p3_live_db_cache': None,
    'p3_live_db_last_fetch': None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ──────────────────────────────────────────────────────
# 2. PAGE CONFIG & CSS
# ──────────────────────────────────────────────────────
st.set_page_config(page_title="RAMBO P3 — مولّد الملفات", page_icon="📡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Cairo:wght@400;600;700;900&display=swap');

.main {
    background: radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%) !important;
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
}

h1 {
    color: #ff007f !important;
    text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.5) !important;
    font-family: 'Orbitron', 'Cairo' !important;
    font-weight: 900 !important;
    text-align: center !important;
    font-size: 52px !important;
    direction: ltr !important;
}

h2 {
    color: #00f0ff !important;
    text-shadow: 0 0 5px #00f0ff !important;
    font-family: 'Orbitron', 'Cairo' !important;
    font-weight: 700 !important;
    text-align: center !important;
}

h3, h4 {
    color: #00f0ff !important;
    font-family: 'Cairo' !important;
    font-weight: 700 !important;
}

p, label, .stMarkdown, .stBody {
    color: #e0e0e0 !important;
    font-size: 18px !important;
    line-height: 1.9 !important;
    direction: rtl !important;
    text-align: right !important;
}

.center-text {
    text-align: center !important;
    direction: rtl !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
    color: #ffffff !important;
    border: 2px solid #ff007f !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    font-size: 1.05rem !important;
    padding: 0.6rem !important;
    box-shadow: 0 0 15px rgba(255,0,127,0.4) !important;
    font-family: 'Cairo' !important;
    width: 100% !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #00b894 0%, #00695c 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    width: 100% !important;
    font-family: 'Cairo' !important;
}

.stButton {
    text-align: center !important;
}

.stInfo {
    background: rgba(0,240,255,0.15) !important;
    border-left: 5px solid #00f0ff !important;
    color: #00f0ff !important;
    direction: rtl !important;
    text-align: right !important;
}

.stSuccess {
    background: rgba(255,0,127,0.15) !important;
    border-left: 5px solid #ff007f !important;
    color: #ff6b9f !important;
    direction: rtl !important;
    text-align: right !important;
}

.stWarning {
    direction: rtl !important;
    text-align: right !important;
}

.stCheckbox label {
    color: #e0e0e0 !important;
}

.stExpander {
    border: 1px solid #00f0ff !important;
    border-radius: 10px !important;
}

.stSelectbox > div > div,
.stTextInput > div > div > input {
    background-color: rgba(13,7,33,0.85) !important;
    color: #00f0ff !important;
    border: 2px solid #00f0ff !important;
    border-radius: 10px !important;
}

.live-badge {
    display: inline-block;
    background: linear-gradient(90deg, #00f0ff22, #ff007f22);
    border: 1px solid #00f0ff;
    border-radius: 8px;
    padding: 6px 14px;
    color: #00f0ff;
    font-size: 0.85rem;
    margin-bottom: 10px;
}

hr {
    border-color: #00f0ff !important;
    opacity: 0.5 !important;
}

.rambo-card {
    background: rgba(13,7,33,0.85);
    border: 2px solid #00f0ff;
    box-shadow: 0 5px 15px rgba(0,240,255,0.35);
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 18px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 3. HEADER
# ──────────────────────────────────────────────────────
st.markdown("<h1>📺 RamboAITV</h1>", unsafe_allow_html=True)
st.markdown("<h2>📡 مولّد ملفات القنوات</h2>", unsafe_allow_html=True)
st.markdown("<p class='center-text' style='color:#ff007f; font-weight:700;'>🇪🇬 بأيدٍ مصرية ودماغ منياوية</p>", unsafe_allow_html=True)
st.markdown("---")

# ──────────────────────────────────────────────────────
# 4. LIVE DB
# ──────────────────────────────────────────────────────
FALLBACK_NILESAT_DB = {
    "AL HAYAT":            {"frequency": 12207, "polarization": "Vertical"},
    "AL HAYAT 2":          {"frequency": 12207, "polarization": "Vertical"},
    "SAT-7 KIDS":          {"frequency": 11353, "polarization": "Vertical"},
    "SAT-7 ARABIC":        {"frequency": 11353, "polarization": "Vertical"},
    "CTV":                 {"frequency": 10815, "polarization": "Horizontal"},
    "CTV (EGYPT)":         {"frequency": 10815, "polarization": "Horizontal"},
    "AGHAPY TV":           {"frequency": 10815, "polarization": "Horizontal"},
    "IQRAA":               {"frequency": 11938, "polarization": "Vertical"},
    "ALMAGD TV":           {"frequency": 10815, "polarization": "Horizontal"},
    "AL RAHMA":            {"frequency": 10873, "polarization": "Vertical"},
    "QURAN KAREEM":        {"frequency": 11727, "polarization": "Vertical"},
    "AL SALAM QURAN":      {"frequency": 10853, "polarization": "Horizontal"},
    "AL JAZEERA HD":       {"frequency": 10853, "polarization": "Horizontal"},
    "AL ARABIYA":          {"frequency": 11938, "polarization": "Vertical"},
    "AL HADATH":           {"frequency": 11938, "polarization": "Vertical"},
    "ECHOROUK TV":         {"frequency": 10922, "polarization": "Vertical"},
    "CBC":                 {"frequency": 12092, "polarization": "Vertical"},
    "EXTRA NEWS":          {"frequency": 12092, "polarization": "Vertical"},
    "ON E":                {"frequency": 12092, "polarization": "Vertical"},
    "MBC 2":               {"frequency": 11938, "polarization": "Vertical"},
    "MBC 4":               {"frequency": 11938, "polarization": "Vertical"},
    "ROTANA CINEMA":       {"frequency": 11938, "polarization": "Vertical"},
    "ON TIME SPORTS 1":    {"frequency": 11861, "polarization": "Vertical"},
    "ON TIME SPORTS 2":    {"frequency": 11861, "polarization": "Vertical"},
    "SPACE TOON":          {"frequency": 11727, "polarization": "Vertical"},
    "TOYOR ALJANNAH":      {"frequency": 11179, "polarization": "Horizontal"},
    "ALHURRA TV":          {"frequency": 11258, "polarization": "Horizontal"},
    "SYRIA TV":            {"frequency": 11258, "polarization": "Horizontal"},
    "QATAR TV":            {"frequency": 10834, "polarization": "Vertical"},
    "FAMILY DRAMA":        {"frequency": 10873, "polarization": "Vertical"},
    "SAMIRA TV":           {"frequency": 10922, "polarization": "Vertical"},
    "ENNAHAR TV":          {"frequency": 10922, "polarization": "Vertical"},
    "WATANIA 1":           {"frequency": 10873, "polarization": "Vertical"},
    "DIJLAH TV":           {"frequency": 10873, "polarization": "Vertical"},
    "DMC":                 {"frequency": 12091, "polarization": "Vertical"},
    "AL NAHAR":            {"frequency": 11785, "polarization": "Vertical"},
    "NILE DRAMA":          {"frequency": 11842, "polarization": "Vertical"},
    "NILE CINEMA":         {"frequency": 11842, "polarization": "Vertical"},
    "NILE NEWS":           {"frequency": 11842, "polarization": "Vertical"},
    "MBC 1":               {"frequency": 11471, "polarization": "Vertical"},
    "MBC 3":               {"frequency": 11471, "polarization": "Vertical"},
    "MBC MASR":            {"frequency": 11219, "polarization": "Vertical"},
    "MBC MASR 2":          {"frequency": 11219, "polarization": "Vertical"},
    "CBC DRAMA":           {"frequency": 11785, "polarization": "Vertical"},
    "ON DRAMA":            {"frequency": 11861, "polarization": "Vertical"},
    "ROTANA DRAMA":        {"frequency": 12226, "polarization": "Vertical"},
    "ROTANA CLASSIC":      {"frequency": 12226, "polarization": "Vertical"},
    "LBC SAT":             {"frequency": 12226, "polarization": "Vertical"},
    "AL MAYADEEN HD":      {"frequency": 11641, "polarization": "Vertical"},
    "SKY NEWS ARABIA":     {"frequency": 11976, "polarization": "Vertical"},
    "BBC ARABIC":          {"frequency": 12206, "polarization": "Vertical"},
}


@st.cache_data(ttl=3600)
def fetch_nilesat_live_db_p3():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get("https://www.dthsat.com/Nile-Sat", headers=headers, timeout=12)
        resp.raise_for_status()
        live_db = {}
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', resp.text, re.DOTALL | re.IGNORECASE)
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
            cols = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            if len(cols) >= 3:
                ch_name = cols[0].upper().strip()
                try:
                    freq = int(re.sub(r'\D', '', cols[1]))
                except (ValueError, IndexError):
                    continue
                polarity = cols[2].strip().upper()
                if ch_name and freq > 1000:
                    live_db[ch_name] = {
                        "frequency": freq,
                        "polarization": "Horizontal" if polarity == "H" else "Vertical"
                    }
        return live_db if live_db else None
    except Exception:
        return None


def get_active_db_p3():
    if st.session_state.get('p3_live_db_cache'):
        return st.session_state.p3_live_db_cache
    return {k: v for k, v in FALLBACK_NILESAT_DB.items()}


# ──────────────────────────────────────────────────────
# 5. زر جلب البيانات الحية
# ──────────────────────────────────────────────────────
col_fetch, col_fetch_status = st.columns([2, 4])
with col_fetch:
    if st.button("🌐 جلب أحدث بيانات NileSat من الإنترنت الآن", use_container_width=True, key="p3_fetch_live_btn"):
        with st.spinner("⏳ جاري الجلب من dthsat.com ..."):
            result = fetch_nilesat_live_db_p3()
            if result:
                st.session_state.p3_live_db_cache = result
                st.session_state.p3_live_db_last_fetch = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.toast(f"🛸 تم جلب {len(result):,} قناة من NileSat!")
                st.rerun()
            else:
                st.toast("⚠️ تعذّر الاتصال بـ dthsat.com، سيتم استخدام القاعدة المحلية.", icon="⚠️")

with col_fetch_status:
    if st.session_state.get('p3_live_db_cache'):
        n   = len(st.session_state.p3_live_db_cache)
        lft = st.session_state.get('p3_live_db_last_fetch', '؟')
        st.markdown(
            f"<div class='live-badge'>🟢 ✅ تم جلب بيانات NileSat الحية! إجمالي القنوات: {n:,} | ⏱ {lft}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='live-badge' style='border-color:#ff007f;color:#ff007f;'>"
            "🔴 قاعدة بيانات محلية (اضغط الزر للتحديث)"
            "</div>",
            unsafe_allow_html=True
        )

st.write("---")

# ──────────────────────────────────────────────────────
# 6. CLASSIFIER
# ──────────────────────────────────────────────────────
def ai_classify(name):
    n = name.upper().strip()
    if any(w in n for w in ["CTV","AGHAPY","MESAT","KARMA","ALKARMA","NOURSAT","SAT-7","SAT7","AL HAYAT","HAYAT TV","MIRACLE","COPTIC","CHURCH","LOGOS","ALFADY","SALVATION","LOVEWORLD","KOOGI","NOUR MARIAM","EL HAYAT TV"]):
        return "⛪ مسيحية"
    if any(w in n for w in ["QURAN","RAHMA","MAJD","MAKKA","IQRAA","IQRA","HUDA","WESAL","ISLAM","SUNNAH","AL-MAJD","ALMAJD","PRAYER","AZAN","MEKKA","AL QURAN","AL-QURAN","KAREM","KORAN"]):
        return "🕌 إسلامية"
    if any(w in n for w in ["MOSALSALAT","DRAMA","SERIES","KHOLASA","MASRAWI","SHAHID","MUSALSAL","SERIE","MUSALSALAT"]):
        return "🎬 دراما"
    if any(w in n for w in ["CINEMA","ROTANA","AFLAM","MIX","FOX","MBC2","MBC 2","MBC4","MBC 4","MBC MAX","ACTION","RAMBO","MOVIE","FILM","COMEDY","OSN MOVIES","STAR MOVIES"]):
        return "🍿 أفلام"
    if any(w in n for w in ["SPACE TOON","SPACETOON","CARTOON","MAJID","KIDS","TOYOR","BABY","JUNIOR","BOOMERANG","DISNEY","BARAEM","NICKELODEON"]):
        return "👶 أطفال"
    if any(w in n for w in ["SPORT","SPORTS","ONTIME","ON TIME","KASS","AD_SPORTS","AD SPORTS","SSC","BEIN","MATCH","FOOTBALL","SOCCER","GOLF","TENNIS","OLYMPIC","STADIUM"]):
        return "⚽ رياضة"
    if any(w in n for w in ["NEWS","JAZEERA","ARABIYA","HADATH","SKY NEWS","BBC","CNN","EXTRA NEWS","CBC","SADA","BALADI","NILE NEWS","AL GHAD","ALARABY","MAYADEEN","MASR","EGYPT","AL HURRA","FRANCE 24","RT ARABIC"]):
        return "📰 أخبار"
    return "📺 عامة"


# ──────────────────────────────────────────────────────
# 7. LIVE FREQ DB
# ──────────────────────────────────────────────────────
LIVE_FREQ_DB = {
    "AL JAZEERA HD":         {"freq": 10853, "src": "lyngsat"},
    "AL JAZEERA MUBASHER":   {"freq": 10853, "src": "lyngsat"},
    "AL ARABIYA":            {"freq": 11938, "src": "lyngsat"},
    "AL HADATH":             {"freq": 11938, "src": "lyngsat"},
    "SKY NEWS ARABIA":       {"freq": 11938, "src": "flysat"},
    "BBC ARABIC":            {"freq": 11938, "src": "lyngsat"},
    "RT ARABIC":             {"freq": 11938, "src": "lyngsat"},
    "AL HURRA":              {"freq": 11727, "src": "lyngsat"},
    "FRANCE 24 ARABIC":      {"freq": 11938, "src": "lyngsat"},
    "MBC 1":                 {"freq": 11938, "src": "lyngsat"},
    "MBC 2":                 {"freq": 11938, "src": "lyngsat"},
    "MBC 3":                 {"freq": 11938, "src": "lyngsat"},
    "MBC 4":                 {"freq": 11938, "src": "lyngsat"},
    "MBC ACTION":            {"freq": 11938, "src": "lyngsat"},
    "MBC MASR":              {"freq": 11938, "src": "lyngsat"},
    "MBC MASR 2":            {"freq": 11938, "src": "lyngsat"},
    "CBC":                   {"freq": 12092, "src": "lyngsat"},
    "CBC DRAMA":             {"freq": 12092, "src": "lyngsat"},
    "EXTRA NEWS":            {"freq": 12092, "src": "lyngsat"},
    "ON E":                  {"freq": 12092, "src": "lyngsat"},
    "ON DRAMA":              {"freq": 12092, "src": "lyngsat"},
    "ON TIME SPORTS 1":      {"freq": 11861, "src": "lyngsat"},
    "ON TIME SPORTS 2":      {"freq": 11861, "src": "lyngsat"},
    "ON TIME SPORTS 3":      {"freq": 11861, "src": "lyngsat"},
    "ROTANA CINEMA":         {"freq": 11938, "src": "lyngsat"},
    "ROTANA CLASSIC":        {"freq": 11938, "src": "lyngsat"},
    "ROTANA DRAMA":          {"freq": 11938, "src": "lyngsat"},
    "SPACE TOON":            {"freq": 11727, "src": "lyngsat"},
    "TOYOR AL JANNAH":       {"freq": 11179, "src": "lyngsat"},
    "AGHAPY TV":             {"freq": 11179, "src": "lyngsat"},
    "SAT-7 ARABIC":          {"freq": 11354, "src": "lyngsat"},
    "SAT-7 KIDS":            {"freq": 11354, "src": "lyngsat"},
    "AL HAYAT":              {"freq": 11392, "src": "lyngsat"},
    "IQRAA":                 {"freq": 11938, "src": "lyngsat"},
    "QURAN KAREEM":          {"freq": 11727, "src": "lyngsat"},
    "HUDA TV":               {"freq": 11727, "src": "lyngsat"},
    "NILE NEWS":             {"freq": 11785, "src": "lyngsat"},
    "NILE DRAMA":            {"freq": 11785, "src": "lyngsat"},
    "NILE CINEMA":           {"freq": 11785, "src": "lyngsat"},
    "DMC":                   {"freq": 12091, "src": "lyngsat"},
    "DMC DRAMA":             {"freq": 12091, "src": "lyngsat"},
    "AL NAHAR":              {"freq": 11785, "src": "lyngsat"},
    "SADA AL BALAD":         {"freq": 11785, "src": "lyngsat"},
    "CBC SOFRA":             {"freq": 12092, "src": "lyngsat"},
    "CBC EXTRA":             {"freq": 12092, "src": "lyngsat"},
    "SSC 1":                 {"freq": 11727, "src": "flysat"},
    "SSC 2":                 {"freq": 11727, "src": "flysat"},
    "SSC 3":                 {"freq": 11727, "src": "flysat"},
    "BEIN SPORTS 1 ARABIC":  {"freq": 10853, "src": "lyngsat"},
    "BEIN SPORTS 2 ARABIC":  {"freq": 10853, "src": "lyngsat"},
    "AD SPORTS 1":           {"freq": 11938, "src": "lyngsat"},
    "AD SPORTS 2":           {"freq": 11938, "src": "lyngsat"},
}

# ──────────────────────────────────────────────────────
# 8. EXTENDED NEW CHANNELS
# ──────────────────────────────────────────────────────
EXTENDED_NEW_CHANNELS = [
    {"name": "Al Qahera News",       "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "DMC",                  "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "DMC Drama",            "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "DMC Sport",            "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Nahar",             "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Nahar Drama",       "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Nahar Sport",       "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Sada Al Balad",        "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Ten",                  "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Ten Sports",           "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Alhayat Musalsalat",   "freq": 11392, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "CBC Sofra",            "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "CBC Extra",            "freq": 12092, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Panorama Drama",       "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Panorama Film",        "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Melody Drama",         "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Melody Aflam",         "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Zee Alwan",            "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Zee Aflam",            "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SSC Extra 1",          "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SSC Extra 2",          "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "AD Sports 3",          "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "beIN Sports 5 Arabic", "freq": 10853, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "beIN Sports 6 Arabic", "freq": 10853, "pol": "Horizontal", "sat_id": "3530"},
    {"name": "Shahid Kids",          "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Jeem TV",              "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC Bollywood",        "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rotana Khalijia",      "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Araby TV",          "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Ghad",              "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Mayadeen HD",       "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Manar",             "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "OTV Lebanon",          "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "LBC HD",               "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Watan TV",             "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
]

# ──────────────────────────────────────────────────────
# 9. CHANNEL DATABASES
# ──────────────────────────────────────────────────────
NILESAT_DB = [
    {"name": "AGHAPY TV",             "freq": 10815, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Hayat",              "freq": 11392, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Karma Family",       "freq": 10815, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Alfady",                "freq": 11096, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Alkarma Discipleship",  "freq": 11392, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Alkarma ME 1",          "freq": 11096, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "AlKarma Praise",        "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "CTV EGYPT",             "freq": 12687, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Koogi",                 "freq": 11096, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Logos TV",              "freq": 11096, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Loveworld Arabic",      "freq": 11096, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MESat",                 "freq": 11602, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nour Mariam",           "freq": 11096, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Noursat",               "freq": 10815, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SALVATION TV MENA",     "freq": 11096, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SAT-7 ARABIC",          "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SAT-7 KIDS",            "freq": 11354, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Quran",              "freq": 11258, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "AL RAHMA",              "freq": 10873, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Almajd General",        "freq": 11373, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Huda TV",               "freq": 11564, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Makkah TV",             "freq": 12399, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Misr Quran Kareem",     "freq": 11861, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Quran Kareem",          "freq": 11411, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Saudi CH For Quran",    "freq": 12149, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Saudi CH For Sunnah",   "freq": 12149, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "IQRAA",                 "freq": 11938, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al-Nahar Drama",        "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "CBC Drama",             "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "dmc drama",             "freq": 12091, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC Drama",             "freq": 11471, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC MASR DRAMA HD",     "freq": 11219, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Melody Drama",          "freq": 11678, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile Drama",            "freq": 11842, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "ON Drama",              "freq": 11861, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Panorama Drama",        "freq": 12053, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rotana Drama",          "freq": 12226, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Zee Alwan",             "freq": 11277, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Dolly Drama",           "freq": 11678, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Drama Live",            "freq": 11678, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Aflam 1",               "freq": 11177, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Aflam 2",               "freq": 11177, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC 2",                 "freq": 11219, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC 4",                 "freq": 11471, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC Action",            "freq": 11471, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Melody Aflam",          "freq": 11678, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Mix",                   "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile Cinema",           "freq": 11842, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile Comedy",           "freq": 11842, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Panorama Film",         "freq": 12053, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rotana Cinema EGY",     "freq": 12226, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rotana Cinema KSA",     "freq": 12226, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rotana Classic",        "freq": 12226, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rotana Khalijia",       "freq": 12226, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Zee Aflam",             "freq": 12322, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Cinema 1",              "freq": 11177, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "BATOOT KIDS TV",        "freq": 11678, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Cartoon Network",       "freq": 11137, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SPACETOON ARABIC",      "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Toyor Aljanah",         "freq": 11258, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Karameesh TV",          "freq": 11430, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Kidsy",                 "freq": 10727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "AD Sport 1 HD",         "freq": 11411, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "AD Sport 2 HD",         "freq": 11411, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "AlHayat Sport",         "freq": 12206, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Alkass one HD",         "freq": 11919, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "beIN SPORTS",           "freq": 11054, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "beIN SPORTS 5",         "freq": 11013, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "DUBAI SPORTS 1 HD",     "freq": 12418, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Jordan Sport",          "freq": 11957, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "KSA SPORTS 1",          "freq": 12149, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "KSA SPORTS 2",          "freq": 12149, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile Sport",            "freq": 11842, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "ON TIME SPORTS 1",      "freq": 11861, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "ON TIME SPORTS 2",      "freq": 11861, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SSC 1",                 "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SSC 2",                 "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "SSC 3",                 "freq": 11727, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Arabiya",            "freq": 11747, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Hadath",             "freq": 11471, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Jazeera",            "freq": 10971, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Jazeera HD",         "freq": 12521, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Mayadeen HD",        "freq": 11641, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Qahera News",        "freq": 11747, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "BBC Arabic",            "freq": 12206, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "CBC",                   "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "CBC HD",                "freq": 12091, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "CBC Sofra",             "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "CNN",                   "freq": 11137, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "dmc",                   "freq": 12091, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Echorouk News",         "freq": 10921, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Extra News",            "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC MASR",              "freq": 12015, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC MASR 2",            "freq": 11219, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Nile News",             "freq": 11842, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "ON E",                  "freq": 11861, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Sada El Balad",         "freq": 11823, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Sky News Arabia",       "freq": 11976, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al-Nahar One",          "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "France 24",             "freq": 12206, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Hurra HD",           "freq": 11258, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "RT ARABIC HD",          "freq": 11957, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Abu Dhabi TV HD",       "freq": 11411, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Dubai TV HD",           "freq": 12418, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Jordan HD",             "freq": 11957, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Kuwait TV 1",           "freq": 11054, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "LBC SAT",               "freq": 12226, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC 1",                 "freq": 11471, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC 3",                 "freq": 11471, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "MBC Bollywood",         "freq": 11471, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Qatar TV HD",           "freq": 10834, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Rotana Music",          "freq": 12226, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Saudi TV",              "freq": 12149, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Syria TV",              "freq": 10971, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "TeN TV",                "freq": 11842, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Al Sharqiya HD",        "freq": 11785, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Dijlah TV HD",          "freq": 11258, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Mazzika",               "freq": 11900, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "ROYA HD",               "freq": 11957, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Samira TV",             "freq": 10921, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Ennahar TV Algerie",    "freq": 10921, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Echorouk TV",           "freq": 10921, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Sudan TV",              "freq": 11747, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "2M Maroc",              "freq": 12015, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "Libya Al Ahrar HD",     "freq": 10815, "pol": "Vertical",   "sat_id": "3530"},
    {"name": "DW Arabia HD",          "freq": 11137, "pol": "Vertical",   "sat_id": "3530"},
]

ARABSAT_DB = [
    {"name": "MBC 1 HD",        "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "MBC 2 HD",        "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "MBC 3 HD",        "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "MBC 4 HD",        "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "MBC Action HD",   "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "MBC Masr HD",     "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "beIN Sports 1",   "freq": 12245, "pol": "Vertical",   "sat_id": "2600"},
    {"name": "beIN Sports 2",   "freq": 12245, "pol": "Vertical",   "sat_id": "2600"},
    {"name": "beIN Sports 3",   "freq": 12245, "pol": "Vertical",   "sat_id": "2600"},
    {"name": "Dubai TV HD",     "freq": 12092, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "Abu Dhabi TV HD", "freq": 12092, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "Saudi 1 HD",      "freq": 12149, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "Saudi 2 HD",      "freq": 12149, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "Rotana Cinema HD","freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "Al Arabiya HD",   "freq": 12034, "pol": "Horizontal", "sat_id": "2600"},
    {"name": "Al Jazeera HD",   "freq": 12245, "pol": "Vertical",   "sat_id": "2600"},
]

COUNTRY_CODE_MAP = {
    "🇪🇬 مصر": "EGY",      "🇸🇦 السعودية": "SAU",  "🇦🇪 الإمارات": "ARE",
    "🇯🇴 الأردن": "JOR",   "🇱🇧 لبنان": "LBN",      "🇸🇩 السودان": "SDN",
    "🇩🇿 الجزائر": "DZA",  "🇲🇦 المغرب": "MAR",     "🇹🇳 تونس": "TUN",
    "🇱🇾 ليبيا": "LBY",    "🇮🇶 العراق": "IRQ",     "🇸🇾 سوريا": "SYR",
    "🇾🇪 اليمن": "YEM",    "🇰🇼 الكويت": "KWT",     "🇶🇦 قطر": "QAT",
    "🇧🇭 البحرين": "BHR",  "🇴🇲 عُمان": "OMN",
}

SAT_OPTS     = ["🛰️ نايل سات 7°W", "🛰️ عرب سات / بدر 26°E", "🛰️ هوت بيرد 13°E", "🛰️ يوتلسات 8°W"]
COUNTRY_OPTS = list(COUNTRY_CODE_MAP.keys())
INCH_OPTS    = ["32", "43", "49", "50", "55", "65", "75", "86"]
YEAR_OPTS    = ["2024 / 2025 (جديد)", "2022 / 2023", "2020 / 2021", "2018 / 2019", "2016 / 2017 (قديم)"]
ALL_CATS     = ["⛪ مسيحية", "🕌 إسلامية", "🎬 دراما", "🍿 أفلام", "👶 أطفال", "⚽ رياضة", "📰 أخبار", "📺 عامة"]


def is_modern_year(year_str):
    return "2024" in year_str or "2022" in year_str or "2020" in year_str

def get_channel_db(sat_choice):
    if "عرب سات" in sat_choice or "Badr" in sat_choice:
        return ARABSAT_DB
    return NILESAT_DB

# ──────────────────────────────────────────────────────
# 10. FILE GENERATORS
# ──────────────────────────────────────────────────────
def generate_legacy_xml(channels, country_code, model_name, sat_choice):
    sat_handle = "4" if "عرب" in sat_choice else "5"
    xml_header = (
        '<?xml version="1.0" encoding="UTF-8"?>\r\n\r\n'
        '<TLLDATA>\r\n<ModelInfo>\r\n'
        f'<ModelName type="0">{model_name}</ModelName>\r\n'
        '<CloneVersion type="1">\r\n<MajorVersion>100</MajorVersion>\r\n'
        '<MinorVersion>000</MinorVersion>\r\n<SatelliteDBVersion>400</SatelliteDBVersion>\r\n'
        '</CloneVersion>\r\n<DTVInfo type="0">DTV_DVB</DTVInfo>\r\n'
        f'<BroadcastCountrySetting type="0">{country_code}</BroadcastCountrySetting>\r\n'
        '<country type="0">JA</country>\r\n</ModelInfo>\r\n'
    )
    sat_db = (
        '<SatelliteDB>\r\n<SATDBInfo>\r\n<SatHdrInfo>\r\n'
        '<MagicNo type="0">0</MagicNo>\r\n<SatSlotStatusTable>\r\n'
        '<slot0 type="0">255</slot0>\r\n<slot1 type="0">255</slot1>\r\n'
        '<slot2 type="0">255</slot2>\r\n<slot3 type="0">255</slot3>\r\n'
        '<slot4 type="0">255</slot4>\r\n<slot5 type="0">255</slot5>\r\n'
        '<slot6 type="0">0</slot6>\r\n<slot7 type="0">0</slot7>\r\n'
        '</SatSlotStatusTable>\r\n<Reserved type="0">0</Reserved>\r\n'
        '<CurrEndIndex type="0">0</CurrEndIndex>\r\n</SatHdrInfo>\r\n</SATDBInfo>\r\n'
        '<SettingIDDBInfo>\r\n<SettingIDInfo>\r\n<tbl1>\r\n<TPList>\r\n</TPList>\r\n</tbl1>\r\n'
        '</SettingIDInfo>\r\n</SettingIDDBInfo>\r\n</SatelliteDB>\r\n'
    )
    channel_open  = '<CHANNEL>\r\n<ATV>\r\n</ATV>\r\n<DTV>\r\n'
    channel_close = '\r\n</DTV>\r\n</CHANNEL>\r\n</TLLDATA>'
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
            '<favoriteIdxA>250</favoriteIdxA>\r\n<favoriteIdxB>250</favoriteIdxB>\r\n'
            '<favoriteIdxC>250</favoriteIdxC>\r\n<favoriteIdxD>250</favoriteIdxD>\r\n'
            '<favoriteIdxE>250</favoriteIdxE>\r\n<favoriteIdxF>250</favoriteIdxF>\r\n'
            '<favoriteIdxG>250</favoriteIdxG>\r\n<favoriteIdxH>250</favoriteIdxH>\r\n'
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
    import base64
    sat_name     = sat_info.get("name", "NILESAT 7.0W")
    sat_id       = channels[0]["sat_id"] if channels else "3530"
    sat_location = sat_info.get("loc", "7.0W")
    channel_list = []
    for idx, ch in enumerate(channels, start=1):
        name_b64 = base64.b64encode(ch["name"].ljust(40, '\x00').encode("utf-8")).decode()
        channel_list.append({
            "disabled": False, "cellID": 0, "videoStreamType": 27,
            "specialData": 1154931754, "pcrPid": 8191,
            "sourceIndex": "SATELLITE DIGITAL", "regionId": 0,
            "audioDesc": False, "signalLossDay": 0, "homeTP": False,
            "primaryCh": False, "userSelCHNo": True, "altPhysicalNum": 0,
            "isDVBI": False, "userSubtitleLangCode": 0, "virtualChannel": False,
            "majorNumber": idx, "physicalNumber": 50, "skipped": False,
            "minorNumber": 0, "videoPid": 8191, "transSystem": "DVBS",
            "deleted": False, "validLCN": False, "isFVP": False,
            "conflict": False, "setIdHandle": 1, "astraMfCh": False,
            "optrBlocked": False, "factoryDefault": False, "Invisible": False,
            "networkId": 1918, "locked": False, "satelliteId": sat_id,
            "hdStatus": 1, "coderate": 1, "serviceIdentifier": 0,
            "dvbss2": 1, "chNameByte": False, "solveNeed": False,
            "prev_tsId": 1, "LCNPriority": 0, "userDualmonoType": 0,
            "audioPid": 8191, "chNameBase64": name_b64, "nitVersion": 2,
            "ipChannel": False, "userCustomize": True,
            "frequency": ch["freq"], "channelName": ch["name"],
            "discarded": False, "orgPhysicalNum": 0, "disableUpdate": False,
            "prev_onId": 1, "adultChannel": 0, "mapType": "CUSTOMIZED",
            "audioSetbyUser": False, "fineTuned": False, "conflictNumber": 0,
            "programNum": idx, "subtitleSetbyUser": False,
            "userEditChNumber": True, "bandwidth": "BW_8M",
            "rfIpChannel": False, "userAudio": 8191, "SVCID": idx,
            "TSID": 23, "isMultipleLCN": False, "numUnSel": False,
            "scrambled": False, "stillPicture": False,
            "tpId": f"{sat_id}{ch['freq']}0", "usedChName": False,
            "altChannel": False, "serviceType": 1, "ac3AudioType": False,
            "isOtherBroadcast": False, "ONID": 110, "userSubtitle": 8191,
            "profileV2": 0
        })
    broadcast_data = {
        "modelInfo": {"country": country_full},
        "bouquetList": [], "settingIdList": [{"satelliteId": sat_id, "Selected": True}],
        "channelList": channel_list, "motorPositionObj": {},
        "operatorConfigObj": {}, "lcnStoreObj": {}, "currActvStatObj": {},
        "satelliteList": [{
            "tpListLoad": True, "angleToGo": "65.65E", "TransponderList": [],
            "satelliteName": sat_name, "factoryDefault": False,
            "deleteFlag": False, "satelliteId": sat_id, "satLocation": sat_location
        }],
        "positionConfigObj": {}, "homeTpList": [], "tkgsConfigObj": {}
    }
    tll_content = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<TLLDATA>\n<ModelInfo>\n'
        f'<ModelName type="0">{model_name}</ModelName>\n<CloneVersion type="1">\n'
        f'<MajorVersion>100</MajorVersion>\n<MinorVersion>000</MinorVersion>\n'
        f'<SatelliteDBVersion>400</SatelliteDBVersion>\n</CloneVersion>\n'
        f'<DTVInfo type="0">DTV_DVB</DTVInfo>\n'
        f'<BroadcastCountrySetting type="0">{country_code}</BroadcastCountrySetting>\n'
        f'</ModelInfo>\n<legacybroadcast>'
        f'{json.dumps(broadcast_data, ensure_ascii=False, separators=(",", ":"))}'
        f'</legacybroadcast>\n</TLLDATA>'
    )
    return tll_content.encode("utf-8")


def generate_report(channels, sat, country, file_type):
    lines = [
        "=" * 60,
        "  RAMBO — تقرير مولّد ملفات القنوات",
        f"  التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        f"  القمر الصناعي: {sat}",
        f"  بلد البث:      {country}",
        f"  نوع الملف:     {file_type}",
        f"  إجمالي القنوات: {len(channels)}",
        "=" * 60, ""
    ]
    for idx, ch in enumerate(channels, start=1):
        cat = ai_classify(ch["name"])
        lines.append(f"  {idx:03d}. {ch['name']:<35} | {ch['freq']} | {cat}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────
# 11. STEP 1 — FORM
# ──────────────────────────────────────────────────────
if st.session_state.p3_step == 1:
    st.markdown("### 🛰️ الخطوة 1: معلومات الإعداد")

    col1, col2 = st.columns(2)
    with col1:
        sat_choice     = st.selectbox("القمر الصناعي *", options=[""] + SAT_OPTS, key="p3_sat")
        country_choice = st.selectbox("بلد البث *", options=[""] + COUNTRY_OPTS, key="p3_country")
        year_choice    = st.selectbox("سنة الصنع *", options=[""] + YEAR_OPTS, key="p3_year")

    with col2:
        inch_choice  = st.selectbox("حجم الشاشة (بوصة)", options=[""] + INCH_OPTS, key="p3_inch")
        model_choice = st.text_input("موديل الشاشة (اختياري)", placeholder="مثال: 55UN7340PVA", key="p3_model")
        if year_choice:
            if is_modern_year(year_choice):
                st.info("✅ نوع الملف: **حديث (Modern JSON)** — مناسب لشاشات 2020+")
            else:
                st.info("✅ نوع الملف: **قديم (Legacy XML)** — مناسب لشاشات ما قبل 2020")

    st.write("---")

    # ── ترتيب الفئات ──
    st.markdown("### 🎛️ ترتيب الفئات")
    user_priority = st.multiselect("اختر الفئات بالترتيب المطلوب (الأول = الأعلى):", options=ALL_CATS, default=[], key="p3_cat_order")
    final_priority = list(user_priority)
    for c in ALL_CATS:
        if c not in final_priority:
            final_priority.append(c)

    if sat_choice:
        from collections import defaultdict
        ch_db_preview = get_channel_db(sat_choice)
        cats_preview = defaultdict(list)
        for ch in ch_db_preview:
            cats_preview[ai_classify(ch["name"])].append(ch["name"])
        st.markdown("##### 📊 معاينة توزيع القنوات:")
        col_p1, col_p2 = st.columns(2)
        for i, cat in enumerate(final_priority):
            if cat in cats_preview:
                lst  = cats_preview[cat]
                star = "⭐ " if cat in user_priority else ""
                with (col_p1 if i % 2 == 0 else col_p2):
                    with st.expander(f"{star}{cat} — ({len(lst)} قناة)"):
                        st.caption(", ".join(lst[:30]) + ("..." if len(lst) > 30 else ""))

    st.write("---")

    # ── ميزات التحديث الذكي ──
    st.markdown("### ⚡ ميزات التحديث الذكي")
    col_ai1, col_ai2 = st.columns(2)
    with col_ai1:
        do_update_freq = st.checkbox("⚛️ تحديث الترددات تلقائياً", value=False, key="p3_do_freq")
        if do_update_freq:
            st.caption("⚡ سيتم مقارنة الترددات الحالية بقاعدة البيانات المحدثة وتصحيح أي تردد قديم.")
    with col_ai2:
        do_new_ch = st.checkbox("✨ إضافة القنوات الجديدة المتاحة", value=False, key="p3_do_newch")
        if do_new_ch:
            st.caption("✨ سيتم فحص القنوات الجديدة المتاحة على القمر وإضافتها تلقائياً للملف.")

    st.write("")
    col_btn, _, _ = st.columns([2, 1, 1])
    with col_btn:
        if st.button("▶️ توليد الملف", use_container_width=True):
            errors = []
            if not sat_choice:     errors.append("⚠️ اختر القمر الصناعي.")
            if not country_choice: errors.append("⚠️ اختر بلد البث.")
            if not year_choice:    errors.append("⚠️ اختر سنة الصنع.")
            for e in errors:
                st.warning(e)

            if not errors:
                inch_str     = inch_choice if inch_choice else "55"
                model_name   = model_choice.strip() if model_choice.strip() else f"LG{inch_str}XXXXX"
                country_code = COUNTRY_CODE_MAP.get(country_choice, "EGY")
                is_mod       = is_modern_year(year_choice)
                ch_db        = [dict(ch) for ch in get_channel_db(sat_choice)]

                if "نايل" in sat_choice:
                    sat_info = {"name": "NILESAT 7.0W", "loc": "7.0W"}
                elif "عرب" in sat_choice:
                    sat_info = {"name": "ARABSAT 26.0E", "loc": "26.0E"}
                elif "هوت" in sat_choice:
                    sat_info = {"name": "HOTBIRD 13.0E", "loc": "13.0E"}
                else:
                    sat_info = {"name": "EUTELSAT 8.0W", "loc": "8.0W"}

                ai_freq_log  = []
                ai_newch_log = []

                if do_update_freq:
                    ACTIVE_DB = get_active_db_p3()
                    for ch in ch_db:
                        name_up  = ch["name"].upper().strip()
                        db_match = LIVE_FREQ_DB.get(name_up)
                        new_freq = db_match["freq"] if db_match else None
                        src      = db_match["src"]  if db_match else "local"
                        if new_freq is None:
                            live_entry = ACTIVE_DB.get(name_up) or ACTIVE_DB.get(
                                next((k for k in ACTIVE_DB if k in name_up or name_up in k), ""), None
                            )
                            if live_entry:
                                new_freq = live_entry["frequency"]
                                src = "dthsat/local"
                        if new_freq and int(ch["freq"]) != int(new_freq):
                            ai_freq_log.append({"channel": ch["name"], "old": ch["freq"], "new": new_freq, "source": src})
                            ch["freq"] = new_freq

                if do_new_ch:
                    existing_upper = {ch["name"].upper().strip() for ch in ch_db}
                    sat_id = ch_db[0].get("sat_id", "3530") if ch_db else "3530"
                    for nc in EXTENDED_NEW_CHANNELS:
                        if nc["name"].upper().strip() not in existing_upper:
                            new_ch = dict(nc)
                            new_ch["sat_id"] = sat_id
                            ch_db.append(new_ch)
                            ai_newch_log.append({"name": nc["name"], "freq": nc["freq"], "cat": ai_classify(nc["name"])})
                            existing_upper.add(nc["name"].upper().strip())
                    ACTIVE_DB = get_active_db_p3()
                    for db_name_upper, db_info in ACTIVE_DB.items():
                        is_present = any(db_name_upper in ex or ex in db_name_upper for ex in existing_upper)
                        if not is_present:
                            new_ch = {"name": db_name_upper.title(), "freq": db_info["frequency"], "pol": db_info["polarization"], "sat_id": sat_id}
                            ch_db.append(new_ch)
                            ai_newch_log.append({"name": new_ch["name"], "freq": new_ch["freq"], "cat": ai_classify(new_ch["name"])})
                            existing_upper.add(db_name_upper)

                ch_db.sort(key=lambda ch: final_priority.index(ai_classify(ch["name"])) if ai_classify(ch["name"]) in final_priority else len(final_priority))

                country_full_map = {
                    "EGY":"Egypt","SAU":"Saudi Arabia","ARE":"United Arab Emirates",
                    "JOR":"Jordan","LBN":"Lebanon","SDN":"Sudan","DZA":"Algeria",
                    "MAR":"Morocco","TUN":"Tunisia","LBY":"Libya","IRQ":"Iraq",
                    "SYR":"Syria","YEM":"Yemen","KWT":"Kuwait","QAT":"Qatar",
                    "BHR":"Bahrain","OMN":"Oman"
                }
                country_full = country_full_map.get(country_code, "Egypt")

                if is_mod:
                    out_bytes       = generate_modern_json(ch_db, country_code, model_name, country_full, sat_info)
                    file_type_label = "Modern JSON (2020+)"
                else:
                    out_bytes       = generate_legacy_xml(ch_db, country_code, model_name, sat_choice)
                    file_type_label = "Legacy XML (pre-2020)"

                report_txt = generate_report(ch_db, sat_choice, country_choice, file_type_label)

                st.session_state.p3_answers = {
                    "sat": sat_choice, "country": country_choice, "inch": inch_str,
                    "model": model_name, "year": year_choice,
                    "file_type": file_type_label, "ch_count": len(ch_db), "is_modern": is_mod,
                    "ai_freq_log": ai_freq_log, "ai_newch_log": ai_newch_log,
                    "cat_priority": final_priority,
                }
                st.session_state.p3_output_bytes     = out_bytes
                st.session_state.p3_report_txt       = report_txt
                st.session_state.p3_channels_preview = ch_db
                st.session_state.p3_step             = 2
                st.rerun()

# ──────────────────────────────────────────────────────
# 12. STEP 2 — PREVIEW & DOWNLOAD
# ──────────────────────────────────────────────────────
elif st.session_state.p3_step == 2:
    ans = st.session_state.p3_answers

    st.success("🎉 تم توليد الملف بنجاح! جاهز للتحميل.")
    st.markdown("### 📊 الخطوة 2: معاينة الملف المولَّد")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("القمر الصناعي:", ans.get('sat', '')[:20])
    with col2: st.metric("بلد البث:", ans.get('country', '')[:15])
    with col3: st.metric("نوع الملف:", "Modern JSON" if ans.get('is_modern') else "Legacy XML")
    with col4: st.metric("إجمالي القنوات:", ans.get('ch_count', 0))

    st.write("---")

    freq_log  = ans.get('ai_freq_log', [])
    newch_log = ans.get('ai_newch_log', [])
    cat_prio  = ans.get('cat_priority', [])

    if freq_log:
        with st.expander(f"⚛️ تم تحديث الترددات — {len(freq_log)} قناة تم تحديث ترددها", expanded=True):
            st.table([{"القناة": e['channel'], "التردد القديم": e['old'], "التردد الجديد": e['new'], "المصدر": e.get('source','')} for e in freq_log])

    if newch_log:
        with st.expander(f"✨ تم إضافة قنوات جديدة — {len(newch_log)} قناة جديدة تم إضافتها", expanded=True):
            st.table([{"اسم القناة": e['name'], "التردد": e['freq'], "الفئة": e['cat']} for e in newch_log])

    if freq_log or newch_log:
        st.write("---")

    # معاينة الفئات
    from collections import defaultdict as _dd
    cats_dist = _dd(list)
    for ch in st.session_state.p3_channels_preview:
        cats_dist[ai_classify(ch["name"])].append(ch["name"])

    st.markdown("#### 📊 معاينة توزيع القنوات:")
    col_p1, col_p2 = st.columns(2)
    display_order = cat_prio if cat_prio else ALL_CATS
    for i, cat in enumerate(display_order):
        if cat in cats_dist:
            lst = cats_dist[cat]
            with (col_p1 if i % 2 == 0 else col_p2):
                with st.expander(f"{cat} — ({len(lst)} قناة)"):
                    st.caption(", ".join(lst[:40]) + ("..." if len(lst) > 40 else ""))

    st.write("---")

    # معاينة الجدول
    st.markdown("#### 📋 عينة من القنوات المضمنة:")
    preview_data = []
    for idx, ch in enumerate(st.session_state.p3_channels_preview[:30], start=1):
        preview_data.append({"الرقم": idx, "اسم القناة": ch['name'], "التردد": ch['freq'], "الفئة": ai_classify(ch['name'])})
    st.table(preview_data)
    if len(st.session_state.p3_channels_preview) > 30:
        st.caption(f"... و {len(st.session_state.p3_channels_preview) - 30} قناة أخرى في الملف الكامل.")

    st.write("---")

    # أزرار التحميل
    col_d1, col_d2, col_d3 = st.columns([2, 2, 1])
    with col_d1:
        st.download_button(
            label="📥 تحميل ملف الشاشة (GlobalClone00001.TLL)",
            data=st.session_state.p3_output_bytes,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream",
            use_container_width=True,
        )
    with col_d2:
        st.download_button(
            label="📄 تحميل تقرير القنوات (Channels_List.txt)",
            data=st.session_state.p3_report_txt,
            file_name="Channels_List.txt",
            mime="text/plain; charset=utf-8",
            use_container_width=True,
        )
    with col_d3:
        if st.button("🔄 إنشاء ملف جديد", use_container_width=True):
            st.session_state.p3_step             = 1
            st.session_state.p3_output_bytes     = None
            st.session_state.p3_report_txt       = None
            st.session_state.p3_channels_preview = []
            st.rerun()

    # ملحوظة LG
    st.write("---")
    lg_trick_text = (
        "في بعض الحالات، بعد تنزيل ملف القنوات على الشاشة، قد تشعر أن القنوات ليست منظمة كما رتبتها. "
        "لحل هذا الأمر فوراً واجبار الشاشة على تفعيل الترتيب الصحيح، قم بالآتي:\n\n"
        "1. من إعدادات التلفزيون اختار القنوات (Channels).\n"
        "2. بعد ذلك اختار مدير القنوات (Channel Manager).\n"
        "3. اختار التعديل على كل القنوات (Edit All Channels).\n"
        "4. ستظهر لك القنوات المرتبة ويكون بعضها في وضع مخفي، قم بتحديد كل القنوات واختار استعادة (Restore).\n\n"
        "ملحوظة: تفعل هذه الخطوة فقط إذا شعرت أن الملف بعد التنزيل غير مرتب كما حددته على الموقع."
    )
    trick_lines = lg_trick_text.split('\n')
    st.markdown(f"""
<div style="background:rgba(255,193,7,0.1);border:2px solid #ffc107;border-radius:14px;padding:22px;margin-top:10px;">
<div style="color:#ffc107;font-size:1.1rem;font-weight:bold;margin-bottom:12px;">💡 ملحوظة فنية هامة جداً بعد تنزيل الملف على شاشة LG:</div>
{''.join(f'<div style="margin:6px 0;line-height:1.7;color:#e0e0e0;">{line}</div>' for line in trick_lines if line.strip())}
</div>
""", unsafe_allow_html=True)
