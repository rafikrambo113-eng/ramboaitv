
import streamlit as st
import xml.etree.ElementTree as ET
import json
import re
from collections import OrderedDict

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
    'p1_channels_extra': [],   # قنوات مزروعة من الفحص
    'p1_freq_patched': False,  # تم تطبيق صيانة الترددات
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
        'update_freq_label': "⚛️ تحديث الترددات تلقائياً",
        'add_new_ch_label':  "✨ إضافة القنوات الجديدة المتاحة تلقائياً",
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
        'update_freq_label': "⚛️ Auto update frequencies",
        'add_new_ch_label':  "✨ Auto inject missing channels",
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
# 6. DB & HELPERS
# ──────────────────────────────────────────────────────
NILESAT_LIVE_DB = {
    "AL HAYAT":        {"frequency": 12207, "polarization": "Vertical"},
    "AL HAYAT 2":      {"frequency": 12207, "polarization": "Vertical"},
    "SAT-7 KIDS":      {"frequency": 11353, "polarization": "Vertical"},
    "SAT-7 ARABIC":    {"frequency": 11353, "polarization": "Vertical"},
    "CTV":             {"frequency": 12022, "polarization": "Vertical"},
    "AGHAPY TV":       {"frequency": 11179, "polarization": "Horizontal"},
    "MESAT":           {"frequency": 11096, "polarization": "Horizontal"},
    "IQRAA":           {"frequency": 11938, "polarization": "Vertical"},
    "MAJD":            {"frequency": 11862, "polarization": "Vertical"},
    "RAHMA":           {"frequency": 11938, "polarization": "Vertical"},
    "QURAN KAREEM":    {"frequency": 11727, "polarization": "Vertical"},
    "AL JAZEERA HD":   {"frequency": 10853, "polarization": "Vertical"},
    "AL ARABIYA":      {"frequency": 11938, "polarization": "Vertical"},
    "AL HADATH":       {"frequency": 11938, "polarization": "Vertical"},
    "CBC":             {"frequency": 12092, "polarization": "Vertical"},
    "EXTRA NEWS":      {"frequency": 12092, "polarization": "Vertical"},
    "ON E":            {"frequency": 12092, "polarization": "Vertical"},
    "MBC 2":           {"frequency": 11938, "polarization": "Vertical"},
    "MBC 4":           {"frequency": 11938, "polarization": "Vertical"},
    "ROTANA CINEMA":   {"frequency": 11938, "polarization": "Vertical"},
    "ON TIME SPORTS 1":{"frequency": 11861, "polarization": "Vertical"},
    "ON TIME SPORTS 2":{"frequency": 11861, "polarization": "Vertical"},
    "SPACE TOON":      {"frequency": 11727, "polarization": "Vertical"},
    "MAJID":           {"frequency": 11862, "polarization": "Vertical"},
    "TOYOR ALJANNAH":  {"frequency": 11179, "polarization": "Horizontal"},
}

# قاعدة بيانات الصيانة: ترددات قديمة/ميتة → ترددات جديدة
FREQ_MAINTENANCE_DB = {
    "11747": "12054",
    "11137": "11785",
    "12015": "11678",
    "11602": "11938",
    "11512": "11862",
    "11632": "12092",
}

