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
# إعداد الصفحة + CSS مستقبلي
# ─────────────────────────────────────────────
st.set_page_config(page_title="RamboAITV — مرتب القنوات الذكي", page_icon="📺", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Cairo:wght@400;600;700;900&display=swap');

/* الخلفية المستقبيلية */
.main {
    background: radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%) !important;
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
}

/* العناوين بألوان نيون */
h1 {
    color: #ff007f !important;
    text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.5) !important;
    font-family: 'Orbitron', 'Cairo' !important;
    font-weight: 900 !important;
    text-align: center !important;
    font-size: 52px !important;
    direction: ltr !important;
}

h2 {
    color: #00f0ff !important;
    text-shadow: 0 0 5px #00f0ff !important;
    font-family: 'Orbitron', 'Cairo' !important;
    font-weight: 700 !important;
    text-align: center !important;
}

h3, h4 {
    color: #00f0ff !important;
    text-shadow: 0 0 5px #00f0ff !important;
    font-family: 'Cairo' !important;
    font-weight: 700 !important;
}

/* النصوص */
p, label, .stMarkdown, .stBody {
    color: #e0e0e0 !important;
    font-size: 18px !important;
    line-height: 1.9 !important;
    direction: rtl !important;
    text-align: right !important;
}

/* التوسيط للنصوص المطلوبة */
.center-text {
    text-align: center !important;
    direction: rtl !important;
}

.center-rtl {
    text-align: center !important;
    direction: rtl !important;
}

/* الأزرار بمستقبلية */
.stButton>button {
    background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
    color: #ffffff !important;
    border: 2px solid #ff007f !important;
    border-radius: 14px !important;
    font-weight: bold !important;
    font-size: 18px !important;
    padding: 12px 24px !important;
    box-shadow: 0 0 15px rgba(255,0,127,0.4) !important;
    transition: all 0.3s ease !important;
    font-family: 'Cairo' !important;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #ff6b9f 0%, #cc5577 100%) !important;
    box-shadow: 0 0 25px rgba(255,0,127,0.7) !important;
    transform: translateY(-3px) !important;
}

/* توسيط الأزرار */
.stButton {
    text-align: center !important;
}

/* الصناديق */
.stBlock {
    background: rgba(13, 7, 33, 0.85) !important;
    border: 2px solid #00f0ff !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 0 20px rgba(0,240,255,0.3) !important;
}

/* info و success */
.stInfo {
    background: rgba(0,240,255,0.15) !important;
    border-left: 5px solid #00f0ff !important;
    color: #00f0ff !important;
    direction: rtl !important;
    text-align: right !important;
}

.stSuccess {
    background: rgba(255,0,127,0.15) !important;
    border-left: 5px solid #ff007f !important;
    color: #ff6b9f !important;
    direction: rtl !important;
    text-align: right !important;
}

/* الفواصل */
hr {
    border-color: #00f0ff !important;
    opacity: 0.5 !important;
}

/* الروابط */
a {
    color: #00f0ff !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# الهيدر الرئيسي
# ─────────────────────────────────────────────
st.markdown("<h1>📺 RamboAITV</h1>", unsafe_allow_html=True)
st.markdown("<p class='center-text' style='font-size:24px; color:#00f0ff; font-weight:700;'>⚡ أول موقع مصري ذكي لترتيب قنوات LG بالذكاء الاصطناعي</p>", unsafe_allow_html=True)
st.markdown("<p class='center-text' style='color:#ff007f; font-weight:700; font-size:20px;'>🇪🇬 بأيدٍ مصرية ودماغ منياوية</p>", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# المقدمة
# ─────────────────────────────────────────────
st.header("🎯 مش محتاج تدور على ملف قنوات تليفزيون LG تاني!")

st.markdown("<p class='center-text'>هل بتعاني من فوضى ترتيب القنوات على شاشة الـ LG (الرسيفر الداخلي)؟</p>", unsafe_allow_html=True)
st.markdown("<p class='center-text'>زهقت من البحث اليدوي عن الترددات الجديدة؟</p>", unsafe_allow_html=True)

st.markdown("")
st.success("🚀 بكل فخر، بنقدم لكم RamboAITV!")
st.info("**الموقع الأول من نوعه** \"بأيدٍ مصرية ودماغ منياوية\"، اللي بيحل لك أزمة ترتيب القنوات **بضغطة زر** وبقوة **الذكاء الاصطناعي!**")

st.markdown("---")

# ─────────────────────────────────────────────
# ليه تختار RamboAITV؟
# ─────────────────────────────────────────────
st.header("🌟 ليه تختار RamboAITV؟")

st.markdown("<p class='center-text'>🎨 الموقع مصمم بـ **3 صفحات احترافية** لخدمتك:</p>", unsafe_allow_html=True)

st.markdown("")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1️⃣ الترتيب الذكي")
    st.markdown("**(بالفئات/Categories)**")
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
    st.markdown("<p class='center-text' style='margin-bottom:10px;'>🧠 الترتيب الذكي (بالفئات)</p>", unsafe_allow_html=True)
    if st.button("فتح الصفحة", key="btn_smart_sort"):
        st.session_state.page = 'page1_catogary_sorter'
        st.rerun()

with col_btn2:
    st.markdown("<p class='center-text' style='margin-bottom:10px;'>✋ الترتيب اليدوي</p>", unsafe_allow_html=True)
    if st.button("فتح الصفحة", key="btn_manual_sort"):
        st.session_state.page = 'page2_manual_sorter'
        st.rerun()

with col_btn3:
    st.markdown("<p class='center-text' style='margin-bottom:10px;'>🤖 توليد بالذكاء الاصطناعي</p>", unsafe_allow_html=True)
    if st.button("فتح الصفحة", key="btn_ai_generate"):
        st.session_state.page = 'page3_generate_sorter'
        st.rerun()

# ─────────────────────────────────────────────
# الفوتر
# ─────────────────────────────────────────────
st.markdown("---")

st.markdown("<p class='center-text' style='font-size:22px; color:#ff007f; font-weight:bold;'>🛠️ DEVELOPER ENG: RAFIK NATHAN</p>", unsafe_allow_html=True)
st.markdown("<p class='center-text'>📱 MOBILE / الموبايل: +201280339779</p>", unsafe_allow_html=True)
st.markdown("<p class='center-text'>✉️ E-MAIL: rafikrambo113@gmail.com</p>", unsafe_allow_html=True)

whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"
st.markdown("<p class='center-text'></p>", unsafe_allow_html=True)
st.link_button("WhatsApp 💬", whatsapp_url)
