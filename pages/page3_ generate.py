import streamlit as st
import datetime

# إعداد الصفحة
st.set_page_config(page_title="RAMBO - توليد ملف القنوات", page_icon="⚙️", layout="centered")

st.title("⚙️ RAMBO - مولد ملفات القنوات")
st.subheader("قم بتعبئة البيانات لتوليد ملف القنوات المناسب")

# نموذج إدخال البيانات
with st.form("generator_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        satellite = st.text_input("🛰️ القمر الصناعي (إجباري)", placeholder="مثال: Nilesat 7W")
        country = st.text_input("🌍 بلد البث (إجباري)", placeholder="مثال: Egypt")
        inch = st.selectbox("📏 البوصة (اختياري)", ["غير محدد", "32", "43", "50", "55", "65"])
        
    with col2:
        model = st.text_input("📺 الموديل (اختياري)", placeholder="مثال: 32LH604U")
        year = st.selectbox("📅 سنة الصنع (إجباري)", ["2023", "2024", "2025", "2026"])
        
    submitted = st.form_submit_button("🚀 توليد الملف الآن")

# منطق المعالجة
if submitted:
    if not satellite or not country or not year:
        st.error("⚠️ يرجى تعبئة جميع الحقول الإجبارية (القمر، البلد، السنة).")
    else:
        # تحديد ما إذا كان الملف جديد أم قديم بناءً على السنة
        is_new_version = int(year) >= 2025
        
        st.divider()
        st.success(f"✅ تم استقبال البيانات بنجاح!")
        
        # عرض ملخص
        st.info(f"""
        **ملخص الطلب:**
        - **القمر:** {satellite}
        - **البلد:** {country}
        - **التصنيف:** {'ملف حديث (Modern)' if is_new_version else 'ملف قديم (Legacy)'}
        """)
        
        # محاكاة توليد الملف
        with st.spinner('جاري توليد الهيكل البرمجي...'):
            # هنا يتم وضع الكود الذي يربط بـ XML الخاص بك
            # إذا كان قديم، نولد نص XML
            # إذا كان جديد، نولد JSON داخل XML
            import time
            time.sleep(2)
            
        st.balloons()
        st.write("---")
        st.download_button(
            label="📥 تحميل ملف القنوات الناتج",
            data="<DATA>...</DATA>", # هنا يتم وضع البيانات الناتجة
            file_name=f"ChannelList_{year}_{'New' if is_new_version else 'Old'}.TLL",
            mime="application/octet-stream"
        )
        
        if is_new_version:
            st.warning("💡 ملاحظة: هذا الملف متوافق مع شاشات LG الحديثة بنظام WebOS.")
        else:
            st.warning("💡 ملاحظة: هذا الملف متوافق مع الموديلات الكلاسيكية.")

# إضافة رابط للعودة للصفحات الأخرى
st.sidebar.markdown("### 🧭 التنقل")
if st.sidebar.button("⬅️ العودة للرئيسية"):
    st.switch_page("main.py") # تأكد من تعديل اسم الملف حسب مشروعك
