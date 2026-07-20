import streamlit as st

st.set_page_config(page_title="Rambo AI TV — مرتب القنوات الذكي", page_icon="📺", layout="wide")

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
# ليه تختار RamboAITV؟ (عمودين بس)
# ─────────────────────────────────────────────
st.header("🌟 ليه تختار Rambo AI TV؟")

st.markdown("<p class='center-text'>🎨 الموقع مصمم بصفحتين احترافيتين لخدمتك:</p>", unsafe_allow_html=True)

st.markdown("")
col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ الترتيب الذكي بالفئات")
    st.markdown("**(ترتيب تلقائي كامل)**")
    st.write("ارفع ملف قنواتك اللي سحبته من شاشتك، والموقع هيقوم أوتوماتيكياً بترتيبه لك حسب الفئات (رياضة، أفلام، أخبار.. إلخ) بالأولوية اللي تحددها.")
    st.write("✅ ترتيب كل القنوات في ثواني")
    st.write("✅ ملف القنوات المحدث جاهز للتحميل والتشغيل على شاشتك على طول")

with col2:
    st.subheader("2️⃣ نقل الترتيب بين ملفين")
    st.markdown("**(نقل الترتيب الذكي ⚡)**")
    st.write("هات أي ملف قنوات عاجبك ترتيبه (قديم أو جاي من أي مقاس شاشة أو موديل)، وارفع معاه ملف شاشتك الحالي، والموقع هينقل لك نفس الترتيب على ملفك فورًا — كل قناة بتاخد رقمها من الملف المرجعي وبيادها.")
    st.write("✅ مطابقة تلقائية للقنوات بالاسم")
    st.write("✅ تقرير فوري بعدد القنوات اللي اتنقل لها الترتيب والقنوات الجديدة")

st.markdown("---")

# ─────────────────────────────────────────────
# أزرار التنقل للصفحات
# ─────────────────────────────────────────────
st.header("🚀 جرب الموقع دلوقتي")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    st.page_link("pages/1_🧠_الترتيب_الذكي.py", label="🧠 الترتيب الذكي بالفئات", icon="🧠")

with col_btn2:
    st.page_link("pages/1_🧠_الترتيب_الذكي.py", label="⚡ نقل الترتيب بين ملفين", icon="⚡")

# ─────────────────────────────────────────────
# الفوتر
# ─────────────────────────────────────────────
st.markdown("---")

st.markdown("<p class='center-text' style='font-size:22px; color:#ff007f; font-weight:bold;'>🛠️ DEVELOPER ENG: RAFIK NATHAN</p>", unsafe_allow_html=True)
st.markdown("<p class='center-text' style='font-size:22px; color:#00f0ff; font-weight:bold;'>للعلم بيتم عمل تحديثات للموقع يوميًا لمواكبة التحديثات التكنولوجية الجديدة</p>", unsafe_allow_html=True)
