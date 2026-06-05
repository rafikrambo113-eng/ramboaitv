import streamlit as st

# إعداد الصفحة
st.set_page_config(page_title="RamboAITV", layout="wide")

# كود التنسيق (ده اللي بيظبط شكل العربي والإنجليزي)
st.markdown("""
    <style>
        /* إجبار الصفحة كلها على اتجاه اليمين */
        html, body, [data-testid="stAppViewContainer"] {
            direction: rtl;
            text-align: right;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        /* تنسيق الصندوق عشان ميبقاش "قرف" وشكله نضيف */
        .rambo-box {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 20px;
            border: 2px solid #e0e0e0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1, h2, h3 { color: #1e3a8a; }
        .highlight { color: #d97706; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# محتوى الصفحة
with st.container():
    st.markdown("""
    <div class="rambo-box">
        <h1 style="text-align: center;">مش محتاج تدور على ملف قنوات تليفزيون LG تاني! 📺✨</h1>
        <p style="font-size: 18px;">هل بتعاني من فوضى ترتيب القنوات على شاشة الـ LG (الرسيفر الداخلي)؟ زهقت من البحث اليدوي عن الترددات الجديدة؟</p>
        <p style="font-size: 18px;">بكل فخر، بنقدم لكم <b>RamboAITV</b>، الموقع الأول من نوعه "بأيدٍ مصرية ودماغ منياوية"، اللي بيحل لك أزمة ترتيب القنوات بضغطة زر وبقوة الذكاء الاصطناعي! 🚀</p>
        
        <h3>ليه تختار RamboAITV؟</h3>
        <ul style="margin-right: 20px;">
            <li><b>1️⃣ الترتيب الذكي (بالفئات):</b> ارفع ملفك، والموقع هيرتبهولك حسب الفئات أوتوماتيكياً.</li>
            <li><b>2️⃣ الترتيب اليدوي:</b> تحكم كامل في ترتيب قنواتك قناة قناة.</li>
            <li><b>3️⃣ توليد الملفات بالذكاء الاصطناعي:</b> اكتب بيانات جهازك والموقع يجهزلك الملف من الصفر!</li>
        </ul>

        <p class="highlight" style="font-size: 20px;">🔥 ميزتان خارقتان للذكاء الاصطناعي:</p>
        <ul style="margin-right: 20px;">
            <li><b>تحديث الترددات:</b> وداعاً لمشكلة "بدون إشارة".</li>
            <li><b>اكتشاف القنوات الجديدة:</b> دايماً في قلب الحدث.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
