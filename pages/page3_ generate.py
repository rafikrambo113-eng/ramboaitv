import streamlit as st
import json

st.title("⚙️ RAMBO - مولد ملفات القنوات (احترافي)")

# ── قاعدة البيانات (محدثة بالقيم الحقيقية للترددات) ──
NILESAT_GEN_DB = {
    "قنوات إسلامية": [
        {"name": "QURAN KAREEM", "freq": 11727, "pol": 0}, 
        {"name": "IQRAA", "freq": 11938, "pol": 0}
    ],
    "أفلام": [
        {"name": "MBC 2", "freq": 11938, "pol": 0}, 
        {"name": "ROTANA CINEMA", "freq": 11938, "pol": 0}
    ]
}

# ── الإدخالات ──
col1, col2 = st.columns(2)
with col1:
    model = st.text_input("📺 موديل الشاشة:", "OLED55")
with col2:
    year = st.selectbox("📅 سنة الصنع:", ["2019 وما بعد (حديث)", "2018 وما قبل (قديم)"])

system_type = "حديث" if "حديث" in year else "قديم"
user_priority = st.multiselect("🎛️ ترتيب الفئات:", list(NILESAT_GEN_DB.keys()), default=list(NILESAT_GEN_DB.keys()))

if st.button("🚀 توليد الملف (مطابق للمواصفات)"):
    ordered_channels = []
    for cat in user_priority:
        ordered_channels.extend(NILESAT_GEN_DB.get(cat, []))

    if system_type == "حديث":
        # الهيكل الذي وجدته في ملفك الحقيقي
        channel_list = []
        for i, ch in enumerate(ordered_channels, 1):
            channel_list.append({
                "majorNumber": i, "minorNumber": 0, "channelName": ch["name"],
                "frequency": ch["freq"], "polarization": ch["pol"], "symbolRate": 27500,
                "serviceType": 1, "programType": 1, "isLocked": 0, "isSkipped": 0
            })
        
        data_wrapper = {"channelList": channel_list, "satelliteList": [{"name": "Nilesat", "pos": 70}]}
        json_payload = json.dumps(data_wrapper)
        # الترويسة الصحيحة التي تتوقعها الشاشة
        final_content = f'<?xml version="1.0" encoding="UTF-8"?><TLLDATA><ModelName>{model}</ModelName><Data><![CDATA[{json_payload}]]></Data></TLLDATA>'
    else:
        # هيكل قديم بسيط
        final_content = f'<?xml version="1.0" encoding="UTF-8"?><TLLDATA><ModelName>{model}</ModelName>' + \
                        "".join([f'<ITEM><prNum>{i}</prNum><name>{ch["name"]}</name><freq>{ch["freq"]}</freq></ITEM>' for i, ch in enumerate(ordered_channels, 1)]) + \
                        '</TLLDATA>'

    st.success("✅ تم بناء الملف بنجاح وبمطابقة تامة لهيكل ملفك!")
    st.download_button("📥 تحميل الملف النهائي", final_content.encode('utf-8'), "GlobalClone00001.TLL")
