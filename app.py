import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# ── Session ──
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

UI_TEXT = {
    'ar': {
        'title': "📺 RAMBO - المنسق العالمي لشاشات LG",
        'subtitle': "⚡ نظام ذكي لترتيب القنوات",
        'upload_label': "🚀 اختر ملف القنوات",
        'update_freq_label': "⚛️ تحديث الترددات تلقائياً",
        'add_new_ch_label': "✨ إضافة القنوات الجديدة تلقائياً",
        'success_read': "🛸 تم قراءة الملف: ",
        'search_header': "🔍 البحث عن القنوات",
        'search_placeholder': "اكتب اسم القناة...",
        'search_col_num': "رقم",
        'search_col_name': "القناة",
        'search_col_cat': "الفئة",
        'search_col_freq': "التردد",
        'search_no_results': "لا توجد نتائج",
        'config_title': "🎛️ ترتيب الفئات",
        'multiselect_label': "اختار ترتيب الفئات",
        'preview_title': "📊 المعاينة",
        'channels_count': "قناة",
        'ready_msg': "تم تجهيز الملف",
        'btn_download_tll': "تحميل TLL",
        'btn_download_txt': "تحميل التقرير"
    },
    'en': {
        'title': "RAMBO LG Sorter",
        'subtitle': "Smart Channel Sorting System",
        'upload_label': "Upload TLL",
        'update_freq_label': "Auto update frequencies",
        'add_new_ch_label': "Auto add channels",
        'success_read': "File loaded: ",
        'search_header': "Search Channels",
        'search_placeholder': "Search...",
        'search_col_num': "No",
        'search_col_name': "Channel",
        'search_col_cat': "Category",
        'search_col_freq': "Freq",
        'search_no_results': "No results",
        'config_title': "Category Order",
        'multiselect_label': "Select order",
        'preview_title': "Preview",
        'channels_count': "channels",
        'ready_msg': "File ready",
        'btn_download_tll': "Download TLL",
        'btn_download_txt': "Download TXT"
    }
}

t = UI_TEXT[st.session_state.lang]

st.set_page_config(layout="wide")
st.title(t['title'])
st.markdown(t['subtitle'])

# ── DB ──
NILESAT_LIVE_DB = {
    "MBC 2": {"frequency": 11938, "polarization": "Vertical"},
    "CBC": {"frequency": 12092, "polarization": "Vertical"},
    "ON E": {"frequency": 12092, "polarization": "Vertical"},
    "AL HAYAT": {"frequency": 12207, "polarization": "Vertical"},
    "SAT-7 KIDS": {"frequency": 11353, "polarization": "Vertical"},
}

ALL_CATEGORIES = ["News", "Movies", "Kids", "Sports", "Religious", "General"]

def classify(name):
    n = name.upper()
    if "CBC" in n or "NEWS" in n:
        return "News"
    if "MBC" in n or "MOVIE" in n:
        return "Movies"
    if "KID" in n:
        return "Kids"
    if "SPORT" in n:
        return "Sports"
    if "QURAN" in n or "HAYAT" in n:
        return "Religious"
    return "General"

uploaded_file = st.file_uploader(t['upload_label'], type=["TLL"])

