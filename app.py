import streamlit as st

# إعداد الصفحة
st.set_page_config(page_title="RamboAITV", layout="wide")

def display_header():
    # كود التنسيق لضمان أن العربي والإنجليزي يظهران بشكل صحيح
    st.markdown("""
    <style>
        .main-container {
            direction: rtl;
            text-align: right;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            border-right: 10px solid #ff4b4b;
        }
        .highlight { color: #008080; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div class="main-container">
            <h1 style="text-align: center;">مش محتاج تدور على ملف قنوات تليفزيون LG تاني! 📺✨</h1>
            <p style="font-size: 18px;">هل بتعاني من فوضى ترتيب القنوات على شاشة الـ LG (الرسيفر الداخلي)؟ زهقت من البحث اليدوي عن الترددات الجديدة؟</p>
            <p style="font-size: 18px;">بكل فخر، بنقدم لكم <b>RamboAITV</b>، الموقع الأول من نوعه "بأيدٍ مصرية ودماغ منياوية"، اللي بيحل لك أزمة ترتيب القنوات بضغطة زر وبقوة الذكاء الاصطناعي! 🚀</p>
            
            <h3>ليه تختار RamboAITV؟</h3>
            <ul>
                <li><b>1️⃣ الترتيب الذكي (بالفئات):</b> ارفع ملفك، والموقع هيرتبهولك حسب الفئات أوتوماتيكياً.</li>
                <li><b>2️⃣ الترتيب اليدوي:</b> تحكم كامل في ترتيب قنواتك قناة قناة.</li>
                <li><b>3️⃣ توليد الملفات بالذكاء الاصطناعي:</b> اكتب بيانات جهازك والموقع يجهزلك الملف من الصفر!</li>
            </ul>

            <p class="highlight">🔥 ميزتان خارقتان بالذكاء الاصطناعي:</p>
            <ul>
                <li><b>تحديث الترددات:</b> وداعاً لمشكلة "بدون إشارة".</li>
                <li><b>اكتشاف القنوات الجديدة:</b> دايماً في قلب الحدث.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# استدعاء الإعلان
display_header()

# هيكل التنقل بين الصفحات الثلاث
page = st.sidebar.radio("اختر الخدمة:", ["الترتيب الذكي (Categories)", "الترتيب اليدوي", "توليد ملف بالذكاء الاصطناعي"])

if page == "الترتيب الذكي (Categories)":
    st.header("الترتيب الذكي")
    # هنا تضع كود صفحة الكاتوجري
elif page == "الترتيب اليدوي":
    st.header("الترتيب اليدوي")
    # هنا تضع كود صفحة اليدوي
else:
    st.header("توليد الملف بالذكاء الاصطناعي")
    # هنا تضع كود صفحة التوليد
