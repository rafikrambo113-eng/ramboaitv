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

st.title(t["title"])
st.caption(t["subtitle"])

col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("🌐 English" if st.session_state.lang == "ar" else "🌐 العربية"):
        st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
        st.rerun()
with col_theme:
    if st.button("☀️ Light Mode" if st.session_state.theme == "dark" else "🌙 Dark Mode"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

uploaded_file = st.file_uploader(t["upload_label"], type=["TLL"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    try:
        file_text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        file_text = file_bytes.decode("latin-1")

    file_text_cleaned = re.sub(r"^\s+", "", file_text)

    try:
        root = ET.fromstring(file_text_cleaned.encode("utf-8"))
    except Exception:
        root = ET.fromstring(file_text_cleaned.encode("latin-1"))

    model_setting = root.find(".//ModelName")
    model_name = model_setting.text if model_setting is not None else "Unknown LG TV"

    legacy_broadcast_tag = root.find(".//legacybroadcast")
    is_modern = legacy_broadcast_tag is not None and legacy_broadcast_tag.text

    st.info(f"{t['success_read']} **{model_name}**")

    update_freq = st.checkbox(t["update_freq_label"], value=True)
    add_new_ch = st.checkbox(t["add_new_ch_label"], value=True)

    channels_to_sort = []
    report_changes = []
    existing_names_upper = set()

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

                    report_changes.append({
                        "channel": db_name,
                        "category": ai_classify(db_name),
                        "old_freq": "missing",
                        "new_freq": str(db_info["frequency"])
                    })

    else:
        item_blocks = re.findall(r"(<ITEM>.*?</ITEM>)", file_text, re.DOTALL)
        items_list = []

        for item_str in item_blocks:
            name_match = re.search(r"<vchName>(.*?)</vchName>", item_str)
            freq_match = re.search(r"<frequency>(.*?)</frequency>", item_str)
            ch_name = name_match.group(1) if name_match else "Unknown"
            name_up = ch_name.upper()
            existing_names_upper.add(name_up)

            if update_freq and name_up in NILESAT_LIVE_DB:
                live_freq = str(NILESAT_LIVE_DB[name_up]["frequency"])
                item_str = re.sub(r"<frequency>\d+</frequency>", f"<frequency>{live_freq}</frequency>", item_str)
            else:
                live_freq = freq_match.group(1) if freq_match else "N/A"

            items_list.append({
                "name": ch_name,
                "freq": live_freq,
                "raw_str": item_str,
                "is_injected": False
            })

        if add_new_ch and item_blocks:
            sample_item = item_blocks[0]
            for db_name, db_info in NILESAT_LIVE_DB.items():
                if db_name not in existing_names_upper:
                    new_item = re.sub(r"<vchName>.*?</vchName>", f"<vchName>{db_name}</vchName>", sample_item)
                    new_item = re.sub(r"<frequency>\d+</frequency>", f"<frequency>{db_info['frequency']}</frequency>", new_item)
                    items_list.append({
                        "name": db_name,
                        "freq": str(db_info["frequency"]),
                        "raw_str": new_item,
                        "is_injected": True
                    })

        channels_to_sort = items_list

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
    st.subheader(t["preview_title"])

    col1, col2 = st.columns(2)
    for i, cat_name in enumerate(final_priority):
        if cat_name in categorized:
            ch_list = categorized[cat_name]
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                is_user_chosen = "⭐ " if cat_name in user_priority else ""
                expander_title = f"{is_user_chosen}{cat_name} — ({len(ch_list)} {t['channels_count']})"
                with st.expander(expander_title):
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

    st.info(f"{t['lg_trick_title']} {t['lg_trick_text']}")
else:
    st.info("ارفع ملف TLL لبدء الترتيب.")
