
# Build the FIXED Streamlit app - no file writing, memory-only

code = r'''import streamlit as st
import xml.etree.ElementTree as ET
import json
import io

# ── تهيئة الجلسة ──
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# ══════════════════════════════════════════════
# 🌍 قواعد البيانات المنفصلة حسب البلد
# ══════════════════════════════════════════════

# ── قاعدة بيانات مصر (NileSat 7W) ──
EGYPT_CHANNEL_DB = [
    # ⛪ مسيحية
    {"name": "CTV",              "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AGHAPY TV",        "frequency": 11179, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MESAT",            "frequency": 11096, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SAT-7 ARABIC",     "frequency": 11353, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SAT-7 KIDS",       "frequency": 11353, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL HAYAT",         "frequency": 12207, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL HAYAT 2",       "frequency": 12207, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "NOURSAT",          "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "ALKARMA TV",       "frequency": 12073, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    # 🕌 إسلامية
    {"name": "QURAN KAREEM",     "frequency": 11727, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "RAHMA",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MAJD",             "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "IQRAA",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "HUDA TV",          "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "WESAL",            "frequency": 11727, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL MAJD",          "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    # 🎬 مسلسلات ودراما
    {"name": "DRAMA MBC",        "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC MASR 2",       "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SHAHID",           "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MASRAWI DRAMA",    "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "NILE DRAMA",       "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL HAYAH DRAMA",   "frequency": 12092, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    # 🍿 أفلام
    {"name": "ROTANA CINEMA",    "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "ROTANA CLASSIC",   "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC 2",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC 4",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC MAX",          "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "NILE CINEMA",      "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "FOX MOVIES",       "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    # 👶 أطفال
    {"name": "SPACE TOON",       "frequency": 11727, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MAJID",            "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "TOYOR ALJANNAH",   "frequency": 11179, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "CARTOON NETWORK",  "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "BABY TV",          "frequency": 11727, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC3",             "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    # ⚽ رياضة
    {"name": "ON TIME SPORTS 1", "frequency": 11861, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "ON TIME SPORTS 2", "frequency": 11861, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SSC SPORT 1",      "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SSC SPORT 2",      "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AD SPORTS",        "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "BEIN SPORTS 1",    "frequency": 11054, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "BEIN SPORTS 2",    "frequency": 11054, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "NILE SPORT",       "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    # 📰 أخبار
    {"name": "AL JAZEERA HD",    "frequency": 10853, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL ARABIYA",       "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL HADATH",        "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "CBC",              "frequency": 12092, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "EXTRA NEWS",       "frequency": 12092, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "ON E",             "frequency": 12092, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SKY NEWS ARABIA",  "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "BBC ARABIC",       "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "CAIRO NEWS",       "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SADA ELBALAD",     "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    # 📺 عامة ومنوعات
    {"name": "MBC 1",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC MASR",         "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "NILE FAMILY",      "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL HAYAH",         "frequency": 12092, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "DMC",              "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "DMC DRAMA",        "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL NAHAR",         "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL NAHAR DRAMA",   "frequency": 12022, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "TEN",              "frequency": 12073, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
]

# ── قاعدة بيانات السعودية (ArabSat 26E + NileSat) ──
SAUDI_CHANNEL_DB = [
    # ⛪ مسيحية
    {"name": "SAT-7 ARABIC",     "frequency": 11353, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SAT-7 KIDS",       "frequency": 11353, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "NOURSAT",          "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    # 🕌 إسلامية
    {"name": "QURAN KAREEM",     "frequency": 11727, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MAJD",             "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "IQRAA",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SAUDI QURAN",      "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    {"name": "SAUDI SUNNAH",     "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    {"name": "MAKKAH TV",        "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    {"name": "MADINAH TV",       "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    # 🎬 مسلسلات ودراما
    {"name": "DRAMA MBC",        "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC MASR 2",       "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SHAHID",           "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "NILE DRAMA",       "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SBC DRAMA",        "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    # 🍿 أفلام
    {"name": "ROTANA CINEMA",    "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "ROTANA CLASSIC",   "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC 2",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC 4",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC MAX",          "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "ROTANA AFLAM+",    "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    # 👶 أطفال
    {"name": "SPACE TOON",       "frequency": 11727, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MAJID",            "frequency": 11862, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "CARTOON NETWORK",  "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "BABY TV",          "frequency": 11727, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC3",             "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SPACETOON",        "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    # ⚽ رياضة
    {"name": "SSC SPORT 1",      "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SSC SPORT 2",      "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AD SPORTS",        "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "BEIN SPORTS 1",    "frequency": 11054, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "BEIN SPORTS 2",    "frequency": 11054, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SAUDI SPORT 1",    "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    {"name": "SAUDI SPORT 2",    "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    {"name": "KSA SPORTS 1",     "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    # 📰 أخبار
    {"name": "AL JAZEERA HD",    "frequency": 10853, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL ARABIYA",       "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL HADATH",        "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SKY NEWS ARABIA",  "frequency": 11785, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "BBC ARABIC",       "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "AL EKHBARIYA",     "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    {"name": "SAUDI NEWS",       "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    # 📺 عامة ومنوعات
    {"name": "MBC 1",            "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "MBC MASR",         "frequency": 11938, "polarization": "Vertical",   "symbolRate": 27500, "satellite": "NileSat 7W"},
    {"name": "SBC",              "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    {"name": "THIKRAYAT TV",     "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    {"name": "ROTANA KHALIJIAH", "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
    {"name": "ROTANA MUSIC",     "frequency": 12149, "polarization": "Horizontal", "symbolRate": 27500, "satellite": "ArabSat 26E"},
]

# ══════════════════════════════════════════════
# 🎛️ إعدادات LG حسب النظام والموديل
# ══════════════════════════════════════════════

LG_MODELS = {
    "Legacy": {
        "description_ar": "نظام قديم (2014-2019) — XML nodes",
        "description_en": "Legacy System (2014-2019) — XML nodes",
        "models": ["43LM6300", "49UF6409", "55LB630V", "55UH605V", "65UB950V", "OLED65E7V"],
        "format": "legacy_xml"
    },
    "Modern": {
        "description_ar": "نظام حديث (2020+) — JSON in legacybroadcast",
        "description_en": "Modern System (2020+) — JSON in legacybroadcast",
        "models": ["UA85006LA", "55CX6LA", "65C8PLA", "OLED77CS9LA", "55OLEDC9PLA", "50UP7550", "55UN7340PVA", "65NANO80"],
        "format": "modern_json"
    }
}

LG_SCREEN_SIZES = ["43", "50", "55", "65", "75", "86"]

BROADCAST_COUNTRIES = {
    "ar": {"egypt": "🇪🇬 مصر", "saudi": "🇸🇦 السعودية", "both": "🌍 كلاهما"},
    "en": {"egypt": "🇪🇬 Egypt", "saudi": "🇸🇦 Saudi Arabia", "both": "🌍 Both"}
}

# ══════════════════════════════════════════════
# 📝 نصوص الواجهة
# ══════════════════════════════════════════════

UI_TEXT = {
    'ar': {
        'title': "📺 RAMBO — مولّد ملف القنوات من الصفر",
        'subtitle': "⚡ أنشئ ملف TLL جديد كلياً لشاشات LG بدون الحاجة لرفع ملف قديم",
        'intro_box': "🛰️ هذه الصفحة تقوم بتوليد ملف GlobalClone00001.TLL جديد تماماً من الصفر بالاعتماد على قاعدة بيانات القنوات المدمجة. اختر النظام والبلد والفئات وحدد الترتيب ثم حمّل الملف مباشرةً على الفلاشة.",
        'system_select_label': "⚙️ اختر نظام الشاشة:",
        'system_legacy': "نظام قديم (Legacy XML) — 2014-2019",
        'system_modern': "نظام حديث (Modern JSON) — 2020+",
        'country_select_label': "🌍 اختر بلد البث:",
        'size_select_label': "📐 اختر حجم الشاشة (بوصة):",
        'model_select_label': "📺 اختر موديل الشاشة:",
        'search_header': "🔍 محرك البحث الذكي في قاعدة البيانات المدمجة:",
        'search_placeholder': "اكتب اسم القناة للبحث في قاعدة البيانات...",
        'search_col_num': "الرقم",
        'search_col_name': "اسم القناة",
        'search_col_cat': "الفئة",
        'search_col_freq': "التردد",
        'search_col_sat': "القمر",
        'search_no_results': "⚠️ لم يتم العثور على قنوات مطابقة.",
        'config_title': "🎛️ مصفوفة ترتيب الفئات:",
        'config_tip': "💡 اختر الفئات بالترتيب الفعلي المفضل لديك — الأول سيظهر في أعلى القائمة على الشاشة.",
        'multiselect_label': "اضغط لبناء تسلسل ترتيب الفئات:",
        'preview_title': "📊 معاينة توزيع القنوات المولّدة:",
        'channels_count': "قناة",
        'db_stats_title': "📡 إحصائيات قاعدة البيانات المدمجة:",
        'total_channels': "إجمالي القنوات",
        'total_cats': "عدد الفئات",
        'btn_generate': "⚡ توليد الملف الآن",
        'ready_msg': "🌌 تم توليد ملف القنوات الجديد بنجاح! الملفات جاهزة للتحميل:",
        'btn_download_tll': "📥 تحميل ملف الشاشة الجديد (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 تحميل تقرير القنوات المولّدة (Channels_List.txt)",
        'txt_header': "📄 تقرير ملف القنوات المولّد من الصفر — RAMBO",
        'txt_order': "🛠️ ترتيب الفئات المختار: ",
        'txt_system': "⚙️ نظام الملف: ",
        'txt_country': "🌍 بلد البث: ",
        'txt_size': "📐 حجم الشاشة: ",
        'txt_model': "📺 الموديل: ",
        'lg_trick_title': "💡 ملحوظة فنية هامة بعد تنزيل الملف على شاشة LG:",
        'lg_trick_text': "في بعض الحالات، بعد تنزيل ملف القنوات على الشاشة، قد تشعر أن القنوات ليست منظمة كما رتبتها. لحل هذا الأمر فوراً واجبار الشاشة على تفعيل الترتيب الصحيح، قم بالآتي:\n1. من إعدادات التلفزيون اختار القنوات (Channels).\n2. بعد ذلك اختار مدير القنوات (Channel Manager).\n3. اختار التعديل على كل القنوات (Edit All Channels).\n4. ستظهر لك القنوات المرتبة ويكون بعضها في وضع مخفي، قم بتحديد كل القنوات واختار استعادة (Restore).\n*ملحوظة: تفعل هذه الخطوة فقط إذا شعرت أن الملف بعد التنزيل غير مرتب كما حددته على الموقع.*",
        'page_badge': "الصفحة 3 — مولّد متقدم",
        'warning_no_priority': "⚠️ لم تقم باختيار أي فئة. سيتم استخدام الترتيب الافتراضي."
    },
    'en': {
        'title': "📺 RAMBO — Channel File Generator (From Scratch)",
        'subtitle': "⚡ Build a brand-new TLL file for LG TVs — No upload required",
        'intro_box': "🛰️ This page generates a complete GlobalClone00001.TLL file from scratch using the built-in satellite channel database. Just choose the system, country, categories, set the order, and download directly to your USB drive.",
        'system_select_label': "⚙️ Select TV System:",
        'system_legacy': "Legacy System (XML) — 2014-2019",
        'system_modern': "Modern System (JSON) — 2020+",
        'country_select_label': "🌍 Select Broadcast Country:",
        'size_select_label': "📐 Select Screen Size (inch):",
        'model_select_label': "📺 Select Your TV Model:",
        'search_header': "🔍 Smart Search Engine in Built-in Database:",
        'search_placeholder': "Search channel name in database...",
        'search_col_num': "No.",
        'search_col_name': "Channel Name",
        'search_col_cat': "Category",
        'search_col_freq': "Frequency",
        'search_col_sat': "Satellite",
        'search_no_results': "⚠️ No matching channels found.",
        'config_title': "🎛️ Category Sorting Priority Matrix:",
        'config_tip': "💡 Select categories in your preferred order — first selected = top of your TV list.",
        'multiselect_label': "Click to build your category order sequence:",
        'preview_title': "📊 Live Channel Distribution Preview:",
        'channels_count': "Channels",
        'db_stats_title': "📡 Built-in Database Statistics:",
        'total_channels': "Total Channels",
        'total_cats': "Number of Categories",
        'btn_generate': "⚡ Generate File Now",
        'ready_msg': "🌌 New channel file generated successfully! Ready for download:",
        'btn_download_tll': "📥 Download New TV File (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 Download Generated Channel Report (Channels_List.txt)",
        'txt_header': "📄 From-Scratch Channel File Report — RAMBO",
        'txt_order': "🛠️ Selected Category Priority: ",
        'txt_system': "⚙️ File System: ",
        'txt_country': "🌍 Broadcast Country: ",
        'txt_size': "📐 Screen Size: ",
        'txt_model': "📺 Model: ",
        'lg_trick_title': "💡 Critical Technical Tip After Uploading to LG TV:",
        'lg_trick_text': "In some cases, after importing the file into your LG TV, the channels might not appear perfectly sorted. To fix this:\n1. Open TV Settings -> Channels.\n2. Select Channel Manager.\n3. Choose Edit All Channels.\n4. Select All Channels and click Restore.\n*Note: Only required if the TV cache mixed the sorting order after USB upload.*",
        'page_badge': "Page 3 — Advanced Generator",
        'warning_no_priority': "⚠️ No categories selected. Default order will be used."
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
    .main {{ background: {bg_style} !important; color: {text_color} !important; font-family: {{ "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif" }}; }}
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
    .system-badge {{ background: linear-gradient(135deg, #ff007f33, #00f0ff33); border: 1px solid #ff007f55; border-radius: 8px; padding: 2px 10px; font-size: 11px; color: #ff007f; display: inline-block; margin-left: 8px; }}
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
# 🎛️ اختيارات النظام والبلد والحجم
# ══════════════════════════════════════════════

st.write("---")
st.write(f"### ⚙️ {t['system_select_label']}")

col_sys1, col_sys2 = st.columns(2)
with col_sys1:
    system_type = st.radio(
        "",
        options=["Legacy", "Modern"],
        format_func=lambda x: t['system_legacy'] if x == "Legacy" else t['system_modern'],
        horizontal=True,
        index=1
    )

with col_sys2:
    st.info(LG_MODELS[system_type]["description_ar"] if st.session_state.lang == 'ar' else LG_MODELS[system_type]["description_en"])

st.write("---")
col_country, col_size, col_model = st.columns(3)

with col_country:
    country_key = st.selectbox(
        t['country_select_label'],
        options=["egypt", "saudi", "both"],
        format_func=lambda x: BROADCAST_COUNTRIES[st.session_state.lang][x]
    )

with col_size:
    screen_size = st.selectbox(t['size_select_label'], options=LG_SCREEN_SIZES, index=2)

with col_model:
    available_models = LG_MODELS[system_type]["models"]
    selected_model = st.selectbox(t['model_select_label'], options=available_models)

# ── تحديد قاعدة البيانات النشطة ──
if country_key == "egypt":
    FULL_CHANNEL_DB = EGYPT_CHANNEL_DB
    country_display = "🇪🇬 مصر" if st.session_state.lang == 'ar' else "🇪🇬 Egypt"
elif country_key == "saudi":
    FULL_CHANNEL_DB = SAUDI_CHANNEL_DB
    country_display = "🇸🇦 السعودية" if st.session_state.lang == 'ar' else "🇸🇦 Saudi Arabia"
else:
    seen = set()
    FULL_CHANNEL_DB = []
    for ch in EGYPT_CHANNEL_DB + SAUDI_CHANNEL_DB:
        if ch["name"] not in seen:
            seen.add(ch["name"])
            FULL_CHANNEL_DB.append(ch)
    country_display = "🌍 كلاهما" if st.session_state.lang == 'ar' else "🌍 Both"

# ══════════════════════════════════════════════
# 🏷️ الفئات المتاحة
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

def ai_classify(channel_name):
    name = channel_name.upper().strip()
    if name in ["MBC MASR", "MBC1", "MBC 1"]:
        return ALL_AVAILABLE_CATEGORIES[7]
    CHRISTIAN_KW = ["CTV", "AGHAPY", "MESAT", "KARMA", "ALKARMA", "NOURSAT", "SAT-7", "SAT7", "AL HAYAT", "HAYAT TV", "MIRACLE", "COPTIC", "CHURCH"]
    if any(w in name for w in CHRISTIAN_KW): return ALL_AVAILABLE_CATEGORIES[0]
    ISLAMIC_KW = ["QURAN", "RAHMA", "MAJD", "MAKKA", "IQRAA", "IQRA", "HUDA", "WESAL", "ISLAM", "SUNNAH", "MADINAH"]
    if any(w in name for w in ISLAMIC_KW): return ALL_AVAILABLE_CATEGORIES[1]
    DRAMA_KW = ["MOSALSALAT", "DRAMA", "SERIES", "KHOLASA", "MASRAWI", "SHAHID"]
    if any(w in name for w in DRAMA_KW): return ALL_AVAILABLE_CATEGORIES[2]
    MOVIE_KW = ["CINEMA", "ROTANA", "AFLAM", "MIX", "FOX", "MBC2", "MBC 2", "MBC4", "MBC 4", "MBC MAX", "ACTION", "RAMBO", "MOVIE", "FILM", "COMEDY"]
    if any(w in name for w in MOVIE_KW): return ALL_AVAILABLE_CATEGORIES[3]
    KIDS_KW = ["SPACE TOON", "SPACETOON", "CN", "CARTOON", "MAJID", "KIDS", "TOM", "TOYOR", "BABY", "JUNIOR", "MBC3"]
    if any(w in name for w in KIDS_KW): return ALL_AVAILABLE_CATEGORIES[4]
    SPORT_KW = ["SPORT", "SPORTS", "ONTIME", "ON TIME", "KASS", "AD_SPORTS", "AD SPORTS", "SSC", "BEIN", "MATCH", "KSA SPORTS"]
    if any(w in name for w in SPORT_KW): return ALL_AVAILABLE_CATEGORIES[5]
    NEWS_KW = ["NEWS", "JAZEERA", "ARABIYA", "HADATH", "CAIRO", "SKY NEWS", "BBC", "CNN", "EXTRA NEWS", "CBC", "ON E", "SADA", "BALADI", "EKHBARIYA"]
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
    sat_label = "NileSat 7W" if country_key == "egypt" else ("ArabSat 26E" if country_key == "saudi" else "Multi-Sat")
    st.markdown(f'<div class="stat-card"><div class="stat-num">🛰️</div><div class="stat-label">{sat_label}</div></div>', unsafe_allow_html=True)
with col_s4:
    st.markdown(f'<div class="stat-card"><div class="stat-num">LG</div><div class="stat-label">{system_type} .TLL</div></div>', unsafe_allow_html=True)

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
                t['search_col_freq']: f"{ch['frequency']} MHz ({ch['polarization']})",
                t['search_col_sat']: ch.get("satellite", "N/A")
            })
    if results: st.table(results)
    else: st.warning(t['search_no_results'])

# ── مصفوفة ترتيب الفئات ──
st.write("---")
st.write(f"### {t['config_title']}")
st.info(t['config_tip'])
user_priority = st.multiselect(t['multiselect_label'], options=ALL_AVAILABLE_CATEGORIES, default=[])
if len(user_priority) == 0:
    st.warning(t['warning_no_priority'])

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

# ══════════════════════════════════════════════
# 🔧 دوال بناء الملفات
# ══════════════════════════════════════════════

def build_legacy_xml(channels_sorted, model_name, screen_size, country):
    """بناء ملف TLL بنظام Legacy (XML nodes) — للشاشات 2014-2019"""
    root = ET.Element("TLLDATA")
    
    meta = ET.SubElement(root, "MetaData")
    ET.SubElement(meta, "ModelName").text = model_name
    ET.SubElement(meta, "ScreenSize").text = f"{screen_size}inch"
    ET.SubElement(meta, "Country").text = country
    ET.SubElement(meta, "SystemType").text = "Legacy"
    ET.SubElement(meta, "SchemaVersion").text = "1.0"
    
    ch_list = ET.SubElement(root, "ChannelList")
    for rank, ch in enumerate(channels_sorted, start=1):
        ch_node = ET.SubElement(ch_list, "Channel")
        ET.SubElement(ch_node, "prNum").text = str(rank)
        ET.SubElement(ch_node, "name").text = ch["name"]
        ET.SubElement(ch_node, "frequency").text = str(ch["frequency"])
        ET.SubElement(ch_node, "polarization").text = ch["polarization"]
        ET.SubElement(ch_node, "symbolRate").text = str(ch.get("symbolRate", 27500))
        ET.SubElement(ch_node, "serviceType").text = "1"
        ET.SubElement(ch_node, "invisible").text = "0"
        ET.SubElement(ch_node, "lockMode").text = "0"
        ET.SubElement(ch_node, "skipMode").text = "0"
        ET.SubElement(ch_node, "sourceIndex").text = "3"
        ET.SubElement(ch_node, "ptcNumber").text = str(rank)
        ET.SubElement(ch_node, "satellite").text = ch.get("satellite", "NileSat 7W")
    
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_body = ET.tostring(root, encoding="unicode")
    return (xml_declaration + xml_body).encode('utf-8')

def build_modern_json(channels_sorted, model_name, screen_size, country):
    """بناء ملف TLL بنظام Modern (JSON in legacybroadcast) — للشاشات 2020+"""
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
            "ptcNumber": rank,
            "satellite": ch.get("satellite", "NileSat 7W"),
            "country": country,
            "screenSize": f"{screen_size}inch"
        })

    broadcast_data = {
        "schemaVersion": "1.0",
        "regionType": "SATELLITE",
        "modelName": model_name,
        "screenSize": f"{screen_size}inch",
        "country": country,
        "systemType": "Modern",
        "channelList": channel_list_json
    }

    root_xml = ET.Element("TLLDATA")
    model_node = ET.SubElement(root_xml, "ModelName")
    model_node.text = model_name
    
    meta_node = ET.SubElement(root_xml, "MetaData")
    ET.SubElement(meta_node, "ScreenSize").text = f"{screen_size}inch"
    ET.SubElement(meta_node, "Country").text = country
    ET.SubElement(meta_node, "SystemType").text = "Modern"
    
    legacy_node = ET.SubElement(root_xml, "legacybroadcast")
    legacy_node.text = json.dumps(broadcast_data, ensure_ascii=False, separators=(',', ':'))

    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_body = ET.tostring(root_xml, encoding="unicode")
    return (xml_declaration + xml_body).encode('utf-8')

# ── زر التوليد ──
st.write("---")
if st.button(t['btn_generate'], use_container_width=True):

    # بناء الملف حسب النظام المختار
    if system_type == "Legacy":
        final_tll_bytes = build_legacy_xml(channels_sorted, selected_model, screen_size, country_display)
    else:
        final_tll_bytes = build_modern_json(channels_sorted, selected_model, screen_size, country_display)

    # ══ بناء التقرير النصي ══
    txt_report = f"{t['txt_header']}\n" + "=" * 60 + "\n"
    txt_report += f"{t['txt_system']}{system_type}\n"
    txt_report += f"{t['txt_country']}{country_display}\n"
    txt_report += f"{t['txt_size']}{screen_size} inch\n"
    txt_report += f"{t['txt_model']}{selected_model}\n"
    txt_report += f"{t['txt_order']}" + " → ".join(final_priority) + "\n" + "=" * 60 + "\n\n"
    for rank, ch in enumerate(channels_sorted, start=1):
        cat = ai_classify(ch["name"])
        sat = ch.get("satellite", "N/A")
        txt_report += f"No. {rank:03d} : {ch['name']:<28} | Freq: {ch['frequency']} MHz | {ch['polarization']:<10} | Sat: {sat:<12} | {cat}\n"

    # ══ عرض رسالة النجاح ══
    st.success(t['ready_msg'])
    
    st.markdown(f"""
    <div style="background:{intro_bg}; border:2px solid {intro_border}; border-radius:14px; padding:14px; margin-bottom:16px;">
        <p style="margin:0; font-size:14px; line-height:1.8;">
        <b>{t['txt_system']}</b> <span class="system-badge">{system_type}</span><br>
        <b>{t['txt_country']}</b> {country_display}<br>
        <b>{t['txt_size']}</b> {screen_size} inch<br>
        <b>{t['txt_model']}</b> {selected_model}<br>
        <b>{t['txt_order']}</b> {" → ".join(final_priority)}
        </p>
    </div>
    """, unsafe_allow_html=True)

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
'''

# Save to file
output_path = "/mnt/agents/output/page3_generate_fixed.py"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(code)

print(f"✅ File saved successfully!")
print(f"📁 Path: {output_path}")
print(f"📊 Lines: {len(code.splitlines())}")
print(f"📏 Size: {len(code):,} bytes")
print(f"\n🔍 Checking for 'open(' in code...")
open_count = code.count('open(')
print(f"   Found {open_count} occurrences of 'open('")
if open_count == 0:
    print("   ✅ SAFE: No file writing operations!")
else:
    print("   ⚠️ WARNING: Found open() calls!")
