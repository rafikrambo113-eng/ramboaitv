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
    'p1_file_loaded': False,
    'scan_done_p1': False,
    'maint_done_p1': False,
    'inserted_list_p1': [],
    'maint_details_p1': [],
    'p1_channels_extra': [],
    'p1_freq_patched': False,
    'live_db_cache': None,
    'live_db_last_fetch': None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ──────────────────────────────────────────────────────
# 2. PAGE CONFIG
# ──────────────────────────────────────────────────────
st.set_page_config(page_title="RAMBO — الترتيب الذكي بالفئات", page_icon="🧠", layout="wide")

# ──────────────────────────────────────────────────────
# 3. CSS
# ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Cairo:wght@400;600;700;900&display=swap');

header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }
footer { display: none !important; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"],
section.main,
.main,
.block-container,
[data-testid="block-container"],
div.stApp,
.stApp {
    background: radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%) !important;
    background-color: #05020d !important;
}

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

div[data-testid="stFileUploader"] {
    background: rgba(13,7,33,0.85) !important;
    border: 2px solid #00f0ff !important;
    box-shadow: 0 5px 15px rgba(0,240,255,0.35) !important;
    border-radius: 14px !important;
    padding: 18px !important;
    margin-bottom: 20px !important;
}

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
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 4. HEADER
# ──────────────────────────────────────────────────────
st.markdown("<h1>📺 RamboAITV</h1>", unsafe_allow_html=True)
st.markdown("<h2>🧠 الترتيب الذكي بالفئات</h2>", unsafe_allow_html=True)
st.markdown("<p class='center-text' style='color:#ff007f; font-weight:700;'>🇪🇬 بأيدٍ مصرية ودماغ منياوية</p>", unsafe_allow_html=True)
st.markdown("---")

# ──────────────────────────────────────────────────────
# 5. FALLBACK DB
# ──────────────────────────────────────────────────────
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

@st.cache_data(ttl=3600)
def fetch_nilesat_live_db():
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
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


def get_active_db():
    if st.session_state.live_db_cache:
        return st.session_state.live_db_cache
    return {k: v for k, v in FALLBACK_NILESAT_DB.items()}


# ──────────────────────────────────────────────────────
# 6. زر جلب البيانات الحية
# ──────────────────────────────────────────────────────
col_fetch, col_fetch_status = st.columns([2, 4])
with col_fetch:
    if st.button("🌐 جلب أحدث بيانات NileSat من الإنترنت الآن", use_container_width=True):
        with st.spinner("⏳ جاري الجلب من dthsat.com ..."):
            result = fetch_nilesat_live_db()
            if result:
                st.session_state.live_db_cache = result
                st.session_state.live_db_last_fetch = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.scan_done_p1  = False
                st.session_state.maint_done_p1 = False
                st.session_state.p1_channels_extra = []
                st.session_state.maint_details_p1  = []
                st.session_state.inserted_list_p1  = []
                st.toast(f"🛸 تم جلب {len(result):,} قناة من NileSat!")
                st.rerun()
            else:
                st.toast("⚠️ تعذّر الاتصال بـ dthsat.com، سيتم استخدام القاعدة المحلية.", icon="⚠️")

