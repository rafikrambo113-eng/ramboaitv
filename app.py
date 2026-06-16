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
st.set_page_config(page_title="Rambo_ AI_ TV — مرتب القنوات الذكي", page_icon="📺", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Cairo:wght@400;600;700;900&display=swap');

/* ── إخفاء شريط Streamlit العلوي (Manage / Share / Deploy) ── */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }
footer { display: none !important; }

/* ── فرض الخلفية السوداء على كل العناصر ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"],
section.main,
.main,
.block-container,
[data-testid="block-container"],
div.stApp,
.stApp {
    background: radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%) !important;
    background-color: #05020d !important;
}

.main {
    background: radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%) !important;
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
}

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
    font-family: 'Cairo' !important;
    font-weight: 700 !important;
}

p, label, .stMarkdown, .stBody {
    color: #e0e0e0 !important;
    font-size: 18px !important;
    line-height: 1.9 !important;
    direction: rtl !important;
    text-align: right !important;
}

.center-text {
    text-align: center !important;
    direction: rtl !important;
}

.stButton>button {
    background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
    color: #ffffff !important;
    border: 2px solid #ff007f !important;
    border-radius: 14px !important;
    font-weight: bold !important;
    font-size: 18px !important;
    padding: 12px 24px !important;
    box-shadow: 0 0 15px rgba(255,0,127,0.4) !important;
    font-family: 'Cairo' !important;
}

.stButton {
    text-align: center !important;
}

.stLinkButton>a {
    background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
    color: #ffffff !important;
    border: 2px solid #ff007f !important;
    border-radius: 14px !important;
    font-weight: bold !important;
    font-size: 18px !important;
    padding: 12px 24px !important;
    box-shadow: 0 0 15px rgba(255,0,127,0.4) !important;
    font-family: 'Cairo' !important;
    text-decoration: none !important;
}

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

hr {
    border-color: #00f0ff !important;
    opacity: 0.5 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# الهيدر الرئيسي
# ─────────────────────────────────────────────
st.markdown("<h1>📺 Rambo AI TV</h1>", unsafe_allow_html=True)
st.markdown("<p class='center-text' style='font-size:24px; color:#00f0ff; font-weight:700;'>⚡ أول موقع مصري ذكي لترتيب قنوات إل جي بالذكاء الاصطناعي</p>", unsafe_allow_html=True)
st.markdown("<p class='center-text' style='color:#ff007f; font-weight:700; font-size:20px;'>🇪🇬 بأيدٍ مصرية ودماغ منياوية</p>", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# المقدمة
# ─────────────────────────────────────────────
st.header("🎯 مش محتاج تدور على ملف قنوات تليفزيون إل جي تاني!")

st.markdown("<p class='center-text'>هل بتعاني من فوضى ترتيب القنوات على شاشة إل جي (الرسيفر الداخلي)؟</p>", unsafe_allow_html=True)
st.markdown("<p class='center-text'>زهقت من البحث اليدوي عن الترددات الجديدة؟</p>", unsafe_allow_html=True)

st.markdown("")
st.success("🚀 بكل فخر، بنقدم لكم Rambo AI TV!")
st.info("**الموقع الأول من نوعه** \"بأيدٍ مصرية ودماغ منياوية\"، اللي بيحل لك أزمة ترتيب القنوات **بضغطة زر** وبقوة **الذكاء الاصطناعي!**")

st.markdown("---")

# ─────────────────────────────────────────────
# ليه تختار RamboAITV؟ (4 أعمدة)
# ─────────────────────────────────────────────
st.header("🌟 ليه تختار Rambo AI TV؟")

st.markdown("<p class='center-text'>🎨 الموقع مصمم بـ **4 صفحات احترافية** لخدمتك:</p>", unsafe_allow_html=True)

st.markdown("")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("1️⃣ الترتيب الذكي")
    st.markdown("**(بالفئات/Categories)**")
    st.write("ارفع ملف قنواتك اللي سحبته على الفلاشة، والموقع هيقوم أوتوماتيكياً بترتيبه لك حسب الفئات (رياضة، أفلام، أخبار.. إلخ).")
    st.write("✅ تحميل ملف Text للترتيب")
    st.write("✅ ملف القنوات المحدث جاهز للتشغيل")

with col2:
    st.subheader("2️⃣ الترتيب اليدوي")
    st.markdown("**(تحكم كامل)**")
    st.write("ليك تحكم كامل! رتب قنواتك قناة قناة حسب ذوقك، واعتمد ترتيبك الخاص.")
    st.write("✅ تحميل ملف مرتب ومحدث")
    st.write("✅ بكل سهولة وبساطة")

with col3:
    st.subheader("3️⃣ توليد بالذكاء")
    st.markdown("**(ميزة حصرية! 🔥)**")
    st.write("لأول مرة، بس اكتب موديل جهازك، بلد البث، وسنة الصنع، والذكاء الاصطناعي هيقوم بتوليد ملف قنوات متوافق مع شاشتك من الصفر!")

with col4:
    st.subheader("4️⃣ محول ملف القنوات")
    st.markdown("**(نقل الترتيب الذكي ⚡)**")
    st.write("هات أي ملف قنوات عاجبك ترتيبه من النت (قديم، جديد، أي مقاس شاشة)، وارفع معاه ملف شاشتك الأصلي، والموقع هينقل لك نفس الترتيب على ملفك فوراً مع تحديث الترددات وقراءة بيانات الموديل!")

st.markdown("---")

# ─────────────────────────────────────────────
# الميزات الخارقة للذكاء الاصطناعي
# ─────────────────────────────────────────────
st.header("🔥 ميزات خارقة للذكاء الاصطناعي داخل الموقع")

col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.subheader("📡 تحديث الترددات وتوافق الموديلات")
    st.write("وداعاً للقنوات اللي بتظهر 'بدون إشارة' أو الملفات غير المتوافقة.")
    st.write("الموقع بيلفظ الترددات الميتة، ويقرأ بيانات موديل شاشتك لضمان تشغيل الملف بنسبة 100%.")

with col_ai2:
    st.subheader("🆕 اكتشاف القنوات الجديدة")
    st.write("الموقع بيعرفك تلقائياً بالقنوات الحديثة اللي بدأت بثها مؤخراً على القمر الصناعي عشان تكون دائماً في قلب الحدث!")

st.markdown("---")

# ─────────────────────────────────────────────
# أزرار التنقل للصفحات
# ─────────────────────────────────────────────
st.header("🚀 جرب الموقع دلوقتي")

col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

with col_btn1:
    st.link_button("🧠 الترتيب الذكي (بالفئات)", "https://ramboaitv.streamlit.app/page1_catogary_sorter")

with col_btn2:
    st.link_button("✋ الترتيب اليدوي", "https://ramboaitv.streamlit.app/page2_manual_sorter")

with col_btn3:
    st.link_button("🤖 توليد بالذكاء الاصطناعي", "https://ramboaitv.streamlit.app/page3_generate_sorter")

with col_btn4:
    st.link_button("⚡ محول ملف القنوات", "https://ramboaitv.streamlit.app/page4_convert_tv_file")

# ─────────────────────────────────────────────
# الفوتر
# ─────────────────────────────────────────────
st.markdown("---")

st.markdown("<p class='center-text' style='font-size:22px; color:#ff007f; font-weight:bold;'>🛠️ DEVELOPER ENG: RAFIK NATHAN</p>", unsafe_allow_html=True)
st.markdown("<p class='center-text'>📱 MOBILE / الموبايل: +</p>", unsafe_allow_html=True)
st.markdown("<p class='center-text'>✉️ E-MAIL: </p>", unsafe_allow_html=True)

whatsapp_url = "https://api.whatsapp.com/send?phone=&text=Hello%20Developer%20Rafik%20Rambo"
st.link_button("WhatsApp 💬", whatsapp_url)
