import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# تهيئة الجلسة
if 'lang' not in st.session_state: st.session_state.lang = 'ar'
if 'theme' not in st.session_state: st.session_state.theme = 'dark'

# --- (تم اختصار UI_TEXT هنا لضمان الكفاءة، هو نفسه كودك الأصلي) ---
# إذا كنت تحتاج النص الأصلي بالكامل، يمكنك إبقاؤه في الأعلى كما كان.
UI_TEXT = {'ar': {'title': "📺 RAMBO - المنسق العالمي لشاشات LG", 'ready_msg': "تمت المعالجة بنجاح!", 'btn_download_tll': "📥 تحميل الملف المعدل TLL", 'btn_download_txt': "📄 تحميل تقرير الترتيب TXT"}}
t = UI_TEXT['ar']

st.set_page_config(page_title="RAMBO", layout="wide")

# دالة تصنيف القنوات
def ai_classify(name):
    name = name.upper()
    if any(x in name for x in ["CTV", "AGHAPY", "MESAT", "SAT-7"]): return "⛪ قنوات مسيحية"
    if any(x in name for x in ["QURAN", "RAHMA", "MAJD", "IQRAA"]): return "🕌 قنوات إسلامية"
    if any(x in name for x in ["DRAMA", "SERIES", "SHAHID"]): return "🎬 مسلسلات ودراما"
    if any(x in name for x in ["CINEMA", "ROTANA", "MBC2", "MOVIE"]): return "🍿 أفلام"
    if any(x in name for x in ["SPACE", "KIDS", "MAJID", "TOYOR"]): return "👶 أطفال"
    if any(x in name for x in ["SPORT", "ONTIME", "BEIN"]): return "⚽ رياضة"
    if any(x in name for x in ["NEWS", "JAZEERA", "ARABIYA"]): return "📰 أخبار"
    return "📺 قنوات عامة"

uploaded_file = st.file_uploader("🚀 اختر ملف القنوات TLL:", type=["TLL"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_text = file_bytes.decode('utf-8', errors='ignore')
    
    # استخراج القنوات (شاشات قديمة)
    items = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)
    data = []
    for item in items:
        name = re.search(r'<vchName>(.*?)</vchName>', item).group(1) if re.search(r'<vchName>(.*?)</vchName>', item) else "Unknown"
        data.append({"name": name, "raw": item})

    # ترتيب الفئات
    categories = ["⛪ قنوات مسيحية", "🕌 قنوات إسلامية", "🎬 مسلسلات ودراما", "🍿 أفلام", "👶 أطفال", "⚽ رياضة", "📰 أخبار", "📺 قنوات عامة"]
    priority = st.multiselect("ترتيب الفئات:", categories, default=categories)
    
    # الترتيب الفعلي
    data.sort(key=lambda x: priority.index(ai_classify(x['name'])) if ai_classify(x['name']) in priority else 99)
    
    # إعادة الترقيم (هذا الجزء كان مفقوداً في محاولاتنا السابقة)
    new_items = []
    txt_report = "تقرير الترتيب:\n"
    for i, item in enumerate(data, start=1):
        raw = item['raw']
        # تحديث رقم القناة prNum
        if "<prNum>" in raw:
            raw = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{i}</prNum>', raw)
        else:
            raw = raw.replace("<ITEM>", f"<ITEM>\n<prNum>{i}</prNum>")
        new_items.append(raw)
        txt_report += f"{i} - {item['name']}\n"
    
    # دمج التغييرات
    full_xml = file_text[:file_text.find("<ITEM>")] + "\n".join(new_items) + file_text[file_text.rfind("</ITEM>")+7:]
    
    st.success("تم ترتيب القنوات بنجاح!")
    
    # أزرار التحميل
    st.download_button("📥 تحميل الملف المعدل TLL", data=full_xml.encode('utf-8'), file_name="GlobalClone00001.TLL")
    st.download_button("📄 تحميل تقرير الترتيب TXT", data=txt_report, file_name="List.txt")
