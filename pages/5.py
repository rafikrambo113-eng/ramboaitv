import streamlit as st

st.set_page_config(page_title="دليل البث المباشر للمباريات", page_icon="⚽", layout="centered")

st.title("📺 دليل تشغيل مباريات اليوم المباشر")
st.write("بسبب حماية مواقع الكورة ومنعها للتشغيل المدمج، الأزرار دي هتفتح لك أقوى مواقع البث الحية حالياً في صفحة جديدة فوراً عشان تتفرج بدون تقطيع وبأعلى جودة، وتقدر تنقلها للشاشة الـ LG.")

st.markdown("---")
st.write("### 🚀 اختر موقع البث وابدأ المشاهدة فوراً:")

# قائمة بأقوى مواقع البث المستقرة والشغالة حالياً
SITES = {
    "🔥 موقع يلا شوت (Yalla Shoot)": "https://yalla-shoot.io/",
    "⚽ موقع كورة لايف (Kora Live)": "https://live.kooora4live.com/",
    "🏆 موقع الأسطورة (Live HD7)": "https://live.livehd7.club/",
    "📺 موقع كورة سيتي (Kora City)": "https://www.koracity.com/"
}

# إنشاء أزرار روابط مباشرة تفتح في صفحة جديدة تلقائياً
for name, url in SITES.items():
    st.link_button(name, url, use_container_width=True)

st.markdown("---")
st.info("💡 **نصيحة لشاشة الـ LG:** افتح الصفحة دي من متصفح الموبايل، واضغط على الموقع اللي شغال عليه الماتش، وأول ما يشتغل الفيديو استخدم خاصية الـ Smart Share أو تطبيق Web Video Caster عشان ترمي الماتش على الشاشة الكبيرة فوراً بكامل الجودة وبدون إعلانات.")
