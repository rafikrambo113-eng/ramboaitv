import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

st.set_page_config(page_title="RAMBO - LG Sorter", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

if "lang" not in st.session_state:
    st.session_state.lang = "ar"
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

UI_TEXT = {
    "ar": {
        "title": "📺 RAMBO - المنسق العالمي لشاشات LG",
        "subtitle": "⚡ ترتيب ذكي لملفات قنوات LG",
        "upload_label": "🚀 اختر ملف القنوات (GlobalClone00001.TLL) من الفلاشة:",
        "update_freq_label": "⚛️ تحديث الترددات تلقائياً",
        "add_new_ch_label": "✨ إضافة القنوات الجديدة المتاحة تلقائياً",
        "success_read": "🛸 تم قراءة الهيكل بنجاح! الموديل الحالي: ",
        "search_header": "🔍 البحث عن قناة داخل الملف:",
        "search_placeholder": "اكتب اسم القناة هنا...",
        "search_col_num": "الرقم",
        "search_col_name": "اسم القناة",
        "search_col_cat": "الفئة",
        "search_col_freq": "التردد",
        "search_no_results": "⚠️ لا توجد نتائج مطابقة.",
        "config_title": "🎛️ ترتيب الفئات:",
        "multiselect_label": "اختر الفئات بالترتيب المطلوب:",
        "preview_title": "📊 معاينة التوزيع الحالي:",
        "channels_count": "قناة",
        "ready_msg": "✅ تم تجهيز الملف النهائي للتحميل:",
        "btn_download_tll": "📥 تحميل ملف الشاشة النهائي (GlobalClone00001.TLL)",
        "btn_download_txt": "📄 تحميل تقرير الترتيب (Channels_List.txt)",
        "txt_header": "📄 تقرير ترتيب القنوات النهائي",
        "txt_order": "🛠️ ترتيب الفئات المختار: ",
        "lg_trick_title": "💡 ملحوظة فنية:",
        "lg_trick_text": "لو الشاشة لم تُظهر الترتيب كما هو، ادخل Channel Manager ثم Edit All Channels ثم Restore."
    },
    "en": {
        "title": "📺 RAMBO - LG Universal Sorter",
        "subtitle": "⚡ Smart LG channel file sorting",
        "upload_label": "🚀 Upload Channel File (GlobalClone00001.TLL) from USB:",
        "update_freq_label": "⚛️ Auto update frequencies",
        "add_new_ch_label": "✨ Auto inject missing channels",
        "success_read": "🛸 Structure decoded successfully! Current model: ",
        "search_header": "🔍 Search inside file:",
        "search_placeholder": "Type channel name...",
        "search_col_num": "No.",
        "search_col_name": "Channel Name",
        "search_col_cat": "Category",
        "search_col_freq": "Frequency",
        "search_no_results": "⚠️ No matching results.",
        "config_title": "🎛️ Category order:",
        "multiselect_label": "Select categories in desired order:",
        "preview_title": "📊 Current distribution preview:",
        "channels_count": "Channels",
        "ready_msg": "✅ Final file ready for download:",
        "btn_download_tll": "📥 Download Final TV File (GlobalClone00001.TLL)",
        "btn_download_txt": "📄 Download Sorting Report (Channels_List.txt)",
        "txt_header": "📄 Final Channel Sorting Report",
        "txt_order": "🛠️ Selected category priority: ",
        "lg_trick_title": "💡 Technical note:",
        "lg_trick_text": "If the TV does not show the exact order, open Channel Manager, then Edit All Channels, then Restore."
    }
}

t = UI_TEXT[st.session_state.lang]

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

def get_categories():
    return [
        "⛪ قنوات مسيحية" if st.session_state.lang == "ar" else "⛪ Christian Channels",
        "🕌 قنوات إسلامية" if st.session_state.lang == "ar" else "🕌 Islamic Channels",
        "🎬 مسلسلات ودراما" if st.session_state.lang == "ar" else "🎬 Drama & Series",
        "🍿 أفلام عربية وأجنبية" if st.session_state.lang == "ar" else "🍿 Movies (Ar/En)",
        "👶 أطفال وكرتون" if st.session_state.lang == "ar" else "👶 Kids & Cartoon",
        "⚽ رياضة" if st.session_state.lang == "ar" else "⚽ Sports",
        "📰 أخبار وسياسة" if st.session_state.lang == "ar" else "📰 News & Politics",
        "📺 قنوات عامة ومنوعات" if st.session_state.lang == "ar" else "📺 General Channels"
    ]

ALL_AVAILABLE_CATEGORIES = get_categories()

def ai_classify(channel_name):
    name = channel_name.upper().strip()
    christian_kw = ["CTV", "AGHAPY", "MESAT", "KARMA", "ALKARMA", "NOURSAT", "SAT-7", "SAT7", "AL HAYAT", "HAYAT TV", "MIRACLE", "COPTIC", "CHURCH"]
    if any(w in name for w in christian_kw):
        return ALL_AVAILABLE_CATEGORIES[0]
    islamic_kw = ["QURAN", "RAHMA", "MAJD", "MAKKA", "IQRAA", "IQRA", "HUDA", "WESAL", "ISLAM", "SUNNAH"]
    if any(w in name for w in islamic_kw):
        return ALL_AVAILABLE_CATEGORIES[1]
    drama_kw = ["MOSALSALAT", "DRAMA", "SERIES", "KHOLASA", "MASRAWI", "SHAHID"]
    if any(w in name for w in drama_kw):
        return ALL_AVAILABLE_CATEGORIES[2]
    movie_kw = ["CINEMA", "ROTANA", "AFLAM", "MIX", "FOX", "MBC2", "MBC 2", "MBC4", "MBC 4", "MBC MAX", "ACTION", "RAMBO", "MOVIE", "FILM", "COMEDY"]
    if any(w in name for w in movie_kw):
        return ALL_AVAILABLE_CATEGORIES[3]
    kids_kw = ["SPACE TOON", "SPACETOON", "CN", "CARTOON", "MAJID", "KIDS", "TOM", "TOYOR", "BABY", "JUNIOR"]
    if any(w in name for w in kids_kw):
        return ALL_AVAILABLE_CATEGORIES[4]
    sport_kw = ["SPORT", "SPORTS", "ONTIME", "ON TIME", "KASS", "AD_SPORTS", "AD SPORTS", "SSC", "BEIN", "MATCH"]
    if any(w in name for w in sport_kw):
        return ALL_AVAILABLE_CATEGORIES[5]
    news_kw = ["NEWS", "JAZEERA", "ARABIYA", "HADATH", "CAIRO", "SKY NEWS", "BBC", "CNN", "EXTRA NEWS", "CBC", "ON E", "SADA", "BALADI", "MASR"]
    if any(w in name for w in news_kw):
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
}

