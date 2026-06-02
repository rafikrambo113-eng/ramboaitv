import streamlit as st
import json

# --- إعدادات التصميم ---
st.set_page_config(page_title="RAMBO Generator", layout="wide")
st.markdown("""
    <style>
    .generator-card { background: #1a1a2e; border: 2px solid #00f0ff; border-radius: 14px; padding: 25px; }
    </style>
""", unsafe_allow_html=True)

# --- قاعدة البيانات ---
NILESAT_GEN_DB = {
    "قنوات إسلامية": [{"name": "QURAN KAREEM", "freq": 11727, "pol": 0}, {"name": "IQRAA", "freq": 11938, "pol": 0}],
    "أفلام": [{"name": "MBC 2", "freq": 11938, "pol": 0}, {"name": "ROTANA CINEMA", "freq": 11938, "pol": 0}]
}

st.title("⚙️ RAMBO - مولد ملفات القنوات")

# --- الإدخالات ---
col1, col2 = st.columns(2)
with col1:
    model = st.text_input("📺 موديل الشاشة:", "OLED55")
with col2:
    year = st.selectbox("📅 النظام:", ["حديث", "قديم"])

user_priority = st.multiselect("🎛️ الفئات:", list(NILESAT_GEN_DB.keys()), default=list(NILESAT_GEN_DB.keys()))

# --- زر التوليد ---
if st.button("🚀 توليد الملف النهائي"):
    ordered_channels = []
    for cat in user_priority:
        ordered_channels.extend(NILESAT_GEN_DB.get(cat, []))

    if year == "حديث":
        # هيكل متوافق مع JSON الخاص بشاشات LG الحديثة
        channel_list = []
        for i, ch in enumerate(ordered_channels, 1):
            channel_list.append({
                "major": i, "minor": 0, "name": ch["name"],
                "freq": ch["freq"], "pol": ch["pol"], "symbol": 27500,
                "service": 1, "type": 1
            })
        
        json_data = json.dumps({"channels": channel_list, "satellites": [{"name": "Nilesat", "pos": 70}]})
        final_content = f'<?xml version="1.0" encoding="UTF-8"?><TLLDATA><ModelName>{model}</ModelName><Data><![CDATA[{json_data}]]></Data></TLLDATA>'
    else:
        # هيكل الـ XML للأنظمة القديمة
        items = "".join([f'<ITEM><prNum>{i}</prNum><name>{ch["name"]}</name></ITEM>' for i, ch in enumerate(ordered_channels, 1)])
        final_content = f'<?xml version="1.0" encoding="UTF-8"?><TLLDATA><ModelName>{model}</ModelName>{items}</TLLDATA>'

    st.success("✅ تم بناء الملف بنجاح!")
    
    # --- أزرار التحميل ---
    st.download_button("📥 تحميل TLL", final_content.encode('utf-8'), "GlobalClone00001.TLL", "application/octet-stream")
    st.download_button("📄 تحميل تقرير TXT", "\n".join([ch["name"] for ch in ordered_channels]), "Report.txt")

    st.warning("💡 ملاحظة: إذا استمر الخطأ في ChanSort، تأكد من أنك تفتح الملف عبر قائمة File -> Open وقم باختيار LG TLL.")
