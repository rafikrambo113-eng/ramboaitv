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
# CSS السيبراني الفاخر
# ─────────────────────────────────────────────
if st.session_state.theme == 'dark':
    bg_style = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)"
    text_color = "#00f0ff"
    box_bg = "rgba(13, 7, 33, 0.85)"
    box_border = "#00f0ff"
    box_shadow = "rgba(0, 240, 255, 0.35)"
    text_shadow = "0 0 5px rgba(0, 240, 255, 0.4)"
    accent_color = "#ff007f"
    secondary_color = "#00f0ff"
else:
    bg_style = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
    text_color = "#0d0722"
    box_bg = "#ffffff"
    box_border = "#ff007f"
    box_shadow = "rgba(255, 0, 127, 0.15)"
    text_shadow = "none"
    accent_color = "#ff007f"
    secondary_color = "#00f0ff"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Cairo:wght@400;600;700;900&display=swap');
    
    .main {{ background: {bg_style} !important; color: {text_color} !important; font-family: 'Cairo', sans-serif; }}
    
    h1 {{ 
        color: {accent_color} !important; 
        text-shadow: 0 0 10px {accent_color}, 0 0 25px rgba(255,0,127,0.4) !important; 
        text-align: center; 
        font-weight: 900; 
        font-size: 52px !important;
        margin-top: 10px !important;
        margin-bottom: 5px !important;
    }}
    
    h2 {{ 
        color: {secondary_color} !important; 
        text-shadow: {text_shadow};
        font-weight: 700;
        margin-top: 35px !important;
        margin-bottom: 20px !important;
    }}
    
    h3 {{ 
        color: {secondary_color} !important;
        font-weight: 700 !important;
        margin-bottom: 15px !important;
    }}
    
    .hero-subtitle {{
        text-align: center;
        font-size: 24px !important;
        color: {secondary_color} !important;
        font-weight: 700 !important;
        margin-bottom: 5px !important;
    }}
    
    .egyptian-badge {{
        background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
        color: white !important;
        padding: 12px 30px !important;
        border-radius: 35px !important;
        font-weight: 700 !important;
        display: inline-block !important;
        margin: 15px 0 40px 0 !important;
        font-size: 18px !important;
        text-shadow: 0 0 10px rgba(255,0,127,0.5) !important;
    }}
    
    .section-box {{
        background: linear-gradient(135deg, rgba(0,240,255,0.08) 0%, rgba(255,0,127,0.08) 100%) !important;
        border: 2px solid {box_border} !important;
        border-radius: 18px !important;
        padding: 35px !important;
        margin-bottom: 30px !important;
    }}
    
    .intro-text {{
        font-size: 19px !important;
        text-align: center;
        margin-bottom: 20px !important;
        line-height: 1.9 !important;
    }}
    
    .highlight-box {{
        background: rgba(0,240,255,0.12) !important;
        border-left: 6px solid {secondary_color} !important;
        border-radius: 14px !important;
        padding: 25px !important;
        margin: 25px 0 !important;
        text-align: center !important;
    }}
    
    .feature-box {{
        background: {box_bg} !important;
        border: 2px solid {box_border} !important;
        box-shadow: 0px 5px 20px {box_shadow} !important;
        border-radius: 18px !important;
        padding: 28px !important;
        margin-bottom: 20px !important;
        transition: all 0.3s ease !important;
        height: 100% !important;
    }}
    
    .feature-box:hover {{
        transform: translateY(-8px) !important;
        box-shadow: 0px 12px 35px {box_shadow} !important;
    }}
    
    .ai-box {{
        background: linear-gradient(135deg, rgba(0,240,255,0.15) 0%, rgba(255,0,127,0.15) 100%) !important;
        border: 2px solid {box_border} !important;
        border-radius: 16px !important;
        padding: 25px !important;
        height: 100% !important;
    }}
    
    .nav-button {{
        background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
        color: #ffffff !important;
        border: 2px solid #ff007f !important;
        border-radius: 16px !important;
        font-weight: bold !important;
        font-size: 19px !important;
        padding: 15px !important;
        width: 100% !important;
        margin: 10px 0 !important;
        transition: all 0.3s ease !important;
    }}
    
    .nav-button:hover {{
        background: linear-gradient(135deg, #ff6b9f 0%, #aa5575 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 0 20px rgba(255,0,127,0.5) !important;
    }}
    
    ul {{
        margin-left: 20px !important;
    }}
    
    li {{
        margin-bottom: 12px !important;
        font-size: 17px !important;
    }}
    
    .check-list {{
        list-style: none !important;
        margin-left: 0 !important;
    }}
    
    .check-list li {{
        padding-left: 30px !important;
        position: relative !important;
    }}
    
    .check-list li::before {{
        content: "✅" !important;
        position: absolute !important;
        left: 0 !important;
        color: {secondary_color} !important;
    }}
    
    .sub-title {{
        color: {accent_color} !important;
        font-weight: 700 !important;
        font-size: 20px !important;
        margin-bottom: 10px !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# الهيدر الرئيسي
# ─────────────────────────────────────────────
st.markdown('<h1>📺 RamboAITV</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">⚡ أول موقع مصري ذكي لترتيب قنوات LG بالذكاء الاصطناعي</p>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;"><span class="egyptian-badge">🇪🇬 بأيدٍ مصرية ودماغ منياوية</span></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# المقدمة
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-box">
    <h2 style="text-align:center;">🎯 مش محتاج تدور على ملف قنوات تليفزيون LG تاني!</h2>
    
    <p class="intro-text">
        <span style="color:#ff007f; font-weight:700;">هل بتعاني من فوضى ترتيب القنوات على شاشة الـ LG</span> (الرسيفر الداخلي)؟
    </p>
    <p class="intro-text">
        <span style="color:#00f0ff; font-weight:700;">زهقت من البحث اليدوي عن الترددات الجديدة؟</span>
    </p>
    
    <div class="highlight-box">
        <p style="font-size:21px; color:#ff007f; font-weight:700; margin-bottom:15px;">
            🚀 بكل فخر، بنقدم لكم RamboAITV!
        </p>
        <p style="font-size:19px;">
            الموقع الأول من نوعه <span style="color:#00f0ff; font-weight:700;">"بأيدٍ مصرية ودماغ منياوية"</span>، 
            اللي بيحل لك أزمة ترتيب القنوات <span style="color:#ff007f; font-weight:700;">بضغطة زر</span> وبقوة <span style="color:#00f0ff; font-weight:700;">الذكاء الاصطناعي!</span>
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ليه تختار RamboAITV؟
# ─────────────────────────────────────────────
st.markdown('<h2 style="text-align:center;">🌟 ليه تختار RamboAITV؟</h2>', unsafe_allow_html=True)

st.markdown('<p style="text-align:center; font-size:18px; margin-bottom:30px;">🎨 الموقع مصمم بـ <span style="color:#ff007f; font-weight:700; font-size:20px;">3 صفحات احترافية</span> لخدمتك:</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3 style="color:#00f0ff; text-align:center;">1️⃣ الترتيب الذكي</h3>
        <p style="color:#ff007f; text-align:center; font-weight:700; margin-bottom:15px;">(بالفئات/Categories)</p>
        <p>ارفع ملف قنواتك اللي سحبته على الفلاشة، والموقع <span style="color:#00f0ff; font-weight:700;">هيقوم أوتوماتيكياً بترتيبه لك حسب الفئات</span> (رياضة، أفلام، أخبار.. إلخ).</p>
        <ul class="check-list">
            <li>تحميل ملف Text للترتيب</li>
            <li>ملف القنوات المحدث جاهز للتشغيل</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3 style="color:#00f0ff; text-align:center;">2️⃣ الترتيب اليدوي</h3>
        <p>ليك <span style="color:#ff007f; font-weight:700;">تحكم كامل!</span> رتب قنواتك قناة قناة حسب ذوقك، واعتمد ترتيبك الخاص.</p>
        <ul class="check-list">
            <li>تحميل ملف مرتب ومحدث</li>
            <li>بكل سهولة وبساطة</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box" style="border:2px solid #ff6b9f;">
        <h3 style="color:#00f0ff; text-align:center;">3️⃣ توليد بالذكاء الاصطناعي</h3>
        <p style="color:#ff007f; text-align:center; font-weight:700; margin-bottom:10px;">(ميزة حصرية! 🔥)</p>
        <p>لأول مرة، بس <span style="color:#00f0ff; font-weight:700;">اكتب موديل جهازك، بلد البث، وسنة الصنع</span>، والذكاء الاصطناعي هيقوم بتوليد ملف قنوات متوافق مع شاشتك <span style="color:#ff007f; font-weight:700;">من الصفر!</span></p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# الميزات الخارقة للذكاء الاصطناعي
# ─────────────────────────────────────────────
st.markdown('<h2 style="text-align:center; margin-top:50px;">🔥 ميزتان خارقتان للذكاء الاصطناعي داخل الموقع</h2>', unsafe_allow_html=True)

col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.markdown("""
    <div class="ai-box" style="border-left:6px solid #00f0ff;">
        <h3 style="color:#00f0ff; text-align:center;">📡 تحديث الترددات</h3>
        <p style="font-size:18px; text-align:center; margin-top:15px;">
            <span style="color:#ff007f; font-weight:700;">وداعاً للقنوات اللي بتظهر "بدون إشارة"</span>
        </p>
        <p style="text-align:center;">الموقع بيلفظ الترددات الميتة والقديمة ويحدثها أوتوماتيكياً</p>
    </div>
    """, unsafe_allow_html=True)

with col_ai2:
    st.markdown("""
    <div class="ai-box" style="border-left:6px solid #ff007f;">
        <h3 style="color:#ff007f; text-align:center;">🆕 اكتشاف القنوات الجديدة</h3>
        <p style="font-size:18px; text-align:center; margin-top:15px;">
            الموقع <span style="color:#00f0ff; font-weight:700;">بيعرفك تلقائياً</span> بالقنوات الحديثة اللي بدأت بثها مؤخراً
        </p>
        <p style="text-align:center;">عشان تكون <span style="color:#ff007f; font-weight:700;">دائماً في قلب الحدث!</span></p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# أزرار التنقل للصفحات
# ─────────────────────────────────────────────
st.markdown('<h2 style="text-align:center; margin-top:60px;">🚀 جرب الموقع دلوقتي</h2>', unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("🧠 الترتيب الذكي (بالفئات)", key="btn_smart_sort", help="الانتقال لصفحة الترتيب الذكي بالفئات"):
        st.session_state.page = 'page1_catogary_sorter'
        st.rerun()

with col_btn2:
    if st.button("✋ الترتيب اليدوي", key="btn_manual_sort", help="الانتقال لصفحة الترتيب اليدوي"):
        st.session_state.page = 'page2_manual_sorter'
        st.rerun()

with col_btn3:
    if st.button("🤖 توليد بالذكاء الاصطناعي", key="btn_ai_generate", help="الانتقال لصفحة التوليد بالذكاء الاصطناعي"):
        st.session_state.page = 'page3_generate_sorter'
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
padding:40px;
text-align:center;
border-radius:22px;
margin-top:70px;
font-family:'Cairo', Arial;
">
<div style="color:#ff007f;font-size:28px;font-weight:bold;margin-bottom:15px;">
🛠️ DEVELOPER ENG: RAFIK NATHAN
</div>
<div style="margin:12px 0;font-size:18px;">
📱 <b>MOBILE / الموبايل:</b> +201280339779
</div>
<div style="margin:12px 0;font-size:18px;">
✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com
</div>
<a href="{whatsapp_url}" target="_blank"
style="
color:#25d366;
padding:16px 40px;
border-radius:38px;
display:inline-block;
font-weight:bold;
border:2px solid #25d366;
text-decoration:none;
margin-top:25px;
font-size:18px;
background:rgba(37,211,102,0.1);
">
WhatsApp
</a>
</div>
""", unsafe_allow_html=True)