if uploaded_file:

    file_bytes = uploaded_file.read()

    # ── FIX XML SAFELY ──
    try:
        file_text = file_bytes.decode("utf-8", errors="ignore")
        root = ET.fromstring(file_text.encode("utf-8"))
    except:
        file_text = file_bytes.decode("latin-1", errors="ignore")
        root = ET.fromstring(file_text.encode("latin-1", errors="ignore"))

    model = root.find(".//ModelName")
    model_name = model.text if model is not None else "Unknown"

    legacy = root.find(".//legacybroadcast")
    is_modern = legacy is not None and legacy.text

    st.success(t['success_read'] + model_name)

    update_freq = st.checkbox(t['update_freq_label'], value=True)
    add_new = st.checkbox(t['add_new_ch_label'], value=True)

    user_order = st.multiselect(t['multiselect_label'], ALL_CATEGORIES, default=ALL_CATEGORIES)
    priority = user_order + [c for c in ALL_CATEGORIES if c not in user_order]

    channels = []
    report = []

    # ───────────────────────── MODERN ─────────────────────────
    if is_modern:

        data = json.loads(legacy.text)
        ch_list = data.get("channelList", [])

        existing = set()

        for ch in ch_list:
            name = ch.get("channelName")
            freq = str(ch.get("frequency"))
            up = name.upper()
            existing.add(up)

            if update_freq and up in NILESAT_LIVE_DB:
                ch["frequency"] = NILESAT_LIVE_DB[up]["frequency"]

            channels.append({
                "name": name,
                "freq": ch["frequency"],
                "node": ch,
                "injected": False
            })

        # ADD NEW
        if add_new:
            sample = ch_list[0]
            for k, v in NILESAT_LIVE_DB.items():
                if k not in existing:
                    new = sample.copy()
                    new["channelName"] = k
                    new["frequency"] = v["frequency"]
                    channels.append({
                        "name": k,
                        "freq": v["frequency"],
                        "node": new,
                        "injected": True
                    })

        channels.sort(key=lambda x: priority.index(classify(x["name"])))

        for i, c in enumerate(channels, 1):
            c["node"]["majorNumber"] = i

        legacy.text = json.dumps(data)

        final_file = ET.tostring(root, encoding="utf-8")

    # ───────────────────────── OLD ─────────────────────────
    else:

        items = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)

        parsed = []
        existing = set()

        for it in items:
            name = re.search(r'<vchName>(.*?)</vchName>', it)
            freq = re.search(r'<frequency>(.*?)</frequency>', it)

            name = name.group(1) if name else "Unknown"
            f = freq.group(1) if freq else "0"

            existing.add(name.upper())

            parsed.append({
                "name": name,
                "freq": f,
                "raw": it,
                "injected": False
            })

        if add_new:
            sample = items[0]
            for k, v in NILESAT_LIVE_DB.items():
                if k not in existing:
                    new = sample.replace("<vchName>.*?</vchName>", f"<vchName>{k}</vchName>")
                    new = re.sub(r'<frequency>\d+</frequency>', f'<frequency>{v["frequency"]}</frequency>', new)

                    parsed.append({
                        "name": k,
                        "freq": v["frequency"],
                        "raw": new,
                        "injected": True
                    })

        parsed.sort(key=lambda x: priority.index(classify(x["name"])))

        rebuilt = []
        for i, c in enumerate(parsed, 1):
            r = c["raw"]
            if "<prNum>" in r:
                r = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{i}</prNum>', r)
            else:
                r = r.replace("<ITEM>", f"<ITEM>\n<prNum>{i}</prNum>")
            rebuilt.append(r)

        start = file_text.find("<ITEM>")
        end = file_text.rfind("</ITEM>") + 6

        final_file = (file_text[:start] + "\n".join(rebuilt) + file_text[end:]).encode()

    # ── SEARCH ──
    st.write("---")
    q = st.text_input(t['search_placeholder']).upper()

    if q:
        res = [c for c in channels if q in c["name"].upper()]
        if res:
            st.write(res)
        else:
            st.warning(t['search_no_results'])

    # ── PREVIEW ──
    st.write("---")
    st.write(t['preview_title'])

    grouped = {}
    for c in channels:
        cat = classify(c["name"])
        grouped.setdefault(cat, []).append(c["name"])

    for cat in priority:
        if cat in grouped:
            st.write(f"{cat}: {grouped[cat]}")

    # ── DOWNLOAD ──
    st.success(t['ready_msg'])

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(t['btn_download_tll'], final_file, "GlobalClone00001.TLL")

    with col2:
        st.download_button(t['btn_download_txt'], str(grouped), "Channels.txt")
