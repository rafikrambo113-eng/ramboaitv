import streamlit as st
import json

# تهيئة اللغة
if 'lang' not in st.session_state: st.session_state.lang = 'ar'

# نصوص الواجهة
UI_TEXT = {
    'ar': {'title': "مولد القنوات", 'btn': "توليد الملف", 'config_title': "إعدادات الترتيب"},
    'en': {'title': "Channel Generator", 'btn': "Generate File", 'config_title': "Sorting Settings"}
}

# تعريف t فوراً بعد القاموس
t = UI_TEXT[st.session_state.lang]

st.title(t['title'])

# إضافة مفتاح ثابت key لتجنب خطأ التكرار
if st.button("🌐 English/Ar", key="lang_toggle"):
    st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
    st.rerun()

st.write(f"### {t['config_title']}")

# زر التوليد مع مفتاح ثابت
if st.button(t['btn'], key="gen_btn_final"):
    # هنا تضع منطق بناء ملف الـ JSON أو الـ XML
    data = {"status": "success", "message": "File Generated"}
    st.json(data)
    st.success("✅ تم التوليد!")
