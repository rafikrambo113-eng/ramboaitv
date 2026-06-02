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
        'title': "📺 RAMBO — مولّد ملف القنوات من الصفر",
        'subtitle': "⚡ أنشئ ملف TLL جديد كلياً لشاشات LG بدون الحاجة لرفع ملف قديم",
        'intro_box': "🛰️ هذه الصفحة تقوم بتوليد ملف GlobalClone00001.TLL جديد تماماً من الصفر بالاعتماد على قاعدة بيانات القنوات المدمجة (نايل سات). اختر الفئات وحدد الترتيب ثم حمّل الملف مباشرةً على الفلاشة.",
        'model_select_label': "📺 اختر موديل شاشتك:",
        'model_options': ["LG_CUSTOM_NILESAT_2025", "55UN7340PVA", "65NANO80", "43LM6300", "50UP7550"],
        'search_header': "🔍 محرك البحث الذكي في قاعدة البيانات المدمجة:",
        'search_placeholder': "اكتب اسم القناة للبحث في قاعدة البيانات...",
        'search_col_num': "الرقم",
        'search_col_name': "اسم القناة",
        'search_col_cat': "الفئة",
        'search_col_freq': "التردد",
        'search_no_results': "⚠️ لم يتم العثور على قنوات مطابقة.",
        'config_title': "🎛️ مصفوفة ترتيب الفئات:",
        'config_tip': "💡 اختر الفئات بالترتيب الفعلي المفضل لديك — الأول سيظهر في أعلى القائمة على الشاشة.",
        'multiselect_label': "اضغط لبناء تسلسل ترتيب الفئات:",
        'preview_title': "📊 معاينة توزيع القنوات المولّدة:",
        'channels_count': "قناة",
        'db_stats_title': "📡 إحصائيات قاعدة البيانات المدمجة:",
        'total_channels': "إجمالي القنوات في قاعدة البيانات",
        'total_cats': "عدد الفئات",
        'btn_generate': "⚡ توليد الملف الآن",
        'ready_msg': "🌌 تم توليد ملف القنوات الجديد بنجاح! الملفات جاهزة للتحميل:",
        'btn_download_tll': "📥 تحميل ملف الشاشة الجديد (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 تحميل تقرير القنوات المولّدة (Channels_List.txt)",
        'txt_header': "📄 تقرير ملف القنوات المولّد من الصفر — RAMBO Page 3",
        'txt_order': "🛠️ ترتيب الفئات المختار: ",
        'lg_trick_title': "💡 ملحوظة فنية هامة بعد تنزيل الملف على شاشة LG:",
        'lg_trick_text': "في بعض الحالات، بعد تنزيل ملف القنوات على الشاشة، قد تشعر أن القنوات ليست منظمة كما رتبتها. لحل هذا الأمر فوراً واجبار الشاشة على تفعيل الترتيب الصحيح، قم بالآتي:\n1. من إعدادات التلفزيون اختار القنوات (Channels).\n2. بعد ذلك اختار مدير القنوات (Channel Manager).\n3. اختار التعديل على كل القنوات (Edit All Channels).\n4. ستظهر لك القنوات المرتبة ويكون بعضها في وضع مخفي، قم بتحديد كل القنوات واختار استعادة (Restore).\n*ملحوظة: تفعل هذه الخطوة فقط إذا شعرت أن الملف بعد التنزيل غير مرتب كما حددته على الموقع.*",
        'page_badge': "الصفحة 3 — مولّد من الصفر"
    },
    'en': {
        'title': "📺 RAMBO — Channel File Generator (From Scratch)",
        'subtitle': "⚡ Build a brand-new TLL file for LG TVs — No upload required",
        'intro_box': "🛰️ This page generates a complete GlobalClone00001.TLL file from scratch using the built-in satellite channel database (NileSat). Just choose your categories, set the order, and download directly to your USB drive.",
        'model_select_label': "📺 Select Your TV Model:",
        'model_options': ["LG_CUSTOM_NILESAT_2025", "55UN7340PVA", "65NANO80", "43LM6300", "50UP7550"],
        'search_header': "🔍 Smart Search Engine in Built-in Database:",
        'search_placeholder': "Search channel name in database...",
        'search_col_num': "No.",
        'search_col_name': "Channel Name",
        'search_col_cat': "Category",
        'search_col_freq': "Frequency",
        'search_no_results': "⚠️ No matching channels found.",
        'config_title': "🎛️ Category Sorting Priority Matrix:",
        'config_tip': "💡 Select categories in your preferred order — first selected = top of your TV list.",
        'multiselect_label': "Click to build your category order sequence:",
        'preview_title': "📊 Live Channel Distribution Preview:",
        'channels_count': "Channels",
        'db_stats_title': "📡 Built-in Database Statistics:",
        'total_channels': "Total Channels in Database",
        'total_cats': "Number of Categories",
        'btn_generate': "⚡ Generate File Now",
        'ready_msg': "🌌 New channel file generated successfully! Ready for download:",
        'btn_download_tll': "📥 Download New TV File (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 Download Generated Channel Report (Channels_List.txt)",
        'txt_header': "📄 From-Scratch Channel File Report — RAMBO Page 3",
        'txt_order': "🛠️ Selected Category Priority: ",
        'lg_trick_title': "💡 Critical Technical Tip After Uploading to LG TV:",
        'lg_trick_text': "In some cases, after importing the file into your LG TV, the channels might not appear perfectly sorted. To fix this:\n1. Open TV Settings -> Channels.\n2. Select Channel Manager.\n3. Choose Edit All Channels.\n4. Select All Channels and click Restore.\n*Note: Only required if the TV cache mixed the sorting order after USB upload.*",
        'page_badge': "Page 3 — From-Scratch Generator"
    }
}

