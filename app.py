import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# ── Session ──
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# ── UI TEXT (مختصر بدون تغيير) ──
UI_TEXT = {
    'ar': {
        'title': "📺 RAMBO - المنسق العالمي لشاشات LG",
        'subtitle': "⚡ هندسة متطورة لترتيب ملفات القنوات",
        'upload_label': "🚀 اختر ملف القنوات (TLL):",
        'success_read': "🛸 تم قراءة الملف بنجاح: ",
        'search_header': "🔍 البحث داخل القنوات:",
        'search_placeholder': "اكتب اسم القناة...",
        'search_no_results': "⚠️ لا توجد نتائج",
        'config_title': "🎛️ ترتيب الكاتيجوري",
        'multiselect_label': "اختار ترتيب الفئات:",
        'preview_title': "📊 المعاينة",
        'channels_count': "قناة",
        'ready_msg': "🌌 تم تجهيز الملف بنجاح",
        'btn_download_tll': "📥 تحميل TLL",
        'btn_download_txt': "📄 تحميل TXT"
    }
}

t = UI_TEXT[st.session_state.lang]

st.set_page_config(page_title="RAMBO", layout="wide")

st.title(t['title'])
st.markdown(t['subtitle'])

# ── DB ──
NILESAT_LIVE_DB = {
    "MBC 2": {"frequency": 11938, "polarization": "Vertical"},
    "MBC 4": {"frequency": 11938, "polarization": "Vertical"},
    "AL HAYAT": {"frequency": 12207, "polarization": "Vertical"},
    "IQRAA": {"frequency": 11938, "polarization": "Vertical"},
    "ON TIME SPORTS 1": {"frequency": 11861, "polarization": "Vertical"},
}

ALL_AVAILABLE_CATEGORIES = [
    "Islamic",
    "Movies",
    "Sports",
    "News",
    "Kids",
    "General"
]

def ai_classify(name):
    n = name.upper()

    if any(x in n for x in ["QURAN", "IQRA", "HAYAT"]):
        return "Islamic"
    if any(x in n for x in ["MBC", "CINEMA", "MOVIE"]):
        return "Movies"
    if any(x in n for x in ["SPORT"]):
        return "Sports"
    if any(x in n for x in ["NEWS", "BBC", "CNN"]):
        return "News"
    if any(x in n for x in ["KIDS", "CARTOON"]):
        return "Kids"

    return "General"


# ── Upload ──
uploaded_file = st.file_uploader(t['upload_label'], type=["TLL"])

if uploaded_file:

    file_bytes = uploaded_file.read()

    try:
        file_text = file_bytes.decode("utf-8")
    except:
        file_text = file_bytes.decode("latin-1")

    root = ET.fromstring(file_text.encode("utf-8"))

    st.info(t['success_read'])

    # ── OLD SYSTEM FIX + NEW SYSTEM ──
    channels_to_sort = []
    existing = set()

    # ===== MODERN =====
    legacy = root.find(".//legacybroadcast")

    if legacy is not None:

        data = json.loads(legacy.text)
        channels = data.get("channelList", [])

        for ch in channels:
            name = ch.get("channelName", "")
            freq = str(ch.get("frequency", ""))

            existing.add(name.upper())

            category = ai_classify(name)

            channels_to_sort.append({
                "name": name,
                "freq": freq,
                "node": ch,
                "category": category
            })

    # ===== OLD ITEM SYSTEM FIXED =====
    else:

        items = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)

        for it in items:

            name = re.search(r'<vchName>(.*?)</vchName>', it)
            freq = re.search(r'<frequency>(.*?)</frequency>', it)

            name = name.group(1) if name else "Unknown"
            freq = freq.group(1) if freq else "0"

            existing.add(name.upper())

            category = ai_classify(name)

            channels_to_sort.append({
                "name": name,
                "freq": freq,
                "raw": it,
                "category": category
            })

    # ── CATEGORY ORDER ──
    user_order = st.multiselect(t['multiselect_label'], ALL_AVAILABLE_CATEGORIES)

    final_order = user_order + [c for c in ALL_AVAILABLE_CATEGORIES if c not in user_order]

    # 🔥 FIXED SORT (IMPORTANT)
    channels_sorted = sorted(
        channels_to_sort,
        key=lambda x: final_order.index(x["category"])
    )

    # ── TXT ──
    txt = "CHANNEL REPORT\n\n"

    # ── BUILD FILE ──
    if legacy is not None:

        data["channelList"] = []

        for i, ch in enumerate(channels_sorted, 1):

            node = ch["node"]
            node["majorNumber"] = i

            data["channelList"].append(node)

            txt += f"{i}. {ch['name']} | {ch['freq']}\n"

        legacy.text = json.dumps(data, ensure_ascii=False)

        final_file = ET.tostring(root, encoding="utf-8")

    else:

        new_items = []

        for i, ch in enumerate(channels_sorted, 1):

            raw = ch["raw"]

            if "<prNum>" in raw:
                raw = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{i}</prNum>', raw)
            else:
                raw = raw.replace("<ITEM>", f"<ITEM>\n<prNum>{i}</prNum>")

            new_items.append(raw)

            txt += f"{i}. {ch['name']} | {ch['freq']}\n"

        combined = "\n".join(new_items)

        start = file_text.find("<ITEM>")
        end = file_text.rfind("</ITEM>") + 7

        if start != -1:
            final_out = file_text[:start] + combined + file_text[end:]
        else:
            final_out = combined

        final_file = final_out.encode("utf-8")


    st.success(t['ready_msg'])

    col1, col2 = st.columns(2)

    with col1:
        st.download_button("📥 TLL", final_file, file_name="GlobalClone00001.TLL")

    with col2:
        st.download_button("📄 TXT", txt, file_name="Channels.txt")
