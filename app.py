import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

UI_TEXT = {
    'ar': {
        'title': "RAMBO - المنسق العالمي لشاشات LG",
        'subtitle': "هندسة متطورة لترتيب ملفات القنوات بالتأثيرات السيبرانية مصفوفة (3D)",
        'upload_label': "اختر ملف القنوات (GlobalClone00001.TLL) من الفلاشة:",
        'update_freq_label': "تفعيل الصيانة الذكية وتحديث الترددات تلقائياً",
        'add_new_ch_label': "فحص وزرع القنوات الجديدة المتاحة تلقائياً",
        'success_read': "تم قراءة الهيكل بنجاح! الموديل الحالي: ",
        'search_header': "محرك البحث الذكي عن القنوات داخل الملف:",
        'search_placeholder': "اكتب اسم القناة هنا للبحث...",
        'search_col_num': "الرقم",
        'search_col_name': "اسم القناة",
        'search_col_cat': "الفئة",
        'search_col_freq': "التردد",
        'search_no_results': "لم يتم العثور على قنوات مطابقة.",
        'config_title': "مصفوفة ترتيب الفئات المخصصة:",
        'config_tip': "ملحوظة: اضغط على الفئات بالترتيب المفضل.",
        'multiselect_label': "اختر ترتيب الفئات:",
        'preview_title': "معاينة حية لتوزيع القنوات:",
        'channels_count': "قناة",
        'ready_msg': "تم اعادة الهيكلة بنجاح! الملفات جاهزة:",
        'btn_download_tll': "تحميل ملف الشاشة (TLL)",
        'btn_download_txt': "تحميل التقرير (TXT)",
        'txt_header': "تقرير الترتيب النهائي",
        'txt_order': "ترتيب الفئات: ",
        'lg_trick_title': "ملحوظة فنية بعد التنزيل على الشاشة:",
        'lg_trick_text': "لضمان ترتيب القنوات正确 بعد التنزيل: 1. ادخل الاعدادات ثم القنوات 2. مدير القنوات 3. تعديل على كل القنوات 4. حدد الكل واستعادة"
    },
    'en': {
        'title': "RAMBO - LG Universal Channel Sorter",
        'subtitle': "Next-Gen AI Architecture for Channel Layouts",
        'upload_label': "Upload Channel File (GlobalClone00001.TLL):",
        'update_freq_label': "Activate Frequency Auto-Update",
        'add_new_ch_label': "Scan and Inject New Channels",
        'success_read': "Structure Decoded! Model: ",
        'search_header': "Channel Search Engine:",
        'search_placeholder': "Type channel name...",
        'search_col_num': "No.",
        'search_col_name': "Channel Name",
        'search_col_cat': "Category",
        'search_col_freq': "Frequency",
        'search_no_results': "No matches found.",
        'config_title': "Custom Category Priority:",
        'config_tip': "Hint: Click categories in order.",
        'multiselect_label': "Select category order:",
        'preview_title': "Live Channel Preview:",
        'channels_count': "Channels",
        'ready_msg': "Quantum Matrix Ready! Assets:",
        'btn_download_tll': "Download TV Config (TLL)",
        'btn_download_txt': "Download Report (TXT)",
        'txt_header': "Final Sorting Report",
        'txt_order': "Category Order: ",
        'lg_trick_title': "Technical Tip After Upload:",
        'lg_trick_text': "To ensure sorting: 1.Settings 2.Channels 3.Channel Manager 4.Edit All 5.Select All and Restore"
    }
}

t = UI_TEXT[st.session_state.lang]
st.set_page_config(page_title="RAMBO - LG Sorter", page_icon="⚡", layout="wide")

