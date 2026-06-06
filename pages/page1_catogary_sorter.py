import streamlit as st
import xml.etree.ElementTree as ET
import json
import re
import requests

from datetime import datetime

# ──────────────────────────────────────────────────────
# 1. SESSION STATE
# ──────────────────────────────────────────────────────
for key, val in {
    'lang': 'ar',
    'theme': 'dark',
    'p1_file_loaded': False,
    'scan_done_p1': False,
    'maint_done_p1': False,
    'inserted_list_p1': [],
    'maint_details_p1': [],
    'p1_channels_extra': [],
    'p1_freq_patched': False,
    'live_db_cache': None,        # ← قاعدة البيانات الحية من dthsat.com
    'live_db_last_fetch': None,   # ← وقت آخر جلب
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ──────────────────────────────────────────────────────
# 2. UI TEXT
# ──────────────────────────────────────────────────────
UI_TEXT = {
    'ar': {
        'title':             "📺 RAMBO — المُرتِّب الذكي بالفئات",
        'subtitle':          "⚡ ارفع ملف القنوات، رتّب الفئات، وحمّل الملف المعدَّل",
        'upload_label':      "🚀 اختر ملف القنوات (GlobalClone00001.TLL) من الفلاشة:",
        'success_read':      "🛸 تم قراءة الملف بنجاح! الموديل: ",
        'auto_features_title': "⚙️ خيارات الفحص الذكي والصيانة الفورية للملف",
        'chk_scan_inject':   "📡 تفعيل الفحص التلقائي وزرع القنوات الجديدة المتاحة على القمر فوراً",
        'chk_modern_maint':  "🔧 تفعيل الصيانة الحديثة وتحديث الترددات الميتة والقديمة تلقائياً",
        'btn_fetch_live':    "🌐 جلب أحدث بيانات NileSat من الإنترنت الآن",
        'fetching':          "⏳ جاري الجلب من dthsat.com ...",
        'fetch_success':     "✅ تم جلب بيانات NileSat الحية! إجمالي القنوات: ",
        'fetch_fail':        "⚠️ تعذّر الاتصال بـ dthsat.com، سيتم استخدام القاعدة المحلية.",
        'live_db_info':      "📡 قاعدة البيانات الحية — آخر تحديث: ",
        'search_header':     "🔍 البحث عن قناة داخل الملف:",
        'search_placeholder':"اكتب اسم القناة هنا...",
        'search_col_num':    "الرقم",
        'search_col_name':   "اسم القناة",
        'search_col_cat':    "الفئة",
        'search_col_freq':   "التردد",
        'search_no_results': "⚠️ لا توجد نتائج مطابقة.",
        'config_title':      "🎛️ ترتيب الفئات:",
        'multiselect_label': "اختر الفئات بالترتيب المطلوب:",
        'preview_title':     "📊 معاينة التوزيع الحالي:",
        'channels_count':    "قناة",
        'ready_msg':         "✅ تم تجهيز الملف النهائي للتحميل:",
        'btn_download_tll':  "📥 تحميل ملف الشاشة النهائي (GlobalClone00001.TLL)",
        'btn_download_txt':  "📄 تحميل تقرير الترتيب (Channels_List.txt)",
        'btn_reset':         "🔄 إعادة تهيئة / رفع ملف جديد",
        'txt_header':        "📄 تقرير ترتيب القنوات النهائي",
        'txt_order':         "🛠️ ترتيب الفئات المختار: ",
        'lg_trick_title':    "💡 ملحوظة فنية هامة جداً بعد تنزيل الملف على شاشة LG:",
        'lg_trick_text': (
            "في بعض الحالات، بعد تنزيل ملف القنوات على الشاشة، قد تشعر أن القنوات ليست منظمة كما رتبتها. "
            "لحل هذا الأمر فوراً واجبار الشاشة على تفعيل الترتيب الصحيح، قم بالآتي:\n\n"
            "1. من إعدادات التلفزيون اختار القنوات (Channels).\n"
            "2. بعد ذلك اختار مدير القنوات (Channel Manager).\n"
            "3. اختار التعديل على كل القنوات (Edit All Channels).\n"
            "4. ستظهر لك القنوات المرتبة ويكون بعضها في وضع مخفي، قم بتحديد كل القنوات واختار استعادة (Restore).\n\n"
            "ملحوظة: تفعل هذه الخطوة فقط إذا شعرت أن الملف بعد التنزيل غير مرتب كما حددته على الموقع."
        ),
        'no_file_msg':       "⬆️ ارفع ملف TLL أولاً لتبدأ العمل.",
    },
    'en': {
        'title':             "📺 RAMBO — Smart Category Sorter",
        'subtitle':          "⚡ Upload your channel file, sort categories, download the result",
        'upload_label':      "🚀 Upload Channel File (GlobalClone00001.TLL) from USB:",
        'success_read':      "🛸 File Parsed Successfully! Model: ",
        'auto_features_title': "⚙️ Smart Auto-Maintenance & Scanning Options",
        'chk_scan_inject':   "📡 Enable Auto-Scan & Inject newly available Satellite Channels",
        'chk_modern_maint':  "🔧 Enable Modern Maintenance & Auto-Update dead frequencies",
        'btn_fetch_live':    "🌐 Fetch Latest NileSat Data from Internet Now",
        'fetching':          "⏳ Fetching from dthsat.com ...",
        'fetch_success':     "✅ Live NileSat data fetched! Total channels: ",
        'fetch_fail':        "⚠️ Could not reach dthsat.com, using local database.",
        'live_db_info':      "📡 Live Database — Last updated: ",
        'search_header':     "🔍 Search inside file:",
        'search_placeholder':"Type channel name...",
        'search_col_num':    "No.",
        'search_col_name':   "Channel Name",
        'search_col_cat':    "Category",
        'search_col_freq':   "Frequency",
        'search_no_results': "⚠️ No matching results.",
        'config_title':      "🎛️ Category order:",
        'multiselect_label': "Select categories in desired order:",
        'preview_title':     "📊 Current distribution preview:",
        'channels_count':    "Channels",
        'ready_msg':         "✅ Final file ready for download:",
        'btn_download_tll':  "📥 Download Final TV File (GlobalClone00001.TLL)",
        'btn_download_txt':  "📄 Download Sorting Report (Channels_List.txt)",
        'btn_reset':         "🔄 Reset / Upload New File",
        'txt_header':        "📄 Final Channel Sorting Report",
        'txt_order':         "🛠️ Selected category priority: ",
        'lg_trick_title':    "💡 Important Technical Note After Loading File on LG TV:",
        'lg_trick_text': (
            "In some cases, after loading the channel file onto the TV, you may feel the channels are not "
            "organized as you sorted them. To fix this immediately and force the TV to apply the correct order:\n\n"
            "1. From TV Settings, select Channels.\n"
            "2. Then select Channel Manager.\n"
            "3. Select Edit All Channels.\n"
            "4. The sorted channels will appear with some hidden — select all channels and choose Restore.\n\n"
            "Note: Only perform this step if you feel the file after loading is not sorted as you set on the site."
        ),
        'no_file_msg':       "⬆️ Upload a TLL file to start.",
    }
}

t = UI_TEXT[st.session_state.lang]

# ──────────────────────────────────────────────────────
# 3. PAGE CONFIG
# ──────────────────────────────────────────────────────
st.set_page_config(page_title="RAMBO P1 — Sorter", page_icon="⚡", layout="wide")

# ──────────────────────────────────────────────────────
# 4. CSS
# ──────────────────────────────────────────────────────
if st.session_state.theme == 'dark':
    bg  = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)"
    tc, bb, bord = "#00f0ff", "rgba(13,7,33,0.85)", "#00f0ff"
    bsh, tsh = "rgba(0,240,255,0.35)", "0 0 5px rgba(0,240,255,0.4)"
    table_head_bg = "#0d0722"