t = UI_TEXT[st.session_state.lang]

st.set_page_config(page_title="RAMBO P3 — Generator", page_icon="⚡", layout="wide")

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
    intro_bg = "rgba(0, 240, 255, 0.06)"
    intro_border = "#00f0ff"
    stats_bg = "rgba(255, 0, 127, 0.07)"
    stats_border = "#ff007f"
else:
    bg_style = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
    text_color = "#0d0722"
    box_bg = "#ffffff"
    box_border = "#ff007f"
    box_shadow = "rgba(255, 0, 127, 0.15)"
    text_shadow_glow = "none"
    footer_bg = "#110926"
    footer_text = "#ffffff"
    intro_bg = "rgba(255, 0, 127, 0.05)"
    intro_border = "#ff007f"
    stats_bg = "rgba(0, 240, 255, 0.07)"
    stats_border = "#00f0ff"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
    .main {{ background: {bg_style} !important; color: {text_color} !important; font-family: { "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif" }; }}
    h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255, 0, 127, 0.4) !important; text-align: center; font-weight: 900; margin-top: 5px; }}
    h3, p, label, .stMarkdown, .stInfo, div[data-testid="stMarkdownContainer"] p {{ color: {text_color} !important; text-shadow: {text_shadow_glow}; }}
    .stTextInput>div>div>input {{ background-color: {box_bg} !important; color: {text_color} !important; border: 2px solid {box_border} !important; border-radius: 10px !important; }}
    .stCheckbox, .stMultiSelect, div[data-testid="stExpander"], .rambo-box {{ background: {box_bg} !important; border: 2px solid {box_border} !important; box-shadow: 0px 5px 15px {box_shadow} !important; border-radius: 14px !important; padding: 18px !important; margin-bottom: 20px !important; }}
    .lg-trick-box {{ background: {box_bg} !important; border: 2px solid #ff007f !important; box-shadow: 0px 5px 15px rgba(255, 0, 127, 0.25) !important; border-radius: 14px !important; padding: 18px !important; margin-top: 25px !important; }}
    .stButton>button {{ background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important; color: #ffffff !important; border: 2px solid #ff007f !important; border-radius: 12px !important; font-weight: bold; }}
    .page3-badge {{ background: linear-gradient(135deg, #00f0ff22, #ff007f22); border: 1px solid #00f0ff55; border-radius: 30px; padding: 4px 16px; font-size: 13px; color: #00f0ff; display: inline-block; margin-bottom: 10px; }}
    .stat-card {{ background: {stats_bg}; border: 2px solid {stats_border}; border-radius: 12px; padding: 16px 22px; text-align: center; }}
    .stat-num {{ font-size: 36px; font-weight: 900; color: #ff007f; }}
    .stat-label {{ font-size: 13px; color: {text_color}; margin-top: 4px; }}
    .futuristic-cyber-footer {{ background: {footer_bg}; border: 2px solid #00f0ff; color: {footer_text} !important; padding: 35px; text-align: center; border-radius: 20px; margin-top: 65px; font-family: 'Orbitron', sans-serif; }}
    .footer-dev {{ color: #ff007f; font-size: 26px; font-weight: bold; }}
    .cyber-whatsapp-btn {{ color: #25d366 !important; padding: 14px 35px; border-radius: 35px; display: inline-block; font-weight: bold; border: 2px solid #25d366; text-decoration: none; margin-top: 20px; }}
    </style>
""", unsafe_allow_html=True)

# ── Badge الصفحة ──
st.markdown(f'<div class="page3-badge">🆕 {t["page_badge"]}</div>', unsafe_allow_html=True)
st.title(t['title'])
st.markdown(f"<h3>{t['subtitle']}</h3>", unsafe_allow_html=True)

# ── صندوق التعريف ──
st.markdown(f"""
<div style="background:{intro_bg}; border:2px solid {intro_border}; border-radius:14px; padding:18px; margin-bottom:24px;">
    <p style="margin:0; font-size:15px; line-height:1.7;">{t['intro_box']}</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 🛰️ قاعدة البيانات الكاملة — نايل سات + عرب سات
# ══════════════════════════════════════════════
ALL_AVAILABLE_CATEGORIES = [
    "⛪ قنوات مسيحية"  if st.session_state.lang == 'ar' else "⛪ Christian Channels",
    "🕌 قنوات إسلامية" if st.session_state.lang == 'ar' else "🕌 Islamic Channels",
    "🎬 مسلسلات ودراما" if st.session_state.lang == 'ar' else "🎬 Drama & Series",
    "🍿 أفلام عربية وأجنبية" if st.session_state.lang == 'ar' else "🍿 Movies (Ar/En)",
    "👶 أطفال وكرتون"  if st.session_state.lang == 'ar' else "👶 Kids & Cartoon",
    "⚽ رياضة"          if st.session_state.lang == 'ar' else "⚽ Sports",
    "📰 أخبار وسياسة"   if st.session_state.lang == 'ar' else "📰 News & Politics",
    "📺 قنوات عامة ومنوعات" if st.session_state.lang == 'ar' else "📺 General Channels"
]

FULL_CHANNEL_DB = [
    # ── مسيحية
    {"name": "CTV",              "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "AGHAPY TV",        "frequency": 11179, "polarization": "Horizontal", "symbolRate": 27500},
    {"name": "MESAT",            "frequency": 11096, "polarization": "Horizontal", "symbolRate": 27500},
    {"name": "SAT-7 ARABIC",     "frequency": 11353, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "SAT-7 KIDS",       "frequency": 11353, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "AL HAYAT",         "frequency": 12207, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "AL HAYAT 2",       "frequency": 12207, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "NOURSAT",          "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "ALKARMA TV",       "frequency": 12073, "polarization": "Vertical",   "symbolRate": 27500},
    # ── إسلامية
    {"name": "QURAN KAREEM",     "frequency": 11727, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "RAHMA",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "MAJD",             "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "IQRAA",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "HUDA TV",          "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "WESAL",            "frequency": 11727, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "AL MAJD",          "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500},
    # ── مسلسلات ودراما
    {"name": "DRAMA MBC",        "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "MBC MASR 2",       "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "SHAHID",           "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "MASRAWI DRAMA",    "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "NILE DRAMA",       "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "AL HAYAH DRAMA",   "frequency": 12092, "polarization": "Vertical",   "symbolRate": 27500},
    # ── أفلام
    {"name": "ROTANA CINEMA",    "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "ROTANA CLASSIC",   "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "MBC 2",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "MBC 4",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "MBC MAX",          "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "NILE CINEMA",      "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "FOX MOVIES",       "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500},
    # ── أطفال
    {"name": "SPACE TOON",       "frequency": 11727, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "MAJID",            "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "TOYOR ALJANNAH",   "frequency": 11179, "polarization": "Horizontal", "symbolRate": 27500},
    {"name": "CARTOON NETWORK",  "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "BABY TV",          "frequency": 11727, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "MBC3",             "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    # ── رياضة
    {"name": "ON TIME SPORTS 1", "frequency": 11861, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "ON TIME SPORTS 2", "frequency": 11861, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "SSC SPORT 1",      "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "SSC SPORT 2",      "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "AD SPORTS",        "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "BEIN SPORTS 1",    "frequency": 11054, "polarization": "Horizontal", "symbolRate": 27500},
    {"name": "BEIN SPORTS 2",    "frequency": 11054, "polarization": "Horizontal", "symbolRate": 27500},
    {"name": "NILE SPORT",       "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500},
    # ── أخبار
    {"name": "AL JAZEERA HD",    "frequency": 10853, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "AL ARABIYA",       "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "AL HADATH",        "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "CBC",              "frequency": 12092, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "EXTRA NEWS",       "frequency": 12092, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "ON E",             "frequency": 12092, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "SKY NEWS ARABIA",  "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "BBC ARABIC",       "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "CAIRO NEWS",       "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "SADA ELBALAD",     "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500},
    # ── عامة ومنوعات
    {"name": "MBC 1",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "MBC MASR",         "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "NILE FAMILY",      "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "AL HAYAH",         "frequency": 12092, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "DMC",              "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "DMC DRAMA",        "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "AL NAHAR",         "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "AL NAHAR DRAMA",   "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500},
    {"name": "TEN",              "frequency": 12073, "polarization": "Vertical",   "symbolRate": 27500},
]

def ai_classify(channel_name):
    name = channel_name.upper().strip()
    CHRISTIAN_KW = ["CTV", "AGHAPY", "MESAT", "KARMA", "ALKARMA", "NOURSAT", "SAT-7", "SAT7", "AL HAYAT", "HAYAT TV", "MIRACLE", "COPTIC", "CHURCH"]
    if any(w in name for w in CHRISTIAN_KW): return ALL_AVAILABLE_CATEGORIES[0]
    ISLAMIC_KW = ["QURAN", "RAHMA", "MAJD", "MAKKA", "IQRAA", "IQRA", "HUDA", "WESAL", "ISLAM", "SUNNAH"]
    if any(w in name for w in ISLAMIC_KW): return ALL_AVAILABLE_CATEGORIES[1]
    DRAMA_KW = ["MOSALSALAT", "DRAMA", "SERIES", "KHOLASA", "MASRAWI", "SHAHID"]
    if any(w in name for w in DRAMA_KW): return ALL_AVAILABLE_CATEGORIES[2]
    MOVIE_KW = ["CINEMA", "ROTANA", "AFLAM", "MIX", "FOX", "MBC2", "MBC 2", "MBC4", "MBC 4", "MBC MAX", "ACTION", "RAMBO", "MOVIE", "FILM", "COMEDY"]
    if any(w in name for w in MOVIE_KW): return ALL_AVAILABLE_CATEGORIES[3]
    KIDS_KW = ["SPACE TOON", "SPACETOON", "CN", "CARTOON", "MAJID", "KIDS", "TOM", "TOYOR", "BABY", "JUNIOR", "MBC3"]
    if any(w in name for w in KIDS_KW): return ALL_AVAILABLE_CATEGORIES[4]
    SPORT_KW = ["SPORT", "SPORTS", "ONTIME", "ON TIME", "KASS", "AD_SPORTS", "AD SPORTS", "SSC", "BEIN", "MATCH"]
    if any(w in name for w in SPORT_KW): return ALL_AVAILABLE_CATEGORIES[5]
    NEWS_KW = ["NEWS", "JAZEERA", "ARABIYA", "HADATH", "CAIRO", "SKY NEWS", "BBC", "CNN", "EXTRA NEWS", "CBC", "ON E", "SADA", "BALADI", "MASR"]
    if any(w in name for w in NEWS_KW): return ALL_AVAILABLE_CATEGORIES[6]
    return ALL_AVAILABLE_CATEGORIES[7]

# ── إحصائيات قاعدة البيانات ──
cat_counts = {}
for ch in FULL_CHANNEL_DB:
    cat = ai_classify(ch["name"])
    cat_counts[cat] = cat_counts.get(cat, 0) + 1

st.write("---")
st.write(f"### {t['db_stats_title']}")
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.markdown(f'<div class="stat-card"><div class="stat-num">{len(FULL_CHANNEL_DB)}</div><div class="stat-label">{t["total_channels"]}</div></div>', unsafe_allow_html=True)
with col_s2:
    st.markdown(f'<div class="stat-card"><div class="stat-num">{len(ALL_AVAILABLE_CATEGORIES)}</div><div class="stat-label">{t["total_cats"]}</div></div>', unsafe_allow_html=True)
with col_s3:
    st.markdown(f'<div class="stat-card"><div class="stat-num">🛰️</div><div class="stat-label">NileSat 7W + ArabSat</div></div>', unsafe_allow_html=True)
with col_s4:
    st.markdown(f'<div class="stat-card"><div class="stat-num">LG</div><div class="stat-label">Compatible (.TLL)</div></div>', unsafe_allow_html=True)

# ── اختيار موديل الشاشة ──
st.write("---")
selected_model = st.selectbox(t['model_select_label'], options=t['model_options'])

# ── محرك البحث في قاعدة البيانات ──
st.write("---")
st.write(f"### {t['search_header']}")
search_query = st.text_input("", placeholder=t['search_placeholder']).strip().upper()
if search_query:
    results = []
    for idx, ch in enumerate(FULL_CHANNEL_DB, start=1):
        if search_query in ch["name"].upper():
            results.append({
                t['search_col_num']: idx,
                t['search_col_name']: ch["name"],
                t['search_col_cat']: ai_classify(ch["name"]),
                t['search_col_freq']: f"{ch['frequency']} MHz ({ch['polarization']})"
            })
    if results: st.table(results)
    else: st.warning(t['search_no_results'])

# ── مصفوفة ترتيب الفئات ──
st.write("---")
st.write(f"### {t['config_title']}")
st.info(t['config_tip'])
user_priority = st.multiselect(t['multiselect_label'], options=ALL_AVAILABLE_CATEGORIES, default=[])
final_priority = list(user_priority)
for cat in ALL_AVAILABLE_CATEGORIES:
    if cat not in final_priority:
        final_priority.append(cat)

# ── ترتيب القنوات حسب الأولوية ──
channels_sorted = sorted(FULL_CHANNEL_DB, key=lambda x: final_priority.index(ai_classify(x["name"])))

# ── المعاينة الحية ──
categorized = {}
for ch in channels_sorted:
    cat = ai_classify(ch["name"])
    if cat not in categorized: categorized[cat] = []
    categorized[cat].append(f"{ch['name']} ({ch['frequency']} MHz)")

st.write("---")
st.write(f"### {t['preview_title']}")
col1, col2 = st.columns(2)
for i, cat_name in enumerate(final_priority):
    if cat_name in categorized:
        ch_list = categorized[cat_name]
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            is_user_chosen = "⭐ " if cat_name in user_priority else ""
            with st.expander(f"{is_user_chosen}{cat_name} — ({len(ch_list)} {t['channels_count']})"):
                st.write(", ".join(ch_list))

# ── زر التوليد ──
st.write("---")
if st.button(t['btn_generate'], use_container_width=True):

    # ══ بناء XML للشاشات الحديثة (نموذج JSON داخل legacybroadcast) ══
    channel_list_json = []
    for rank, ch in enumerate(channels_sorted, start=1):
        channel_list_json.append({
            "majorNumber": rank,
            "minorNumber": 0,
            "channelName": ch["name"],
            "frequency": ch["frequency"],
            "polarization": ch["polarization"],
            "symbolRate": ch.get("symbolRate", 27500),
            "serviceType": "1",
            "invisible": 0,
            "lockMode": 0,
            "skipMode": 0,
            "sourceIndex": 3,
            "ptcNumber": rank
        })

    broadcast_data = {
        "schemaVersion": "1.0",
        "regionType": "SATELLITE",
        "channelList": channel_list_json
    }

    # ══ بناء الهيكل الـ XML الكامل ══
    root_xml = ET.Element("TLLDATA")
    model_node = ET.SubElement(root_xml, "ModelName")
    model_node.text = selected_model

    legacy_node = ET.SubElement(root_xml, "legacybroadcast")
    legacy_node.text = json.dumps(broadcast_data, ensure_ascii=False, separators=(',', ':'))

    # إضافة XML declaration
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_body = ET.tostring(root_xml, encoding="unicode")
    final_xml_str = xml_declaration + xml_body
    final_tll_bytes = final_xml_str.encode('utf-8')

    # ══ بناء التقرير النصي ══
    txt_report = f"{t['txt_header']} ({selected_model})\n" + "=" * 55 + "\n"
    txt_report += f"{t['txt_order']}" + " → ".join(final_priority) + "\n" + "=" * 55 + "\n\n"
    for rank, ch in enumerate(channels_sorted, start=1):
        cat = ai_classify(ch["name"])
        txt_report += f"No. {rank:03d} : {ch['name']:<28} | Freq: {ch['frequency']} MHz | {ch['polarization']:<10} | {cat}\n"

    # ══ عرض رسالة النجاح ══
    st.success(t['ready_msg'])

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(
            label=t['btn_download_tll'],
            data=final_tll_bytes,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream"
        )
    with col_btn2:
        st.download_button(
            label=t['btn_download_txt'],
            data=txt_report,
            file_name="Channels_List_Generated.txt",
            mime="text/plain; charset=utf-8"
        )

    # ── الملحوظة الفنية ──
    st.markdown(f"""
        <div class="lg-trick-box">
            <h4 style="color: #ff007f; margin-top:0;">{t['lg_trick_title']}</h4>
            <p style="white-space: pre-line; margin-bottom:0; font-size:15px; line-height: 1.6;">{t['lg_trick_text']}</p>
        </div>
    """, unsafe_allow_html=True)

# ── الفوتر الفني ──
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
