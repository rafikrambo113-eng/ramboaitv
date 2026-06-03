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
    bg_style = "radial-gradient(circle at 50% 0%, #110926 0%, #05020d 100%)"
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

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
    .main { background: radial-gradient(circle at 50% 0%, #110926 0%, #05020d 100%) !important; color: #00f0ff !important; font-family: 'Cairo', sans-serif; }
    h1 { color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255, 0, 127, 0.4) !important; text-align: center; font-weight: 900; margin-top: 5px; }
    h3, p, label, .stMarkdown, .stInfo, div[data-testid="stMarkdownContainer"] p { color: #00f0ff !important; text-shadow: 0 0 5px rgba(0, 240, 255, 0.4); }
    .stTextInput>div>div>input { background-color: rgba(13, 7, 33, 0.85) !important; color: #00f0ff !important; border: 2px solid #00f0ff !important; border-radius: 10px !important; }
    .stCheckbox, .stMultiSelect, div[data-testid="stExpander"], div[data-testid="stFileUploader"], .lg-trick-box { background: rgba(13, 7, 33, 0.85) !important; border: 2px solid #00f0ff !important; box-shadow: 0px 5px 15px rgba(0, 240, 255, 0.35) !important; border-radius: 14px !important; padding: 18px !important; margin-bottom: 20px !important; }
    .lg-trick-box { border-color: #ff007f !important; box-shadow: 0px 5px 15px rgba(255, 0, 127, 0.25) !important; }
    .stButton>button { background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important; color: #ffffff !important; border: 2px solid #ff007f !important; border-radius: 12px !important; font-weight: bold; }
    .futuristic-cyber-footer { background: #080314; border: 2px solid #00f0ff; color: #ffffff !important; padding: 35px; text-align: center; border-radius: 20px; margin-top: 65px; font-family: 'Orbitron', sans-serif; }
    .footer-dev { color: #ff007f; font-size: 26px; font-weight: bold; }
    .cyber-whatsapp-btn { color: #25d366 !important; padding: 14px 35px; border-radius: 35px; display: inline-block; font-weight: bold; border: 2px solid #25d366; text-decoration: none; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title(t['title'])
st.markdown("<h3>{}</h3>".format(t['subtitle']), unsafe_allow_html=True)

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
    if any(w in name for w in KIDS_KW): return ALL_AVAILABLE_CATEGORIES[4]
    SPORT_KW = ["SPORT", "SPORTS", "ONTIME", "ON TIME", "KASS", "AD_SPORTS", "AD SPORTS", "SSC", "BEIN", "MATCH"]
    if any(w in name for w in SPORT_KW): return ALL_AVAILABLE_CATEGORIES[5]
    NEWS_KW = ["NEWS", "JAZEERA", "ARABIYA", "HADATH", "CAIRO", "SKY NEWS", "BBC", "CNN", "EXTRA NEWS", "CBC", "ON E", "SADA", "BALADI", "MASR"]
    if any(w in name for w in NEWS_KW): return ALL_AVAILABLE_CATEGORIES[6]
    return ALL_AVAILABLE_CATEGORIES[7]

# ── رفع الملف والمعالجة ──
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

    st.info("{} **{}**".format(t['success_read'], model_name))

    st.markdown("""
        <div class="lg-trick-box">
            <h4 style="color: #ff007f; margin-top:0;">{title}</h4>
            <p style="white-space: pre-line; margin-bottom:0; font-size:14px;">{text}</p>
        </div>
    """.format(title=t['lg_trick_title'], text=t['lg_trick_text']), unsafe_allow_html=True)

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
                        report_changes.append({
                            "القناة": ch_name, "الفئة (Category)": ai_classify(ch_name),
                            "التردد القديم": "{} MHz".format(old_freq), "التردد الجديد": "{} MHz".format(live_freq)
                        })
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
                        
                        channels_to_sort.append({
                            "name": db_name, 
                            "freq": str(db_info["frequency"]), 
                            "node_data": new_node,
                            "is_injected": True
                        })
                        report_changes.append({
                            "القناة": db_name, "الفئة (Category)": ai_classify(db_name),
                            "التردد القديم": "غير موجودة (مضافة)", "التردد الجديد": "{} MHz".format(db_info['frequency'])
                        })

        except Exception as json_err:
            st.error("⚠️ خطأ في معالجة الملف: {}".format(str(json_err)))
    else:
        item_blocks = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)
        
        items_list = []
        for item_str in item_blocks:
            name_match = re.search(r'<vchName>(.*?)</vchName>', item_str)
            freq_match = re.search(r'<frequency>(.*?)</frequency>', item_str)
            ch_name = name_match.group(1) if name_match else "Unknown"
            
            if update_freq and ch_name.upper() in NILESAT_LIVE_DB:
                live_freq = str(NILESAT_LIVE_DB[ch_name.upper()]["frequency"])
                item_str = re.sub(r'<frequency>\d+</frequency>', '<frequency>{}</frequency>'.format(live_freq), item_str)
            else:
                live_freq = freq_match.group(1) if freq_match else "N/A"
            
            items_list.append({"name": ch_name, "freq": live_freq, "raw_str": item_str, "is_injected": False})

        if add_new_ch and item_blocks:
            sample_item = item_blocks[0]
            existing_names_upper = {ch["name"].upper() for ch in items_list}
            for db_name, db_info in NILESAT_LIVE_DB.items():
                if db_name not in existing_names_upper:
                    new_item = re.sub(r'<vchName>.*?</vchName>', '<vchName>{}</vchName>'.format(db_name), sample_item)
                    freq_num = str(db_info["frequency"])
                    new_item = re.sub(r'<frequency>\d+</frequency>', '<frequency>{}</frequency>'.format(freq_num), new_item)
                    items_list.append({"name": db_name, "freq": str(db_info["frequency"]), "raw_str": new_item, "is_injected": True})

        channels_to_sort = items_list

    # ── محرك البحث ──
    st.write("---")
    st.write("### {}".format(t['search_header']))
    search_query = st.text_input("", placeholder=t['search_placeholder']).strip().upper()
    if search_query:
        search_results = []
        for idx, ch in enumerate(channels_to_sort, start=1):
            if search_query in ch["name"].upper():
                search_results.append({
                    t['search_col_num']: idx, t['search_col_name']: ch["name"],
                    t['search_col_cat']: ai_classify(ch["name"]), t['search_col_freq']: ch["freq"]
                })
        if search_results: 
            st.table(search_results)
        else: 
            st.warning(t['search_no_results'])

    # ── مصفوفة الترتيب ──
    st.write("---")
    st.write("### {}".format(t['config_title']))
    user_priority = st.multiselect(t['multiselect_label'], options=ALL_AVAILABLE_CATEGORIES, default=[])
    final_priority = list(user_priority)
    for cat in ALL_AVAILABLE_CATEGORIES:
        if cat not in final_priority: 
            final_priority.append(cat)

    channels_sorted = sorted(channels_to_sort, key=lambda x: final_priority.index(ai_classify(x["name"])))

    # المعاينة الحية
    categorized = {}
    for ch in channels_sorted:
        cat = ai_classify(ch["name"])
        if cat not in categorized: 
            categorized[cat] = []
        categorized[cat].append(ch["name"])

    st.write("---")
    st.write("### {}".format(t['preview_title']))
    col1, col2 = st.columns(2)
    for i, cat_name in enumerate(final_priority):
        if cat_name in categorized:
            ch_list = categorized[cat_name]
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                is_user_chosen = "⭐ " if cat_name in user_priority else ""
                with st.expander("{}{} — ({} {})".format(is_user_chosen, cat_name, len(ch_list), t['channels_count'])):
                    st.write(", ".join(ch_list))

    if report_changes:
        st.write("---")
        st.write("### 🔁 سجل التعديلات والزرع والصيانة الذكية:")
        st.table(report_changes)

    # ── التصدير ──
    text_report = "{} ({})\n".format(t['txt_header'], model_name) + "="*50 + "\n"
    text_report += "{} ".format(t['txt_order']) + " -> ".join(final_priority) + "\n" + "="*50 + "\n\n"

    if is_modern:
        # ═══════════════════════════════════════════════
        # 🔧 الشاشات الحديثة — التصحيح: إعادة تعيين الـ JSON
        # ═══════════════════════════════════════════════
        final_list_modern = []
        for index, ch in enumerate(channels_sorted, start=1):
            node = ch["node_data"]
            node["majorNumber"] = index
            final_list_modern.append(node)
            tag_status = " [NEW] " if ch["is_injected"] else ""
            text_report += "No. {:03d} : {:25} | Freq: {}{}\n".format(index, ch['name'], ch['freq'], tag_status)
        
        broadcast_data["channelList"] = final_list_modern
        
        # ✅ التصحيح الرئيسي: إعادة تعيين legacy_broadcast_tag.text قبل الـ tostring
        legacy_broadcast_tag.text = json.dumps(broadcast_data, ensure_ascii=False, separators=(',', ':'))
        
        final_xml_bytes = ET.tostring(root, encoding="utf-8")
    else:
        item_strings_sorted = []
        for index, ch in enumerate(channels_sorted, start=1):
            raw = ch["raw_str"]
            if "<prNum>" in raw:
                raw = re.sub(r'<prNum>\d+</prNum>', '<prNum>{}</prNum>'.format(index), raw)
            else:
                raw = raw.replace("<ITEM>", "<ITEM>\r\n<prNum>{}</prNum>".format(index))
            item_strings_sorted.append(raw)
            tag_status = " [NEW] " if ch["is_injected"] else ""
            text_report += "No. {:03d} : {:25} | Freq: {}{}\n".format(index, ch['name'], ch['freq'], tag_status)

        combined_items_str = "\r\n".join(item_strings_sorted)
        start_idx = file_text.find("<ITEM>")
        end_idx = file_text.rfind("</ITEM>") + len("</ITEM>")

        if start_idx != -1 and end_idx != -1:
            final_text_output = file_text[:start_idx] + combined_items_str + file_text[end_idx:]
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

# ── الفوتر الفني ──
whatsapp_url = ("https://api.whatsapp.com/send?phone=201280339779"
                "&text=Hello%20Developer%20Rafik%20Rambo%2C%20"
                "I%20have%20an%20inquiry%20regarding%20your%20LG%20TV%20Sorter%20script%3A")
st.markdown("""
    <div class="futuristic-cyber-footer">
        <div class="footer-dev">🛠️ DEVELOPER ENG: RAFIK RAMBO</div>
        <div class="footer-item">📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
        <div class="footer-item">✉️ <b>E-MAIL / البريد الإلكتروني:</b> rafikrambo113@gmail.com</div>
        <a href="{url}" target="_blank" class="cyber-whatsapp-btn">WhatsApp Web</a>
    </div>
""".format(url=whatsapp_url), unsafe_allow_html=True)
