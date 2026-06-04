import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'loaded_file_name' not in st.session_state:
    st.session_state.loaded_file_name = ""
if 'channels' not in st.session_state:
    st.session_state.channels = []
if 'is_modern' not in st.session_state:
    st.session_state.is_modern = False
if 'root' not in st.session_state:
    st.session_state.root = None
if 'broadcast_data' not in st.session_state:
    st.session_state.broadcast_data = None
if 'file_text_original' not in st.session_state:
    st.session_state.file_text_original = ""
if 'model_name' not in st.session_state:
    st.session_state.model_name = ""
if 'legacy_tag' not in st.session_state:
    st.session_state.legacy_tag = None

UI_TEXT = {
    'ar': {
        'title': "📺 RAMBO - المُرتب العالمي لشاشات LG",
        'subtitle': "⚡ ترتيب ذكي لملفات قنوات LG",
        'upload_label': "🚀 اختر ملف القنوات (GlobalClone00001.TLL) من الفلاشة:",
        'update_freq_label': "⚛️ تحديث الترددات تلقائياً",
        'add_new_ch_label': "✨ إضافة القنوات الجديدة المتاحة تلقائياً",
        'success_read': "🛸 تم قراءة الملف بنجاح!",
        'model_label': "الموديل:",
        'system_label': "النظام:",
        'total_label': "إجمالي القنوات:",
        'search_header': "🔍 البحث عن قناة داخل الملف:",
        'search_placeholder': "اكتب اسم القناة هنا...",
        'search_col_num': "الرقم",
        'search_col_name': "اسم القناة",
        'search_col_cat': "الفئة",
        'search_col_freq': "التردد",
        'search_no_results': "⚠️ لا توجد نتائج مطابقة.",
        'config_title': "🎛️ ترتيب الفئات:",
        'multiselect_label': "اختر الفئات بالترتيب المطلوب:",
        'preview_title': "📊 معاينة التوزيع الحالي:",
        'channels_count': "قناة",
        'ready_msg': "✅ تم تجهيز الملف النهائي للتحميل:",
        'btn_download_tll': "📥 تحميل ملف الشاشة النهائي (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 تحميل تقرير الترتيب (Channels_List.txt)",
        'txt_header': "📄 تقرير ترتيب القنوات النهائي",
        'txt_order': "🛠️ ترتيب الفئات المختار: ",
        'lg_trick_title': "💡 ملحوظة فنية:",
        'lg_trick_text': "لو الشاشة لم تُظهر الترتيب كما هو، ادخل Channel Manager ثم Edit All Channels ثم Restore.",
        'no_file': "⬆️ ارفع ملف TLL أولاً لتبدأ العمل."
    },
    'en': {
        'title': "📺 RAMBO - LG Universal Sorter",
        'subtitle': "⚡ Smart LG channel file sorting",
        'upload_label': "🚀 Upload Channel File (GlobalClone00001.TLL) from USB:",
        'update_freq_label': "⚛️ Auto update frequencies",
        'add_new_ch_label': "✨ Auto inject missing channels",
        'success_read': "🛸 File parsed successfully!",
        'model_label': "Model:",
        'system_label': "System:",
        'total_label': "Total channels:",
        'search_header': "🔍 Search inside file:",
        'search_placeholder': "Type channel name...",
        'search_col_num': "No.",
        'search_col_name': "Channel Name",
        'search_col_cat': "Category",
        'search_col_freq': "Frequency",
        'search_no_results': "⚠️ No matching results.",
        'config_title': "🎛️ Category order:",
        'multiselect_label': "Select categories in desired order:",
        'preview_title': "📊 Current distribution preview:",
        'channels_count': "Channels",
        'ready_msg': "✅ Final file ready for download:",
        'btn_download_tll': "📥 Download Final TV File (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 Download Sorting Report (Channels_List.txt)",
        'txt_header': "📄 Final Channel Sorting Report",
        'txt_order': "🛠️ Selected category priority: ",
        'lg_trick_title': "💡 Technical note:",
        'lg_trick_text': "If the TV does not show the exact order, open Channel Manager, then Edit All Channels, then Restore.",
        'no_file': "⬆️ Upload a TLL file to start."
    }
}

t = UI_TEXT[st.session_state.lang]
st.set_page_config(page_title="RAMBO - LG Sorter", page_icon="⚡", layout="wide")

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
    text_shadow = "0 0 5px rgba(0, 240, 255, 0.4)"
else:
    bg_style = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
    text_color = "#0d0722"
    box_bg = "#ffffff"
    box_border = "#ff007f"
    box_shadow = "rgba(255, 0, 127, 0.15)"
    text_shadow = "none"

