import streamlit as st
import xml.etree.ElementTree as ET
import json
import re
import requests
from datetime import datetime

# ─────────────────────────────────────────────
# 1. تهيئة الجلسة (Session State)
# ─────────────────────────────────────────────
defaults = {
    'lang': 'ar',
    'theme': 'dark',
    'channels': [],
    'ordered_channels': [],
    'is_modern': False,
    'root': None,
    'broadcast_data': None,
    'file_text_original': "",
    'model_name': "",
    'edit_finished': False,
    'p2_uploader_key': 0,
    'live_db_cache': None,
    'live_db_last_fetch': None,
    'scan_done_p2': False,
    'maint_done_p2': False,
    'inserted_list_p2': [],
    'maint_details_p2': [],
    'p2_freq_patches': {},
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────
# 2. قواميس النصوص (عربي / إنجليزي)
# ─────────────────────────────────────────────
UI = {
    'ar': {
        'title':                "📺 RAMBO — المُرتب اليدوي المطور",
        'subtitle':             "⚡ نظام الترتيب الذكي المستقل: اضغط زرع، عدل أرقامك، ثم اضغط حفظ التعديلات",
        'upload_label':         "🚀 ارفع ملف القنوات (GlobalClone00001.TLL):",
        'success_read':         "🛸 تم قراءة الملف بنجاح! الموديل: ",
        'search_ph':            "🔍 ابحث عن قناة بالاسم في الملف الأصلي...",
        'all_ch_title':         "📋 1. جدول القنوات الكلي المتوفرة",
        'ordered_title':        "📊 2. جدول الترتيب النهائي (اكتب أرقام الترتيب هنا واضغط حفظ بالأسفل)",
        'col_action':           "إجراء",
        'btn_add_to_order':     "➕ زرع",
        'auto_features_title':  "⚙️ خيارات الفحص الذكي والصيانة الفورية للملف",
        'chk_scan_inject':      "📡 تفعيل الفحص التلقائي وزرع القنوات الجديدة المتاحة على القمر فوراً",
        'chk_modern_maint':     "🔧 تفعيل الصيانة الحديثة وتحديث الترددات الميتة والقديمة تلقائياً",
        'btn_fetch_live':       "🌐 جلب أحدث بيانات NileSat من الإنترنت الآن",
        'fetching':             "⏳ جاري الجلب من dthsat.com ...",
        'fetch_success':        "✅ تم جلب بيانات NileSat الحية! إجمالي القنوات: ",
        'fetch_fail':           "⚠️ تعذّر الاتصال بـ dthsat.com، سيتم استخدام القاعدة المحلية.",
        'preview_title':        "🏁 استخراج وتنزيل الملفات النهائية",
        'btn_tll':              "📥 تحميل ملف الشاشة المعدل (GlobalClone00001.TLL)",
        'btn_txt':              "📄 تحميل تقرير لستة الترتيب (Channels_List.txt)",
        'txt_header':           "📄 تقرير الترتيب اليدوي المطور — RAMBO Page 2",
        'no_file':              "⬆️ ارفع ملف TLL أولاً لتبدأ العمل.",
        'btn_reset':            "🔄 إعادة ترتيب ملف جديد",
        'ready_msg':            "🌌 تم اعتماد الترتيب الجديد وعمل التقرير بنجاح! الملفات جاهزة الآن:",
    },
    'en': {
        'title':                "📺 RAMBO — Advanced Manual Sorter",
        'subtitle':             "⚡ Stable Smart Sorting System: Inject, edit order numbers, then click Save",
        'upload_label':         "🚀 Upload Channel File (GlobalClone00001.TLL):",
        'success_read':         "🛸 File Parsed Successfully! Model: ",
        'search_ph':            "🔍 Search channel name in original pool...",
        'all_ch_title':         "📋 1. All Available Channels",
        'ordered_title':        "📊 2. Final Custom List (Change numbers then click save below)",
        'col_action':           "Action",
        'btn_add_to_order':     "➕ Inject",
        'auto_features_title':  "⚙️ Smart Auto-Maintenance & Scanning Options",
        'chk_scan_inject':      "📡 Enable Auto-Scan & Inject newly available Satellite Channels",
        'chk_modern_maint':     "🔧 Enable Modern Maintenance & Auto-Update dead frequencies",
        'btn_fetch_live':       "🌐 Fetch Latest NileSat Data from Internet Now",
        'fetching':             "⏳ Fetching from dthsat.com ...",
        'fetch_success':        "✅ Live NileSat data fetched! Total channels: ",
        'fetch_fail':           "⚠️ Could not reach dthsat.com, using local database.",
        'preview_title':        "🏁 Export & Download Final Files",
        'btn_tll':              "📥 Download TV File (GlobalClone00001.TLL)",
        'btn_txt':              "📄 Download Sorted List Report (Channels_List.txt)",
        'txt_header':           "📄 Manual Sorting Advanced Report — RAMBO Page 2",
        'no_file':              "⬆️ Upload a TLL file to start.",
        'btn_reset':            "🔄 Reset Page",
        'ready_msg':            "🌌 Sorting completed & report generated! Ready for download:",
    }
}

t = UI[st.session_state.lang]

# ─────────────────────────────────────────────
# 3. إعداد الصفحة والـ CSS
# ─────────────────────────────────────────────
st.set_page_config(page_title="RAMBO P2 — Advanced Sorter", page_icon="🎛️", layout="wide")

if st.session_state.theme == 'dark':
    bg_style      = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)"
    text_color    = "#00f0ff"
    box_bg        = "rgba(13,7,33,0.85)"
    box_border    = "#00f0ff"
    box_shadow    = "rgba(0,240,255,0.35)"
    text_shadow   = "0 0 5px rgba(0,240,255,0.4)"
    table_head_bg = "#0d0722"
