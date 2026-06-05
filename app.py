import streamlit as st

# ─────────────────────────────────────────────
# تهيئة الجلسة (Session State) بشكل مستقر
# ─────────────────────────────────────────────
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# ─────────────────────────────────────────────
# إعداد الصفحة
# ─────────────────────────────────────────────
st.set_page_config(page_title="RamboAITV — مرتب القنوات الذكي", page_icon="📺", layout="wide")

# ─────────────────────────────────────────────
# CSS السيبراني الفاخر
# ─────────────────────────────────────────────
if st.session_state.theme == 'dark':
    bg_style, text_color, box_bg, box_border = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)", "#00f0ff", "rgba(13, 7, 33, 0.85)", "#00f0ff"
    box_shadow, text_shadow = "rgba(0, 240, 255, 0.35)", "0 0 5px rgba(0, 240, 255, 0.4)"
    accent_color, secondary_color = "#ff007f", "#00f0ff"
else:
    bg_style, text_color, box_bg, box_border = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)", "#0d0722", "#ffffff", "#ff007f"
    box_shadow, text_shadow = "rgba(255, 0, 127, 0.15)", "none"
    accent_color, secondary_color = "#ff007f", "#00f0ff"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Cairo:wght@400;600;700;900&display=swap');
    
    .main {{ background: {bg_style} !important; color: {text_color} !important; font-family: 'Cairo', sans-serif; }}
    
    h1 {{ 
        color: {accent_color} !important; 
        text-shadow: 0 0 10px {accent_color}, 0 0 25px rgba(255,0,127,0.4) !important; 
        text-align: center; 
        font-weight: 900; 
        font-size: 42px !important;
        margin-top: 10px !important;
    }}
    
    h2 {{ 
        color: {secondary_color} !important; 
        text-shadow: {text_shadow};
        font-weight: 700;
        margin-top: 30px !important;
    }}
    
    h3, p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] p {{ 
        color: {text_color} !important; 
        text-shadow: {text_shadow};
        font-size: 17px !important;
        line-height: 1.8 !important;
    }}
    
    .hero-title {{
        text-align: center;
        font-size: 48px !important;
        font-weight: 900 !important;
        color: {accent_color} !important;
        text-shadow: 0 0 15px {accent_color}, 0 0 30px rgba(255,0,127,0.5) !important;
        margin-bottom: 10px !important;
    }}
    
    .hero-subtitle {{
        text-align: center;
        font-size: 22px !important;
        color: {secondary_color} !important;
        font-weight: 600 !important;
        margin-bottom: 40px !important;
    }}
    
    .feature-box {{
        background: {box_bg} !important;
        border: 2px solid {box_border} !important;
        box-shadow: 0px 5px 20px {box_shadow} !important;
        border-radius: 18px !important;
        padding: 25px !important;
        margin-bottom: 20px !important;
        transition: all 0.3s ease !important;
    }}
    
    .feature-box:hover {{
        transform: translateY(-5px) !important;
        box-shadow: 0px 10px 30px {box_shadow} !important;
    }}
    
    .section-box {{
        background: linear-gradient(135deg, rgba(0,240,255,0.08) 0%, rgba(255,0,127,0.08) 100%) !important;
        border: 2px solid {box_border} !important;
        border-radius: 16px !important;
        padding: 30px !important;
        margin-bottom: 25px !important;
    }}
    
    .highlight-text {{
        color: {secondary_color} !important;
        font-weight: 700 !important;
        font-size: 18px !important;
    }}
    
    .egyptian-badge {{
        background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
        color: white !important;
        padding: 10px 25px !important;
        border-radius: 30px !important;
        font-weight: 700 !important;
        display: inline-block !important;
        margin: 15px 0 !important;
    }}
    
    .stButton>button {{ 
        background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important; 
        color: #ffffff !important; 
        border: 2px solid #ff007f !important; 
        border-radius: 14px !important; 
        font-weight: bold !important; 
        width: 100% !important;
        font-size: 18px !important;
        padding: 12px !important;
    }}
    
    .nav-button {{
        background: linear-gradient(135deg, #00f0ff 0%, #0077aa 100%) !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        margin: 10px !important;
    }}
    
    ul {{
        margin-left: 20px !important;
    }}
    
    li {{
        margin-bottom: 10px !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# الهيدر الرئيسي
# ─────────────────────────────────────────────
st.markdown('<h1 class="hero-title">📺 RamboAITV</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">⚡ أول موقع مصري ذكي لترتيب قنوات LG بالذكاء الاصطناعي</p>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center;"><span class="egyptian-badge">🇪🇬 بأيدٍ مصرية ودماغ منياوية</span></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# المقدمة
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-box">
    <h2 style="text-align:center; margin-bottom:20px;">🎯 مش محتاج تدور على ملف قنوات تليفزيون LG تاني!</h2>
    
    <p style="font-size:18px; text-align:center; margin-bottom:15px;">
        <span style="color:#ff007f; font-weight:700;">هل بتعاني من فوضى ترتيب القنوات على شاشة الـ LG</span> (الرسيفر الداخلي)؟<br>
        <span style="color:#00f0ff; font-weight:700;">زهقت من البحث اليدوي عن الترددات الجديدة؟</span>
    </p>
    
    <p style="font-size:19px; text-align:center; margin-top:25px; padding:20px; background:rgba(0,240,255,0.1); border-radius:12px; border-left:5px solid #00f0ff;">
        <span style="color:#ff007f; font-weight:700; font-size:20px;">🚀 بكل فخر، بنقدم لكم RamboAITV!</span><br>
        الموقع الأول من نوعه <span style="color:#00f0ff; font-weight:700;">"بأيدٍ مصرية ودماغ منياوية"</span>، 
        اللي بيحل لك أزمة ترتيب القنوات <span style="color:#ff007f; font-weight:700;">بضغطة زر</span> وبقوة <span style="color:#00f0ff; font-weight:700;">الذكاء الاصطناعي!</span>
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
### ليه تختار RamboAITV؟
# ─────────────────────────────────────────────
st.markdown('<h2 style="text-align:center;">🌟 ليه تختار RamboAITV؟</h2>', unsafe_allow_html=True)

st.markdown("""
<div class="section-box">
    <p style="text-align:center; font-size:18px; font-weight:700; margin-bottom:25px;">
        🎨 الموقع مصمم بـ <span style="color:#ff007f; font-size:20px;">3 صفحات احترافية</span> لخدمتك:
    </p>
""", unsafe_allow_html=True)

# الصفحات الثلاث
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3 style="color:#00f0ff; text-align:center; margin-bottom:15px;">1️⃣ الترتيب الذكي</h3>
        <p style="color:#ff007f; text-align:center; font-weight:700;">(بالفئات/Categories)</p>
        <p style="font-size:16px;">
            ارفع ملف قنواتك اللي سحبته على الفلاشة، والموقع <span style="color:#00f0ff; font-weight:700;">هيقوم أوتوماتيكياً بترتيبه لك حسب الفئات</span> (رياضة، أفلام، أخبار.. إلخ).
        </p>
        <p style="font-size:16px; margin-top:15px;">
            ✅ تحميل ملف Text للترتيب<br>
            ✅ ملف القنوات المحدث جاهز للتشغيل
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3 style="color:#00f0ff; text-align:center; margin-bottom:15px;">2️⃣ الترتيب اليدوي</h3>
        <p style="font-size:16px;">
            <span style="color:#ff007f; font-weight:700;">ليك تحكم كامل!</span> رتب قنواتك قناة قناة حسب ذوقك، واعتمد ترتيبك الخاص.
        </p>
        <p style="font-size:16px; margin-top:15px;">
            ✅ descarga ملف مرتب ومحدث<br>
            ✅ بكل سهولة وبساطة
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box">
        <h3 style="color:#00f0ff; text-align:center; margin-bottom:15px;">3️⃣ توليد بالذكاء الاصطناعي</h3>
        <p style="color:#ff007f; text-align:center; font-weight:700; font-size:15px;">(ميزة حصرية! 🔥)</p>
        <p style="font-size:16px;">
            لأول مرة، بس <span style="color:#00f0ff; font-weight:700;">اكتب موديل جهازك، بلد البث، وسنة الصنع</span>، والذكاء الاصطناعي هيقوم بتوليد ملف قنوات متوافق مع شاشتك <span style="color:#ff007f; font-weight:700;">من الصفر!</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
### الميزات الخارقة للذكاء الاصطناعي
# ─────────────────────────────────────────────
st.markdown('<h2 style="text-align:center;">🔥 ميزتان خارقتان للذكاء الاصطناعي داخل الموقع</h2>', unsafe_allow_html=True)

col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.markdown("""
    <div class="feature-box" style="border-left:5px solid #00f0ff;">
        <h3 style="color:#00f0ff; text-align:center;">📡 تحديث الترددات</h3>
        <p style="font-size:17px; text-align:center; margin-top:15px;">
            <span style="color:#ff007f; font-weight:700;">وداعاً للقنوات اللي بتظهر "بدون إشارة"</span><br>
            الموقع بيلفظ الترددات الميتة والقديمة ويحدثها أوتوماتيكياً
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_ai2:
    st.markdown("""
    <div class="feature-box" style="border-left:5px solid #ff007f;">
        <h3 style="color:#ff007f; text-align:center;">🆕 اكتشاف القنوات الجديدة</h3>
        <p style="font-size:17px; text-align:center; margin-top:15px;">
            الموقع <span style="color:#00f0ff; font-weight:700;">بيعرفك تلقائياً</span> بالقنوات الحديثة اللي بدأت بثها مؤخراً على القمر الصناعي<br>
            عشان تكون <span style="color:#ff007f; font-weight:700;">دائماً في قلب الحدث!</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# أزرار التنقل للصفحات
# ─────────────────────────────────────────────
st.markdown('<h2 style="text-align:center; margin-top:50px;">🚀 جرب الموقع دلوقتي</h2>', unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("🧠 الترتيب الذكي\n(بالفئات)", key="btn_smart_sort", help="الانتقال لصفحة الترتيب الذكي بالفئات"):
        st.session_state['page'] = 'smart_sort'
        st.rerun()

with col_btn2:
    if st.button("✋ الترتيب اليدوي", key="btn_manual_sort", help="الانتقال لصفحة الترتيب اليدوي"):
        st.session_state['page'] = 'manual_sort'
        st.rerun()

with col_btn3:
    if st.button("🤖 توليد بالذكاء الاصطناعي", key="btn_ai_generate", help="الانتقال لصفحة التوليد بالذكاء الاصطناعي"):
        st.session_state['page'] = 'ai_generate'
        st.rerun()

# ─────────────────────────────────────────────
# الفوتر
# ─────────────────────────────────────────────
st.markdown("---")

whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"
st.markdown(f"""
<div style="
background:#0f172a;
border:2px solid #00f0ff;
color:#ffffff;
padding:35px;
text-align:center;
border-radius:20px;
margin-top:65px;
font-family:Arial;
">
<div style="color:#ff007f;font-size:26px;font-weight:bold;">
🛠️ DEVELOPER ENG: RAFIK NATHAN
</div>
<div style="margin-top:10px;">
📱 <b>MOBILE / الموبايل:</b> +201280339779
</div>
<div style="margin-top:10px;">
✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com
</div>
<a href="{whatsapp_url}" target="_blank"
style="
color:#25d366;
padding:14px 35px;
border-radius:35px;
display:inline-block;
font-weight:bold;
border:2px solid #25d366;
text-decoration:none;
margin-top:20px;
">
WhatsApp
</a>
</div>
""", unsafe_allow_html=True)