with col_fetch_status:
    if st.session_state.live_db_cache:
        n   = len(st.session_state.live_db_cache)
        lft = st.session_state.live_db_last_fetch or "؟"
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
# 7. CATEGORY LISTS & AI CLASSIFIER
# ──────────────────────────────────────────────────────
ALL_AVAILABLE_CATEGORIES = [
    "⛪ قنوات مسيحية",
    "🕌 قنوات إسلامية",
    "🎬 مسلسلات ودراما",
    "🍿 أفلام عربية وأجنبية",
    "👶 أطفال وكرتون",
    "⚽ رياضة",
    "📰 أخبار وسياسة",
    "📺 قنوات عامة ومنوعات",
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
                                "FAMILY DRAMA","FAMILY HIKAYAT","4G DRAMA","BEIRUT DRAMA","QUEEN DRAMA",
                                "DRAMA ALWAN","DRAMA 1"]):
        return ALL_AVAILABLE_CATEGORIES[2]
    if any(w in name for w in ["CINEMA","ROTANA","AFLAM","MIX","FOX","MBC2","MBC 2","MBC4","MBC 4",
                                "MBC MAX","ACTION","RAMBO","MOVIE","FILM","COMEDY","4G AFLAM","4G CINEMA",
                                "4G CIMA","4G FILM","4G CLASSIC","TOP MOVIES","CINEMA PRO"]):
        return ALL_AVAILABLE_CATEGORIES[3]
    if any(w in name for w in ["SPACE TOON","SPACETOON","CN","CARTOON","MAJID","KIDS","TOM","TOYOR",
                                "BABY","JUNIOR","BATOOT","KARAMEESH","BANNOUTA","COOKIES KIDS"]):
        return ALL_AVAILABLE_CATEGORIES[4]
    if any(w in name for w in ["SPORT","SPORTS","ONTIME","ON TIME","KASS","AD_SPORTS","AD SPORTS",
                                "SSC","BEIN","MATCH","FOOTBALL","EL-HEDDAF","HEDDAF"]):
        return ALL_AVAILABLE_CATEGORIES[5]
    if any(w in name for w in ["NEWS","JAZEERA","ARABIYA","HADATH","CAIRO","SKY NEWS","BBC","CNN",
                                "EXTRA NEWS","CBC","ON E","SADA","BALADI","MASR","EGYPT NOW","KAHERA",
                                "ECHOROUK","ENNAHAR","AL 24","ALSHARQIYA","AL ASSEMA","ALHURRA",
                                "ALARABY","MISR TV","PALESTINE","CHANNEL 24"]):
        return ALL_AVAILABLE_CATEGORIES[6]
    return ALL_AVAILABLE_CATEGORIES[7]


# ──────────────────────────────────────────────────────
# 8. HELPERS
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
# 9. ─── الدالة الجديدة لتوليد الـ XML بنفس شكل الأصل ───
# ──────────────────────────────────────────────────────
def build_final_xml_bytes(root, original_file_text):
    """
    يحاول يحافظ على XML declaration وترتيب الـ attributes
    عشان برنامج LG Channel Editor يقدر يفتح الملف.
    """
    try:
        # استخرج الـ XML declaration الأصلي لو موجود
        decl_match = re.match(r'(<\?xml[^?]*\?>)', original_file_text.strip())
        xml_decl = decl_match.group(1) if decl_match else '<?xml version="1.0" encoding="UTF-8"?>'

        # نص الـ XML بدون declaration
        body = ET.tostring(root, encoding="unicode", xml_declaration=False)

        # دمج الـ declaration مع الـ body
        final_text = xml_decl + "\n" + body
        return final_text.encode("utf-8")
    except Exception:
        # Fallback
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)


# ──────────────────────────────────────────────────────
# 10. FILE UPLOADER + RESET
# ──────────────────────────────────────────────────────
if 'p1_uploader_key' not in st.session_state:
    st.session_state.p1_uploader_key = 0

col_up, col_reset = st.columns([5, 1])
with col_up:
    uploaded_file = st.file_uploader(
        "🚀 اختر ملف القنوات (GlobalClone00001.TLL) من الفلاشة:",
        type=["TLL"],
        key=f"p1_uploader_{st.session_state.p1_uploader_key}"
    )
