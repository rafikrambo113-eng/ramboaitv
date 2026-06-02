import streamlit as st
import json
import xml.etree.ElementTree as ET

# ── التنسيق الجمالي (متطابق مع صفحة 1) ──
st.markdown("""
    <style>
    .generator-card { background: rgba(13, 7, 33, 0.85); border: 2px solid #00f0ff; border-radius: 14px; padding: 25px; margin-bottom: 25px; box-shadow: 0px 5px 15px rgba(0, 240, 255, 0.2); }
    h1 { color: #ff007f !important; text-align: center; }
    .stButton>button { background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important; color: white !important; width: 100%; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ── قاعدة البيانات (موسعة) ──
NILESAT_GEN_DB = {
    "⛪ قنوات مسيحية": ["CTV", "AGHAPY", "MESAT", "SAT-7"],
    "🕌 قنوات إسلامية": ["QURAN", "IQRAA", "MAJD", "RAHMA"],
    "🎬 مسلسلات ودراما": ["CBC DRAMA", "ON DRAMA", "MBC DRAMA"],
    "🍿 أفلام": ["MBC 2", "MBC MAX", "ROTANA CINEMA"],
    "👶 أطفال": ["SPACE TOON", "MAJID", "CN ARABIC"],
    "⚽ رياضة": ["ON TIME 1", "ON TIME 2", "AL KASS"],
    "📰 أخبار": ["AL JAZEERA", "AL ARABIYA", "EXTRA NEWS"]
}

st.title("⚙️ RAMBO - مولد ملفات القنوات")
st.markdown("### ⚡ بناء ملفات قنوات LG من الصفر")

# ── الإدخالات (توزيع متطابق مع صفحة 1) ──
st.markdown('<div class="generator-card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    sat = st.selectbox("🛰️ القمر الصناعي (إجباري):", ["Nilesat 7W"])
    country = st.selectbox("🌍 بلد البث (إجباري):", ["مصر", "السعودية", "الإمارات"])
with col2:
    model = st.text_input("📺 موديل الشاشة (اختياري):")
    year = st.selectbox("📅 سنة الصنع (لتحديد النظام):", ["2019 وما بعد (نظام حديث)", "2018 وما قبل (نظام قديم)"])

# ── المنطق الذكي ──
system_type = "حديث" if "حديث" in year else "قديم"
st.info(f"💡 النظام المكتشف للملف المولد: **{system_type}**")

# ── عرض الكاتوجري وعدد القنوات ──
st.write("---")
st.write("### 📊 تفاصيل المحتوى المولد:")
for cat, channels in NILESAT_GEN_DB.items():
    with st.expander(f"{cat} — (عدد: {len(channels)} قنوات)"):
        st.write(f"القنوات: {', '.join(channels)}")

# ── خيارات التوليد ──
update_freq = st.checkbox("⚛️ تحديث الترددات تلقائياً", value=True)
add_new_ch = st.checkbox("✨ زرع القنوات الجديدة", value=True)

# ── ترتيب الكاتوجري ──
user_priority = st.multiselect("🎛️ الترتيب عن طريق الكاتوجري فقط:", list(NILESAT_GEN_DB.keys()), default=list(NILESAT_GEN_DB.keys()))
st.markdown('</div>', unsafe_allow_html=True)

# ── زر التوليد ──
if st.button("🚀 توليد الملف النهائي"):
    st.success(f"✅ تم بنجاح بناء هيكلية الملف بنظام الـ {system_type}")
    
    # محاكاة التوليد
    if system_type == "حديث":
        file_content = "JSON_DATA_STRUCTURE"
    else:
        file_content = "XML_ITEM_STRUCTURE"
        
    # أزرار التحميل
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button("📥 تحميل TLL", file_content, "GlobalClone00001.TLL")
    with col_btn2:
        st.download_button("📄 تحميل التقرير", "Report Data", "Channels_List.txt")

    st.warning("💡 بعد تنزيل الملف: ادخل مدير القنوات -> تعديل كل القنوات -> استعادة (Restore).")