col_lang, col_theme = st.columns([1.2, 1.5])
with col_lang:
    if st.button("EN/AR"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
        st.rerun()
with col_theme:
    if st.button("Light/Dark"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

bg_style = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)" if st.session_state.theme == 'dark' else "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
text_color = "#00f0ff" if st.session_state.theme == 'dark' else "#0d0722"
box_bg = "rgba(13, 7, 33, 0.85)" if st.session_state.theme == 'dark' else "#ffffff"
box_border = "#00f0ff" if st.session_state.theme == 'dark' else "#ff007f"
box_shadow = "rgba(0, 240, 255, 0.35)" if st.session_state.theme == 'dark' else "rgba(255, 0, 127, 0.15)"
footer_bg = "#080314" if st.session_state.theme == 'dark' else "#110926"
footer_text = "#ffffff"
font_family = "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif"

st.markdown(f"""<style>@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');.main {{ background: {bg_style} !important; color: {text_color} !important; font-family: {font_family}; }}h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f !important; text-align: center; font-weight: 900; }}h3, p, label {{ color: {text_color} !important; }}.stTextInput>div>div>input {{ background-color: {box_bg} !important; color: {text_color} !important; border: 2px solid {box_border} !important; border-radius: 10px !important; }}.stCheckbox, .stMultiSelect {{ background: {box_bg} !important; border: 2px solid {box_border} !important; box-shadow: 0px 5px 15px {box_shadow} !important; border-radius: 14px !important; padding: 18px !important; margin-bottom: 20px !important; }}.stButton>button {{ background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important; color: #ffffff !important; border: 2px solid #ff007f !important; border-radius: 12px !important; font-weight: bold; }}.footer {{ background: {footer_bg}; border: 2px solid #00f0ff; color: {footer_text} !important; padding: 35px; text-align: center; border-radius: 20px; margin-top: 65px; }}</style>""", unsafe_allow_html=True)

st.title(t['title'])
st.markdown(f"<h3>{t['subtitle']}</h3>", unsafe_allow_html=True)

NILESAT_LIVE_DB = {
    "AL HAYAT": {"frequency": 12207, "polarization": "Vertical"},
    "AL HAYAT 2": {"frequency": 12207, "polarization": "Vertical"},
    "SAT-7 KIDS": {"frequency": 11353, "polarization": "Vertical"},
    "SAT-7 ARABIC": {"frequency": 11353, "polarization": "Vertical"},
    "CTV": {"frequency": 12022, "polarization": "Vertical"},
    "AGHAPY TV": {"frequency": 11179, "polarization": "Horizontal"},
    "MESAT": {"frequency": 11096, "polarization": "Horizontal"},
    "IQRAA": {"frequency": 11938, "polarization": "Vertical"},
    "MAJD": {"frequency": 11862, "polarization": "Vertical"},
    "RAHMA": {"frequency": 11938, "polarization": "Vertical"},
    "QURAN KAREEM": {"frequency": 11727, "polarization": "Vertical"},
    "AL JAZEERA HD": {"frequency": 10853, "polarization": "Vertical"},
    "AL ARABIYA": {"frequency": 11938, "polarization": "Vertical"},
    "AL HADATH": {"frequency": 11938, "polarization": "Vertical"},
    "CBC": {"frequency": 12092, "polarization": "Vertical"},
    "EXTRA NEWS": {"frequency": 12092, "polarization": "Vertical"},
    "ON E": {"frequency": 12092, "polarization": "Vertical"},
    "MBC 2": {"frequency": 11938, "polarization": "Vertical"},
    "MBC 4": {"frequency": 11938, "polarization": "Vertical"},
    "ROTANA CINEMA": {"frequency": 11938, "polarization": "Vertical"},
    "ON TIME SPORTS 1": {"frequency": 11861, "polarization": "Vertical"},
    "ON TIME SPORTS 2": {"frequency": 11861, "polarization": "Vertical"},
    "SPACE TOON": {"frequency": 11727, "polarization": "Vertical"},
    "MAJID": {"frequency": 11862, "polarization": "Vertical"},
    "TOYOR OSHAY": {"frequency": 11179, "polarization": "Horizontal"}
}

ALL_AVAILABLE_CATEGORIES = [
    "⛪ Christian Channels" if st.session_state.lang == 'en' else "⛪ قنوات مسيحية",
    "🕌 Islamic Channels" if st.session_state.lang == 'en' else "🕌 قنوات إسلامية",
    "🎬 Drama and Series" if st.session_state.lang == 'en' else "🎬 مسلسلات ودراما",
    "🍿 Movies" if st.session_state.lang == 'en' else "🍿 أفلام",
    "👶 Kids and Cartoon" if st.session_state.lang == 'en' else "👶 أطفال وكرتون",
    "⚽ Sports" if st.session_state.lang == 'en' else "⚽ رياضة",
    "📰 News" if st.session_state.lang == 'en' else "📰 أخبار",
    "📺 General Channels" if st.session_state.lang == 'en' else "📺 قنوات عامة"
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
    if any(w in name for w in KIDS_KW): return ALL_AVAILABLE_CATEGORIES[4]
    SPORT_KW = ["SPORT", "SPORTS", "ONTIME", "ON TIME", "KASS", "AD_SPORTS", "AD SPORTS", "SSC", "BEIN", "MATCH"]
    if any(w in name for w in SPORT_KW): return ALL_AVAILABLE_CATEGORIES[5]
    NEWS_KW = ["NEWS", "JAZEERA", "ARABIYA", "HADATH", "CAIRO", "SKY NEWS", "BBC", "CNN", "EXTRA NEWS", "CBC", "ON E", "SADA", "BALADI", "MASR"]
    if any(w in name for w in NEWS_KW): return ALL_AVAILABLE_CATEGORIES[6]
    return ALL_AVAILABLE_CATEGORIES[7]

uploaded_file = st.file_uploader(t['upload_label'], type=["TLL"])

if uploaded_file is not None:
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
    model_name = model_setting.text if model_setting is not None else "Unknown LG TV"

    legacy_broadcast_tag = root.find(".//legacybroadcast")
    is_modern = legacy_broadcast_tag is not None and legacy_broadcast_tag.text

    st.info(f"{t['success_read']} **{model_name}**")

    st.markdown(f"<div style='background:{box_bg};border:2px solid #ff007f;padding:18px;border-radius:14px;margin-bottom:20px;'><h4 style='color:#ff007f;margin-top:0;'>{t['lg_trick_title']}</h4><p style='font-size:14px;'>{t['lg_trick_text']}</p></div>", unsafe_allow_html=True)

    update_freq = st.checkbox(t['update_freq_label'], value=True)
    add_new_ch = st.checkbox(t['add_new_ch_label'], value=True)

    channels_to_sort = []
    report_changes = []
    existing_names_upper = set()

    if is_modern:
        try:
            broadcast_data = json.loads(legacy_broadcast_tag.text.strip())
            channels_list = broadcast_data.get("channelList", [])

            for ch in channels_list:
                ch_name = ch.get("channelName", "Unknown")
                old_freq = str(ch.get("frequency", "N/A"))
                name_up = ch_name.upper()
                existing_names_upper.add(name_up)

                if update_freq and name_up in NILESAT_LIVE_DB:
                    live_freq = NILESAT_LIVE_DB[name_up]["frequency"]
                    if old_freq != str(live_freq):
                        report_changes.append({"Channel": ch_name, "Category": ai_classify(ch_name), "Old Freq": old_freq + " MHz", "New Freq": str(live_freq) + " MHz"})
                        ch["frequency"] = int(live_freq)
                        ch["polarization"] = NILESAT_LIVE_DB[name_up]["polarization"]
                        old_freq = str(live_freq)

                channels_to_sort.append({"name": ch_name, "freq": old_freq, "node_data": ch, "is_injected": False})

            if add_new_ch and channels_list:
                sample_node = channels_list[0]
                for db_name, db_info in NILESAT_LIVE_DB.items():
                    if db_name not in existing_names_upper:
                        new_node = sample_node.copy()
                        new_node["channelName"] = db_name
                        new_node["frequency"] = db_info["frequency"]
                        new_node["polarization"] = db_info["polarization"]
                        new_node["invisible"] = 0
                        channels_to_sort.append({"name": db_name, "freq": str(db_info["frequency"]), "node_data": new_node, "is_injected": True})
                        report_changes.append({"Channel": db_name, "Category": ai_classify(db_name), "Old Freq": "Not Found", "New Freq": str(db_info["frequency"]) + " MHz"})

        except Exception as json_err:
            st.error(f"Error: {str(json_err)}")
    else:
        item_blocks = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)

        for item_str in item_blocks:
            name_match = re.search(r'<vchName>(.*?)</vchName>', item_str)
            freq_match = re.search(r'<frequency>(.*?)</frequency>', item_str)
            ch_name = name_match.group(1) if name_match else "Unknown"
            old_freq = freq_match.group(1) if freq_match else "N/A"
            name_up = ch_name.upper()
            existing_names_upper.add(name_up)

            if update_freq and name_up in NILESAT_LIVE_DB:
                live_freq = str(NILESAT_LIVE_DB[name_up]["frequency"])
                if old_freq != live_freq:
                    report_changes.append({"Channel": ch_name, "Category": ai_classify(ch_name), "Old Freq": old_freq + " MHz", "New Freq": live_freq + " MHz"})
                    item_str = re.sub(r'<frequency>\d+</frequency>', f'<frequency>{live_freq}</frequency>', item_str)
                    old_freq = live_freq

            channels_to_sort.append({"name": ch_name, "freq": old_freq, "raw_str": item_str, "is_injected": False
