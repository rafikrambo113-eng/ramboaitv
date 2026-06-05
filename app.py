import streamlit as st

# ─────────────────────────────────────────────
# تهيئة الجلسة (Session State)
# ─────────────────────────────────────────────
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ─────────────────────────────────────────────
# إعداد الصفحة
# ─────────────────────────────────────────────
st.set_page_config(page_title="RamboAITV — مرتب القنوات الذكي", page_icon="📺", layout="wide")

# ─────────────────────────────────────────────
# الهيدر الرئيسي
# ─────────────────────────────────────────────
st.title("📺 RamboAITV")
st.markdown("⚡ أول موقع مصري ذكي لترتيب قنوات LG بالذكاء الاصطناعي")
st.markdown("🇪🇬 بأيدٍ مصرية ودماغ منياوية")

st.markdown("---")

# ─────────────────────────────────────────────
# المقدمة
# ─────────────────────────────────────────────
st.header("🎯 مش محتاج تدور على ملف قنوات تليفزيون LG تاني!")

st.write("هل بتعاني من فوضى ترتيب القنوات على شاشة الـ LG (الرسيفر الداخلي)؟")
st.write("زهقت من البحث اليدوي عن الترددات الجديدة؟")

st.markdown("")
st.success("🚀 بكل فخر، بنقدم لكم RamboAITV!")
st.info("""
الموقع الأول من نوعه **"بأيدٍ مصرية ودماغ منياوية"**، 
اللي بيحل لك أزمة ترتيب القنوات **بضغطة زر** وبقوة **الذكاء الاصطناعي!**
""")

st.markdown("---")

# ─────────────────────────────────────────────
# ليه تختار RamboAITV؟
# ─────────────────────────────────────────────
st.header("🌟 ليه تختار RamboAITV؟")

st.markdown("🎨 الموقع مصمم بـ **3 صفحات احترافية** لخدمتك:")

st.markdown("")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1️⃣ الترتيب الذكي (بالفئات/Categories)")
    st.write("ارفع ملف قنواتك اللي سحبته على الفلاشة، والموقع هيقوم أوتوماتيكياً بترتيبه لك حسب الفئات (رياضة، أفلام، أخبار.. إلخ).")
    st.write("✅ تحميل ملف Text للترتيب")
    st.write("✅ ملف القنوات المحدث جاهز للتشغيل")

with col2:
    st.subheader("2️⃣ الترتيب اليدوي")
    st.write("ليك تحكم كامل! رتب قنواتك قناة قناة حسب ذوقك، واعتمد ترتيبك الخاص.")
    st.write("✅ تحميل ملف مرتب ومحدث")
    st.write("✅ بكل سهولة وبساطة")

with col3:
    st.subheader("3️⃣ توليد بالذكاء الاصطناعي")
    st.markdown("**(ميزة حصرية! 🔥)**")
    st.write("لأول مرة، بس اكتب موديل جهازك، بلد البث، وسنة الصنع، والذكاء الاصطناعي هيقوم بتوليد ملف قنوات متوافق مع شاشتك من الصفر!")

st.markdown("---")

# ─────────────────────────────────────────────
# الميزات الخارقة للذكاء الاصطناعي
# ─────────────────────────────────────────────
st.header("🔥 ميزتان خارقتان للذكاء الاصطناعي داخل الموقع")

col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.subheader("📡 تحديث الترددات")
    st.write("وداعاً للقنوات اللي بتظهر 'بدون إشارة'")
    st.write("الموقع بيلفظ الترددات الميتة والقديمة ويحدثها أوتوماتيكياً")

with col_ai2:
    st.subheader("🆕 اكتشاف القنوات الجديدة")
    st.write("الموقع بيعرفك تلقائياً بالقنوات الحديثة اللي بدأت بثها مؤخراً على القمر الصناعي")
    st.write("عشان تكون دائماً في قلب الحدث!")

st.markdown("---")

# ─────────────────────────────────────────────
# أزرار التنقل للصفحات
# ─────────────────────────────────────────────
st.header("🚀 جرب الموقع دلوقتي")

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("🧠 الترتيب الذكي (بالفئات)"):
        st.session_state.page = 'page1_catogary_sorter'
        st.rerun()

with col_btn2:
    if st.button("✋ الترتيب اليدوي"):
        st.session_state.page = 'page2_manual_sorter'
        st.rerun()

with col_btn3:
    if st.button("🤖 توليد بالذكاء الاصطناعي"):
        st.session_state.page = 'page3_generate_sorter'
        st.rerun()

# ─────────────────────────────────────────────
# الفوتر
# ─────────────────────────────────────────────
st.markdown("---")

st.markdown("**🛠️ DEVELOPER ENG: RAFIK NATHAN**")
st.write("📱 MOBILE / الموبايل: +201280339779")
st.write("✉️ E-MAIL: rafikrambo113@gmail.com")

whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"
st.link_button("WhatsApp", whatsapp_url)
