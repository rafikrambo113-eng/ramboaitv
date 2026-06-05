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
# CSS الأساسي
# ─────────────────────────────────────────────
if st.session_state.theme == 'dark':
    text_color = "#00f0ff"
    accent_color = "#ff007f"
    secondary_color = "#00f0ff"
    bg_color = "#0d0722"
else:
    text_color = "#0d0722"
    accent_color = "#ff007f"
    secondary_color = "#00f0ff"
    bg_color = "#ffffff"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
.main {{ font-family: 'Cairo', sans-serif; background: {bg_color}; }}
h1 {{ color: {accent_color} !important; text-align: center; font-weight: 900; font-size: 52px !important; }}
h2 {{ color: {secondary_color} !important; text-align: center; font-weight: 700; }}
h3 {{ color: {secondary_color} !important; font-weight: 700; }}
.stMarkdown {{ color: {text_color}; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# الهيدر الرئيسي
# ─────────────────────────────────────────────
st.markdown("<h1>📺 RamboAITV</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:24px; color:#00f0ff; font-weight:700;'>⚡ أول موقع مصري ذكي لترتيب قنوات LG بالذكاء الاصطناعي</p>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'><span style='background:linear-gradient(135deg, #ff007f 0%, #aa0055 100%); color:white; padding:12px 30px; border-radius:35px; font-weight:700; font-size:18px; display:inline-block; margin:15px 0 40px 0;'>🇪🇬 بأيد مصرية ودماغ منياوية</span></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# المقدمة - HTML مبسط
# ─────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg, rgba(0,240,255,0.08) 0%, rgba(255,0,127,0.08) 100%); border:2px solid #00f0ff; border-radius:18px; padding:35px; margin-bottom:30px;'>
    <h2>🎯 مش محتاج تدور على ملف قنوات تليفزيون LG تاني!</h2>
    
    <p style='font-size:19px; text-align:center; margin-bottom:15px;'>
        <span style='color:#ff007f; font-weight:700;'>هل بتعاني من فوضى ترتيب القنوات على شاشة الـ LG</span> (الرسيفر الداخلي)؟
    </p>
    <p style='font-size:19px; text-align:center; margin-bottom:25px;'>
        <span style='color:#00f0ff; font-weight:700;'>زهقت من البحث اليدوي عن الترددات الجديدة؟</span>
    </p>
    
    <div style='background:rgba(0,240,255,0.12); border-left:6px solid #00f0ff; border-radius:14px; padding:25px; margin:25px 0; text-align:center;'>
        <p style='font-size:21px; color:#ff007f; font-weight:700; margin-bottom:15px;'>
            🚀 بكل فخر، بنقدم لكم RamboAITV!
        </p>
        <p style='font-size:19px;'>
            الموقع الأول من نوعه <span style='color:#00f0ff; font-weight:700;'>"بأيد مصرية ودماغ منياوية"</span>، 
            اللي بيحل لك أزمة ترتيب القنوات <span style='color:#ff007f; font-weight:700;'>بضغطة زر</span> وبقوة <span style='color:#00f0ff; font-weight:700;'>الذكاء الاصطناعي!</span>
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ليه تختار RamboAITV؟
# ─────────────────────────────────────────────
st.markdown("<h2>🌟 ليه تختار RamboAITV؟</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px; margin-bottom:30px;'>🎨 الموقع مصمم بـ <span style='color:#ff007f; font-weight:700; font-size:20px;'>3 صفحات احترافية</span> لخدمتك:</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background:rgba(13,7,33,0.85); border:2px solid #00f0ff; border-radius:18px; padding:28px; height:100%;'>
        <h3 style='color:#00f0ff; text-align:center;'>1️⃣ الترتيب الذكي</h3>
        <p style='color:#ff007f; text-align:center; font-weight:700; margin-bottom:15px;'>(بالفئات/Categories)</p>
        <p>ارفع ملف قنواتك اللي سحبته على الفلاشة، والموقع <span style='color:#00f0ff; font-weight:700;'>هيقوم أوتوماتيكياً بترتيبه لك حسب الفئات</span> (رياضة، أفلام، أخبار.. إلخ).</p>
        <p style='color:#00f0ff;'>✅ تحميل ملف Text للترتيب</p>
        <p style='color:#00f0ff;'>✅ ملف القنوات المحدث جاهز للتشغيل</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background:rgba(13,7,33,0.85); border:2px solid #00f0ff; border-radius:18px; padding:28px; height:100%;'>
        <h3 style='color:#00f0ff; text-align:center;'>2️⃣ الترتيب اليدوي</h3>
        <p>ليك <span style='color:#ff007f; font-weight:700;'>تحكم كامل!</span> رتب قنواتك قناة قناة حسب ذوقك، واعتمد ترتيبك الخاص.</p>
        <p style='color:#00f0ff;'>✅ تحميل ملف مرتب ومحدث</p>
        <p style='color:#00f0ff;'>✅ بكل سهولة وبساطة</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background:rgba(13,7,33,0.85); border:2px solid #ff6b9f; border-radius:18px; padding:28px; height:100%;'>
        <h3 style='color:#00f0ff; text-align:center;'>3️⃣ توليد بالذكاء الاصطناعي</h3>
        <p style='color:#ff007f; text-align:center; font-weight:700; margin-bottom:10px;'>(ميزة حصرية! 🔥)</p>
        <p>لأول مرة، بس <span style='color:#00f0ff; font-weight:700;'>اكتب موديل جهازك، بلد البث، وسنة الصنع</span>، والذكاء الاصطناعي هيقوم بتوليد ملف قنوات متوافق مع شاشتك <span style='color:#ff007f; font-weight:700;'>من الصفر!</span></p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# الميزات الخارقة
# ─────────────────────────────────────────────
st.markdown("<h2 style='margin-top:50px;'>🔥 ميزتان خارقتان للذكاء الاصطناعي داخل الموقع</h2>", unsafe_allow_html=True)

col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.markdown("""
    <div style='background:linear-gradient(135deg, rgba(0,240,255,0.15) 0%, rgba(255,0,127,0.15) 100%); border:2px solid #00f0ff; border-left:6px solid #00f0ff; border-radius:16px; padding:25px;'>
        <h3 style='color:#00f0ff; text-align:center;'>📡 تحديث الترددات</h3>
        <p style='font-size:18px; text-align:center; margin-top:15px;'>
            <span style='color:#ff007f; font-weight:700;'>وداعاً للقنوات اللي بتظهر "بدون إشارة"</span>
        </p>
        <p style='text-align:center;'>الموقع بيلفظ الترددات الميتة والقديمة ويحدثها أوتوماتيكياً</p>
    </div>
    """, unsafe_allow_html=True)

with col_ai2:
    st.markdown("""
    <div style='background:linear-gradient(135deg, rgba(0,240,255,0.15) 0%, rgba(255,0,127,0.15) 100%); border:2px solid #ff007f; border-left:6px solid #ff007f; border-radius:16px; padding:25px;'>
        <h3 style='color:#ff007f; text-align:center;'>🆕 اكتشاف القنوات الجديدة</h3>
        <p style='font-size:18px; text-align:center; margin-top:15px;'>
            الموقع <span style='color:#00f0ff; font-weight:700;'>بيعرفك تلقائياً</span> بالقنوات الحديثة اللي بدأت بثها مؤخراً
        </p>
        <p style='text-align:center;'>عشان تكون <span style='color:#ff007f; font-weight:700;'>دائماً في قلب الحدث!</span></p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# أزرار التنقل
# ─────────────────────────────────────────────
st.markdown("<h2 style='margin-top:60px;'>🚀 جرب الموقع دلوقتي</h2>", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("🧠 الترتيب الذكي (بالفئات)", key="btn_smart_sort"):
        st.session_state.page = 'page1_catogary_sorter'
        st.rerun()

with col_btn2:
    if st.button("✋ الترتيب اليدوي", key="btn_manual_sort"):
        st.session_state.page = 'page2_manual_sorter'
        st.rerun()

with col_btn3:
    if st.button("🤖 توليد بالذكاء الاصطناعي", key="btn_ai_generate"):
        st.session_state.page = 'page3_generate_sorter'
        st.rerun()

# ─────────────────────────────────────────────
# الفوتر
# ─────────────────────────────────────────────
st.markdown("---")

whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"
st.markdown(f"""
<div style='background:#0f172a; border:2px solid #00f0ff; color:#ffffff; padding:40px; text-align:center; border-radius:22px; margin-top:70px; font-family:Cairo, Arial;'>
    <div style='color:#ff007f; font-size:28px; font-weight:bold; margin-bottom:15px;'>🛠️ DEVELOPER ENG: RAFIK NATHAN</div>
    <div style='margin:12px 0; font-size:18px;'>📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
    <div style='margin:12px 0; font-size:18px;'>✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com</div>
    <a href='{whatsapp_url}' target='_blank' style='color:#25d366; padding:16px 40px; border-radius:38px; display:inline-block; font-weight:bold; border:2px solid #25d366; text-decoration:none; margin-top:25px; font-size:18px; background:rgba(37,211,102,0.1);'>WhatsApp</a>
</div>
""", unsafe_allow_html=True)
