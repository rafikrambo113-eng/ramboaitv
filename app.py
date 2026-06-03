<think>
The user is saying that in the old files (legacy format), when they read the channel file and modify the categories, and then download the text file, it is sorted according to their choice. However, when downloading the channel file (TLL), nothing changes.

They want me to fix this part so that the TLL file is also sorted according to the user's category priority selection.

Let me analyze the code:

1. The code reads the file (either modern JSON-based or legacy ITEM-based)
2. It classifies channels into categories
3. It allows the user to select a priority order for categories
4. It sorts the channels based on this priority
5. It generates the text report sorted
6. It also needs to generate the TLL file sorted

Looking at the code, I can see the issue. For the modern format (is_modern = True), the code does sort and modify the channels properly:
```python
final_list_modern = []
for index, ch in enumerate(channels_sorted, start=1):
    node = ch["node_data"]
    node["majorNumber"] = index
    final_list_modern.append(node)
```

But for the legacy format (else branch), the code does try to sort and update the prNum:
```python
item_strings_sorted = []
for index, ch in enumerate(channels_sorted, start=1):
    raw = ch["raw_str"]
    if "<prNum>" in raw:
        raw = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{index}</prNum>', raw)
    else:
        raw = raw.replace("<ITEM>", f"<ITEM>\r\n<prNum>{index}</prNum>")
    item_strings_sorted.append(raw)
```

However, the problem might be that:
1. The prNum might not exist in the original file, so it's being added but maybe not correctly
2. The XML structure might be different than expected
3. There might be an issue with how the items are being reconstructed
 
I'll investigate the sorting mechanism and XML reconstruction process. The key is ensuring the channel order is preserved and correctly written back to the legacy file format. I'll verify the sorting logic and XML reconstruction steps to identify any potential issues with the ITEM tag processing.
</think>ليك الكود الكامل بعد الإصلاح:

```python
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
# 🛰️ DATABASE — نايل سات
# ══════════════════════════════════════════════
NILESAT_LIVE_DB = {
    "AL HAYAT":         {"frequency": 12207, "polarization": "Vertical"},
    "AL HAYAT 2":       {"frequency": 12207, "polarization": "Vertical"},
    "SAT-7 KIDS":       {"frequency": 11353, "polarization": "Vertical"},
    "SAT-7 ARABIC":     {"frequency": 11353, "polarization": "Vertical"},
    "CTV":              {"frequency": 12022, "polarization": "Vertical"},
    "AGHAPY TV":        {"frequency": 11179, "polarization": "Horizontal"},
    "MESAT":            {"frequency": 11096, "polarization": "Horizontal"},
    "IQRAA":            {"frequency": 11938, "polarization": "Vertical"},
    "MAJD":             {"frequency": 11862, "polarization": "Vertical"},
    "RAHMA":            {"frequency": 11938, "polarization": "Vertical"},
    "QURAN KAREEM":     {"frequency": 11727, "polarization": "Vertical"},
    "AL JAZEERA HD":    {"frequency": 10853, "polarization": "Vertical"},
    "AL ARABIYA":       {"frequency": 11938, "polarization": "Vertical"},
    "AL HADATH":        {"frequency": 11938, "polarization": "Vertical"},
    "CBC":              {"frequency": 12092, "polarization": "Vertical"},
    "EXTRA NEWS":       {"frequency": 12092, "polarization": "Vertical"},
    "ON E":             {"frequency": 12092, "polarization": "Vertical"},
    "MBC 2":            {"frequency": 11938, "polarization": "Vertical"},
    "MBC 4":            {"frequency": 11938, "polarization": "Vertical"},
    "ROTANA CINEMA":    {"frequency": 11938, "polarization": "Vertical"},
    "ON TIME SPORTS 1": {"frequency": 11861, "polarization": "Vertical"},
    "ON TIME SPORTS 2": {"frequency": 11861, "polarization": "Vertical"},
    "SPACE TOON":       {"frequency": 11727, "polarization": "Vertical"},
    "MAJID":            {"frequency": 11862, "polarization": "Vertical"},
    "TOYOR ALJANNAH":   {"frequency": 11179, "polarization": "Horizontal"}
}

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
    KIDS_KW = ["SPACE TOON", "SPACETOON", "CN", "CARTOON", "MAJID", "KIDS", "TOM", "TOYOR", "BABY", "JUNIOR"]
    if any(w in name for
