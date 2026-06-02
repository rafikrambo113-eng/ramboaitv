import streamlit as st
import json

# ── التنسيق الجمالي ──
st.markdown("""
    <style>
    .generator-card { background: rgba(13, 7, 33, 0.85); border: 2px solid #00f0ff; border-radius: 14px; padding: 25px; margin-bottom: 25px; box-shadow: 0px 5px 15px rgba(0, 240, 255, 0.2); }
    h1 { color: #ff007f !important; text-align: center; }
    .stButton>button { background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important; color: white !important; width: 100%; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ── قاعدة البيانات ──
NILESAT_GEN_DB = {
    "⛪ قنوات مسيحية": ["CTV", "AGHAPY", "MESAT", "SAT-7"],
    "🕌 قنوات إسلامية": ["QURAN", "IQRAA", "MAJD", "RAHMA"],
    "🎬 مسلسلات ودراما": ["CBC DRAMA", "ON DRAMA", "MBC DRAMA"],
    "🍿 أفلام": ["MBC 2", "MBC MAX", "ROTANA CINEMA"],
    "👶 أطفال": ["SPACE TOON", "MAJID", "CN ARABIC"],
    "⚽ رياضة": ["ON TIME 1", "ON TIME 2", "AL KASS"],
    "📰 أخبار": ["AL JAZEERA", "AL ARABIYA", "EXTRA NEWS"]
}

st.title("⚙️ RAMBO - مولد ملفات القنوات")
st.markdown("### ⚡ بناء ملفات قنوات LG من الصفر")

# ── الإدخالات ──
st.markdown('<div class="generator-card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    sat = st.selectbox("🛰️ القمر الصناعي:", ["Nilesat 7W"])
    country = st.selectbox("🌍 بلد البث:", ["مصر", "السعودية", "الإمارات"])
with col2:
    model = st.text_input("📺 موديل الشاشة (اختياري):")
    year = st.selectbox("📅 سنة الصنع:", ["2019 وما بعد (نظام حديث)", "2018 وما قبل (نظام قديم)"])

system_type = "حديث" if "حديث" in year else "قديم"
st.info(f"💡 النظام المكتشف: **{system_type}**")

# ── عرض الكاتوجري ──
st.write("### 📊 تفاصيل المحتوى:")
for cat, channels in NILESAT_GEN_DB.items():
    with st.expander(f"{cat} — (عدد: {len(channels)})"):
        st.write(f"القنوات: {', '.join(channels)}")

update_freq = st.checkbox("⚛️ تحديث الترددات تلقائياً", value=True)
add_new_ch = st.checkbox("✨ زرع القنوات الجديدة", value=True)
user_priority = st.multiselect("🎛️ ترتيب الفئات:", list(NILESAT_GEN_DB.keys()), default=list(NILESAT_GEN_DB.keys()))
st.markdown('</div>', unsafe_allow_html=True)

# ── زر التوليد ──
if st.button("🚀 توليد الملف النهائي"):
    ordered_channels = []
    for cat in user_priority:
        for ch_name in NILESAT_GEN_DB.get(cat, []):
            ordered_channels.append({"name": ch_name, "freq": 11000, "pol": "Vertical"})

    if system_type == "حديث":
        # هيكل JSON متوافق مع ChanSort
        channel_list = [{
            "channelName": ch["name"], "majorNumber": i, "minorNumber": 0, 
            "frequency": ch["freq"], "polarization": 0, "programType": 0, 
            "serviceType": 1, "encrypted": False, "skipped": False, "locked": False
        } for i, ch in enumerate(ordered_channels, 1)]
        
        json_str = json.dumps({"channelList": channel_list, "satelliteList": [{"satelliteName": "Nilesat", "satellitePosition": 70}]}, ensure_ascii=False)
        final_content = f'<?xml version="1.0" encoding="UTF-8"?><TLLDATA><ModelName>GlobalClone</ModelName><Data><![CDATA[{json_str}]]></Data></TLLDATA>'
    else:
        # هيكل XML للموديلات القديمة
        items = "".join([f'<ITEM><prNum>{i}</prNum><vchName>{ch["name"]}</vchName><frequency>{ch["freq"]}</frequency><polarization>{ch["pol"]}</polarization></ITEM>' for i, ch in enumerate(ordered_channels, 1)])
        final_content = f'<?xml version="1.0" encoding="utf-8"?><TLLDATA><ModelName>GlobalClone</ModelName>{items}</TLLDATA>'

    report_content = "تقرير ملف القنوات RAMBO\n" + "="*30 + "\n" + "\n".join([f"{i}. {ch['name']}" for i, ch in enumerate(ordered_channels, 1)])

    st.success(f"✅ تم بناء ملف الـ {system_type} بنجاح!")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button("📥 تحميل TLL", final_content.encode('utf-8'), "GlobalClone00001.TLL", "application/octet-stream")
    with col_btn2:
        st.download_button("📄 تحميل تقرير TXT", report_content, "Channels_List.txt", "text/plain")

    st.warning("💡 بعد تنزيل الملف: ادخل مدير القنوات -> تعديل كل القنوات -> استعادة (Restore).")
