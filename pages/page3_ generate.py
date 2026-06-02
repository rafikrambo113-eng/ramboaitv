import streamlit as st
import json

# 1. التنسيق (لا تضع أي if st.button قبل هذا)
st.markdown("""
    <style>
    .generator-card { background: rgba(13, 7, 33, 0.85); border: 2px solid #00f0ff; border-radius: 14px; padding: 25px; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# 2. البيانات
NILESAT_GEN_DB = {
    "⛪ قنوات مسيحية": ["CTV", "AGHAPY", "MESAT", "SAT-7"],
    "🕌 قنوات إسلامية": ["QURAN", "IQRAA", "MAJD", "RAHMA"],
    "🎬 مسلسلات ودراما": ["CBC DRAMA", "ON DRAMA", "MBC DRAMA"],
    "🍿 أفلام": ["MBC 2", "MBC MAX", "ROTANA CINEMA"],
    "👶 أطفال": ["SPACE TOON", "MAJID", "CN ARABIC"],
    "⚽ رياضة": ["ON TIME 1", "ON TIME 2", "AL KASS"],
    "📰 أخبار": ["AL JAZEERA", "AL ARABIYA", "EXTRA NEWS"]
}

# 3. واجهة الإدخال
st.title("⚙️ RAMBO - مولد ملفات القنوات")
col1, col2 = st.columns(2)
with col1:
    sat = st.selectbox("🛰️ القمر الصناعي:", ["Nilesat 7W"])
    country = st.selectbox("🌍 بلد البث:", ["مصر", "السعودية", "الإمارات"])
with col2:
    model = st.text_input("📺 موديل الشاشة:")
    year = st.selectbox("📅 سنة الصنع:", ["2019 وما بعد (نظام حديث)", "2018 وما قبل (نظام قديم)"])

system_type = "حديث" if "حديث" in year else "قديم"
update_freq = st.checkbox("⚛️ تحديث الترددات تلقائياً", value=True)
add_new_ch = st.checkbox("✨ زرع القنوات الجديدة", value=True)
user_priority = st.multiselect("🎛️ الترتيب عن طريق الكاتوجري:", list(NILESAT_GEN_DB.keys()), default=list(NILESAT_GEN_DB.keys()))

# 4. زر التوليد (هنا السحر! لا تضعه فوق!)
if st.button("🚀 توليد الملف النهائي"):
    ordered_channels = []
    for cat in user_priority:
        for ch_name in NILESAT_GEN_DB.get(cat, []):
            ordered_channels.append({"name": ch_name, "freq": "11000", "pol": "Vertical"})

    if system_type == "حديث":
        channel_list = [{"channelName": ch["name"], "majorNumber": i, "minorNumber": 0, "frequency": 11000, "polarization": ch["pol"], "satelliteName": "Nilesat", "serviceType": 1} for i, ch in enumerate(ordered_channels, 1)]
        payload = json.dumps({"channelList": channel_list, "satelliteList": [{"satelliteName": "Nilesat"}]}, ensure_ascii=False)
        final_content = f'<?xml version="1.0" encoding="utf-8"?><TLLDATA><ModelName>{model or "RAMBO"}</ModelName><legacybroadcast><![CDATA[{payload}]]></legacybroadcast></TLLDATA>'
    else:
        items = "".join([f'<ITEM><prNum>{i}</prNum><vchName>{ch["name"]}</vchName><frequency>{ch["freq"]}</frequency><polarization>{ch["pol"]}</polarization></ITEM>' for i, ch in enumerate(ordered_channels, 1)])
        final_content = f'<?xml version="1.0" encoding="utf-8"?><TLLDATA><ModelName>{model or "RAMBO"}</ModelName>{items}</TLLDATA>'

    report_content = "تقرير ملف القنوات RAMBO\n" + "="*30 + "\n" + "\n".join([f"{i}. {ch['name']}" for i, ch in enumerate(ordered_channels, 1)])

    st.success(f"✅ تم بناء ملف الـ {system_type} بنجاح!")
    
    c1, c2 = st.columns(2)
    with c1: st.download_button("📥 تحميل TLL", final_content.encode('utf-8'), "GlobalClone00001.TLL")
    with c2: st.download_button("📄 تحميل TXT", report_content, "Channels_List.txt")
