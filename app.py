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
    bg_style = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
    text_color = "#1a73e8"
    box_bg = "rgba(255, 255, 255, 0.95)"
    box_border = "#1a73e8"
    box_shadow = "rgba(26, 115, 232, 0.25)"
    text_shadow_glow = "none"
    footer_bg = "#e8eaed"
    footer_text = "#202124"

# Inject CSS
st.markdown(f"""
    <style>
        .stApp {{ background: {bg_style}; }}
        h1, h2, h3, .title-text {{ color: {text_color}; text-shadow: {text_shadow_glow}; }}
        .cyber-box {{ background: {box_bg}; border: 1px solid {box_border}; border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px {box_shadow}; }}
        .stTextInput > div > div > input {{ background: {box_bg}; color: {text_color}; border: 1px solid {box_border}; }}
        .futuristic-cyber-footer {{ background: {footer_bg}; padding: 20px; border-radius: 10px; margin-top: 30px; text-align: center; color: {footer_text}; }}
        .cyber-whatsapp-btn {{ display: inline-block; background: #25D366; color: white; padding: 10px 20px; border-radius: 25px; text-decoration: none; margin-top: 10px; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f"<h1 class='title-text'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:{text_color}; font-size:18px;'>{t['subtitle']}</p>", unsafe_allow_html=True)

# ── قاعدة بيانات الأقمار الحية ──
NILESAT_LIVE_DB = {
    "AL NILET": {"frequency": 11766, "category": "News"},
    "AL NILET NEWS": {"frequency": 11766, "category": "News"},
    "NILE TV": {"frequency": 11766, "category": "National"},
    "AL OULA": {"frequency": 11488, "category": "National"},
    "AL OULA 2": {"frequency": 11488, "category": "National"},
    "AL MASRYIA": {"frequency": 11488, "category": "National"},
    "ON TV": {"frequency": 11823, "category": "Private"},
    "ON E": {"frequency": 11823, "category": "Private"},
    "DMC": {"frequency": 11296, "category": "Private"},
    "DMC DRAMA": {"frequency": 11296, "category": "Drama"},
    "CBC": {"frequency": 11938, "category": "Private"},
    "CBC SOFRA": {"frequency": 11938, "category": "Drama"},
    "EXTRA NEWS": {"frequency": 12149, "category": "News"},
    "AL ARABIYA": {"frequency": 12149, "category": "News"},
    "AL-HADATH": {"frequency": 12149, "category": "News"},
    "AL JAZEERA": {"frequency": 12284, "category": "News"},
    "AL JAZEERA DOCUMENTARY": {"frequency": 12284, "category": "Documentary"},
    "MBC": {"frequency": 11476, "category": "Private"},
    "MBC DRAMA": {"frequency": 11476, "category": "Drama"},
    "MBC MAX": {"frequency": 11476, "category": "Drama"},
    "ROTANA": {"frequency": 11585, "category": "Music"},
    "ROTANA DRAMA": {"frequency": 11585, "category": "Drama"},
    "ROTANA CLIP": {"frequency": 11585, "category": "Music"},
    "MEKAMLEK": {"frequency": 12034, "category": "Drama"},
    "ALHAYA": {"frequency": 12034, "category": "Drama"},
    "STAR MOVIES": {"frequency": 11938, "category": "Movies"},
    "MOVIE PL": {"frequency": 11938, "category": "Movies"},
    "FOX": {"frequency": 11296, "category": "Movies"},
    "FX": {"frequency": 11296, "category": "Movies"},
    "HBO": {"frequency": 11179, "category": "Movies"},
    "NETFLIX": {"frequency": 11179, "category": "Movies"},
    "STARZ": {"frequency": 11179, "category": "Movies"},
    "OSN": {"frequency": 11179, "category": "Movies"},
    "WEEN": {"frequency": 11823, "category": "Comedy"},
    "AL-MORF": {"frequency": 11823, "category": "Comedy"},
    "TEAM TOO": {"frequency": 11823, "category": "Kids"},
    "TOYOR AL JANAA": {"frequency": 11823, "category": "Kids"},
    "SPACETOON": {"frequency": 11823, "category": "Kids"},
    "CARTOON NETWORK": {"frequency": 11823, "category": "Kids"},
    "NICKELODEON": {"frequency": 11823, "category": "Kids"},
    "BEJUNIOR": {"frequency": 11823, "category": "Kids"},
    "MASSRER": {"frequency": 11958, "category": "Sports"},
    "ON SPORT": {"frequency": 11958, "category": "Sports"},
    "BEIN SPORTS": {"frequency": 11013, "category": "Sports"},
    "BEIN SPORTS XTRA": {"frequency": 11013, "category": "Sports"},
    "KORA": {"frequency": 11804, "category": "Sports"},
    "ALKASS": {"frequency": 11804, "category": "Sports"},
}

def ai_classify(ch_name):
    ch_upper = ch_name.upper()
    for db_name, info in NILESAT_LIVE_DB.items():
        if db_name in ch_upper or ch_upper in db_name:
            return info.get("category", "Other")
    return "Other"

# ── واجهة التحميل ──
st.markdown("---")
col_upload1, col_upload2 = st.columns([3, 1])
with col_upload1:
    st.markdown(f"<div style='color:{text_color}; font-size:16px; margin-bottom:5px;'>{t['upload_label']}</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload", type=["tll", "xml", "txt"], label_visibility="collapsed")

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    try:
        file_text = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        file_text = file_bytes.decode('latin-1')

    item_blocks = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)
    items_list_preview = []
    for item_str in item_blocks:
        name_match = re.search(r'<vchName>(.*?)</vchName>', item_str)
        freq_match = re.search(r'<frequency>(.*?)</frequency>', item_str)
        cat_match = re.search(r'<category>(.*?)</category>', item_str)
        if name_match:
            ch_name = name_match.group(1)
            cat = cat_match.group(1) if cat_match else ai_classify(ch_name)
            freq = freq_match.group(1) if freq_match else "N/A"
            items_list_preview.append({"num": len(items_list_preview) + 1, "name": ch_name, "cat": cat, "freq": freq})

    st.success(t['success_read'] + f" {len(items_list_preview)} {t['channels_count']}")

    # ── محركات البحث ──
    st.markdown("---")
    st.markdown(f"<div class='cyber-box' style='margin: 15px 0;'><h3 style='color:{text_color}; margin-bottom:15px;'>{t['search_header']}</h3>", unsafe_allow_html=True)
    with st.container():
        search_query = st.text_input(t['search_placeholder'], label_visibility="collapsed", key="search_input_main")

    if search_query:
        filtered = [ch for ch in items_list_preview if search_query.upper() in ch["name"].upper()]
        if filtered:
            st.dataframe(filtered, use_container_width=True)
        else:
            st.warning(t['search_no_results'])

    st.markdown("</div>", unsafe_allow_html=True)

    # ── الإعدادات ──
    st.markdown("---")
    st.markdown(f"<div class='cyber-box' style='margin: 15px 0;'><h3 style='color:{text_color}; margin-bottom:10px;'>{t['config_title']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{text_color}; font-size:14px;'>{t['config_tip']}</p>", unsafe_allow_html=True)

    default_order = ["News", "National", "Private", "Drama", "Movies", "Sports
