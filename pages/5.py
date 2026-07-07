import streamlit as st

st.set_page_config(page_title="Rambo Live TV", page_icon="⚽", layout="wide")

st.title("📺 موقع رامبو للبث المباشر (سيرفرات جاهزة)")
st.write("اختر السيرفر اللي شغال عليه الماتش دلوقتي وهيفتحلك المشغل الأصلي فوراً.")

# قائمة بأقوى سيرفرات البث المباشر الجاهزة للمباريات وكأس العالم
servers = {
    "🔥 سيرفر يلا شوت الرئيسي": "https://yalla-shoot.io/",
    "⚽ سيرفر كورة لايف": "https://live.kooora4live.com/",
    "🏆 سيرفر الأسطورة لبث المباريات": "https://live.livehd7.club/"
}

# أزرار سريعة تفتح السيرفرات مباشرة
selected_server = st.radio("اختر سيرفر البث النشط الآن:", list(servers.keys()), horizontal=True)

st.markdown("---")

# فتح السيرفر المختار كمشغل كامل جوه موقعك
st.components.v1.iframe(servers[selected_server], height=700, scrolling=True)