with col_reset:
    st.write("")
    st.write("")
    if st.button("🔄 إعادة تهيئة", use_container_width=True):
        keep = {'live_db_cache', 'live_db_last_fetch'}
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
    st.info("⬆️ ارفع ملف TLL أولاً لتبدأ العمل.")
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

    # ─── حفظ النص الأصلي قبل أي تعديل ───
    try:
        original_file_text = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        original_file_text = file_bytes.decode('latin-1')

    file_text = original_file_text
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
        file_type_desc  = "حديث (2020+)"
    else:
        total_ch = len(re.findall(r'<ITEM>', file_text))
        file_type_label = "Legacy XML"
        file_type_desc  = "قديم (ما قبل 2020)"

    st.success(
        f"🛸 تم قراءة الملف بنجاح! الموديل: **{model_name}** | "
        f"📡 {file_type_label} | "
        f"الإجمالي: {total_ch:,} قناة."
    )

    st.write("---")
    st.write("### ⚙️ خيارات الفحص الذكي والصيانة الفورية للملف")

    ACTIVE_DB = get_active_db()

    col_chk1, col_chk2 = st.columns(2)

    with col_chk1:
        scan_active = st.checkbox("📡 تفعيل الفحص التلقائي وزرع القنوات الجديدة المتاحة على القمر فوراً", value=False, key="chk_scan_p1")

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

            for db_name_upper, db_info in ACTIVE_DB.items():
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
                        f"📡 {nc['name']} (تردد: {nc['frequency']} {pol_full[0]})"
                    )

            st.session_state.scan_done_p1      = True
            st.session_state.inserted_list_p1  = new_inserted_names
            st.session_state.p1_channels_extra = extra_channels

            if new_inserted_names:
                st.toast("📡 تم زرع القنوات الجديدة بنجاح!")
                st.rerun()

        if scan_active:
            if st.session_state.get('inserted_list_p1'):
                injected = st.session_state.inserted_list_p1
                st.markdown(
                    "<div style='background:rgba(0,240,255,0.1);padding:12px;border-radius:10px;"
                    "border-left:4px solid #00f0ff;margin-top:10px;'>",
                    unsafe_allow_html=True
                )
                st.markdown(f"**✨ {len(injected)} قناة جديدة تم زرعها وإضافتها للملف:**")
                for item in injected[:30]:
                    st.markdown(f"<span style='color:#00f0ff;font-size:0.85rem;'>{item}</span>",
                                unsafe_allow_html=True)
                if len(injected) > 30:
                    st.markdown(f"<span style='color:#888;'>... و {len(injected)-30} قناة أخرى</span>",
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#888;margin-top:10px;'>ℹ️ لم يتم العثور على قنوات جديدة للزرع (مضافة بالفعل).</div>",
                            unsafe_allow_html=True)

    with col_chk2:
        maint_active = st.checkbox("🔧 تفعيل الصيانة الحديثة وتحديث الترددات الميتة والقديمة تلقائياً", value=False, key="chk_maint_p1")

        if maint_active and not st.session_state.get('maint_done_p1', False):
            maint_details = []
            freq_patches  = {}

            if is_modern:
                _tmp_bd2 = json.loads(legacy_broadcast_tag.text.strip())
                for ch in _tmp_bd2.get("channelList", []):
                    ch_name  = ch.get("channelName", "Unknown")
                    old_f    = ch.get("frequency", 0)
                    name_up  = ch_name.upper()
                    db_match = ACTIVE_DB.get(name_up) or ACTIVE_DB.get(
                        next((k for k in ACTIVE_DB if k in name_up or name_up in k), ""), None
                    )
                    if db_match:
                        new_f = db_match["frequency"]
                        if str(old_f) != str(new_f):
                            freq_patches[name_up] = str(new_f)
                            maint_details.append(
                                f"🔄 **{ch_name}** | من `{old_f}` إلى `{new_f}`"
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
                                f"🔄 **{ch_name}** | من `{old_f}` إلى `{new_f}`"
                            )

            st.session_state.maint_done_p1    = True
            st.session_state.maint_details_p1 = maint_details
            st.session_state.p1_freq_patches  = freq_patches

            if maint_details:
                st.toast(f"🔧 تم تحديث {len(maint_details)} تردد!")
                st.rerun()

        if maint_active:
            if st.session_state.get('maint_details_p1'):
                details = st.session_state.maint_details_p1
                st.markdown(
                    "<div style='background:rgba(255,0,127,0.1);padding:12px;border-radius:10px;"
                    "border-left:4px solid #ff007f;margin-top:10px;'>",
                    unsafe_allow_html=True
                )
                st.markdown(f"**🔧 {len(details)} تردد تم تحديثه من القاعدة الحية:**")
                for detail in details[:20]:
                    st.markdown(f"<span style='color:#ff007f;font-size:0.85rem;'>{detail}</span>",
                                unsafe_allow_html=True)
                if len(details) > 20:
                    st.markdown(f"<span style='color:#888;'>... و {len(details)-20} تردد آخر</span>",
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#888;margin-top:10px;'>ℹ️ جميع الترددات الحالية مطابقة لأحدث نسخة.</div>",
                            unsafe_allow_html=True)

    st.write("---")

    channels_to_sort     = []
    report_changes       = []
    existing_names_upper = set()

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

    st.markdown("### 🔍 البحث عن قناة داخل الملف:")
    search_query = st.text_input("", placeholder="اكتب اسم القناة هنا...", key="p1_search").strip().upper()
    if search_query:
        results = [
            {"الرقم": idx, "اسم القناة": ch["name"],
             "الفئة": ai_classify(ch["name"]), "التردد": ch["freq"]}
            for idx, ch in enumerate(channels_to_sort, 1)
            if search_query in ch["name"].upper()
        ]
        st.table(results) if results else st.warning("⚠️ لا توجد نتائج مطابقة.")

    st.write("---")
    st.markdown("### 🎛️ ترتيب الفئات:")
    user_priority = st.multiselect("اختر الفئات بالترتيب المطلوب:",
                                   options=ALL_AVAILABLE_CATEGORIES, default=[])
    final_priority = list(user_priority)
    for cat in ALL_AVAILABLE_CATEGORIES:
        if cat not in final_priority:
            final_priority.append(cat)

    channels_sorted = sorted(channels_to_sort,
                             key=lambda x: final_priority.index(ai_classify(x["name"])))

    categorized = {}
    for ch in channels_sorted:
        categorized.setdefault(ai_classify(ch["name"]), []).append(ch["name"])

    st.write("---")
    st.markdown("### 📊 معاينة التوزيع الحالي:")
    col1, col2 = st.columns(2)
    for i, cat_name in enumerate(final_priority):
        if cat_name in categorized:
            ch_list = categorized[cat_name]
            star    = "⭐ " if cat_name in user_priority else ""
            title   = f"{star}{cat_name} — ({len(ch_list)} قناة)"
            with (col1 if i % 2 == 0 else col2):
                with st.expander(title):
                    st.write(", ".join(ch_list))

    if report_changes:
        st.write("---")
        st.markdown("### 🔁 التعديلات")
        st.table(report_changes)

    text_report  = f"📄 تقرير ترتيب القنوات النهائي ({model_name})\n" + "=" * 50 + "\n"
    text_report += "🛠️ ترتيب الفئات المختار: " + " -> ".join(final_priority) + "\n" + "=" * 50 + "\n\n"

    if is_modern:
        final_list_modern = []
        for index, ch in enumerate(channels_sorted, start=1):
            node = normalize_modern_node(ch["node_data"], index)
            final_list_modern.append(node)
            text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}"
            text_report += " [NEW]\n" if ch["is_injected"] else "\n"

        broadcast_data["channelList"] = final_list_modern
        legacy_broadcast_tag.text = json.dumps(broadcast_data, ensure_ascii=False, separators=(',', ':'))

        # ─── الإصلاح الجوهري: الحفاظ على بنية الـ XML الأصلية ───
        final_xml_bytes = build_final_xml_bytes(root, original_file_text)

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

        if start_idx != -1:
            final_text_output = file_text[:start_idx] + combined_items_str + file_text[end_idx:]
        else:
            final_text_output = combined_items_str

        # ─── الإصلاح الجوهري: الحفاظ على نفس الـ encoding بدون إعادة parse ───
        try:
            final_xml_bytes = final_text_output.encode('utf-8')
        except UnicodeEncodeError:
            final_xml_bytes = final_text_output.encode('latin-1')

    st.write("---")
    st.success("✅ تم تجهيز الملف النهائي للتحميل:")

    col_d1, col_d2, col_d3 = st.columns([2, 2, 1])
    with col_d1:
        st.download_button(label="📥 تحميل ملف الشاشة النهائي (GlobalClone00001.TLL)",
                           data=final_xml_bytes,
                           file_name="GlobalClone00001.TLL",
                           mime="application/octet-stream", use_container_width=True)
    with col_d2:
        st.download_button(label="📄 تحميل تقرير الترتيب (Channels_List.txt)",
                           data=text_report,
                           file_name="Channels_List.txt",
                           mime="text/plain; charset=utf-8", use_container_width=True)
    with col_d3:
        if st.button("🔄 إعادة تهيئة / رفع ملف جديد", key="reset_bottom", use_container_width=True):
            keep = {'live_db_cache', 'live_db_last_fetch'}
            new_key = st.session_state.get('p1_uploader_key', 0) + 1
            for k in list(st.session_state.keys()):
                if k not in keep:
                    del st.session_state[k]
            st.session_state.p1_uploader_key = new_key
            st.rerun()

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
Done