else:
    bg  = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
    tc, bb, bord = "#0d0722", "#ffffff", "#ff007f"
    bsh, tsh = "rgba(255,0,127,0.15)", "none"
    table_head_bg = "#0d0722"

ff = "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
.main {{ background: {bg} !important; color: {tc} !important; font-family: {ff}; }}
h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.4) !important;
      text-align: center; font-weight: 900; margin-top: 5px; }}
h3, p, label, .stMarkdown {{ color: {tc} !important; text-shadow: {tsh}; }}
.stTextInput > div > div > input, .stSelectbox > div > div {{
    background-color: {bb} !important; color: {tc} !important;
    border: 2px solid {bord} !important; border-radius: 10px !important;
}}
div[data-testid="stFileUploader"] {{
    background: {bb} !important; border: 2px solid {bord} !important;
    box-shadow: 0 5px 15px {bsh} !important; border-radius: 14px !important;
    padding: 18px !important; margin-bottom: 20px !important;
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
.stCheckbox label {{ color: {tc} !important; }}
.stExpander {{ border: 1px solid {bord} !important; border-radius: 10px !important; }}
.live-badge {{
    display: inline-block; background: linear-gradient(90deg,#00f0ff22,#ff007f22);
    border: 1px solid #00f0ff; border-radius: 8px; padding: 6px 14px;
    color: #00f0ff; font-size: 0.85rem; margin-bottom: 10px;
}}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 5. HEADER CONTROLS
# ──────────────────────────────────────────────────────
col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("🌐 English" if st.session_state.lang == 'ar' else "🌐 العربية"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
        st.rerun()
with col_theme:
    if st.button("☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

st.title(t['title'])
st.markdown(f"<h3 style='text-align:center;'>{t['subtitle']}</h3>", unsafe_allow_html=True)
st.write("---")

# ──────────────────────────────────────────────────────
# 6. LIVE DATABASE FETCHER من dthsat.com
# ──────────────────────────────────────────────────────

# قاعدة احتياطية محلية (تُستخدم إذا فشل الإنترنت)
FALLBACK_NILESAT_DB = {
    "AL HAYAT":            {"frequency": 12207, "polarization": "V"},
    "AL HAYAT 2":          {"frequency": 12207, "polarization": "V"},
    "SAT-7 KIDS":          {"frequency": 11353, "polarization": "V"},
    "SAT-7 ARABIC":        {"frequency": 11353, "polarization": "V"},
    "CTV":                 {"frequency": 10815, "polarization": "H"},
    "CTV (EGYPT)":         {"frequency": 10815, "polarization": "H"},
    "AGHAPY TV":           {"frequency": 10815, "polarization": "H"},
    "IQRAA":               {"frequency": 11938, "polarization": "V"},
    "ALMAGD TV":           {"frequency": 10815, "polarization": "H"},
    "AL RAHMA":            {"frequency": 10873, "polarization": "V"},
    "QURAN KAREEM":        {"frequency": 11727, "polarization": "V"},
    "AL SALAM QURAN":      {"frequency": 10853, "polarization": "H"},
    "DOHAT ALQURAN TV":    {"frequency": 10727, "polarization": "H"},
    "AL JAZEERA HD":       {"frequency": 10853, "polarization": "H"},
    "AL ARABIYA":          {"frequency": 11938, "polarization": "V"},
    "AL HADATH":           {"frequency": 11938, "polarization": "V"},
    "ECHOROUK TV":         {"frequency": 10922, "polarization": "V"},
    "ECHOROUK TV NEWS":    {"frequency": 10922, "polarization": "V"},
    "CBC":                 {"frequency": 12092, "polarization": "V"},
    "EXTRA NEWS":          {"frequency": 12092, "polarization": "V"},
    "ON E":                {"frequency": 12092, "polarization": "V"},
    "MBC 2":               {"frequency": 11938, "polarization": "V"},
    "MBC 4":               {"frequency": 11938, "polarization": "V"},
    "ROTANA CINEMA":       {"frequency": 11938, "polarization": "V"},
    "ON TIME SPORTS 1":    {"frequency": 11861, "polarization": "V"},
    "ON TIME SPORTS 2":    {"frequency": 11861, "polarization": "V"},
    "SPACE TOON":          {"frequency": 11727, "polarization": "V"},
    "BATOOT KIDS":         {"frequency": 10853, "polarization": "H"},
    "KARAMEESH":           {"frequency": 10815, "polarization": "H"},
    "TOYOR ALJANNAH":      {"frequency": 11179, "polarization": "H"},
    "NOURSAT":             {"frequency": 10815, "polarization": "H"},
    "ALKARMA TV FAMILY":   {"frequency": 10815, "polarization": "H"},
    "MIRACLE CHANNEL":     {"frequency": 10815, "polarization": "H"},
    "ALHURRA TV":          {"frequency": 11258, "polarization": "H"},
    "SYRIA TV":            {"frequency": 11258, "polarization": "H"},
    "PALESTINE TV":        {"frequency": 10727, "polarization": "H"},
    "QATAR TV":            {"frequency": 10834, "polarization": "V"},
    "QATAR TV 2":          {"frequency": 10834, "polarization": "V"},
    "AL ASSEMA":           {"frequency": 10853, "polarization": "H"},
    "DRAMA 1":             {"frequency": 10853, "polarization": "H"},
    "FAMILY DRAMA":        {"frequency": 10873, "polarization": "V"},
    "4G AFLAM":            {"frequency": 10853, "polarization": "H"},
    "4G CINEMA":           {"frequency": 10853, "polarization": "H"},
    "4G DRAMA":            {"frequency": 10853, "polarization": "H"},
    "TOP MOVIES (EGYPT)":  {"frequency": 10873, "polarization": "V"},
    "SAMIRA TV":           {"frequency": 10922, "polarization": "V"},
    "ENNAHAR TV":          {"frequency": 10922, "polarization": "V"},
    "WATANIA 1":           {"frequency": 10873, "polarization": "V"},
    "LIBYA AL-AHRAR TV":   {"frequency": 10815, "polarization": "H"},
    "EL HAYAT TV":         {"frequency": 10922, "polarization": "V"},
    "MISR TV":             {"frequency": 10727, "polarization": "H"},
    "AJMAN TV":            {"frequency": 11258, "polarization": "H"},
    "ALSHARQIYA NEWS":     {"frequency": 10873, "polarization": "V"},
    "DIJLAH TV":           {"frequency": 10873, "polarization": "V"},
}


@st.cache_data(ttl=3600)  # كاش لمدة ساعة
def fetch_nilesat_live_db():
    """
    يجلب قائمة قنوات NileSat الحية من dthsat.com
    ويُعيد dict: {CHANNEL_NAME_UPPER: {frequency, polarization}}
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(
            "https://www.dthsat.com/Nile-Sat",
            headers=headers,
            timeout=12
        )
        resp.raise_for_status()

        # استخراج صفوف <tr> من كل جداول HTML باستخدام regex فقط
        live_db = {}
        # نجيب كل الصفوف من الصفحة
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', resp.text, re.DOTALL | re.IGNORECASE)
        for row in rows:
            # نجيب كل الخلايا <td>
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
            # تنظيف من HTML tags
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


def get_active_db():
    """يُعيد قاعدة البيانات النشطة (حية أو احتياطية)"""
    if st.session_state.live_db_cache:
        return st.session_state.live_db_cache
    return {k: v for k, v in FALLBACK_NILESAT_DB.items()}


# ──────────────────────────────────────────────────────
# 7. زر جلب البيانات الحية — يظهر دائماً في الأعلى
# ──────────────────────────────────────────────────────
col_fetch, col_fetch_status = st.columns([2, 4])
with col_fetch:
    if st.button(t['btn_fetch_live'], use_container_width=True):
        with st.spinner(t['fetching']):
            result = fetch_nilesat_live_db()
            if result:
                st.session_state.live_db_cache = result
                st.session_state.live_db_last_fetch = datetime.now().strftime("%Y-%m-%d %H:%M")
                # إعادة تعيين الفحص والصيانة عشان يأخذ البيانات الجديدة
                st.session_state.scan_done_p1  = False
                st.session_state.maint_done_p1 = False
                st.session_state.p1_channels_extra = []
                st.session_state.maint_details_p1  = []
                st.session_state.inserted_list_p1  = []
                st.toast("🛸 " + (f"تم جلب {len(result):,} قناة من NileSat!" if st.session_state.lang == 'ar'
                                  else f"Fetched {len(result):,} channels from NileSat!"))
                st.rerun()
            else:
                st.toast("⚠️ " + (t['fetch_fail']), icon="⚠️")

with col_fetch_status:
    if st.session_state.live_db_cache:
        n   = len(st.session_state.live_db_cache)
        lft = st.session_state.live_db_last_fetch or "?"
        st.markdown(
            f"<div class='live-badge'>🟢 {t['fetch_success']}{n:,} | ⏱ {lft}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='live-badge' style='border-color:#ff007f;color:#ff007f;'>"
            f"🔴 {'قاعدة بيانات محلية (اضغط الزر للتحديث)' if st.session_state.lang == 'ar' else 'Local DB (press button to update)'}"
            f"</div>",
            unsafe_allow_html=True
        )

st.write("---")

# ──────────────────────────────────────────────────────
# 8. CATEGORY LISTS & AI CLASSIFIER
# ──────────────────────────────────────────────────────
ALL_AVAILABLE_CATEGORIES = [
    "⛪ قنوات مسيحية"       if st.session_state.lang == 'ar' else "⛪ Christian Channels",
    "🕌 قنوات إسلامية"      if st.session_state.lang == 'ar' else "🕌 Islamic Channels",
    "🎬 مسلسلات ودراما"     if st.session_state.lang == 'ar' else "🎬 Drama & Series",
    "🍿 أفلام عربية وأجنبية" if st.session_state.lang == 'ar' else "🍿 Movies (Ar/En)",
    "👶 أطفال وكرتون"       if st.session_state.lang == 'ar' else "👶 Kids & Cartoon",
    "⚽ رياضة"              if st.session_state.lang == 'ar' else "⚽ Sports",
    "📰 أخبار وسياسة"       if st.session_state.lang == 'ar' else "📰 News & Politics",
    "📺 قنوات عامة ومنوعات" if st.session_state.lang == 'ar' else "📺 General Channels",
]

def ai_classify(channel_name):
    name = channel_name.upper().strip()
    if any(w in name for w in ["CTV","AGHAPY","MESAT","KARMA","ALKARMA","NOURSAT","SAT-7","SAT7",
                                "AL HAYAT","HAYAT TV","MIRACLE","COPTIC","CHURCH","LOVEWORLD",
                                "CHRIST ARMY","ALMAHABA","AL BASIRA","AL NADA","ANOINTING","ROSE TV"]):
        return ALL_AVAILABLE_CATEGORIES[0]
    if any(w in name for w in ["QURAN","RAHMA","MAJD","MAKKA","IQRAA","IQRA","HUDA","WESAL","ISLAM",
                                "SUNNAH","DOHAT","AL SALAM QURAN","AL SALAM SUNNAH","MENHAG","RAWHANYAT",
                                "ALKAFEEL","KUNUZ","KUNOUZ","AL NUJABA","ZITOUNA","ALGHADEER"]):
        return ALL_AVAILABLE_CATEGORIES[1]
    if any(w in name for w in ["MOSALSALAT","DRAMA","SERIES","KHOLASA","MASRAWI","SHAHID","NILE DRAMA",
                                "AL SA3AA MOSALSALATE","DOLLY MOSALSALAT","RAMADAN DRAMA","SHOOF DRAMA",
                                "FAMILY DRAMA","FAMILY HIKAYAT","4G DRAMA","BEIRUT DRAMA","QUEEN DRAMA",
                                "DRAMA ALWAN","DRAMA 1"]):
        return ALL_AVAILABLE_CATEGORIES[2]
    if any(w in name for w in ["CINEMA","ROTANA","AFLAM","MIX","FOX","MBC2","MBC 2","MBC4","MBC 4",
                                "MBC MAX","ACTION","RAMBO","MOVIE","FILM","COMEDY","4G AFLAM","4G CINEMA",
                                "4G CIMA","4G FILM","4G CLASSIC","AL SHASHA CINEMA","ALYAOUM CINEMA",
                                "BEIRUT AFLAM","BEIRUT CINEMA","BEIRUT CLASSIC","CIMA TUBE","CINEMA TUBE",
                                "TOP MOVIES","CINEMA PRO","TOK TOK CINEMA","TOK TOK CIMA","ORPIT PLUS"]):
        return ALL_AVAILABLE_CATEGORIES[3]
    if any(w in name for w in ["SPACE TOON","SPACETOON","CN","CARTOON","MAJID","KIDS","TOM","TOYOR",
                                "BABY","JUNIOR","BATOOT","KARAMEESH","BANNOUTA","COOKIES KIDS"]):
        return ALL_AVAILABLE_CATEGORIES[4]
    if any(w in name for w in ["SPORT","SPORTS","ONTIME","ON TIME","KASS","AD_SPORTS","AD SPORTS",
                                "SSC","BEIN","MATCH","FOOTBALL","EL-HEDDAF","HEDDAF","7BESHA ACTION"]):
        return ALL_AVAILABLE_CATEGORIES[5]
    if any(w in name for w in ["NEWS","JAZEERA","ARABIYA","HADATH","CAIRO","SKY NEWS","BBC","CNN",
                                "EXTRA NEWS","CBC","ON E","SADA","BALADI","MASR","EGYPT NOW","KAHERA",
                                "ECHOROUK","ENNAHAR","AL 24","ALSHARQIYA","AL ASSEMA","ALHURRA",
                                "ALARABY","MISR TV","PALESTINE","CHANNEL 24"]):
        return ALL_AVAILABLE_CATEGORIES[6]
    return ALL_AVAILABLE_CATEGORIES[7]


# ──────────────────────────────────────────────────────
# 9. HELPERS
# ──────────────────────────────────────────────────────
def set_item_prnum(raw, index):
    if "<prNum>" in raw:
        raw = re.sub(r"<prNum>\d+</prNum>", f"<prNum>{index}</prNum>", raw)
    else:
        raw = raw.replace("<ITEM>", f"<ITEM>\r\n<prNum>{index}</prNum>")
    return raw

def normalize_modern_node(node, index):
    node["majorNumber"] = index
    node["category"]    = ai_classify(node.get("channelName", ""))
    node["Invisible"]   = False
    node["skipped"]     = False
    node["deleted"]     = False
    node["userSelCHNo"] = True
    return node


# ──────────────────────────────────────────────────────
# 10. FILE UPLOADER + RESET
# ──────────────────────────────────────────────────────
if 'p1_uploader_key' not in st.session_state:
    st.session_state.p1_uploader_key = 0

col_up, col_reset = st.columns([5, 1])
with col_up:
    uploaded_file = st.file_uploader(
        t['upload_label'], type=["TLL"],
        key=f"p1_uploader_{st.session_state.p1_uploader_key}"
    )
with col_reset:
    st.write("")
    st.write("")
    if st.button(t['btn_reset'], use_container_width=True):
        keep = {'lang', 'theme', 'live_db_cache', 'live_db_last_fetch'}
        new_key = st.session_state.get('p1_uploader_key', 0) + 1
        for k in list(st.session_state.keys()):
            if k not in keep:
                del st.session_state[k]
        st.session_state.p1_uploader_key = new_key
        st.rerun()

# ──────────────────────────────────────────────────────
# 11. MAIN LOGIC
# ──────────────────────────────────────────────────────
if uploaded_file is None:
    st.info(t['no_file_msg'])
else:
    if st.session_state.get("p1_last_file_name") != uploaded_file.name:
        st.session_state.scan_done_p1     = False
        st.session_state.maint_done_p1    = False
        st.session_state.inserted_list_p1 = []
        st.session_state.maint_details_p1 = []
        st.session_state.p1_channels_extra = []
        st.session_state.p1_freq_patches   = {}
        st.session_state.p1_last_file_name = uploaded_file.name

    file_bytes = uploaded_file.read()
    try:
        file_text = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        file_text = file_bytes.decode('latin-1')

    file_text_cleaned = re.sub(r'^\s+', '', file_text)
    try:
        root = ET.fromstring(file_text_cleaned.encode('utf-8'))
    except Exception:
        root = ET.fromstring(file_text_cleaned.encode('latin-1'))

    model_setting = root.find(".//ModelName")
    model_name    = model_setting.text if model_setting is not None else "Unknown LG TV"

    legacy_broadcast_tag = root.find(".//legacybroadcast")
    is_modern = legacy_broadcast_tag is not None and legacy_broadcast_tag.text

    if is_modern:
        _bd = json.loads(legacy_broadcast_tag.text.strip())
        total_ch = len(_bd.get("channelList", []))
        file_type_label = "Modern JSON"
        file_type_desc  = "حديث (2020+)" if st.session_state.lang == 'ar' else "Modern (2020+)"
    else:
        total_ch = len(re.findall(r'<ITEM>', file_text))
        file_type_label = "Legacy XML"
        file_type_desc  = "قديم (ما قبل 2020)" if st.session_state.lang == 'ar' else "Legacy (pre-2020)"

    st.success(
        f"{t['success_read']} **{model_name}** | "
        f"📡 {file_type_label} | "
        f"{'الإجمالي' if st.session_state.lang == 'ar' else 'Total'}: {total_ch:,} "
        f"{'قناة' if st.session_state.lang == 'ar' else 'channels'}."
    )

    # ══════════════════════════════════════════════════
    # قسم الفحص والصيانة — الآن يستخدم قاعدة البيانات الحية
    # ══════════════════════════════════════════════════
    st.write("---")
    st.write(f"### {t['auto_features_title']}")

    # نجلب القاعدة النشطة (حية أو احتياطية)
    ACTIVE_DB = get_active_db()

    # بناء قاعدة الصيانة ديناميكياً من القاعدة الحية:
    # نقارن أي قناة في الملف لها تردد مختلف عن القاعدة الحية → نحدّثه
    col_chk1, col_chk2 = st.columns(2)

    with col_chk1:
        scan_active = st.checkbox(t['chk_scan_inject'], value=False, key="chk_scan_p1")

        if scan_active and not st.session_state.get('scan_done_p1', False):
            if is_modern:
                _tmp_bd = json.loads(legacy_broadcast_tag.text.strip())
                current_names_set = {
                    ch.get("channelName", "").upper()
                    for ch in _tmp_bd.get("channelList", [])
                }
            else:
                current_names_set = {
                    m.group(1).upper()
                    for m in re.finditer(r'<vchName>(.*?)</vchName>', file_text)
                }

            new_inserted_names = []
            extra_channels     = []

            # المقارنة: كل قناة في القاعدة الحية غير موجودة في الملف → إضافة
            for db_name_upper, db_info in ACTIVE_DB.items():
                # نتحقق بمطابقة جزئية مرنة
                is_present = any(
                    db_name_upper in existing or existing in db_name_upper
                    for existing in current_names_set
                )
                if not is_present:
                    pol_full = db_info["polarization"]
                    nc = {
                        "name": db_name_upper.title(),
                        "frequency": db_info["frequency"],
                        "polarization": pol_full,
                    }
                    extra_channels.append(nc)
                    new_inserted_names.append(
                        f"📡 {nc['name']} "
                        f"({'تردد' if st.session_state.lang == 'ar' else 'Freq'}: {nc['frequency']} {pol_full[0]})"
                    )

            st.session_state.scan_done_p1      = True
            st.session_state.inserted_list_p1  = new_inserted_names
            st.session_state.p1_channels_extra = extra_channels

            if new_inserted_names:
                st.toast("📡 " + ("تم زرع القنوات الجديدة بنجاح!" if st.session_state.lang == 'ar'
                                  else "New channels injected!"))
                st.rerun()

        if scan_active:
            if st.session_state.get('inserted_list_p1'):
                injected = st.session_state.inserted_list_p1
                st.markdown(
                    "<div style='background:rgba(0,240,255,0.1);padding:12px;border-radius:10px;"
                    "border-left:4px solid #00f0ff;margin-top:10px;'>",
                    unsafe_allow_html=True
                )
                label = (f"**✨ {len(injected)} قناة جديدة تم زرعها وإضافتها للملف:**"
                         if st.session_state.lang == 'ar'
                         else f"**✨ {len(injected)} new channels injected into the file:**")
                st.markdown(label)
                # نعرض أول 30 فقط لتجنب الإطالة
                for item in injected[:30]:
                    st.markdown(f"<span style='color:#00f0ff;font-size:0.85rem;'>{item}</span>",
                                unsafe_allow_html=True)
                if len(injected) > 30:
                    st.markdown(f"<span style='color:#888;'>... و {len(injected)-30} قناة أخرى</span>",
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                msg = ("ℹ️ لم يتم العثور على قنوات جديدة للزرع (مضافة بالفعل)."
                       if st.session_state.lang == 'ar'
                       else "ℹ️ No new channels found to inject (already present).")
                st.markdown(f"<div style='color:#888;margin-top:10px;'>{msg}</div>",
                            unsafe_allow_html=True)

    with col_chk2:
        maint_active = st.checkbox(t['chk_modern_maint'], value=False, key="chk_maint_p1")

        if maint_active and not st.session_state.get('maint_done_p1', False):
            maint_details = []
            freq_patches  = {}

            # مقارنة ترددات الملف بالقاعدة الحية وتحديث المختلف منها
            if is_modern:
                _tmp_bd2 = json.loads(legacy_broadcast_tag.text.strip())
                for ch in _tmp_bd2.get("channelList", []):
                    ch_name  = ch.get("channelName", "Unknown")
                    old_f    = ch.get("frequency", 0)
                    name_up  = ch_name.upper()
                    # بحث في القاعدة الحية
                    db_match = ACTIVE_DB.get(name_up) or ACTIVE_DB.get(
                        next((k for k in ACTIVE_DB if k in name_up or name_up in k), ""), None
                    )
                    if db_match:
                        new_f = db_match["frequency"]
                        if str(old_f) != str(new_f):
                            freq_patches[name_up] = str(new_f)
                            maint_details.append(
                                f"🔄 **{ch_name}** | "
                                f"{'من' if st.session_state.lang == 'ar' else 'from'} `{old_f}` "
                                f"{'إلى' if st.session_state.lang == 'ar' else 'to'} `{new_f}`"
                            )
            else:
                for m in re.finditer(r'<vchName>(.*?)</vchName>.*?<frequency>(\d+)</frequency>',
                                     file_text, re.DOTALL):
                    ch_name = m.group(1)
                    old_f   = m.group(2)
                    name_up = ch_name.upper()
                    db_match = ACTIVE_DB.get(name_up) or ACTIVE_DB.get(
                        next((k for k in ACTIVE_DB if k in name_up or name_up in k), ""), None
                    )
                    if db_match:
                        new_f = str(db_match["frequency"])
                        if old_f != new_f:
                            freq_patches[name_up] = new_f
                            maint_details.append(
                                f"🔄 **{ch_name}** | "
                                f"{'من' if st.session_state.lang == 'ar' else 'from'} `{old_f}` "
                                f"{'إلى' if st.session_state.lang == 'ar' else 'to'} `{new_f}`"
                            )

            st.session_state.maint_done_p1    = True
            st.session_state.maint_details_p1 = maint_details
            st.session_state.p1_freq_patches  = freq_patches

            if maint_details:
                st.toast("🔧 " + (f"تم تحديث {len(maint_details)} تردد!" if st.session_state.lang == 'ar'
                                  else f"Updated {len(maint_details)} frequencies!"))
                st.rerun()

        if maint_active:
            if st.session_state.get('maint_details_p1'):
                details = st.session_state.maint_details_p1
                st.markdown(
                    "<div style='background:rgba(255,0,127,0.1);padding:12px;border-radius:10px;"
                    "border-left:4px solid #ff007f;margin-top:10px;'>",
                    unsafe_allow_html=True
                )
                label = (f"**🔧 {len(details)} تردد تم تحديثه من القاعدة الحية:**"
                         if st.session_state.lang == 'ar'
                         else f"**🔧 {len(details)} frequencies updated from live database:**")
                st.markdown(label)
                for detail in details[:20]:
                    st.markdown(f"<span style='color:#ff007f;font-size:0.85rem;'>{detail}</span>",
                                unsafe_allow_html=True)
                if len(details) > 20:
                    st.markdown(f"<span style='color:#888;'>... و {len(details)-20} تردد آخر</span>",
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                msg = ("ℹ️ جميع الترددات الحالية مطابقة لأحدث نسخة."
                       if st.session_state.lang == 'ar'
                       else "ℹ️ All current frequencies match the latest version.")
                st.markdown(f"<div style='color:#888;margin-top:10px;'>{msg}</div>",
                            unsafe_allow_html=True)

    # ══════════════════════════════════════════════════
    # باقي منطق الصفحة — نفس الكود الأصلي بدون تغيير
    # ══════════════════════════════════════════════════
    st.write("---")

    channels_to_sort     = []
    report_changes       = []
    existing_names_upper = set()

    # ── Modern JSON ──
    if is_modern:
        broadcast_data = json.loads(legacy_broadcast_tag.text.strip())
        channels_list  = broadcast_data.get("channelList", [])
        freq_patches   = st.session_state.get('p1_freq_patches', {})

        for ch in channels_list:
            ch_name  = ch.get("channelName", "Unknown")
            old_freq = str(ch.get("frequency", "N/A"))
            name_up  = ch_name.upper()
            existing_names_upper.add(name_up)

            if "category" not in ch or not ch["category"]:
                ch["category"] = ai_classify(ch_name)

            if name_up in freq_patches:
                new_f = freq_patches[name_up]
                if old_freq != new_f:
                    ch["frequency"] = int(new_f)
                    old_freq = new_f

            channels_to_sort.append({"name": ch_name, "freq": old_freq,
                                      "node_data": ch, "is_injected": False})

        extra_chs = st.session_state.get('p1_channels_extra', [])
        for nc in extra_chs:
            if nc['name'].upper() not in existing_names_upper:
                new_node = channels_list[0].copy() if channels_list else {}
                new_node.update({
                    "channelName":  nc['name'],
                    "frequency":    nc['frequency'],
                    "polarization": nc['polarization'],
                    "Invisible": False, "skipped": False,
                    "deleted": False, "userSelCHNo": True,
                    "category": ai_classify(nc['name']),
                })
                channels_to_sort.append({
                    "name": nc['name'], "freq": str(nc['frequency']),
                    "node_data": new_node, "is_injected": True
                })
                existing_names_upper.add(nc['name'].upper())

    # ── Legacy XML ──
    else:
        item_blocks  = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)
        freq_patches = st.session_state.get('p1_freq_patches', {})

        for item_str in item_blocks:
            name_match = re.search(r'<vchName>(.*?)</vchName>', item_str)
            freq_match = re.search(r'<frequency>(.*?)</frequency>', item_str)
            ch_name    = name_match.group(1) if name_match else "Unknown"
            name_up    = ch_name.upper()
            existing_names_upper.add(name_up)

            if name_up in freq_patches:
                new_f    = freq_patches[name_up]
                item_str = re.sub(r'<frequency>\d+</frequency>',
                                  f'<frequency>{new_f}</frequency>', item_str)
                live_freq = new_f
            else:
                live_freq = freq_match.group(1) if freq_match else "N/A"

            channels_to_sort.append({"name": ch_name, "freq": live_freq,
                                      "raw_str": item_str, "is_injected": False})

        extra_chs = st.session_state.get('p1_channels_extra', [])
        if item_blocks:
            sample_item = item_blocks[0]
            for nc in extra_chs:
                if nc['name'].upper() not in existing_names_upper:
                    new_item = re.sub(r'<vchName>.*?</vchName>',
                                      f'<vchName>{nc["name"]}</vchName>', sample_item)
                    new_item = re.sub(r'<frequency>\d+</frequency>',
                                      f'<frequency>{nc["frequency"]}</frequency>', new_item)
                    channels_to_sort.append({
                        "name": nc['name'], "freq": str(nc['frequency']),
                        "raw_str": new_item, "is_injected": True
                    })
                    existing_names_upper.add(nc['name'].upper())

    # ── Search ──
    st.markdown(f"### {t['search_header']}")
    search_query = st.text_input("", placeholder=t['search_placeholder'], key="p1_search").strip().upper()
    if search_query:
        results = [
            {t['search_col_num']: idx, t['search_col_name']: ch["name"],
             t['search_col_cat']: ai_classify(ch["name"]), t['search_col_freq']: ch["freq"]}
            for idx, ch in enumerate(channels_to_sort, 1)
            if search_query in ch["name"].upper()
        ]
        st.table(results) if results else st.warning(t['search_no_results'])

    # ── Category sort ──
    st.write("---")
    st.markdown(f"### {t['config_title']}")
    user_priority = st.multiselect(t['multiselect_label'],
                                   options=ALL_AVAILABLE_CATEGORIES, default=[])
    final_priority = list(user_priority)
    for cat in ALL_AVAILABLE_CATEGORIES:
        if cat not in final_priority:
            final_priority.append(cat)

    channels_sorted = sorted(channels_to_sort,
                             key=lambda x: final_priority.index(ai_classify(x["name"])))

    # ── Preview ──
    categorized = {}
    for ch in channels_sorted:
        categorized.setdefault(ai_classify(ch["name"]), []).append(ch["name"])

    st.write("---")
    st.markdown(f"### {t['preview_title']}")
    col1, col2 = st.columns(2)
    for i, cat_name in enumerate(final_priority):
        if cat_name in categorized:
            ch_list = categorized[cat_name]
            star    = "⭐ " if cat_name in user_priority else ""
            title   = f"{star}{cat_name} — ({len(ch_list)} {t['channels_count']})"
            with (col1 if i % 2 == 0 else col2):
                with st.expander(title):
                    st.write(", ".join(ch_list))

    if report_changes:
        st.write("---")
        st.markdown("### 🔁 التعديلات" if st.session_state.lang == 'ar' else "### 🔁 Changes")
        st.table(report_changes)

    # ── Build output ──
    text_report  = f"{t['txt_header']} ({model_name})\n" + "=" * 50 + "\n"
    text_report += t['txt_order'] + " -> ".join(final_priority) + "\n" + "=" * 50 + "\n\n"

    if is_modern:
        final_list_modern = []
        for index, ch in enumerate(channels_sorted, start=1):
            node = normalize_modern_node(ch["node_data"], index)
            final_list_modern.append(node)
            text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}"
            text_report += " [NEW]\n" if ch["is_injected"] else "\n"

        broadcast_data["channelList"] = final_list_modern
        legacy_broadcast_tag.text = json.dumps(broadcast_data, ensure_ascii=False, separators=(',', ':'))
        final_xml_bytes = ET.tostring(root, encoding="utf-8")

    else:
        item_strings_sorted = []
        for index, ch in enumerate(channels_sorted, start=1):
            raw = set_item_prnum(ch["raw_str"], index)
            item_strings_sorted.append(raw)
            text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}"
            text_report += " [NEW]\n" if ch["is_injected"] else "\n"

        combined_items_str = "\r\n".join(item_strings_sorted)
        start_idx = file_text.find("<ITEM>")
        end_idx   = file_text.rfind("</ITEM>") + len("</ITEM>")
        final_text_output = (file_text[:start_idx] + combined_items_str + file_text[end_idx:]
                             if start_idx != -1 else combined_items_str)
        try:
            final_xml_bytes = final_text_output.encode('utf-8')
        except UnicodeEncodeError:
            final_xml_bytes = final_text_output.encode('latin-1')

    # ── Download ──
    st.write("---")
    st.success(t['ready_msg'])

    col_d1, col_d2, col_d3 = st.columns([2, 2, 1])
    with col_d1:
        st.download_button(label=t['btn_download_tll'], data=final_xml_bytes,
                           file_name="GlobalClone00001.TLL",
                           mime="application/octet-stream", use_container_width=True)
    with col_d2:
        st.download_button(label=t['btn_download_txt'], data=text_report,
                           file_name="Channels_List.txt",
                           mime="text/plain; charset=utf-8", use_container_width=True)
    with col_d3:
        if st.button(t['btn_reset'], key="reset_bottom", use_container_width=True):
            keep = {'lang', 'theme', 'live_db_cache', 'live_db_last_fetch'}
            new_key = st.session_state.get('p1_uploader_key', 0) + 1
            for k in list(st.session_state.keys()):
                if k not in keep:
                    del st.session_state[k]
            st.session_state.p1_uploader_key = new_key
            st.rerun()

    # ── LG trick note ──
    st.write("---")
    trick_lines = t['lg_trick_text'].split('\n')
    st.markdown(f"""
<div style="background:rgba(255,193,7,0.1);border:2px solid #ffc107;border-radius:14px;padding:22px;margin-top:10px;">
<div style="color:#ffc107;font-size:1.1rem;font-weight:bold;margin-bottom:12px;">{t['lg_trick_title']}</div>
{''.join(f'<div style="margin:6px 0;line-height:1.7;">{line}</div>' for line in trick_lines if line.strip())}
</div>
""", unsafe_allow_html=True)