else:
    bg_style      = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
    text_color    = "#0d0722"
    box_bg        = "#ffffff"
    box_border    = "#ff007f"
    box_shadow    = "rgba(255,0,127,0.15)"
    text_shadow   = "none"
    table_head_bg = "#0d0722"

font_family = "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
.main {{ background: {bg_style} !important; color: {text_color} !important; font-family: {font_family}; }}
h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.4) !important;
      text-align: center; font-weight: 900; margin-top: 5px; }}
h3, p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] p {{
    color: {text_color} !important; text-shadow: {text_shadow}; }}
.stTextInput>div>div>input, .stNumberInput>div>div>input {{
    background-color: {box_bg} !important; color: {text_color} !important;
    border: 2px solid {box_border} !important; border-radius: 10px !important; }}
div[data-testid="stFileUploader"] {{
    background: {box_bg} !important; border: 2px solid {box_border} !important;
    box-shadow: 0px 5px 15px {box_shadow} !important; border-radius: 14px !important;
    padding: 18px !important; margin-bottom: 20px !important; }}
.stButton>button {{
    background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
    color: #ffffff !important; border: 2px solid #ff007f !important;
    border-radius: 12px !important; font-weight: bold; width: 100%; }}
.stDownloadButton>button {{
    background: linear-gradient(135deg, #00b894 0%, #00695c 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; font-weight: bold; width: 100%; }}
.live-badge {{
    display: inline-block; background: linear-gradient(90deg,#00f0ff22,#ff007f22);
    border: 1px solid #00f0ff; border-radius: 8px; padding: 6px 14px;
    color: #00f0ff; font-size: 0.85rem; margin-bottom: 10px; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4. Header Controls
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# 5. قاعدة البيانات الاحتياطية + Fetcher
# ─────────────────────────────────────────────
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
    "DOHAT ALQURAN TV":    {"frequency": 10727, "polarization": "Horizontal"},
    "AL JAZEERA HD":       {"frequency": 10853, "polarization": "Horizontal"},
    "AL ARABIYA":          {"frequency": 11938, "polarization": "Vertical"},
    "AL HADATH":           {"frequency": 11938, "polarization": "Vertical"},
    "ECHOROUK TV":         {"frequency": 10922, "polarization": "Vertical"},
    "ECHOROUK TV NEWS":    {"frequency": 10922, "polarization": "Vertical"},
    "CBC":                 {"frequency": 12092, "polarization": "Vertical"},
    "EXTRA NEWS":          {"frequency": 12092, "polarization": "Vertical"},
    "ON E":                {"frequency": 12092, "polarization": "Vertical"},
    "MBC 2":               {"frequency": 11938, "polarization": "Vertical"},
    "MBC 4":               {"frequency": 11938, "polarization": "Vertical"},
    "ROTANA CINEMA":       {"frequency": 11938, "polarization": "Vertical"},
    "ON TIME SPORTS 1":    {"frequency": 11861, "polarization": "Vertical"},
    "ON TIME SPORTS 2":    {"frequency": 11861, "polarization": "Vertical"},
    "SPACE TOON":          {"frequency": 11727, "polarization": "Vertical"},
    "BATOOT KIDS":         {"frequency": 10853, "polarization": "Horizontal"},
    "KARAMEESH":           {"frequency": 10815, "polarization": "Horizontal"},
    "TOYOR ALJANNAH":      {"frequency": 11179, "polarization": "Horizontal"},
    "NOURSAT":             {"frequency": 10815, "polarization": "Horizontal"},
    "ALKARMA TV FAMILY":   {"frequency": 10815, "polarization": "Horizontal"},
    "MIRACLE CHANNEL":     {"frequency": 10815, "polarization": "Horizontal"},
    "ALHURRA TV":          {"frequency": 11258, "polarization": "Horizontal"},
    "SYRIA TV":            {"frequency": 11258, "polarization": "Horizontal"},
    "PALESTINE TV":        {"frequency": 10727, "polarization": "Horizontal"},
    "QATAR TV":            {"frequency": 10834, "polarization": "Vertical"},
    "QATAR TV 2":          {"frequency": 10834, "polarization": "Vertical"},
    "AL ASSEMA":           {"frequency": 10853, "polarization": "Horizontal"},
    "DRAMA 1":             {"frequency": 10853, "polarization": "Horizontal"},
    "FAMILY DRAMA":        {"frequency": 10873, "polarization": "Vertical"},
    "4G AFLAM":            {"frequency": 10853, "polarization": "Horizontal"},
    "4G CINEMA":           {"frequency": 10853, "polarization": "Horizontal"},
    "4G DRAMA":            {"frequency": 10853, "polarization": "Horizontal"},
    "TOP MOVIES (EGYPT)":  {"frequency": 10873, "polarization": "Vertical"},
    "SAMIRA TV":           {"frequency": 10922, "polarization": "Vertical"},
    "ENNAHAR TV":          {"frequency": 10922, "polarization": "Vertical"},
    "WATANIA 1":           {"frequency": 10873, "polarization": "Vertical"},
    "LIBYA AL-AHRAR TV":   {"frequency": 10815, "polarization": "Horizontal"},
    "EL HAYAT TV":         {"frequency": 10922, "polarization": "Vertical"},
    "MISR TV":             {"frequency": 10727, "polarization": "Horizontal"},
    "AJMAN TV":            {"frequency": 11258, "polarization": "Horizontal"},
    "ALSHARQIYA NEWS":     {"frequency": 10873, "polarization": "Vertical"},
    "DIJLAH TV":           {"frequency": 10873, "polarization": "Vertical"},
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


# ─────────────────────────────────────────────
# 6. زر جلب البيانات الحية
# ─────────────────────────────────────────────
col_fetch, col_fetch_status = st.columns([2, 4])
with col_fetch:
    if st.button(t['btn_fetch_live'], use_container_width=True):
        with st.spinner(t['fetching']):
            result = fetch_nilesat_live_db()
            if result:
                st.session_state.live_db_cache     = result
                st.session_state.live_db_last_fetch = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.scan_done_p2       = False
                st.session_state.maint_done_p2      = False
                st.session_state.inserted_list_p2   = []
                st.session_state.maint_details_p2   = []
                st.session_state.p2_freq_patches    = {}
                st.toast("🛸 " + (f"تم جلب {len(result):,} قناة من NileSat!" if st.session_state.lang == 'ar'
                                  else f"Fetched {len(result):,} channels!"))
                st.rerun()
            else:
                st.toast("⚠️ " + t['fetch_fail'], icon="⚠️")

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

# ─────────────────────────────────────────────
# 7. دوال مساعدة
# ─────────────────────────────────────────────
def reset_all_session_state():
    keys_to_keep = ['lang', 'theme', 'live_db_cache', 'live_db_last_fetch']
    for k in list(st.session_state.keys()):
        if k not in keys_to_keep:
            del st.session_state[k]
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def parse_tll(file_bytes):
    try:
        file_text = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        file_text = file_bytes.decode('latin-1')

    file_text_cleaned = re.sub(r'^\s+', '', file_text)
    root = ET.fromstring(file_text_cleaned.encode('utf-8'))
    legacy_tag = root.find(".//legacybroadcast")
    is_modern  = legacy_tag is not None and legacy_tag.text

    channels = []
    if is_modern:
        bdata = json.loads(legacy_tag.text)
        for idx, ch in enumerate(bdata.get("channelList", [])):
            channels.append({
                "id":       idx,
                "name":     ch.get("channelName", "Unknown"),
                "freq":     str(ch.get("frequency", "N/A")),
                "pol":      ch.get("polarization", "Vertical"),
                "raw_node": ch,
            })
        return channels, True, root, bdata, file_text, legacy_tag
    else:
        items = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)
        for idx, item_str in enumerate(items):
            nm = re.search(r'<vchName>(.*?)</vchName>', item_str)
            fq = re.search(r'<frequency>(.*?)</frequency>', item_str)
            channels.append({
                "id":      idx,
                "name":    nm.group(1) if nm else "Unknown",
                "freq":    fq.group(1) if fq else "N/A",
                "pol":     "Vertical",
                "raw_str": item_str,
            })
        return channels, False, root, None, file_text, None


# ─────────────────────────────────────────────
# 8. رفع الملف + زر إعادة التهيئة
# ─────────────────────────────────────────────
col_up, col_reset_top = st.columns([5, 1])
with col_up:
    uploaded = st.file_uploader(
        t['upload_label'], type=["TLL"],
        key=f"tll_uploader_p2_{st.session_state.p2_uploader_key}"
    )
with col_reset_top:
    st.write("")
    st.write("")
    if st.button(t['btn_reset'], key="reset_top_p2", use_container_width=True):
        new_key = st.session_state.get('p2_uploader_key', 0) + 1
        reset_all_session_state()
        st.session_state.p2_uploader_key = new_key
        st.rerun()

# ─────────────────────────────────────────────
# 9. معالجة الملف المرفوع
# ─────────────────────────────────────────────
if uploaded is not None:
    if st.session_state.get("last_file_name") != uploaded.name:
        for k in ['channels', 'ordered_channels', 'root', 'broadcast_data',
                  'file_text_original', 'model_name', 'edit_finished', 'is_modern',
                  'scan_done_p2', 'maint_done_p2', 'inserted_list_p2',
                  'maint_details_p2', 'p2_freq_patches']:
            st.session_state[k] = defaults.get(k, None) or ([] if 'list' in k or k in ['channels','ordered_channels'] else {})
        st.session_state.channels          = []
        st.session_state.ordered_channels  = []
        st.session_state.inserted_list_p2  = []
        st.session_state.maint_details_p2  = []
        st.session_state.p2_freq_patches   = {}

    st.session_state.last_file_name = uploaded.name

    if not st.session_state.channels:
        try:
            file_bytes = uploaded.read()
            (
                st.session_state.channels,
                st.session_state.is_modern,
                st.session_state.root,
                st.session_state.broadcast_data,
                st.session_state.file_text_original,
                st.session_state.legacy_tag,
            ) = parse_tll(file_bytes)

            model_node = st.session_state.root.find(".//ModelName")
            st.session_state.model_name    = model_node.text if model_node is not None else "LG TV Custom"
            st.session_state.ordered_channels = []
            st.session_state.edit_finished    = False
        except Exception as e:
            st.error(f"❌ خطأ في معالجة الملف: {e}")
            st.stop()

if not st.session_state.channels:
    st.info(t['no_file'])
    st.markdown("""
    <div style="background:#0f172a;border:2px solid #00f0ff;color:white;padding:30px;
    text-align:center;border-radius:15px;margin-top:50px;font-family:Arial;">
    <b></b><br><br>
    📱 <br>✉️ <br><br>
    <a href="" style="color:#25d366;">WhatsApp</a>
    </div>""", unsafe_allow_html=True)
    st.stop()

st.success(
    f"{t['success_read']} **{st.session_state.model_name}** | "
    f"📡 {'Modern JSON' if st.session_state.is_modern else 'Legacy XML'} | "
    f"{'الإجمالي' if st.session_state.lang == 'ar' else 'Total'}: {len(st.session_state.channels):,} "
    f"{'قناة' if st.session_state.lang == 'ar' else 'channels'}."
)

# ─────────────────────────────────────────────
# 10. خيارات الفحص والصيانة الذكية (من قاعدة البيانات الحية)
# ─────────────────────────────────────────────
st.write("---")
st.write(f"### {t['auto_features_title']}")

ACTIVE_DB = get_active_db()
col_chk1, col_chk2 = st.columns(2)

# ── فحص وزرع القنوات الجديدة ──
with col_chk1:
    scan_active = st.checkbox(t['chk_scan_inject'], value=False, key="chk_scan_p2")

    if scan_active and not st.session_state.get('scan_done_p2', False):
        current_names_set = {c.get('name', '').upper() for c in st.session_state.channels}
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
                    "name":        db_name_upper.title(),
                    "frequency":   db_info["frequency"],
                    "polarization": pol_full,
                }
                extra_channels.append(nc)
                new_inserted_names.append(
                    f"📡 {nc['name']} "
                    f"({'تردد' if st.session_state.lang == 'ar' else 'Freq'}: {nc['frequency']} {pol_full[0]})"
                )

        # إضافة القنوات الجديدة لقائمة الكل
        existing_upper = {c.get('name', '').upper() for c in st.session_state.channels}
        sample = st.session_state.channels[0] if st.session_state.channels else {}

        for nc in extra_channels:
            if nc['name'].upper() not in existing_upper:
                new_idx = len(st.session_state.channels)
                if st.session_state.is_modern:
                    raw_node = (sample.get('raw_node') or {}).copy()
                    raw_node.update({
                        "channelName":  nc['name'],
                        "frequency":    nc['frequency'],
                        "polarization": nc['polarization'],
                        "majorNumber":  new_idx + 1,
                        "Invisible": False, "skipped": False,
                        "deleted": False, "userSelCHNo": True,
                    })
                    st.session_state.channels.append({
                        "id": new_idx, "name": nc['name'],
                        "freq": str(nc['frequency']), "pol": nc['polarization'],
                        "raw_node": raw_node,
                    })
                else:
                    raw_str = (
                        f"<ITEM>\r\n<prNum>{new_idx+1}</prNum>\r\n"
                        f"<vchName>{nc['name']}</vchName>\r\n"
                        f"<frequency>{nc['frequency']}</frequency>\r\n</ITEM>"
                    )
                    st.session_state.channels.append({
                        "id": new_idx, "name": nc['name'],
                        "freq": str(nc['frequency']), "pol": nc['polarization'],
                        "raw_str": raw_str,
                    })
                existing_upper.add(nc['name'].upper())

        st.session_state.scan_done_p2     = True
        st.session_state.inserted_list_p2 = new_inserted_names

        if new_inserted_names:
            st.toast("📡 " + ("تم زرع القنوات الجديدة في جدول المتوفر!" if st.session_state.lang == 'ar'
                              else "New channels injected into the pool!"))
            st.rerun()

    if scan_active:
        if st.session_state.get('inserted_list_p2'):
            injected = st.session_state.inserted_list_p2
            st.markdown(
                "<div style='background:rgba(0,240,255,0.1);padding:12px;border-radius:10px;"
                "border-left:4px solid #00f0ff;margin-top:10px;'>",
                unsafe_allow_html=True
            )
            label = (f"**✨ {len(injected)} قناة جديدة تم زرعها في جدول المتوفر:**"
                     if st.session_state.lang == 'ar'
                     else f"**✨ {len(injected)} new channels injected into pool:**")
            st.markdown(label)
            for item in injected[:30]:
                st.markdown(f"<span style='color:#00f0ff;font-size:0.85rem;'>{item}</span>",
                            unsafe_allow_html=True)
            if len(injected) > 30:
                st.markdown(f"<span style='color:#888;'>... و {len(injected)-30} قناة أخرى</span>",
                            unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='color:#888;margin-top:10px;'>"
                f"{'ℹ️ لم يتم العثور على قنوات جديدة (مضافة بالفعل).' if st.session_state.lang == 'ar' else 'ℹ️ No new channels found (already present).'}"
                f"</div>", unsafe_allow_html=True
            )

# ── صيانة الترددات من القاعدة الحية ──
with col_chk2:
    maint_active = st.checkbox(t['chk_modern_maint'], value=False, key="chk_maint_p2")

    if maint_active and not st.session_state.get('maint_done_p2', False):
        maint_details = []
        freq_patches  = {}

        for ch in st.session_state.channels:
            ch_name  = ch.get('name', 'Unknown')
            old_f    = str(ch.get('freq', 'N/A'))
            name_up  = ch_name.upper()

            db_match = ACTIVE_DB.get(name_up) or ACTIVE_DB.get(
                next((k for k in ACTIVE_DB if k in name_up or name_up in k), ""), None
            )
            if db_match:
                new_f = str(db_match["frequency"])
                if old_f != new_f:
                    freq_patches[name_up] = new_f
                    ch['freq'] = new_f
                    if st.session_state.is_modern and 'raw_node' in ch:
                        ch['raw_node']['frequency'] = int(new_f)
                    elif 'raw_str' in ch:
                        ch['raw_str'] = re.sub(
                            r'<frequency>\d+</frequency>',
                            f'<frequency>{new_f}</frequency>',
                            ch['raw_str']
                        )
                    maint_details.append(
                        f"🔄 **{ch_name}** | "
                        f"{'من' if st.session_state.lang == 'ar' else 'from'} `{old_f}` "
                        f"{'إلى' if st.session_state.lang == 'ar' else 'to'} `{new_f}`"
                    )

        st.session_state.maint_done_p2    = True
        st.session_state.maint_details_p2 = maint_details
        st.session_state.p2_freq_patches  = freq_patches

        if maint_details:
            st.toast("🔧 " + (f"تم تحديث {len(maint_details)} تردد!" if st.session_state.lang == 'ar'
                              else f"Updated {len(maint_details)} frequencies!"))
            st.rerun()

    if maint_active:
        if st.session_state.get('maint_details_p2'):
            details = st.session_state.maint_details_p2
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
            st.markdown(
                f"<div style='color:#888;margin-top:10px;'>"
                f"{'ℹ️ جميع الترددات مطابقة لأحدث نسخة.' if st.session_state.lang == 'ar' else 'ℹ️ All frequencies match latest version.'}"
                f"</div>", unsafe_allow_html=True
            )

# ─────────────────────────────────────────────
# 11. Callback لزرع القناة
# ─────────────────────────────────────────────
def add_channel_callback(ch_obj):
    st.session_state.ordered_channels.append(ch_obj.copy())
    st.session_state.edit_finished = False

# ─────────────────────────────────────────────
# 12. واجهة الجدولين المتجاورين
# ─────────────────────────────────────────────
st.write("---")
col_table1, col_table2 = st.columns(2)

with col_table1:
    st.write(f"### {t['all_ch_title']}")
    search_q1 = st.text_input(t['search_ph'], key="src_p2_1").strip().upper()
    filtered_pool = [
        c for c in st.session_state.channels
        if not search_q1 or search_q1 in c.get('name', '').upper()
    ]
    st.write(f"🔎 {'المتاح حسب البحث' if st.session_state.lang == 'ar' else 'Available'}: **{len(filtered_pool)}** {'قناة' if st.session_state.lang == 'ar' else 'channels'}.")

    st.markdown(f"""
    <div style='background:{table_head_bg};padding:8px;border-bottom:2px solid {box_border};
    display:flex;font-weight:bold;color:#00f0ff;text-align:center;'>
        <div style='flex:1;'>{'التردد' if st.session_state.lang == 'ar' else 'Freq'}</div>
        <div style='flex:3;'>{'اسم القناة' if st.session_state.lang == 'ar' else 'Channel Name'}</div>
        <div style='flex:1;'>{t['col_action']}</div>
    </div>""", unsafe_allow_html=True)

    scroll_container = st.container(height=400)
    with scroll_container:
        for ch in filtered_pool[:100]:
            col_f, col_n, col_b = st.columns([1, 3, 1])
            col_f.write(f"`{ch.get('freq', 'N/A')}`")
            col_n.write(f"**{ch.get('name', 'Unknown')}**")
            col_b.button(
                t['btn_add_to_order'],
                key=f"btn_add_{ch['id']}_{len(st.session_state.ordered_channels)}",
                on_click=add_channel_callback,
                args=(ch,)
            )

with col_table2:
    st.write(f"### {t['ordered_title']}")
    ord_list = st.session_state.ordered_channels
    st.write(f"🔢 {'القنوات داخل لستتك الآن' if st.session_state.lang == 'ar' else 'Channels in your list'}: **{len(ord_list)}** {'قناة' if st.session_state.lang == 'ar' else 'channels'}.")

    if ord_list:
        st.markdown(f"""
        <div style='background:{table_head_bg};padding:8px;border-bottom:2px solid {box_border};
        display:flex;font-weight:bold;color:#ff007f;text-align:center;margin-bottom:10px;'>
            <div style='flex:1.2;'>{'الترتيب' if st.session_state.lang == 'ar' else 'Order'}</div>
            <div style='flex:2.5;'>{'اسم القناة' if st.session_state.lang == 'ar' else 'Channel Name'}</div>
            <div style='flex:1.3;'>{'التردد' if st.session_state.lang == 'ar' else 'Freq'}</div>
            <div style='flex:1;'>{'حذف' if st.session_state.lang == 'ar' else 'Del'}</div>
        </div>""", unsafe_allow_html=True)

        scroll_ordered = st.container(height=400)
        new_ranks = {}

        with scroll_ordered:
            for i, ch in enumerate(ord_list):
                col_rank, col_name, col_freq, col_del = st.columns([1.2, 2.5, 1.3, 1])
                with col_rank:
                    new_val = st.number_input(
                        "Order", min_value=1, max_value=2000, value=i + 1,
                        key=f"rank_input_{i}_{ch['id']}", label_visibility="collapsed"
                    )
                    new_ranks[i] = new_val
                col_name.write(f"**{ch.get('name', 'Unknown')}**")
                col_freq.write(f"`{ch.get('freq', 'N/A')}`")
                with col_del:
                    if st.button("🗑️", key=f"del_btn_{i}_{ch['id']}",
                                 help="حذف القناة من قائمة الترتيب"):
                        st.session_state.ordered_channels.pop(i)
                        st.session_state.edit_finished = False
                        st.toast(f"🗑️ تم حذف [{ch.get('name')}]")
                        st.rerun()

        st.write("")
        # ── زر الحفظ — يُظهر الأزرار فوراً بدون خطوة ثانية ──
        if st.button("💾 اعتماد الترتيب الجديد وحفظ التعديلات",
                     key="save_ordered_ranks_btn"):
            indexed_channels = sorted(
                [(new_ranks[idx], ch) for idx, ch in enumerate(ord_list)],
                key=lambda x: x[0]
            )
            st.session_state.ordered_channels = [item[1] for item in indexed_channels]
            st.session_state.edit_finished    = True   # ← يُفعّل الأزرار مباشرة
            st.toast("🎯 " + ("تم الحفظ! الملفات جاهزة للتحميل." if st.session_state.lang == 'ar'
                              else "Saved! Files ready to download."))
            st.rerun()
    else:
        st.info("💡 " + ("اضغط [➕ زرع] من الجدول لتبني قائمتك." if st.session_state.lang == 'ar'
                         else "Press [➕ Inject] from the left table to build your list."))

# ─────────────────────────────────────────────
# 13. التجهيز النهائي والتحميل
#     تظهر الأزرار الـ3 فور الضغط على "حفظ التعديلات"
# ─────────────────────────────────────────────
st.write("---")

final_out_list = st.session_state.ordered_channels

if not final_out_list:
    st.warning("⚠️ " + ("جدولك المخصص فارغ! قم بزرع قنوات أولاً." if st.session_state.lang == 'ar'
                         else "Your custom list is empty! Inject channels first."))

elif st.session_state.edit_finished:
    # ── بناء الملفات ──
    st.success(t['ready_msg'])

    txt_report = f"{t['txt_header']} ({st.session_state.model_name})\n"
    txt_report += "=" * 60 + "\n"
    for rank, ch in enumerate(final_out_list, start=1):
        txt_report += f"No. {rank:03d} : {ch.get('name','Unknown'):<30} | Freq: {ch.get('freq','N/A')} MHz\n"

    root       = st.session_state.root
    legacy_tag = st.session_state.get('legacy_tag')

    if st.session_state.is_modern:
        bdata           = st.session_state.broadcast_data
        final_list_nodes = []
        for rank, ch in enumerate(final_out_list, start=1):
            node = ch["raw_node"]
            node["majorNumber"] = rank
            final_list_nodes.append(node)
        bdata["channelList"] = final_list_nodes
        legacy_tag.text = json.dumps(bdata, ensure_ascii=False)
        final_tll_bytes = ET.tostring(root, encoding="utf-8")
    else:
        file_text    = st.session_state.file_text_original
        item_strings = []
        for rank, ch in enumerate(final_out_list, start=1):
            raw = ch.get(
                "raw_str",
                f"<ITEM>\r\n<vchName>{ch.get('name','Unknown')}</vchName>\r\n"
                f"<frequency>{ch.get('freq','N/A')}</frequency>\r\n</ITEM>"
            )
            if "<prNum>" in raw:
                raw = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{rank}</prNum>', raw)
            else:
                raw = raw.replace("<ITEM>", f"<ITEM>\r\n<prNum>{rank}</prNum>")
            item_strings.append(raw)
        combined = "\r\n".join(item_strings)
        start_i  = file_text.find("<ITEM>")
        end_i    = file_text.rfind("</ITEM>") + len("</ITEM>")
        final_text = (file_text[:start_i] + combined + file_text[end_i:]
                      if start_i != -1 else combined)
        try:
            final_tll_bytes = final_text.encode('utf-8')
        except UnicodeEncodeError:
            final_tll_bytes = final_text.encode('latin-1')

    # ── 3 أزرار تظهر مباشرة ──
    col_d1, col_d2, col_d3 = st.columns([2, 2, 1])
    with col_d1:
        st.download_button(
            label=t['btn_tll'],
            data=final_tll_bytes,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream",
            use_container_width=True
        )
    with col_d2:
        st.download_button(
            label=t['btn_txt'],
            data=txt_report,
            file_name="Channels_List_Manual.txt",
            mime="text/plain; charset=utf-8",
            use_container_width=True
        )
    with col_d3:
        if st.button(t['btn_reset'], key="reset_bottom_p2", use_container_width=True):
            new_key = st.session_state.get('p2_uploader_key', 0) + 1
            reset_all_session_state()
            st.session_state.p2_uploader_key = new_key
            st.rerun()

    # ── ملحوظة LG ──
    st.markdown("""
    <div style="background:rgba(255,193,7,0.1);border:2px solid #ffc107;border-radius:14px;
    padding:22px;margin-top:20px;">
    <div style="color:#ffc107;font-size:1.1rem;font-weight:bold;margin-bottom:12px;">
    💡 ملحوظة فنية هامة جداً بعد تنزيل الملف على شاشة LG:</div>
    <ol style="font-size:15px;line-height:1.7;margin-right:20px;">
        <li>من إعدادات التلفزيون اختار <b>القنوات (Channels)</b>.</li>
        <li>اختار <b>مدير القنوات (Channel Manager)</b>.</li>
        <li>اختار <b>التعديل على كل القنوات (Edit All Channels)</b>.</li>
        <li>حدد كل القنوات واختار <b>استعادة (Restore)</b>.</li>
    </ol>
    <p style="font-size:13px;color:#ffaa55;font-style:italic;margin-bottom:0;">
    *تفعل هذه الخطوة فقط إذا شعرت أن الملف غير مرتب كما حددته.</p>
    </div>""", unsafe_allow_html=True)