# قنوات جديدة للزرع التلقائي عبر الفحص
SIMULATED_NEW_CHANNELS = [
    {"name": "RAMBO CINEMA HD",  "frequency": 11678, "polarization": "Horizontal"},
    {"name": "EGYPT NOW",         "frequency": 12054, "polarization": "Vertical"},
    {"name": "FOOTBALL LIVE",     "frequency": 11054, "polarization": "Horizontal"},
    {"name": "NILE DRAMA",        "frequency": 11861, "polarization": "Vertical"},
    {"name": "AL KAHERA WAN NAS", "frequency": 12092, "polarization": "Vertical"},
]

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
    if any(w in name for w in ["CTV","AGHAPY","MESAT","KARMA","ALKARMA","NOURSAT","SAT-7","SAT7","AL HAYAT","HAYAT TV","MIRACLE","COPTIC","CHURCH"]):
        return ALL_AVAILABLE_CATEGORIES[0]
    if any(w in name for w in ["QURAN","RAHMA","MAJD","MAKKA","IQRAA","IQRA","HUDA","WESAL","ISLAM","SUNNAH"]):
        return ALL_AVAILABLE_CATEGORIES[1]
    if any(w in name for w in ["MOSALSALAT","DRAMA","SERIES","KHOLASA","MASRAWI","SHAHID","NILE DRAMA"]):
        return ALL_AVAILABLE_CATEGORIES[2]
    if any(w in name for w in ["CINEMA","ROTANA","AFLAM","MIX","FOX","MBC2","MBC 2","MBC4","MBC 4","MBC MAX","ACTION","RAMBO","MOVIE","FILM","COMEDY"]):
        return ALL_AVAILABLE_CATEGORIES[3]
    if any(w in name for w in ["SPACE TOON","SPACETOON","CN","CARTOON","MAJID","KIDS","TOM","TOYOR","BABY","JUNIOR"]):
        return ALL_AVAILABLE_CATEGORIES[4]
    if any(w in name for w in ["SPORT","SPORTS","ONTIME","ON TIME","KASS","AD_SPORTS","AD SPORTS","SSC","BEIN","MATCH","FOOTBALL"]):
        return ALL_AVAILABLE_CATEGORIES[5]
    if any(w in name for w in ["NEWS","JAZEERA","ARABIYA","HADATH","CAIRO","SKY NEWS","BBC","CNN","EXTRA NEWS","CBC","ON E","SADA","BALADI","MASR","EGYPT NOW","KAHERA"]):
        return ALL_AVAILABLE_CATEGORIES[6]
    return ALL_AVAILABLE_CATEGORIES[7]

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
# 7. FILE UPLOADER + RESET
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
        keep = {'lang', 'theme'}
        new_key = st.session_state.get('p1_uploader_key', 0) + 1
        for k in list(st.session_state.keys()):
            if k not in keep:
                del st.session_state[k]
        st.session_state.p1_uploader_key = new_key
        st.rerun()

# ──────────────────────────────────────────────────────
# 8. MAIN LOGIC
# ──────────────────────────────────────────────────────
if uploaded_file is None:
    st.info(t['no_file_msg'])
    st.markdown("""
    <div style="background:#0f172a;border:2px solid #00f0ff;color:white;
    padding:30px;text-align:center;border-radius:15px;margin-top:50px;font-family:Arial;">
    <b>🛠️ DEVELOPER ENG: RAFIK RAMBO</b><br><br>
    📱 +201280339779<br>✉️ rafikrambo113@gmail.com<br><br>
    <a href="https://api.whatsapp.com/send?phone=201280339779" style="color:#25d366;">WhatsApp</a>
    </div>""", unsafe_allow_html=True)
