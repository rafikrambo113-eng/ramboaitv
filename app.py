import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# ── تهيئة الجلسة ──
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

UI_TEXT = {
    'ar': {
        'title': "📺 RAMBO - المنسق العالمي لشاشات LG",
        'subtitle': "⚡ هندسة متطورة لترتيب ملفات القنوات بالتأثيرات السيبرانية مصفوفة (3D)",
        'upload_label': "🚀 اختر ملف القنوات (GlobalClone00001.TLL) من الفلاشة:",
        'update_freq_label': "⚛️ تفعيل الصيانة الذكية وتحديث الترددات تلقائياً (حسب القمر المكتشف)",
        'add_new_ch_label': "✨ فحص وزرع القنوات الجديدة المتاحة تلقائياً في القمر الصناعي المكتشف",
        'success_read': "🛸 تم قراءة الهيكل بنجاح! الموديل الحالي: ",
        'search_header': "🔍 محرك البحث الذكي عن القنوات داخل الملف:",
        'search_placeholder': "اكتب اسم القناة هنا للبحث...",
        'search_col_num': "الرقم الحالي",
        'search_col_name': "اسم القناة",
        'search_col_cat': "الفئة (Category)",
        'search_col_freq': "التردد (Frequency)",
        'search_no_results': "⚠️ لم يتم العثور على أي قنوات مطابقة للبحث.",
        'config_title': "🎛️ مصفوفة ترتيب الفئات المخصصة حسب اختيارك اليدوي:",
        'config_tip': "💡 ملحوظة: اضغط على الفئات بالترتيب الفعلي المفضل لديك.",
        'multiselect_label': "اضغط هنا لبناء تسلسل خطة العرض التفاعلي للفئات:",
        'preview_title': "📊 مجسم المعاينة الحية لتوزيع القنوات الحالي:",
        'channels_count': "قناة",
        'ready_msg': "🌌 تم دمج مصفوفة RAMBO وإعادة الهيكلة بنجاح! الملفات جاهزة للتحميل:",
        'btn_download_tll': "📥 تحميل ملف الشاشة النهائي (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 تحميل تقرير الترتيب كملف نصي (Channels_List.txt)",
        'txt_header': "📄 تقرير الترتيب وتحديثات الترددات النهائي لشاشة LG",
        'txt_order': "🛠️ ترتيب الفئات المختار: ",
        'lg_trick_title': "💡 ملحوظة فنية هامة جداً بعد تنزيل الملف على شاشة LG:",
        'lg_trick_text': "في بعض الحالات، بعد تنزيل ملف القنوات على الشاشة، قد تشعر أن القنوات ليست منظمة كما رتبتها. لحل هذا الأمر فوراً واجبار الشاشة على تفعيل الترتيب الصحيح، قم بالآتي:\n1. من إعدادات التلفزيون اختار **القنوات (Channels)**.\n2. بعد ذلك اختار **مدير القنوات (Channel Manager)**.\n3. اختار **التعديل على كل القنوات (Edit All Channels)**.\n4. ستظهر لك القنوات المرتبة ويكون بعضها في وضع مخفي، قم **بتحديد كل القنوات** واختار **استعادة (Restore)**.\n*ملحوظة: تفعل هذه الخطوة فقط إذا شعرت أن الملف بعد التنزيل غير مرتب كما حددته على الموقع.*"
    },
    'en': {
        'title': "📺 RAMBO - LG Universal AI Channel Sorter",
        'subtitle': "⚡ Next-Gen Cyber-Engineered Architecture for 3D Channel Layouts",
        'upload_label': "🚀 Upload Channel File (GlobalClone00001.TLL) from USB Flash:",
        'update_freq_label': "⚛️ Activate Satellite Live Frequency Auto-Update (AI Auto-Detect)",
        'add_new_ch_label': "✨ Scan & Inject New Satellite Channels Automatically based on Sat Detection",
        'success_read': "🛸 Matrix Structure Decoded Successfully! Model Profile: ",
        'search_header': "🔍 Dynamic Channel Search Engine:",
        'search_placeholder': "Type channel name to look up...",
        'search_col_num': "No.",
        'search_col_name': "Channel Name",
        'search_col_cat': "Category",
        'search_col_freq': "Frequency",
        'search_no_results': "⚠️ No channels matching your search criteria.",
        'config_title': "🎛️ Custom Category Priority Control Matrix:",
        'config_tip': "💡 Hint: Click categories in exact order. The first selection populates the absolute top of your TV.",
        'multiselect_label': "Select categories one by one to configure your linear priority:",
        'preview_title': "📊 Channel Grid Live 3D Preview Dashboard:",
        'channels_count': "Channels",
        'ready_msg': "🌌 Quantum Matrix Deployment Successful! Assets ready for transfer:",
        'btn_download_tll': "📥 Download Final TV Configuration (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 Download Sorting Text Diagnostics (Channels_List.txt)",
        'txt_header': "📄 Final LG TV Channel Sorting & Updates Report",
        'txt_order': "🛠️ Selected Category Priority: ",
        'lg_trick_title': "💡 Critical Expert Technical Tip After Uploading to LG TV:",
        'lg_trick_text': "In some cases, after importing the file into your LG TV, you might feel that the channels are not perfectly sorted as configured. To fix this instantly:\n1. Open TV **Settings** -> Go to **Channels**.\n2. Select **Channel Manager**.\n3. Choose **Edit All Channels**.\n4. **Select All Channels** and click **Restore**.\n*Note: Only required if the TV cache mixed the sorting order after USB upload.*"
    }
}