font_family = "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
.main {{ background: {bg_style} !important; color: {text_color} !important; font-family: {font_family}; }}
h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.4) !important; text-align: center; font-weight: 900; margin-top: 5px; }}
h2, h3, p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] p {{ color: {text_color} !important; text-shadow: {text_shadow}; }}
.stTextInput>div>div>input, .stNumberInput>div>div>input, .stMultiSelect>div>div>div {{
    background-color: {box_bg} !important;
    color: {text_color} !important;
    border: 2px solid {box_border} !important;
    border-radius: 10px !important;
}}
div[data-testid="stFileUploader"], .rambo-box {{
    background: {box_bg} !important;
    border: 2px solid {box_border} !important;
    box-shadow: 0px 5px 15px {box_shadow} !important;
    border-radius: 14px !important;
    padding: 18px !important;
    margin-bottom: 20px !important;
}}
.stButton>button {{
    background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
    color: #ffffff !important;
    border: 2px solid #ff007f !important;
    border-radius: 12px !important;
    font-weight: bold;
    width: 100%;
}}
</style>
""", unsafe_allow_html=True)

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
    "TOYOR ALJANNAH": {"frequency": 11179, "polarization": "Horizontal"}
}

ALL_AVAILABLE_CATEGORIES = [
    "⛪ قنوات مسيحية" if st.session_state.lang == 'ar' else "⛪ Christian Channels",
    "🕌 قنوات إسلامية" if st.session_state.lang == 'ar' else "🕌 Islamic Channels",
    "🎬 مسلسلات ودراما" if st.session_state.lang == 'ar' else "🎬 Drama & Series",
    "🍿 أفلام عربية وأجنبية" if st.session_state.lang == 'ar' else "🍿 Movies (Ar/En)",
    "👶 أطفال وكرتون" if st.session_state.lang == 'ar' else "👶 Kids & Cartoon",
    "⚽ رياضة" if st.session_state.lang == 'ar' else "⚽ Sports",
    "📰 أخبار وسياسة" if st.session_state.lang == 'ar' else "📰 News & Politics",
    "📺 قنوات عامة ومنوعات" if st.session_state.lang == 'ar' else "📺 General Channels"
]

def ai_classify(channel_name):
    name = channel_name.upper().strip()
    CHRISTIAN_KW = ["CTV", "AGHAPY", "MESAT", "KARMA", "ALKARMA", "NOURSAT", "SAT-7", "SAT7", "AL HAYAT", "HAYAT TV", "MIRACLE", "COPTIC", "CHURCH"]
    if any(w in name for w in CHRISTIAN_KW):
        return ALL_AVAILABLE_CATEGORIES[0]
    ISLAMIC_KW = ["QURAN", "RAHMA", "MAJD", "MAKKA", "IQRAA", "IQRA", "HUDA", "WESAL", "ISLAM", "SUNNAH"]
    if any(w in name for w in ISLAMIC_KW):
        return ALL_AVAILABLE_CATEGORIES[1]
    DRAMA_KW = ["MOSALSALAT", "DRAMA", "SERIES", "KHOLASA", "MASRAWI", "SHAHID"]
    if any(w in name for w in DRAMA_KW):
        return ALL_AVAILABLE_CATEGORIES[2]
    MOVIE_KW = ["CINEMA", "ROTANA", "AFLAM", "MIX", "FOX", "MBC2", "MBC 2", "MBC4", "MBC 4", "MBC MAX", "ACTION", "RAMBO", "MOVIE", "FILM", "COMEDY"]
    if any(w in name for w in MOVIE_KW):
        return ALL_AVAILABLE_CATEGORIES[3]
    KIDS_KW = ["SPACE TOON", "SPACETOON", "CN", "CARTOON", "MAJID", "KIDS", "TOM", "TOYOR", "BABY", "JUNIOR"]
    if any(w in name for w in KIDS_KW):
        return ALL_AVAILABLE_CATEGORIES[4]
    SPORT_KW = ["SPORT", "SPORTS", "ONTIME", "ON TIME", "KASS", "AD_SPORTS", "AD SPORTS", "SSC", "BEIN", "MATCH"]
    if any(w in name for w in SPORT_KW):
        return ALL_AVAILABLE_CATEGORIES[5]
    NEWS_KW = ["NEWS", "JAZEERA", "ARABIYA", "HADATH", "CAIRO", "SKY NEWS", "BBC", "CNN", "EXTRA NEWS", "CBC", "ON E", "SADA", "BALADI", "MASR"]
    if any(w in name for w in NEWS_KW):
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
    node["category"] = ai_classify(node.get("channelName", ""))
    node["Invisible"] = False
    node["skipped"] = False
    node["deleted"] = False
    node["userSelCHNo"] = True
    return node

def parse_tll(file_bytes):
    try:
        file_text = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        file_text = file_bytes.decode('latin-1')

    file_text_cleaned = re.sub(r'^\s+', '', file_text)
    try:
        root = ET.fromstring(file_text_cleaned.encode('utf-8'))
    except Exception:
        root = ET.fromstring(file_text_cleaned.encode('latin-1'))

    legacy_broadcast_tag = root.find(".//legacybroadcast")
    is_modern = legacy_broadcast_tag is not None and legacy_broadcast_tag.text

    channels = []
    if is_modern:
        broadcast_data = json.loads(legacy_broadcast_tag.text.strip())
        channels_list = broadcast_data.get("channelList", [])
        for ch in channels_list:
            channels.append({
                "name": ch.get("channelName", "Unknown"),
                "freq": str(ch.get("frequency", "N/A")),
                "node_data": ch
            })
        return channels, True, root, broadcast_data, file_text, legacy_broadcast_tag
    else:
        item_blocks = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)
        for item_str in item_blocks:
            name_match = re.search(r'<vchName>(.*?)</vchName>', item_str)
            freq_match = re.search(r'<frequency>(.*?)</frequency>', item_str)
            ch_name = name_match.group(1) if name_match else "Unknown"
            channels.append({
                "name": ch_name,
                "freq": freq_match.group(1) if freq_match else "N/A",
                "raw_str": item_str
            })
        return channels, False, root, None, file_text, None

uploaded_file = st.file_uploader(t['upload_label'], type=["TLL"], key="tll_uploader")

if uploaded_file is not None and st.session_state.get("loaded_file_name") != uploaded_file.name:
    file_bytes = uploaded_file.read()
    channels, is_modern, root, broadcast_data, file_text_original, legacy_tag = parse_tll(file_bytes)
    st.session_state.loaded_file_name = uploaded_file.name
    st.session_state.channels = channels
    st.session_state.is_modern = is_modern
    st.session_state.root = root
    st.session_state.broadcast_data = broadcast_data
    st.session_state.file_text_original = file_text_original
    st.session_state.legacy_tag = legacy_tag
    st.session_state.model_name = root.findtext(".//ModelName", default="Unknown LG TV")

if not st.session_state.channels:
    st.info(t['no_file'])
    st.stop()

system_name = "Modern JSON" if st.session_state.is_modern else "Legacy XML"
st.success(
    f"{t['success_read']} **{st.session_state.model_name}** | "
    f"{t['system_label']} **{system_name}** | "
    f"{t['total_label']} **{len(st.session_state.channels)}**"
)

update_freq = st.checkbox(t['update_freq_label'], value=True)
add_new_ch = st.checkbox(t['add_new_ch_label'], value=True)

channels_to_sort = []
report_changes = []
existing_names_upper = set()

if st.session_state.is_modern:
    broadcast_data = st.session_state.broadcast_data
    channels_list = broadcast_data.get("channelList", [])

    for ch in channels_list:
        ch_name = ch.get("channelName", "Unknown")
        old_freq = str(ch.get("frequency", "N/A"))
        name_up = ch_name.upper()
        existing_names_upper.add(name_up)

        if "category" not in ch or not ch["category"]:
            ch["category"] = ai_classify(ch_name)

        if update_freq and name_up in NILESAT_LIVE_DB:
            live_freq = NILESAT_LIVE_DB[name_up]["frequency"]
            if old_freq != str(live_freq):
                report_changes.append({
                    "channel": ch_name,
                    "category": ai_classify(ch_name),
                    "old_freq": old_freq,
                    "new_freq": str(live_freq)
                })
                ch["frequency"] = int(live_freq)
                ch["polarization"] = NILESAT_LIVE_DB[name_up]["polarization"]
                old_freq = str(live_freq)

        channels_to_sort.append({
            "name": ch_name,
            "freq": old_freq,
            "node_data": ch,
            "is_injected": False
        })

    if add_new_ch and channels_list:
        sample_node = channels_list[0]
        for db_name, db_info in NILESAT_LIVE_DB.items():
            if db_name not in existing_names_upper:
                new_node = json.loads(json.dumps(sample_node))
                new_node["channelName"] = db_name
                new_node["frequency"] = db_info["frequency"]
                new_node["polarization"] = db_info["polarization"]
                new_node["Invisible"] = False
                new_node["skipped"] = False
                new_node["deleted"] = False
                new_node["userSelCHNo"] = True
                new_node["category"] = ai_classify(db_name)
                channels_to_sort.append({
                    "name": db_name,
                    "freq": str(db_info["frequency"]),
                    "node_data": new_node,
                    "is_injected": True
                })
else:
    for ch in st.session_state.channels:
        ch_name = ch["name"]
        old_freq = ch["freq"]
        name_up = ch_name.upper()
        existing_names_upper.add(name_up)

        if update_freq and name_up in NILESAT_LIVE_DB:
            live_freq = str(NILESAT_LIVE_DB[name_up]["frequency"])
            if old_freq != live_freq:
                report_changes.append({
                    "channel": ch_name,
                    "category": ai_classify(ch_name),
                    "old_freq": old_freq,
                    "new_freq": live_freq
                })
                ch["freq"] = live_freq
                ch["raw_str"] = re.sub(r'<frequency>\d+</frequency>', f'<frequency>{live_freq}</frequency>', ch["raw_str"])
                old_freq = live_freq

        channels_to_sort.append({
            "name": ch_name,
            "freq": old_freq,
            "raw_str": ch["raw_str"],
            "is_injected": False
        })

    if add_new_ch and st.session_state.channels:
        sample_item = st.session_state.channels[0]["raw_str"]
        for db_name, db_info in NILESAT_LIVE_DB.items():
            if db_name not in existing_names_upper:
                new_item = re.sub(r'<vchName>.*?</vchName>', f'<vchName>{db_name}</vchName>', sample_item)
                new_item = re.sub(r'<frequency>\d+</frequency>', f'<frequency>{db_info["frequency"]}</frequency>', new_item)
                channels_to_sort.append({
                    "name": db_name,
                    "freq": str(db_info["frequency"]),
                    "raw_str": new_item,
                    "is_injected": True
                })

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

st.write("---")
st.write(f"### {t['config_title']}")
user_priority = st.multiselect(t['multiselect_label'], options=ALL_AVAILABLE_CATEGORIES, default=[])
final_priority = list(user_priority)
for cat in ALL_AVAILABLE_CATEGORIES:
    if cat not in final_priority:
        final_priority.append(cat)

def sort_key(x):
    return final_priority.index(ai_classify(x["name"]))

channels_sorted = sorted(channels_to_sort, key=sort_key)

categorized = {}
for ch in channels_sorted:
    cat = ai_classify(ch["name"])
    categorized.setdefault(cat, []).append(ch["name"])

st.write("---")
st.write(f"### {t['preview_title']}")
col1, col2 = st.columns(2)
for i, cat_name in enumerate(final_priority):
    if cat_name in categorized:
        ch_list = categorized[cat_name]
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            is_user_chosen = "⭐ " if cat_name in user_priority else ""
            expander_title = is_user_chosen + cat_name + " — (" + str(len(ch_list)) + " " + t['channels_count'] + ")"
            with st.expander(expander_title):
                st.write(", ".join(ch_list))

if report_changes:
    st.write("---")
    st.write("### 🔁 التعديلات")
    st.table(report_changes)

text_report = f"{t['txt_header']} ({st.session_state.model_name})\n" + "=" * 50 + "\n"
text_report += t['txt_order'] + " -> ".join(final_priority) + "\n" + "=" * 50 + "\n\n"

if st.session_state.is_modern:
    final_list_modern = []
    for index, ch in enumerate(channels_sorted, start=1):
        node = normalize_modern_node(ch["node_data"], index)
        final_list_modern.append(node)
        tag_status = " [NEW]" if ch["is_injected"] else ""
        text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}{tag_status}\n"

    st.session_state.broadcast_data["channelList"] = final_list_modern
    st.session_state.legacy_tag.text = json.dumps(st.session_state.broadcast_data, ensure_ascii=False, separators=(',', ':'))
    final_xml_bytes = ET.tostring(st.session_state.root, encoding="utf-8")
else:
    item_strings_sorted = []
    for index, ch in enumerate(channels_sorted, start=1):
        raw = set_item_prnum(ch["raw_str"], index)
        item_strings_sorted.append(raw)
        tag_status = " [NEW]" if ch["is_injected"] else ""
        text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}{tag_status}\n"

    combined_items_str = "\r\n".join(item_strings_sorted)
    start_idx = st.session_state.file_text_original.find("<ITEM>")
    end_idx = st.session_state.file_text_original.rfind("</ITEM>") + len("</ITEM>")
    if start_idx != -1 and end_idx != -1:
        final_text_output = st.session_state.file_text_original[:start_idx] + combined_items_str + st.session_state.file_text_original[end_idx:]
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
    st.download_button(
        label=t['btn_download_tll'],
        data=final_xml_bytes,
        file_name="GlobalClone00001.TLL",
        mime="application/octet-stream"
    )
with col_btn2:
    st.download_button(
        label=t['btn_download_txt'],
        data=text_report,
        file_name="Channels_List.txt",
        mime="text/plain; charset=utf-8"
    )

st.markdown(f"""
<div style="background-color: rgba(255, 165, 0, 0.12); border-left: 5px solid #ffa500; padding: 20px; border-radius: 12px; margin-top: 25px;">
    <h4 style="color: #ffa500; margin-top: 0; font-weight: bold;">{t['lg_trick_title']} {t['lg_trick_text']}</h4>
</div>
""", unsafe_allow_html=True)