.main, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%) !important;
    color: #00f0ff !important;
}

h1, h2, h3 {
    color: #ff007f !important;
    text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.4) !important;
    text-align: center;
    font-weight: 900;
}

p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] p, span {
    color: #00f0ff !important;
    text-shadow: 0 0 5px rgba(0, 240, 255, 0.25);
}

div[data-testid="stFileUploader"], .rambo-box {
    background: rgba(13, 7, 33, 0.85) !important;
    border: 2px solid #00f0ff !important;
    box-shadow: 0px 5px 15px rgba(0, 240, 255, 0.35) !important;
    border-radius: 14px !important;
    padding: 18px !important;
    margin-bottom: 20px !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stMultiSelect > div > div,
textarea {
    background-color: rgba(13, 7, 33, 0.85) !important;
    color: #00f0ff !important;
    border: 2px solid #00f0ff !important;
    border-radius: 10px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
    color: #ffffff !important;
    border: 2px solid #ff007f !important;
    border-radius: 12px !important;
    font-weight: bold;
    width: 100%;
}

.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 0 18px rgba(255, 0, 127, 0.45);
}

hr {
    border-color: rgba(0, 240, 255, 0.2) !important;
}

[data-testid="stDataFrame"], [data-testid="stTable"] {
    border: 1px solid rgba(0, 240, 255, 0.25) !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<h1>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align:center;'>{t['subtitle']}</h3>", unsafe_allow_html=True)

col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("" if st.session_state.lang == "ar" else ""):
        st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
        st.rerun()
with col_theme:
    if st.button("" if st.session_state.theme == "dark" else ""):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

uploaded_file = st.file_uploader(t["upload_label"], type=["TLL"])

def parse_file(file_bytes):
    try:
        file_text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        file_text = file_bytes.decode("latin-1")
    file_text_cleaned = re.sub(r"^\s+", "", file_text)
    try:
        root = ET.fromstring(file_text_cleaned.encode("utf-8"))
    except Exception:
        root = ET.fromstring(file_text_cleaned.encode("latin-1"))
    legacy_broadcast_tag = root.find(".//legacybroadcast")
    is_modern = legacy_broadcast_tag is not None and legacy_broadcast_tag.text
    model_setting = root.find(".//ModelName")
    model_name = model_setting.text if model_setting is not None else "Unknown LG TV"
    channels_to_sort = []
    report_changes = []
    existing_names_upper = set()
    broadcast_data = None

    if is_modern:
        broadcast_data = json.loads(legacy_broadcast_tag.text.strip())
        channels_list = broadcast_data.get("channelList", [])
        for ch in channels_list:
            ch_name = ch.get("channelName", "Unknown")
            old_freq = str(ch.get("frequency", "N/A"))
            name_up = ch_name.upper()
            existing_names_upper.add(name_up)
            if "category" not in ch or not ch["category"]:
                ch["category"] = ai_classify(ch_name)
            if name_up in NILESAT_LIVE_DB:
                live_freq = NILESAT_LIVE_DB[name_up]["frequency"]
                if old_freq != str(live_freq):
                    report_changes.append({"channel": ch_name, "category": ai_classify(ch_name), "old_freq": old_freq, "new_freq": str(live_freq)})
                    ch["frequency"] = int(live_freq)
                    ch["polarization"] = NILESAT_LIVE_DB[name_up]["polarization"]
                    old_freq = str(live_freq)
            channels_to_sort.append({"name": ch_name, "freq": old_freq, "node_data": ch, "is_injected": False})
        sample_node = channels_list[0] if channels_list else None
        if sample_node:
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
                    channels_to_sort.append({"name": db_name, "freq": str(db_info["frequency"]), "node_data": new_node, "is_injected": True})
                    report_changes.append({"channel": db_name, "category": ai_classify(db_name), "old_freq": "missing", "new_freq": str(db_info["frequency"])})
    else:
        item_blocks = re.findall(r"(<ITEM>.*?</ITEM>)", file_text, re.DOTALL)
        for item_str in item_blocks:
            name_match = re.search(r"<vchName>(.*?)</vchName>", item_str)
            freq_match = re.search(r"<frequency>(.*?)</frequency>", item_str)
            ch_name = name_match.group(1) if name_match else "Unknown"
            name_up = ch_name.upper()
            existing_names_upper.add(name_up)
            live_freq = freq_match.group(1) if freq_match else "N/A"
            if name_up in NILESAT_LIVE_DB:
                live_freq = str(NILESAT_LIVE_DB[name_up]["frequency"])
                item_str = re.sub(r"<frequency>\d+</frequency>", f"<frequency>{live_freq}</frequency>", item_str)
            channels_to_sort.append({"name": ch_name, "freq": live_freq, "raw_str": item_str, "is_injected": False})
        if item_blocks:
            sample_item = item_blocks[0]
            for db_name, db_info in NILESAT_LIVE_DB.items():
                if db_name not in existing_names_upper:
                    new_item = re.sub(r"<vchName>.*?</vchName>", f"<vchName>{db_name}</vchName>", sample_item)
                    new_item = re.sub(r"<frequency>\d+</frequency>", f"<frequency>{db_info['frequency']}</frequency>", new_item)
                    channels_to_sort.append({"name": db_name, "freq": str(db_info["frequency"]), "raw_str": new_item, "is_injected": True})
                    report_changes.append({"channel": db_name, "category": ai_classify(db_name), "old_freq": "missing", "new_freq": str(db_info["frequency"])})
    return channels_to_sort, report_changes, is_modern, root, broadcast_data, file_text, model_name, legacy_broadcast_tag

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    try:
        channels_to_sort, report_changes, is_modern, root, broadcast_data, file_text, model_name, legacy_broadcast_tag = parse_file(file_bytes)
    except Exception as e:
        st.error(f"❌ خطأ في قراءة الملف: {e}")
        st.stop()

    st.success(f"{t['success_read']} **{model_name}**")

    st.write("---")
    st.subheader(t["search_header"])
    search_query = st.text_input("", placeholder=t["search_placeholder"]).strip().upper()
    if search_query:
        search_results = []
        for idx, ch in enumerate(channels_to_sort, start=1):
            if search_query in ch["name"].upper():
                search_results.append({
                    t["search_col_num"]: idx,
                    t["search_col_name"]: ch["name"],
                    t["search_col_cat"]: ai_classify(ch["name"]),
                    t["search_col_freq"]: ch["freq"]
                })
        if search_results:
            st.table(search_results)
        else:
            st.warning(t["search_no_results"])

    st.write("---")
    st.subheader(t["config_title"])
    ALL_AVAILABLE_CATEGORIES = get_categories()
    user_priority = st.multiselect(t["multiselect_label"], options=ALL_AVAILABLE_CATEGORIES, default=[])
    final_priority = list(user_priority) + [cat for cat in ALL_AVAILABLE_CATEGORIES if cat not in user_priority]

    def sort_key(x):
        return final_priority.index(ai_classify(x["name"]))

    channels_sorted = sorted(channels_to_sort, key=sort_key)

    categorized = {}
    for ch in channels_sorted:
        cat = ai_classify(ch["name"])
        categorized.setdefault(cat, []).append(ch["name"])

    st.write("---")
    st.subheader(t["preview_title"])
    col1, col2 = st.columns(2)
    for i, cat_name in enumerate(final_priority):
        if cat_name in categorized:
            ch_list = categorized[cat_name]
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                is_user_chosen = "⭐ " if cat_name in user_priority else ""
                with st.expander(f"{is_user_chosen}{cat_name} — ({len(ch_list)} {t['channels_count']})"):
                    st.write(", ".join(ch_list))

    if report_changes:
        st.write("---")
        st.subheader("🔁 التعديلات")
        st.table(report_changes)

    text_report = f"{t['txt_header']} ({model_name})\n" + "=" * 50 + "\n"
    text_report += t["txt_order"] + " -> ".join(final_priority) + "\n" + "=" * 50 + "\n\n"

    if is_modern:
        final_list_modern = []
        for index, ch in enumerate(channels_sorted, start=1):
            node = normalize_modern_node(ch["node_data"], index)
            final_list_modern.append(node)
            tag_status = " [NEW]" if ch["is_injected"] else ""
            text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}{tag_status}\n"
        broadcast_data["channelList"] = final_list_modern
        legacy_broadcast_tag.text = json.dumps(broadcast_data, ensure_ascii=False, separators=(",", ":"))
        final_xml_bytes = ET.tostring(root, encoding="utf-8")
    else:
        item_strings_sorted = []
        for index, ch in enumerate(channels_sorted, start=1):
            raw = set_item_prnum(ch["raw_str"], index)
            item_strings_sorted.append(raw)
            tag_status = " [NEW]" if ch["is_injected"] else ""
            text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']}{tag_status}\n"
        combined_items_str = "\r\n".join(item_strings_sorted)
        start_idx = file_text.find("<ITEM>")
        end_idx = file_text.rfind("</ITEM>") + len("</ITEM>")
        if start_idx != -1 and end_idx != -1:
            final_text_output = file_text[:start_idx] + combined_items_str + file_text[end_idx:]
        else:
            final_text_output = combined_items_str
        try:
            final_xml_bytes = final_text_output.encode("utf-8")
        except UnicodeEncodeError:
            final_xml_bytes = final_text_output.encode("latin-1")

    st.write("---")
    st.success(t["ready_msg"])

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(
            label=t["btn_download_tll"],
            data=final_xml_bytes,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream"
        )
    with col_btn2:
        st.download_button(
            label=t["btn_download_txt"],
            data=text_report,
            file_name="Channels_List.txt",
            mime="text/plain; charset=utf-8"
        )

    st.markdown("""
    <div style="background-color: rgba(255, 165, 0, 0.12); border-left: 5px solid #ffa500; padding: 20px; border-radius: 12px; margin-top: 25px;">
        <h4 style="color: #ffa500; margin-top: 0; font-weight: bold;">💡 ملحوظة فنية هامة جداً بعد تنزيل الملف على شاشة LG:</h4>
        <p style="font-size: 15px; line-height: 1.6;">
        في بعض الحالات، بعد تنزيل ملف القنوات على الشاشة، قد تشعر أن القنوات ليست منظمة كما رتبتها. لحل هذا الأمر فوراً واجبار الشاشة على تفعيل الترتيب الصحيح، قم بالآتي:
        </p>
        <ol style="font-size: 15px; line-height: 1.7; margin-right: 20px;">
            <li>من إعدادات التلفزيون اختار <b>القنوات (Channels)</b>.</li>
            <li>بعد ذلك اختار <b>مدير القنوات (Channel Manager)</b>.</li>
            <li>اختار <b>التعديل على كل القنوات (Edit All Channels)</b>.</li>
            <li>ستظهر لك القنوات المرتبة ويكون بعضها في وضع مخفي، قم <b>بتحديد كل القنوات</b> واختار <b>استعادة (Restore)</b>.</li>
        </ol>
        <p style="font-size: 13px; color: #ffaa55; font-style: italic; margin-bottom: 0; margin-top: 10px;">
        *ملحوظة: تفعل هذه الخطوة فقط إذا شعرت أن الملف بعد التنزيل غير مرتب كما حددته على الموقع.
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info(t["no_file"])

whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"
st.markdown(f"""
<div style="background:#080314; border:2px solid #00f0ff; color:#ffffff !important; padding:35px; text-align:center; border-radius:20px; margin-top:65px; font-family:'Orbitron', sans-serif;">
    <div style="color:#ff007f; font-size:26px; font-weight:bold;">🛠️ DEVELOPER ENG: RAFIK RAMBO</div>
    <div>📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
    <div>✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com</div>
    <a href="{whatsapp_url}" target="_blank" style="color:#25d366 !important; padding:14px 35px; border-radius:35px; display:inline-block; font-weight:bold; border:2px solid #25d366; text-decoration:none; margin-top:20px;">WhatsApp Web</a>
</div>
""", unsafe_allow_html=True)
