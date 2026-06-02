import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# ── تهيئة الجلسة ──
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

UI_TEXT = {
    'ar': {
        'title': "⚙️ RAMBO - مولد ملفات القنوات من الصفر",
        'subtitle': "⚡ تخليق وبناء ملفات قنوات LG (حديثة وقديمة) كاملة ومرتبة بدون ملف سابق",
        'system_type_label': "📺 اختر نظام وهيكل الملف المطلوب توليده:",
        'sys_modern': "الموديلات الحديثة (WebOS - نظام JSON المدمج)",
        'sys_legacy': "الموديلات القديمة (نظام كتل ITEM الكلاسيكي)",
        'sat_label': "🛰️ اختر القمر الصناعي الأساسي للتشغيل:",
        'country_label': "🌍 اختر بلد البث الافتراضي (Region):",
        'inch_label': "📐 حجم الشاشة بالبوصة (اختياري - اتركها فارغة إذا لم ترد تحديدها):",
        'inch_placeholder': "مثال: 55",
        'config_title': "🎛️ مصفوفة ترتيب الفئات المخصصة لملفك المولد:",
        'multiselect_label': "اضغط هنا لبناء تسلسل خطة العرض التفاعلي للفئات:",
        'preview_title': "📊 مجسم المعاينة الحية للملف الذي سيتم توليده:",
        'channels_count': "قناة",
        'ready_msg': "🌌 تم توليد مصفوفة القنوات وهيكلتها بنجاح! الملفات جاهزة للتحميل:",
        'btn_download_tll': "📥 تحميل ملف الشاشة المولد (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 تحميل تقرير القنوات المولد (Channels_List.txt)",
        'txt_header': "📄 تقرير ملف القنوات المولد بالكامل عبر منظومة RAMBO",
        'txt_order': "🛠️ تسلسل ترتيب الفئات المستخدم في التوليد: ",
        'lg_trick_title': "💡 ملحوظة فنية هامة جداً بعد تنزيل الملف المولد على شاشة LG:",
        'lg_trick_text': "بما أن الملف مولد من الصفر، لضمان استقرار قراءة التلفزيون للترتيب الجديد وتفعيله فوراً، قم بالآتي بعد تنزيل الملف من الفلاشة:\n1. من إعدادات التلفزيون اختار **القنوات (Channels)**.\n2. بعد ذلك اختار **مدير القنوات (Channel Manager)**.\n3. اختار **التعديل على كل القنوات (Edit All Channels)**.\n4. قم **بتحديد كل القنوات** واختار **استعادة (Restore)**."
    },
    'en': {
        'title': "⚙️ RAMBO - AI Channel File Generator",
        'subtitle': "⚡ Synthesize & Build Complete LG Channel Files (Modern/Legacy) From Scratch",
        'system_type_label': "📺 Select Target TV Architecture Structure:",
        'sys_modern': "Modern Models (WebOS - Embedded JSON Engine)",
        'sys_legacy': "Legacy Models (Classic ITEM Block Engine)",
        'sat_label': "🛰️ Select Primary Satellite:",
        'country_label': "🌍 Select Broadcast Region/Country:",
        'inch_label': "📐 Screen Size in Inches (Optional - Leave empty if unsure):",
        'inch_placeholder': "e.g., 55",
        'config_title': "🎛️ Generated Category Priority Control Matrix:",
        'multiselect_label': "Select categories one by one to configure your layout priority:",
        'preview_title': "📊 Live 3D Preview Dashboard of the Generated File:",
        'channels_count': "Channels",
        'ready_msg': "🌌 Quantum Channel Synthesis Successful! Assets ready for deployment:",
        'btn_download_tll': "📥 Download Generated Configuration (GlobalClone00001.TLL)",
        'btn_download_txt': "📄 Download Generated Diagnostics (Channels_List.txt)",
        'txt_header': "📄 Generated LG TV Channel Sorting & Diagnostics Report",
        'txt_order': "🛠️ Applied Category Priority: ",
        'lg_trick_title': "💡 Critical Expert Technical Tip After Uploading to LG TV:",
        'lg_trick_text': "Since this file is synthesized from scratch, to force the TV cache to clear and accept the new structure flawlessly:\n1. Open TV **Settings** -> Go to **Channels**.\n2. Select **Channel Manager**.\n3. Choose **Edit All Channels**.\n4. **Select All Channels** and click **Restore**."
    }
}

