import streamlit as st

st.set_page_config(page_title="البث المباشر للمباريات", page_icon="⚽", layout="wide")

st.title("📺 شاشة البث المباشر ومباريات اليوم")
st.write("اختر الموقع اللي عايز تتفرج عليه من الأزرار تحت، وهيفتحلك البث المباشر فوراً جوه صفحتك وبدون أي أعطال.")

# قائمة بأقوى مواقع البث المباشر الشغالة حالياً
SITES = {
    "🔥 يلا شوت (Yalla Shoot)": "https://yalla-shoot.io/",
    "⚽ كورة لايف (Kora Live)": "https://live.kooora4live.com/",
    "🏆 الأسطورة لبث المباريات": "https://live.livehd7.club/",
    "📺 كورة سيتي (Kora City)": "https://www.koracity.com/"
}

# عمل الأزرار لاختيار الموقع
if 'current_url' not in st.session_state:
    st.session_state.current_url = "https://yalla-shoot.io/" # الموقع الافتراضي أول ما يفتح
if 'site_name' not in st.session_state:
    st.session_state.site_name = "يلا شوت"

# عرض الأزرار بجانب بعضها بشكل شيك
cols = st.columns(len(SITES))
for idx, (name, url) in enumerate(SITES.items()):
    with cols[idx]:
        if st.button(name, use_container_width=True):
            st.session_state.current_url = url
            st.session_state.site_name = name

st.markdown("---")
st.subheader(f"🎬 المستعرض الحالي: {st.session_state.site_name}")

# السحر كله هنا: فتح الموقع كاملاً بمبارياته ومشغلاته جوه الـ Streamlit
st.components.v1.iframe(st.session_state.current_url, height=800, scrolling=True)