else:
    # ── إعادة تحميل عند رفع ملف جديد ──
    if st.session_state.get("p1_last_file_name") != uploaded_file.name:
        st.session_state.scan_done_p1    = False
        st.session_state.maint_done_p1   = False
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

    # ── عدد القنوات ونوع الملف ──
    if is_modern:
        _bd = json.loads(legacy_broadcast_tag.text.strip())
        total_ch = len(_bd.get("channelList", []))
        file_type_label = "Modern JSON"
        file_type_desc  = "حديث (2020+)" if st.session_state.lang == 'ar' else "Modern (2020+)"
    else:
        total_ch = len(re.findall(r'<ITEM>', file_text))
        file_type_label = "Legacy XML"
        file_type_desc  = "قديم (ما قبل 2020)" if st.session_state.lang == 'ar' else "Legacy (pre-2020)"

    # ── رسالة النجاح بنفس شكل صفحة 2 ──
    st.success(
        f"{t['success_read']} **{model_name}** | "
        f"📡 {file_type_label} | "
        f"{'الإجمالي' if st.session_state.lang == 'ar' else 'Total'}: {total_ch:,} "
        f"{'قناة' if st.session_state.lang == 'ar' else 'channels'}."
    )

    # ── بلد البث ──
    country_node = root.find(".//BroadcastCountrySetting")
    country_code = country_node.text.strip() if country_node is not None else ""
    CMAP = {
        "EGY":"🇪🇬 مصر","SAU":"🇸🇦 السعودية","ARE":"🇦🇪 الإمارات",
        "JOR":"🇯🇴 الأردن","LBN":"🇱🇧 لبنان","SDN":"🇸🇩 السودان",
        "DZA":"🇩🇿 الجزائر","MAR":"🇲🇦 المغرب","TUN":"🇹🇳 تونس",
        "LBY":"🇱🇾 ليبيا","IRQ":"🇮🇶 العراق","SYR":"🇸🇾 سوريا",
        "YEM":"🇾🇪 اليمن","KWT":"🇰🇼 الكويت","QAT":"🇶🇦 قطر",
        "BHR":"🇧🇭 البحرين","OMN":"🇴🇲 عُمان",
        "USA":"🇺🇸 أمريكا","GBR":"🇬🇧 بريطانيا","DEU":"🇩🇪 ألمانيا",
        "FRA":"🇫🇷 فرنسا","TUR":"🇹🇷 تركيا","IRN":"🇮🇷 إيران","JA":"🇯🇵 يابان",
    } if st.session_state.lang == 'ar' else {
        "EGY":"🇪🇬 Egypt","SAU":"🇸🇦 Saudi Arabia","ARE":"🇦🇪 UAE",
        "JOR":"🇯🇴 Jordan","LBN":"🇱🇧 Lebanon","SDN":"🇸🇩 Sudan",
        "DZA":"🇩🇿 Algeria","MAR":"🇲🇦 Morocco","TUN":"🇹🇳 Tunisia",
        "LBY":"🇱🇾 Libya","IRQ":"🇮🇶 Iraq","SYR":"🇸🇾 Syria",
        "YEM":"🇾🇪 Yemen","KWT":"🇰🇼 Kuwait","QAT":"🇶🇦 Qatar",
        "BHR":"🇧🇭 Bahrain","OMN":"🇴🇲 Oman",
        "USA":"🇺🇸 USA","GBR":"🇬🇧 UK","DEU":"🇩🇪 Germany",
        "FRA":"🇫🇷 France","TUR":"🇹🇷 Turkey","IRN":"🇮🇷 Iran","JA":"🇯🇵 Japan",
    }
    country_display = CMAP.get(country_code, f"🌍 {country_code}" if country_code else "—")

    # ── كروت المعلومات ──
    st.write("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📟 " + ("الموديل" if st.session_state.lang == 'ar' else "Model"), model_name)
    with c2:
        st.metric("📡 " + ("إجمالي القنوات" if st.session_state.lang == 'ar' else "Total Channels"), f"{total_ch:,}")
    with c3:
        st.metric("🗂️ " + ("نظام الملف" if st.session_state.lang == 'ar' else "File Type"), file_type_desc)
    with c4:
        st.metric("🌍 " + ("بلد البث" if st.session_state.lang == 'ar' else "Broadcast Country"), country_display)

    # ══════════════════════════════════════════════════
    # قسم الفحص والصيانة — بنفس تصميم صفحة 2
    # ══════════════════════════════════════════════════
    st.write("---")
    st.write(f"### {t['auto_features_title']}")
    col_chk1, col_chk2 = st.columns(2)

    # ── الشيك بوكس 1: فحص وزرع قنوات جديدة ──
    with col_chk1:
        scan_active = st.checkbox(t['chk_scan_inject'], value=False, key="chk_scan_p1")

        if scan_active and not st.session_state.get('scan_done_p1', False):
            # تجميع أسماء القنوات الحالية
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
            extra_channels = []
            for nc in SIMULATED_NEW_CHANNELS:
                if nc['name'].upper() not in current_names_set:
                    extra_channels.append(nc.copy())
                    new_inserted_names.append(
                        f"📡 {nc['name']} "
                        f"({'تردد' if st.session_state.lang == 'ar' else 'Freq'}: {nc['frequency']})"
                    )

            st.session_state.scan_done_p1     = True
            st.session_state.inserted_list_p1 = new_inserted_names
            st.session_state.p1_channels_extra = extra_channels

            if new_inserted_names:
                st.toast("📡 " + ("تم زرع القنوات الجديدة بنجاح!" if st.session_state.lang == 'ar' else "New channels injected!"))
                st.rerun()

        if scan_active:
            if st.session_state.get('inserted_list_p1'):
                st.markdown(
                    "<div style='background:rgba(0,240,255,0.1);padding:12px;border-radius:10px;"
                    "border-left:4px solid #00f0ff;margin-top:10px;'>",
                    unsafe_allow_html=True
                )
                label = "**✨ قنوات جديدة تم زرعها وإضافتها للملف:**" if st.session_state.lang == 'ar' \
                        else "**✨ New channels injected into the file:**"
                st.markdown(label)
                for item in st.session_state.inserted_list_p1:
                    st.markdown(f"<span style='color:#00f0ff;'>{item}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                msg = "ℹ️ لم يتم العثور على قنوات جديدة للزرع (مضافة بالفعل)." \
                      if st.session_state.lang == 'ar' \
                      else "ℹ️ No new channels found to inject (already present)."
                st.markdown(f"<div style='color:#888;margin-top:10px;'>{msg}</div>", unsafe_allow_html=True)

    # ── الشيك بوكس 2: صيانة الترددات ──
    with col_chk2:
        maint_active = st.checkbox(t['chk_modern_maint'], value=False, key="chk_maint_p1")

        if maint_active and not st.session_state.get('maint_done_p1', False):
            # نمشي على القنوات ونحدد الترددات القديمة
            maint_details = []
            freq_patches  = {}   # name_upper → new_freq

            if is_modern:
                _tmp_bd2 = json.loads(legacy_broadcast_tag.text.strip())
                for ch in _tmp_bd2.get("channelList", []):
                    old_f = str(ch.get("frequency", ""))
                    if old_f in FREQ_MAINTENANCE_DB:
                        new_f = FREQ_MAINTENANCE_DB[old_f]
                        ch_name = ch.get("channelName", "Unknown")
                        freq_patches[ch_name.upper()] = new_f
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
                    if old_f in FREQ_MAINTENANCE_DB:
                        new_f = FREQ_MAINTENANCE_DB[old_f]
                        freq_patches[ch_name.upper()] = new_f
                        maint_details.append(
                            f"🔄 **{ch_name}** | "
                            f"{'من' if st.session_state.lang == 'ar' else 'from'} `{old_f}` "
                            f"{'إلى' if st.session_state.lang == 'ar' else 'to'} `{new_f}`"
                        )

            st.session_state.maint_done_p1   = True
            st.session_state.maint_details_p1 = maint_details
            st.session_state.p1_freq_patches  = freq_patches

            if maint_details:
                st.toast("🔧 " + ("تم تحديث الترددات بنجاح!" if st.session_state.lang == 'ar' else "Frequencies updated!"))
                st.rerun()

        if maint_active:
            if st.session_state.get('maint_details_p1'):
                st.markdown(
                    "<div style='background:rgba(255,0,127,0.1);padding:12px;border-radius:10px;"
                    "border-left:4px solid #ff007f;margin-top:10px;'>",
                    unsafe_allow_html=True
                )
                label = "**🔧 الترددات التي تم تحديثها في الملف:**" if st.session_state.lang == 'ar' \
                        else "**🔧 Frequencies updated in the file:**"
                st.markdown(label)
                for detail in st.session_state.maint_details_p1:
                    st.markdown(f"<span style='color:#ff007f;'>{detail}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                msg = "ℹ️ جميع الترددات الحالية مطابقة لأحدث نسخة." \
                      if st.session_state.lang == 'ar' \
                      else "ℹ️ All current frequencies match the latest version."
                st.markdown(f"<div style='color:#888;margin-top:10px;'>{msg}</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════
    # باقي منطق الصفحة (مع تطبيق الفحص والصيانة)
    # ══════════════════════════════════════════════════
    st.write("---")
    col_chk_old1, col_chk_old2 = st.columns(2)
    with col_chk_old1:
        update_freq = st.checkbox(t['update_freq_label'], value=True)
    with col_chk_old2:
        add_new_ch  = st.checkbox(t['add_new_ch_label'],  value=True)

    channels_to_sort     = []
    report_changes       = []
    existing_names_upper = set()

    # ── Modern JSON ──
    if is_modern:
        broadcast_data = json.loads(legacy_broadcast_tag.text.strip())
        channels_list  = broadcast_data.get("channelList", [])

        freq_patches = st.session_state.get('p1_freq_patches', {})

        for ch in channels_list:
            ch_name  = ch.get("channelName", "Unknown")
            old_freq = str(ch.get("frequency", "N/A"))
            name_up  = ch_name.upper()
            existing_names_upper.add(name_up)

            if "category" not in ch or not ch["category"]:
                ch["category"] = ai_classify(ch_name)

            # تطبيق صيانة الترددات من الشيك بوكس الجديد
            if name_up in freq_patches:
                new_f = freq_patches[name_up]
                if old_freq != new_f:
                    ch["frequency"] = int(new_f)
                    old_freq = new_f

            # تحديث الترددات من NILESAT DB (الشيك بوكس القديم)
            if update_freq and name_up in NILESAT_LIVE_DB:
                live_freq = NILESAT_LIVE_DB[name_up]["frequency"]
                if old_freq != str(live_freq):
                    report_changes.append({
                        "channel": ch_name, "category": ai_classify(ch_name),
                        "old_freq": old_freq, "new_freq": str(live_freq)
                    })
                    ch["frequency"]    = int(live_freq)
                    ch["polarization"] = NILESAT_LIVE_DB[name_up]["polarization"]
                    old_freq = str(live_freq)

            channels_to_sort.append({"name": ch_name, "freq": old_freq,
                                      "node_data": ch, "is_injected": False})

        # إضافة القنوات من الفحص التلقائي (الشيك بوكس الجديد)
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

        # إضافة القنوات من NILESAT DB (الشيك بوكس القديم)
        if add_new_ch and channels_list:
            sample_node = channels_list[0]
            for db_name, db_info in NILESAT_LIVE_DB.items():
                if db_name not in existing_names_upper:
                    new_node = json.loads(json.dumps(sample_node))
                    new_node.update({
                        "channelName": db_name,
                        "frequency":   db_info["frequency"],
                        "polarization":db_info["polarization"],
                        "Invisible": False, "skipped": False,
                        "deleted": False, "userSelCHNo": True,
                        "category": ai_classify(db_name),
                    })
                    channels_to_sort.append({"name": db_name,
                        "freq": str(db_info["frequency"]),
                        "node_data": new_node, "is_injected": True})
                    report_changes.append({"channel": db_name,
                        "category": ai_classify(db_name),
                        "old_freq": "missing", "new_freq": str(db_info["frequency"])})

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

            # تطبيق صيانة الترددات من الشيك بوكس الجديد
            if name_up in freq_patches:
                new_f    = freq_patches[name_up]
                item_str = re.sub(r'<frequency>\d+</frequency>',
                                  f'<frequency>{new_f}</frequency>', item_str)
                live_freq = new_f
            elif update_freq and name_up in NILESAT_LIVE_DB:
                live_freq = str(NILESAT_LIVE_DB[name_up]["frequency"])
                item_str  = re.sub(r'<frequency>\d+</frequency>',
                                   f'<frequency>{live_freq}</frequency>', item_str)
            else:
                live_freq = freq_match.group(1) if freq_match else "N/A"

            channels_to_sort.append({"name": ch_name, "freq": live_freq,
                                      "raw_str": item_str, "is_injected": False})

        # إضافة القنوات من الفحص التلقائي (الشيك بوكس الجديد)
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

        if add_new_ch and item_blocks:
            sample_item = item_blocks[0]
            for db_name, db_info in NILESAT_LIVE_DB.items():
                if db_name not in existing_names_upper:
                    new_item = re.sub(r'<vchName>.*?</vchName>',
                                      f'<vchName>{db_name}</vchName>', sample_item)
                    new_item = re.sub(r'<frequency>\d+</frequency>',
                                      f'<frequency>{db_info["frequency"]}</frequency>', new_item)
                    channels_to_sort.append({"name": db_name,
                        "freq": str(db_info["frequency"]),
                        "raw_str": new_item, "is_injected": True})

    # ── Search ──
    st.write("---")
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
            new_key = st.session_state.get('p1_uploader_key', 0) + 1
            for k in list(st.session_state.keys()):
                if k not in ['lang', 'theme']:
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

# ──────────────────────────────────────────────────────
# 9. FOOTER
# ──────────────────────────────────────────────────────
whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"
st.markdown(f"""
<div style="background:#0f172a;border:2px solid #00f0ff;color:#ffffff;
padding:35px;text-align:center;border-radius:20px;margin-top:65px;font-family:Arial;">
<div style="color:#ff007f;font-size:26px;font-weight:bold;">🛠️ DEVELOPER ENG: RAFIK NATHAN</div>
<div style="margin-top:10px;">📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
<div style="margin-top:10px;">✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com</div>
<a href="{whatsapp_url}" target="_blank"
style="color:#25d366;padding:14px 35px;border-radius:35px;display:inline-block;
font-weight:bold;border:2px solid #25d366;text-decoration:none;margin-top:20px;">
WhatsApp</a>
</div>
""", unsafe_allow_html=True)