t = UI_TEXT[st.session_state.lang]

st.set_page_config(page_title="RAMBO - LG Channel Generator", page_icon="⚙️", layout="wide")

# ── أزرار تغيير اللغة والمظهر ──
col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("🌐 English" if st.session_state.lang == 'ar' else "🌐 العربية"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
        st.rerun()
with col_theme:
    if st.button("☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

if st.session_state.theme == 'dark':
    bg_style = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)"
    text_color = "#00f0ff"
    box_bg = "rgba(13, 7, 33, 0.85)"
    box_border = "#00f0ff"
    box_shadow = "rgba(0, 240, 255, 0.35)"
    text_shadow_glow = "0 0 5px rgba(0, 240, 255, 0.4)"
    footer_bg = "#080314"
    footer_text = "#ffffff"
else:
    bg_style = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
    text_color = "#0d0722"
    box_bg = "#ffffff"
    box_border = "#ff007f"
    box_shadow = "rgba(255, 0, 127, 0.15)"
    text_shadow_glow = "none"
    footer_bg = "#110926"
    footer_text = "#ffffff"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
    .main {{ background: {bg_style} !important; color: {text_color} !important; font-family: { "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif" }; }}
    h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255, 0, 127, 0.4) !important; text-align: center; font-weight: 900; margin-top: 5px; }}
    h3, p, label, .stMarkdown, .stInfo, div[data-testid="stMarkdownContainer"] p {{ color: {text_color} !important; text-shadow: {text_shadow_glow}; }}
    .stTextInput>div>div>input {{ background-color: {box_bg} !important; color: {text_color} !important; border: 2px solid {box_border} !important; border-radius: 10px !important; }}
    .stCheckbox, .stMultiSelect, div[data-testid="stExpander"], .lg-trick-box, .generator-card {{ background: {box_bg} !important; border: 2px solid {box_border} !important; box-shadow: 0px 5px 15px {box_shadow} !important; border-radius: 14px !important; padding: 18px !important; margin-bottom: 20px !important; }}
    .lg-trick-box {{ border-color: #ff007f !important; box-shadow: 0px 5px 15px rgba(255, 0, 127, 0.25) !important; margin-top: 25px !important; }}
    .stButton>button {{ background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important; color: #ffffff !important; border: 2px solid #ff007f !important; border-radius: 12px !important; font-weight: bold; }}
    .futuristic-cyber-footer {{ background: {footer_bg}; border: 2px solid #00f0ff; color: {footer_text} !important; padding: 35px; text-align: center; border-radius: 20px; margin-top: 65px; font-family: 'Orbitron', sans-serif; }}
    .footer-dev {{ color: #ff007f; font-size: 26px; font-weight: bold; }}
    .cyber-whatsapp-btn {{ color: #25d366 !important; padding: 14px 35px; border-radius: 35px; display: inline-block; font-weight: bold; border: 2px solid #25d366; text-decoration: none; margin-top: 20px; }}
    </style>
""", unsafe_allow_html=True)

st.title(t['title'])
st.markdown(f"<h3>{t['subtitle']}</h3>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 🛰️ DATABASE — نايل سات الثابت لغرض التوليد
# ══════════════════════════════════════════════
NILESAT_GEN_DB = {
    "AL HAYAT":         {"frequency": 12207, "polarization": "Vertical"},
    "AL HAYAT 2":       {"frequency": 12207, "polarization": "Vertical"},
    "SAT-7 KIDS":       {"frequency": 11353, "polarization": "Vertical"},
    "SAT-7 ARABIC":     {"frequency": 11353, "polarization": "Vertical"},
    "CTV":              {"frequency": 12022, "polarization": "Vertical"},
    "AGHAPY TV":        {"frequency": 11179, "polarization": "Horizontal"},
    "MESAT":            {"frequency": 11096, "polarization": "Horizontal"},
    "IQRAA":            {"frequency": 11938, "polarization": "Vertical"},
    "MAJD":             {"frequency": 11862, "polarization": "Vertical"},
    "RAHMA":            {"frequency": 11938, "polarization": "Vertical"},
    "QURAN KAREEM":     {"frequency": 11727, "polarization": "Vertical"},
    "AL JAZEERA HD":    {"frequency": 10853, "polarization": "Vertical"},
    "AL ARABIYA":       {"frequency": 11938, "polarization": "Vertical"},
    "AL HADATH":        {"frequency": 11938, "polarization": "Vertical"},
    "CBC":              {"frequency": 12092, "polarization": "Vertical"},
    "EXTRA NEWS":       {"frequency": 12092, "polarization": "Vertical"},
    "ON E":             {"frequency": 12092, "polarization": "Vertical"},
    "MBC 2":            {"frequency": 11938, "polarization": "Vertical"},
    "MBC 4":            {"frequency": 11938, "polarization": "Vertical"},
    "ROTANA CINEMA":    {"frequency": 11938, "polarization": "Vertical"},
    "ON TIME SPORTS 1": {"frequency": 11861, "polarization": "Vertical"},
    "ON TIME SPORTS 2": {"frequency": 11861, "polarization": "Vertical"},
    "SPACE TOON":       {"frequency": 11727, "polarization": "Vertical"},
    "MAJID":            {"frequency": 11862, "polarization": "Vertical"},
    "TOYOR ALJANNAH":   {"frequency": 11179, "polarization": "Horizontal"}
}

ALL_AVAILABLE_CATEGORIES = [
    "⛪ Christian Channels" if st.session_state.lang == 'en' else "⛪ قنوات مسيحية",
    "🕌 Islamic Channels"   if st.session_state.lang == 'en' else "🕌 قنوات إسلامية",
    "🎬 Drama & Series"     if st.session_state.lang == 'en' else "🎬 مسلسلات ودراما",
    "🍿 Movies (Ar/En)"     if st.session_state.lang == 'en' else "🍿 أفلام عربية وأجنبية",
    "👶 Kids & Cartoon"     if st.session_state.lang == 'en' else "👶 أطفال وكرتون",
    "⚽ Sports"             if st.session_state.lang == 'en' else "⚽ رياضة",
    "📰 News & Politics"    if st.session_state.lang == 'en' else "📰 أخبار وسياسة",
    "📺 General Channels"   if st.session_state.lang == 'en' else "📺 قنوات عامة ومنوعات"
]

def ai_classify(channel_name):
    name = channel_name.upper().strip()
    CHRISTIAN_KW = ["CTV", "AGHAPY", "MESAT", "KARMA", "ALKARMA", "NOURSAT", "SAT-7", "SAT7", "AL HAYAT", "HAYAT TV", "MIRACLE", "COPTIC", "CHURCH"]
    if any(w in name for w in CHRISTIAN_KW): return ALL_AVAILABLE_CATEGORIES[0]
    ISLAMIC_KW = ["QURAN", "RAHMA", "MAJD", "MAKKA", "IQRAA", "IQRA", "HUDA", "WESAL", "ISLAM", "SUNNAH"]
    if any(w in name for w in ISLAMIC_KW): return ALL_AVAILABLE_CATEGORIES[1]
    DRAMA_KW = ["MOSALSALAT", "DRAMA", "SERIES", "KHOLASA", "MASRAWI", "SHAHID"]
    if any(w in name for w in DRAMA_KW): return ALL_AVAILABLE_CATEGORIES[2]
    MOVIE_KW = ["CINEMA", "ROTANA", "AFLAM", "MIX", "FOX", "MBC2", "MBC 2", "MBC4", "MBC 4", "MBC MAX", "ACTION", "RAMBO", "MOVIE", "FILM", "COMEDY"]
    if any(w in name for w in MOVIE_KW): return ALL_AVAILABLE_CATEGORIES[3]
    KIDS_KW = ["SPACE TOON", "SPACETOON", "CN", "CARTOON", "MAJID", "KIDS", "TOM", "TOYOR", "BABY", "JUNIOR"]
    if any(w in name for w in KIDS_KW): return ALL_AVAILABLE_CATEGORIES[4]
    SPORT_KW = ["SPORT", "SPORTS", "ONTIME", "ON TIME", "KASS", "AD_SPORTS", "AD SPORTS", "SSC", "BEIN", "MATCH"]
    if any(w in name for w in SPORT_KW): return ALL_AVAILABLE_CATEGORIES[5]
    NEWS_KW = ["NEWS", "JAZEERA", "ARABIYA", "HADATH", "CAIRO", "SKY NEWS", "BBC", "CNN", "EXTRA NEWS", "CBC", "ON E", "SADA", "BALADI", "MASR"]
    if any(w in name for w in NEWS_KW): return ALL_AVAILABLE_CATEGORIES[6]
    return ALL_AVAILABLE_CATEGORIES[7]

# ── بطاقة إعدادات التوليد المطلوبة ──
st.markdown('<div class="generator-card">', unsafe_allow_html=True)
col_cfg1, col_cfg2 = st.columns(2)

with col_cfg1:
    system_type = st.radio(t['system_type_label'], options=[t['sys_modern'], t['sys_legacy']])
    satellite = st.selectbox(t['sat_label'], options=["Nilesat 7W (نايل سات)"])

with col_cfg2:
    country = st.selectbox(t['country_label'], options=["Egypt (مصر)", "Saudi Arabia (السعودية)", "UAE (الإمارات)", "Other (آخر)"])
    inch_size = st.text_input(t['inch_label'], placeholder=t['inch_placeholder']).strip()

st.markdown('</div>', unsafe_allow_html=True)

# تحضير الاسم الافتراضي للموديل داخل الملف بناء على المدخلات
chosen_inch = f"{inch_size}LG" if inch_size else "55LG"
generated_model_name = f"{chosen_inch}_RAMBO_GEN"

# بناء مصفوفة القنوات الخام المستهدفة للتوليد
channels_to_generate = []
for name, info in NILESAT_GEN_DB.items():
    channels_to_generate.append({
        "name": name,
        "freq": str(info["frequency"]),
        "polarization": info["polarization"]
    })

# ── مصفوفة الترتيب المخصصة ──
st.write("---")
st.write(f"### {t['config_title']}")
user_priority = st.multiselect(t['multiselect_label'], options=ALL_AVAILABLE_CATEGORIES, default=[])
final_priority = list(user_priority)
for cat in ALL_AVAILABLE_CATEGORIES:
    if cat not in final_priority: final_priority.append(cat)

# فرز القنوات بناءً على الفئات المختارة
channels_sorted = sorted(channels_to_generate, key=lambda x: final_priority.index(ai_classify(x["name"])))

# ── مجسم المعاينة الحية ──
categorized = {}
for ch in channels_sorted:
    cat = ai_classify(ch["name"])
    if cat not in categorized: categorized[cat] = []
    categorized[cat].append(ch["name"])

st.write("---")
st.write(f"### {t['preview_title']}")
col_p1, col_p2 = st.columns(2)
for i, cat_name in enumerate(final_priority):
    if cat_name in categorized:
        ch_list = categorized[cat_name]
        target_col = col_p1 if i % 2 == 0 else col_p2
        with target_col:
            is_user_chosen = "⭐ " if cat_name in user_priority else ""
            with st.expander(f"{is_user_chosen}{cat_name} — ({len(ch_list)} {t['channels_count']})"):
                st.write(", ".join(ch_list))

# ── تخليق الملف الفعلي النهائي ──
text_report = f"{t['txt_header']} ({generated_model_name})\n" + "="*50 + "\n"
text_report += f"{t['txt_order']} " + " -> ".join(final_priority) + "\n" + "="*50 + "\n\n"

if system_type == t['sys_modern']:
    # 💥 تخليق هيكل ملف حديث (WebOS - JSON Embedded) من الصفر 💥
    channel_list_json = []
    for index, ch in enumerate(channels_sorted, start=1):
        ch_node = {
            "channelName": ch["name"],
            "majorNumber": index,
            "minorNumber": 0,
            "frequency": int(ch["freq"]),
            "polarization": ch["polarization"],
            "invisible": 0,
            "skipped": 0,
            "locked": 0,
            "satelliteName": "Nilesat",
            "serviceType": 1
        }
        channel_list_json.append(ch_node)
        text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']} MHz\n"

    broadcast_payload = {
        "channelList": channel_list_json,
        "satelliteList": [{"satelliteName": "Nilesat", "satellitePosition": 70}]
    }
    json_string_payload = json.dumps(broadcast_payload, ensure_ascii=False, separators=(',', ':'))

    # بناء قالب الـ XML الأساسي الحاضن للـ JSON لشاشات LG
    root = ET.Element("TLLDATA")
    model_node = ET.SubElement(root, "ModelName")
    model_node.text = generated_model_name
    
    legacy_tag = ET.SubElement(root, "legacybroadcast")
    legacy_tag.text = json_string_payload

    final_xml_bytes = ET.tostring(root, encoding="utf-8")

else:
    # 💥 تخليق هيكل ملف قديم (Classic ITEM System) من الصفر 💥
    xml_items_list = []
    for index, ch in enumerate(channels_sorted, start=1):
        item_block = (
            f"  <ITEM>\r\n"
            f"    <prNum>{index}</prNum>\r\n"
            f"    <vchName>{ch['name']}</vchName>\r\n"
            f"    <frequency>{ch['freq']}</frequency>\r\n"
            f"    <polarization>{ch['polarization']}</polarization>\r\n"
            f"    <satelliteName>Nilesat</satelliteName>\r\n"
            f"  </ITEM>"
        )
        xml_items_list.append(item_block)
        text_report += f"No. {index:03d} : {ch['name']:<25} | Freq: {ch['freq']} MHz\n"

    combined_items = "\r\n".join(xml_items_list)
    
    # صياغة النص الـ XML الخام الكلاسيكي للموديلات القديمة
    raw_xml_legacy = (
        f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n"
        f"<TLLDATA>\r\n"
        f"  <ModelName>{generated_model_name}</ModelName>\r\n"
        f"{combined_items}\r\n"
        f"</TLLDATA>"
    )
    final_xml_bytes = raw_xml_legacy.encode('utf-8')

# ── منطقة التحميل والإرشادات الفنية ──
st.write("---")
st.success(t['ready_msg'])

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.download_button(label=t['btn_download_tll'], data=final_xml_bytes,
                       file_name="GlobalClone00001.TLL", mime="application/octet-stream")
with col_btn2:
    st.download_button(label=t['btn_download_txt'], data=text_report,
                       file_name="Channels_List.txt", mime="text/plain; charset=utf-8")

# الملحوظة الفنية الهامة جداً بعد التحميل مباشرة
st.markdown(f"""
    <div class="lg-trick-box">
        <h4 style="color: #ff007f; margin-top:0;">{t['lg_trick_title']}</h4>
        <p style="white-space: pre-line; margin-bottom:0; font-size:15px; line-height: 1.6;">{t['lg_trick_text']}</p>
    </div>
""", unsafe_allow_html=True)

# ── الفوتر الفني للمطور ──
whatsapp_url = ("https://api.whatsapp.com/send?phone=201280339779"
                "&text=Hello%20Developer%20Rafik%20Rambo%2C%20"
                "I%20have%20an%20inquiry%20regarding%20your%20LG%20TV%20Generator%20script%3A")
st.markdown(f"""
    <div class="futuristic-cyber-footer">
        <div class="footer-dev">🛠️ DEVELOPER ENG: RAFIK RAMBO</div>
        <div class="footer-item">📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
        <div class="footer-item">✉️ <b>E-MAIL / البريد الإلكتروني:</b> rafikrambo113@gmail.com</div>
        <a href="{whatsapp_url}" target="_blank" class="cyber-whatsapp-btn">WhatsApp Web</a>
    </div>
""", unsafe_allow_html=True)