t = UI_TEXT[st.session_state.lang]

st.set_page_config(page_title="RAMBO - LG Futuristic AI Sorter", page_icon="⚡", layout="wide")

col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("🌐 English" if st.session_state.lang == 'ar' else "🌐 العربية"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
        st.rerun()
with col_theme:
    if st.button("☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

if st.session_state.theme == 'dark':
    bg_style = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)"
    text_color = "#00f0ff"
    box_bg = "rgba(13, 7, 33, 0.85)"
    box_border = "#00f0ff"
    box_shadow = "rgba(0, 240, 255, 0.35)"
    text_shadow_glow = "0 0 5px rgba(0, 240, 255, 0.4)"
    footer_bg = "#080314"
    footer_text = "#ffffff"
else:
    bg_style = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
    text_color = "#0d0722"
    box_bg = "#ffffff"
    box_border = "#ff007f"
    box_shadow = "rgba(255, 0, 127, 0.15)"
    text_shadow_glow = "none"
    footer_bg = "#110926"
    footer_text = "#ffffff"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
    .main {{ background: {bg_style} !important; color: {text_color} !important; font-family: { "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif" }; }}
    h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255, 0, 127, 0.4) !important; text-align: center; font-weight: 900; margin-top: 5px; }}
    h3, p, label, .stMarkdown, .stInfo, div[data-testid="stMarkdownContainer"] p {{ color: {text_color} !important; text-shadow: {text_shadow_glow}; }}
    .stTextInput>div>div>input {{ background-color: {box_bg} !important; color: {text_color} !important; border: 2px solid {box_border} !important; border-radius: 10px !important; }}
    .stCheckbox, .stMultiSelect, div[data-testid="stExpander"], div[data-testid="stFileUploader"], .lg-trick-box {{ background: {box_bg} !important; border: 2px solid {box_border} !important; box-shadow: 0px 5px 15px {box_shadow} !important; border-radius: 14px !important; padding: 18px !important; margin-bottom: 20px !important; }}
    .lg-trick-box {{ border-color: #ff007f !important; box-shadow: 0px 5px 15px rgba(255, 0, 127, 0.25) !important; }}
    .stButton>button {{ background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important; color: #ffffff !important; border: 2px solid #ff007f !important; border-radius: 12px !important; font-weight: bold; }}
    .futuristic-cyber-footer {{ background: {footer_bg}; border: 2px solid #00f0ff; color: {footer_text} !important; padding: 35px; text-align: center; border-radius: 20px; margin-top: 65px; font-family: 'Orbitron', sans-serif; }}
    .footer-dev {{ color: #ff007f; font-size: 26px; font-weight: bold; }}
    .cyber-whatsapp-btn {{ color: #25d366 !important; padding: 14px 35px; border-radius: 35px; display: inline-block; font-weight: bold; border: 2px solid #25d366; text-decoration: none; margin-top: 20px; }}
    </style>
""", unsafe_allow_html=True)

st.title(t['title'])
st.markdown(f"<h3>{t['subtitle']}</h3>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 🛰️ DATABASE — نايل سات (محدّثة وموسّعة)
# ══════════════════════════════════════════════
NILESAT_LIVE_DB = {
    # ── Christian ──
    "AL HAYAT":         {"frequency": 12207, "polarization": "Vertical",   "update_date": "2026-05-10"},
    "AL HAYAT 2":       {"frequency": 12207, "polarization": "Vertical",   "update_date": "2026-05-10"},
    "SAT-7 KIDS":       {"frequency": 11353, "polarization": "Vertical",   "update_date": "2026-04-18"},
    "SAT-7 ARABIC":     {"frequency": 11353, "polarization": "Vertical",   "update_date": "2026-04-18"},
    "SAT-7 PARS":       {"frequency": 11353, "polarization": "Vertical",   "update_date": "2026-04-18"},
    "ALKARMA ME 1":     {"frequency": 11096, "polarization": "Horizontal", "update_date": "2026-02-05"},
    "ALKARMA ME 2":     {"frequency": 11096, "polarization": "Horizontal", "update_date": "2026-02-05"},
    "AGHAPY TV":        {"frequency": 11179, "polarization": "Horizontal", "update_date": "2026-03-12"},
    "CTV":              {"frequency": 12022, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "NOURSAT":          {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-01-10"},
    "MESAT":            {"frequency": 11096, "polarization": "Horizontal", "update_date": "2026-01-10"},
    "MIRACLE CHANNEL":  {"frequency": 11179, "polarization": "Horizontal", "update_date": "2026-03-20"},
    # ── Islamic ──
    "IQRAA":            {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-04-01"},
    "MAJD":             {"frequency": 11862, "polarization": "Vertical",   "update_date": "2026-02-14"},
    "RAHMA":            {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-04-01"},
    "QURAN KAREEM":     {"frequency": 11727, "polarization": "Vertical",   "update_date": "2026-03-05"},
    "MAKKA TV":         {"frequency": 11727, "polarization": "Vertical",   "update_date": "2026-03-05"},
    # ── News ──
    "AL JAZEERA":       {"frequency": 10853, "polarization": "Vertical",   "update_date": "2026-05-20"},
    "AL JAZEERA HD":    {"frequency": 10853, "polarization": "Vertical",   "update_date": "2026-05-20"},
    "AL ARABIYA":       {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-04-15"},
    "AL HADATH":        {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-04-15"},
    "SKY NEWS ARABIA":  {"frequency": 12092, "polarization": "Vertical",   "update_date": "2026-03-30"},
    "CBC":              {"frequency": 12092, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "EXTRA NEWS":       {"frequency": 12092, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "ON E":             {"frequency": 12092, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "CAIRO NEWS":       {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-04-20"},
    "QATAR TV HD":      {"frequency": 10834, "polarization": "Horizontal", "update_date": "2026-05-14"},
    # ── Movies ──
    "MBC 2":            {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-01-20"},
    "MBC 4":            {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-01-20"},
    "MBC MAX":          {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-01-20"},
    "ROTANA CINEMA":    {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-02-01"},
    "ROTANA CLASSIC":   {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-02-01"},
    "ROTANA DRAMA":     {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-02-01"},
    "FOX MOVIES":       {"frequency": 11843, "polarization": "Vertical",   "update_date": "2026-03-10"},
    "AFLAM":            {"frequency": 11179, "polarization": "Horizontal", "update_date": "2026-02-28"},
    "AFLAM 2":          {"frequency": 11179, "polarization": "Horizontal", "update_date": "2026-02-28"},
    "MELODY AFLAM":     {"frequency": 11862, "polarization": "Vertical",   "update_date": "2026-01-15"},
    # ── Sports ──
    "ON TIME SPORTS 1": {"frequency": 11861, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "ON TIME SPORTS 2": {"frequency": 11861, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "ON TIME SPORTS 3": {"frequency": 11861, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "SSC 1":            {"frequency": 11843, "polarization": "Vertical",   "update_date": "2026-04-10"},
    "SSC 2":            {"frequency": 11843, "polarization": "Vertical",   "update_date": "2026-04-10"},
    "AD SPORTS":        {"frequency": 11900, "polarization": "Vertical",   "update_date": "2026-03-15"},
    "AD SPORTS 2":      {"frequency": 11900, "polarization": "Vertical",   "update_date": "2026-03-15"},
    "KASS":             {"frequency": 11727, "polarization": "Vertical",   "update_date": "2026-02-20"},
    # ── Kids ──
    "SPACE TOON":       {"frequency": 11727, "polarization": "Vertical",   "update_date": "2026-01-05"},
    "MAJID":            {"frequency": 11862, "polarization": "Vertical",   "update_date": "2026-01-05"},
    "TOYOR ALJANNAH":   {"frequency": 11179, "polarization": "Horizontal", "update_date": "2026-02-10"},
    "CARTOON NETWORK":  {"frequency": 11843, "polarization": "Vertical",   "update_date": "2026-03-01"},
}

NILESAT_NEW_CHANNELS = [
    {"name": "RAMBO ACTION HD",     "frequency": 10834, "polarization": "Horizontal", "launch_date": "2026-01-15", "source": "Nilesat Official"},
    {"name": "MISHMISH CINEMA",     "frequency": 11938, "polarization": "Vertical",   "launch_date": "2026-04-10", "source": "KingOfSat Database"},
    {"name": "ON TIME SPORTS 4 HD", "frequency": 11861, "polarization": "Vertical",   "launch_date": "2026-05-01", "source": "FlySat Live"},
    {"name": "AL JAZEERA MUBASHER", "frequency": 10853, "polarization": "Vertical",   "launch_date": "2026-03-20", "source": "Nilesat Official"},
    {"name": "SSC EXTRA HD",        "frequency": 11843, "polarization": "Vertical",   "launch_date": "2026-04-25", "source": "FlySat Live"},
    {"name": "TOYOR ALJANNAH 2",    "frequency": 11179, "polarization": "Horizontal", "launch_date": "2026-02-10", "source": "KingOfSat Database"},
    {"name": "CBC DRAMA",           "frequency": 12092, "polarization": "Vertical",   "launch_date": "2026-05-05", "source": "Nilesat Official"},
]

ALL_AVAILABLE_CATEGORIES = [
    "⛪ Christian Channels" if st.session_state.lang == 'en' else "⛪ قنوات مسيحية",
    "🕌 Islamic Channels"   if st.session_state.lang == 'en' else "🕌 قنوات إسلامية",
    "🎬 Drama & Series"     if st.session_state.lang == 'en' else "🎬 مسلسلات ودراما",
    "🍿 Movies (Ar/En)"     if st.session_state.lang == 'en' else "🍿 أفلام عربية وأجنبية",
    "👶 Kids & Cartoon"     if st.session_state.lang == 'en' else "👶 أطفال وكرتون",
    "⚽ Sports"             if st.session_state.lang == 'en' else "⚽ رياضة",
    "📰 News & Politics"    if st.session_state.lang == 'en' else "📰 أخبار وسياسة",
    "📺 General Channels"   if st.session_state.lang == 'en' else "📺 قنوات عامة ومنوعات"
]

# ══════════════════════════════════════════════
# 🤖 ai_classify — محسّنة وموسّعة
# ══════════════════════════════════════════════
def ai_classify(channel_name):
    name = channel_name.upper().strip()

    CHRISTIAN_KW = ["CTV", "AGHAPY", "MESAT", "KARMA", "ALKARMA", "NOURSAT",
                    "SAT-7", "SAT7", "AL HAYAT", "HAYAT TV", "MIRACLE",
                    "COPTIC", "CHRISTIAN", "CHURCH", "CROSS", "GOSPEL",
                    "MARYAM", "VIRGIN", "BISHOP", "POPE", "JESUS", "CHRIST",
                    "FAITH", "HOPE CHANNEL", "3ABN"]
    if any(w in name for w in CHRISTIAN_KW):
        return ALL_AVAILABLE_CATEGORIES[0]

    ISLAMIC_KW = ["QURAN", "RAHMA", "MAJD", "MAKKA", "IQRAA", "IQRA",
                  "HUDA", "WESAL", "ISLAM", "SUNNAH", "MADINAH",
                  "AL RESALAH", "RESALAH", "SAFWA", "HIDAYA", "HIDAYAT",
                  "AHLUL BAYT", "IMAM", "FIQH", "FATWA", "SALAH"]
    if any(w in name for w in ISLAMIC_KW):
        return ALL_AVAILABLE_CATEGORIES[1]

    DRAMA_KW = ["MOSALSALAT", "DRAMA", "SERIES", "KHOLASA", "MASRAWI",
                "ROTANA DRAMA", "CBC DRAMA", "MELODY DRAMA",
                "MBC DRAMA", "SHAHID", "PLUS DRAMA", "AL HAYAT DRAMA"]
    if any(w in name for w in DRAMA_KW):
        return ALL_AVAILABLE_CATEGORIES[2]

    MOVIE_KW = ["CINEMA", "ROTANA", "AFLAM", "MIX", "FOX", "MBC2", "MBC 2",
                "MBC4", "MBC 4", "MBC MAX", "ACTION", "RAMBO", "MISHMISH",
                "MOVIE", "FILM", "MELODY AFLAM", "OSCAR", "COMEDY", "FUN",
                "STAR MOVIES", "THRILLER", "HORROR", "PREMIERE", "SHOWTIME", "CINE"]
    if any(w in name for w in MOVIE_KW):
        return ALL_AVAILABLE_CATEGORIES[3]

    KIDS_KW = ["SPACE TOON", "SPACETOON", "CN", "CARTOON", "MAJID",
               "KIDS", "TOM", "TOYOR", "BABY", "JUNIOR", "NICKELODEON",
               "NICK", "DISNEY", "BOOMERANG", "JIM JAM", "MINIMAX", "LEGO", "MASHA"]
    if any(w in name for w in KIDS_KW):
        return ALL_AVAILABLE_CATEGORIES[4]

    SPORT_KW = ["SPORT", "SPORTS", "ONTIME", "ON TIME", "KASS",
                "AD_SPORTS", "AD SPORTS", "SSC", "BEIN", "MATCH",
                "FOOTBALL", "SOCCER", "GOLF", "NBA", "UFC",
                "EXTREME", "EUROSPORT", "DSF", "FIGHTING", "WWE",
                "OLYMPIC", "RACING"]
    if any(w in name for w in SPORT_KW):
        return ALL_AVAILABLE_CATEGORIES[5]

    NEWS_KW = ["NEWS", "JAZEERA", "ARABIYA", "HADATH", "CAIRO",
               "SKY NEWS", "BBC", "CNN", "FRANCE 24", "RT",
               "EXTRA NEWS", "CBC", "ON E", "SADA", "BALADI",
               "MASR", "MISR", "AHRAR", "EL WATAN", "ALARABY",
               "AL GHAD", "MEKAMELEEN", "HIWAR", "ALAAN"]
    if any(w in name for w in NEWS_KW):
        return ALL_AVAILABLE_CATEGORIES[6]

    return ALL_AVAILABLE_CATEGORIES[7]

# ══════════════════════════════════════════════
# رفع الملف والمعالجة
# ══════════════════════════════════════════════
uploaded_file = st.file_uploader(t['upload_label'], type=["TLL"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    try:
        file_text_original = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        file_text_original = file_bytes.decode('latin-1')

    root = ET.fromstring(file_bytes)
    model_setting = root.find(".//ModelName")
    model_name = model_setting.text if model_setting is not None else "Unknown LG TV"

    legacy_broadcast_tag = root.find(".//legacybroadcast")
    is_modern = legacy_broadcast_tag is not None and legacy_broadcast_tag.text

    st.info(f"{t['success_read']} **{model_name}**")

    st.markdown(f"""
        <div class="lg-trick-box">
            <h4 style="color: #ff007f; margin-top:0;">{t['lg_trick_title']}</h4>
            <p style="white-space: pre-line; margin-bottom:0; font-size:14px;">{t['lg_trick_text']}</p>
        </div>
    """, unsafe_allow_html=True)

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        update_freq = st.checkbox(t['update_freq_label'], value=True)
    with col_opt2:
        add_new_channels = st.checkbox(t['add_new_ch_label'], value=True)

    channels_to_sort = []
    report_changes   = []
    injected_report  = []
    detected_satellite = "Nilesat 7.0°W"

    if is_modern:
        broadcast_data = json.loads(legacy_broadcast_tag.text)
        channels_list  = broadcast_data.get("channelList", [])

        if add_new_channels:
            for nch in NILESAT_NEW_CHANNELS:
                new_node = {
                    "channelName": nch["name"], "frequency": nch["frequency"],
                    "polarization": nch["polarization"], "majorNumber": 0,
                    "serviceType": "1", "scrambled": "false", "symbolRate": "27500"
                }
                channels_list.append(new_node)
                injected_report.append({
                    "اسم القناة": nch["name"], "التردد": f"{nch['frequency']} MHz",
                    "تاريخ الصدور": nch["launch_date"], "المصدر": nch["source"]
                })

        for idx, ch in enumerate(channels_list):
            ch_name  = ch.get("channelName", "Unknown")
            old_freq = str(ch.get("frequency", "N/A"))
            name_up  = ch_name.upper()

            if update_freq and name_up in NILESAT_LIVE_DB:
                live_freq = str(NILESAT_LIVE_DB[name_up]["frequency"])
                if old_freq != live_freq:
                    report_changes.append({
                        "القناة": ch_name,
                        "الفئة (Category)": ai_classify(ch_name),
                        "التردد القديم": f"{old_freq} MHz",
                        "التردد الجديد": f"{live_freq} MHz",
                        "تاريخ التحديث": NILESAT_LIVE_DB[name_up]["update_date"]
                    })
                    ch["frequency"]    = int(live_freq)
                    ch["polarization"] = NILESAT_LIVE_DB[name_up]["polarization"]
                    old_freq = live_freq

            channels_to_sort.append({"id": idx, "name": ch_name, "freq": old_freq, "raw_node": ch})
    else:
        item_blocks = re.findall(r'(<ITEM>.*?</ITEM>)', file_text_original, re.DOTALL)

        for idx, item_str in enumerate(item_blocks):
            name_match = re.search(r'<vchName>(.*?)</vchName>', item_str)
            freq_match = re.search(r'<frequency>(.*?)</frequency>', item_str)
            ch_name  = name_match.group(1) if name_match else "Unknown"
            old_freq = freq_match.group(1) if freq_match else "N/A"
            name_up  = ch_name.upper()

            if update_freq and name_up in NILESAT_LIVE_DB:
                live_freq = str(NILESAT_LIVE_DB[name_up]["frequency"])
                if old_freq != live_freq:
                    report_changes.append({
                        "القناة": ch_name,
                        "الفئة (Category)": ai_classify(ch_name),
                        "التردد القديم": f"{old_freq} MHz",
                        "التردد الجديد": f"{live_freq} MHz",
                        "تاريخ التحديث": NILESAT_LIVE_DB[name_up]["update_date"]
                    })
                    item_str = re.sub(r'<frequency>\d+</frequency>',
                                      f'<frequency>{live_freq}</frequency>', item_str)
                    old_freq = live_freq

            channels_to_sort.append({"id": idx, "name": ch_name, "freq": old_freq, "raw_str": item_str})

        if add_new_channels:
            for nch in NILESAT_NEW_CHANNELS:
                new_item_raw = (f"<ITEM>\r\n<prNum>0</prNum>\r\n"
                                f"<vchName>{nch['name']}</vchName>\r\n"
                                f"<frequency>{nch['frequency']}</frequency>\r\n"
                                f"<serviceType>1</serviceType>\r\n</ITEM>")
                channels_to_sort.append({
                    "id": len(channels_to_sort), "name": nch["name"],
                    "freq": str(nch["frequency"]), "raw_str": new_item_raw
                })
                injected_report.append({
                    "اسم القناة": nch["name"], "التردد": f"{nch['frequency']} MHz",
                    "تاريخ الصدور": nch["launch_date"], "المصدر": nch["source"]
                })

    # ── محرك البحث ──
    st.write("---")
    st.write(f"### {t['search_header']}")
    search_query = st.text_input("", placeholder=t['search_placeholder']).strip().upper()
    if search_query:
        search_results = []
        for idx, ch in enumerate(channels_to_sort, start=1):
            if search_query in ch["name"].upper():
                search_results.append({
                    t['search_col_num']: idx,
                    t['search_col_name']: ch["name"],
                    t['search_col_cat']: ai_classify(ch["name"]),
                    t['search_col_freq']: ch["freq"]
                })
        if search_results:
            st.table(search_results)
        else:
            st.warning(t['search_no_results'])

    # ── مصفوفة الفئات ──
    st.write("---")
    st.write(f"### {t['config_title']}")
    user_priority = st.multiselect(t['multiselect_label'], options=ALL_AVAILABLE_CATEGORIES, default=[])
    final_priority = list(user_priority)
    for cat in ALL_AVAILABLE_CATEGORIES:
        if cat not in final_priority:
            final_priority.append(cat)

    channels_sorted = sorted(channels_to_sort, key=lambda x: final_priority.index(ai_classify(x["name"])))

    categorized = {}
    for ch in channels_sorted:
        cat = ai_classify(ch["name"])
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(ch["name"])

    st.write("---")
    st.write(f"### {t['preview_title']}")
    col1, col2 = st.columns(2)
    for i, cat_name in enumerate(final_priority):
        if cat_name in categorized:
            ch_list    = categorized[cat_name]
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                is_user_chosen = "⭐ " if cat_name in user_priority else ""
                with st.expander(f"{is_user_chosen}{cat_name} — ({len(ch_list)} {t['channels_count']})"):
                    st.write(", ".join(ch_list))

    st.write("---")
    if report_changes:
        st.write(f"### 🔁 سجل صيانة وتحديث الترددات — تبع الـ {detected_satellite}:")
        st.table(report_changes)

    if injected_report:
        st.write(f"### 🆕 تقرير القنوات الجديدة المزروعة — تبع الـ {detected_satellite}:")
        st.table(injected_report)

    # ── بناء الملفات النهائية ──
    text_report  = f"{t['txt_header']} ({model_name})\n"
    text_report += f"🛰️ القمر الصناعي المكتشف: {detected_satellite}\n"
    text_report += "=" * 50 + "\n"

    if report_changes:
        text_report += f"\n🔁 [تحديثات الترددات - {detected_satellite}]:\n"
        for change in report_changes:
            text_report += (f"- {change['القناة']:<20} | {change['الفئة (Category)']:<22} | "
                            f"{change['التردد القديم']:<10} -> {change['التردد الجديد']:<10} | "
                            f"{change['تاريخ التحديث']}\n")

    if injected_report:
        text_report += f"\n🆕 [القنوات الجديدة - {detected_satellite}]:\n"
        for inch in injected_report:
            text_report += (f"- {inch['اسم القناة']:<20} | {inch['التردد']:<12} | "
                            f"{inch['تاريخ الصدور']:<12} | {inch['المصدر']}\n")

    text_report += "\n" + "=" * 50 + "\n\n"

    if is_modern:
        final_list_modern = []
        for index, ch in enumerate(channels_sorted, start=1):
            node = ch["raw_node"]
            node["majorNumber"] = index
            final_list_modern.append(node)
            text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}\n"
        broadcast_data["channelList"] = final_list_modern
        legacy_broadcast_tag.text     = json.dumps(broadcast_data, ensure_ascii=False)
        final_xml_bytes               = ET.tostring(root, encoding="utf-8")
    else:
        item_strings_sorted = []
        for index, ch in enumerate(channels_sorted, start=1):
            raw = ch["raw_str"]
            if "<prNum>" in raw:
                raw = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{index}</prNum>', raw)
            else:
                raw = raw.replace("<ITEM>", f"<ITEM>\r\n<prNum>{index}</prNum>")
            item_strings_sorted.append(raw)
            text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}\n"

        combined_items_str = "\r\n".join(item_strings_sorted)
        start_idx = file_text_original.find("<ITEM>")
        end_idx   = file_text_original.rfind("</ITEM>") + len("</ITEM>")

        if start_idx != -1 and end_idx != -1:
            final_text_output = file_text_original[:start_idx] + combined_items_str + file_text_original[end_idx:]
        else:
            final_text_output = combined_items_str

        try:
            final_xml_bytes = final_text_output.encode('utf-8')
        except UnicodeEncodeError:
            final_xml_bytes = final_text_output.encode('latin-1')

    st.write("---")
    st.success(t['ready_msg'])

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(label=t['btn_download_tll'], data=final_xml_bytes,
                           file_name="GlobalClone00001.TLL", mime="application/octet-stream")
    with col_btn2:
        st.download_button(label=t['btn_download_txt'], data=text_report,
                           file_name="Channels_List.txt", mime="text/plain; charset=utf-8")

# ── الفوتر ──
whatsapp_url = ("https://api.whatsapp.com/send?phone=201280339779"
                "&text=Hello%20Developer%20Rafik%20Rambo%2C%20"
                "I%20have%20an%20inquiry%20regarding%20your%20LG%20TV%20Sorter%20script%3A")
st.markdown(f"""
    <div class="futuristic-cyber-footer">
        <div class="footer-dev">🛠️ DEVELOPER ENG: RAFIK RAMBO</div>
        <div class="footer-item">📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
        <div class="footer-item">✉️ <b>E-MAIL / البريد الإلكتروني:</b> rafikrambo113@gmail.com</div>
        <a href="{whatsapp_url}" target="_blank" class="cyber-whatsapp-btn">WhatsApp Web</a>
    </div>
""", unsafe_allow_html=True)
