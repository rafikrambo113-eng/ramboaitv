import streamlit as st
import xml.etree.ElementTree as ET
import re
import json
from datetime import datetime

# ──────────────────────────────────────────────────────
# 1. SESSION STATE
# ──────────────────────────────────────────────────────
for key, val in {
    'lang': 'ar',
    'theme': 'dark',
    'p4_step': 1,
    'p4_file_bytes': None,
    'p4_file_name': None,
    'p4_info': {},
    'p4_result_bytes': None,
    'p4_uploader_key': 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ──────────────────────────────────────────────────────
# 2. بيانات الموديلات والبلدان
# ──────────────────────────────────────────────────────

# قائمة موديلات LG الشائعة
LG_MODELS = [
    # 2024 / 2025
    "OLED65G4PSA", "OLED55C4PSA", "OLED77C4PSA", "65QNED85T6A",
    "55QNED80T6A", "75UR78006LK", "65UR78006LK", "55UR78006LK",
    "43UR78006LK", "32LQ63806LC", "43LQ63006LA", "50LQ63006LA",
    # 2022 / 2023
    "OLED65C3PSA", "OLED55C3PSA", "65QNED85VPA", "55QNED85VPA",
    "75UR80006LJ", "65UR80006LJ", "55UR80006LJ", "43UR80006LJ",
    "50UR80006LJ", "32LQ630BPSA", "43LQ630BPSA", "50LQ630BPSA",
    "65UQ80006LB", "55UQ80006LB", "50UQ80006LB", "43UQ80006LB",
    # 2020 / 2021
    "OLED65CX6LA", "OLED55CX6LA", "65NANO86VPA", "55NANO86VPA",
    "75UP80006LR", "65UP80006LR", "55UP80006LR", "43UP80006LR",
    "50UP80006LR", "32LQ630BPSA", "43UP75006LF", "50UP75006LF",
    # 2018 / 2019 (Legacy)
    "65SM9010PLA", "55SM9010PLA", "65SK8500PLA", "55SK8500PLA",
    "43UK6300PLB", "49UK6300PLB", "55UK6300PLB", "65UK6300PLB",
    "32LK6100PLB", "43LK6100PLB", "49LK6100PLB", "55LK6100PLB",
    "32LM550BPVA", "43LM5500PLA", "49LM5500PLA", "55LM5500PLA",
    # 2016 / 2017 (قديم جداً)
    "65UH950V", "55UH950V", "49UH850V", "43UH850V",
    "32LH604U-TB", "43LH604V", "49LH604V", "55LH604V",
    "32LH570U", "43LH570V", "49LH570V", "55LH570V",
    "32LH530V", "43LH530V", "49LH530V",
]

# كودات البلدان - بتشمل الكودين والتلاتة حروف
COUNTRIES = {
    "🇪🇬 مصر":         {"code2": "EG",  "code3": "EGY"},
    "🇸🇦 السعودية":     {"code2": "SA",  "code3": "SAU"},
    "🇦🇪 الإمارات":     {"code2": "AE",  "code3": "ARE"},
    "🇯🇴 الأردن":       {"code2": "JO",  "code3": "JOR"},
    "🇱🇧 لبنان":        {"code2": "LB",  "code3": "LBN"},
    "🇸🇩 السودان":      {"code2": "SD",  "code3": "SDN"},
    "🇩🇿 الجزائر":      {"code2": "DZ",  "code3": "DZA"},
    "🇲🇦 المغرب":       {"code2": "MA",  "code3": "MAR"},
    "🇹🇳 تونس":         {"code2": "TN",  "code3": "TUN"},
    "🇱🇾 ليبيا":        {"code2": "LY",  "code3": "LBY"},
    "🇮🇶 العراق":       {"code2": "IQ",  "code3": "IRQ"},
    "🇸🇾 سوريا":        {"code2": "SY",  "code3": "SYR"},
    "🇾🇪 اليمن":        {"code2": "YE",  "code3": "YEM"},
    "🇰🇼 الكويت":       {"code2": "KW",  "code3": "KWT"},
    "🇶🇦 قطر":          {"code2": "QA",  "code3": "QAT"},
    "🇧🇭 البحرين":      {"code2": "BH",  "code3": "BHR"},
    "🇴🇲 عُمان":        {"code2": "OM",  "code3": "OMN"},
    "🇵🇸 فلسطين":       {"code2": "PS",  "code3": "PSE"},
    "🌐 عالمي (JA)":    {"code2": "JA",  "code3": "JA"},
}

# عكس للبحث
CODE_TO_COUNTRY = {}
for name, codes in COUNTRIES.items():
    CODE_TO_COUNTRY[codes["code2"]] = name
    CODE_TO_COUNTRY[codes["code3"]] = name

# ──────────────────────────────────────────────────────
# 3. UI TEXT
# ──────────────────────────────────────────────────────
UI = {
    'ar': {
        'title':         "🔄 RAMBO — محوّل ملفات TLL",
        'subtitle':      "⚡ حوّل ملف قنواتك لأي موديل أو بلد بث في ثوانٍ",
        'upload_label':  "📂 ارفع ملف TLL الأصلي:",
        'step1_title':   "📋 الخطوة 1: رفع الملف",
        'step2_title':   "⚙️ الخطوة 2: اختر التحويل المطلوب",
        'step3_title':   "✅ الخطوة 3: تحميل الملف المحوّل",
        'file_info':     "📊 معلومات الملف المرفوع:",
        'current_model': "الموديل الحالي",
        'current_country':"البلد الحالي",
        'file_type':     "نوع الملف",
        'ch_count':      "عدد القنوات",
        'modern':        "حديث (JSON)",
        'legacy':        "قديم (XML)",
        'change_model':  "🖥️ تغيير الموديل",
        'change_country':"🌍 تغيير البلد",
        'new_model_lbl': "اختر الموديل الجديد:",
        'new_country_lbl':"اختر بلد البث الجديد:",
        'or_type_model': "أو اكتب الموديل يدوياً:",
        'btn_convert':   "🔄 تحويل الآن",
        'btn_download':  "📥 تحميل الملف المحوّل",
        'btn_reset':     "🔄 تحويل ملف جديد",
        'success':       "✅ تم التحويل بنجاح! الملف جاهز للتحميل.",
        'no_change':     "⚠️ لم تختر أي تغيير! اختر موديل أو بلد جديد.",
        'changes_made':  "📝 التغييرات المطبّقة:",
        'model_changed': "الموديل",
        'country_changed':"البلد",
        'from':          "من",
        'to':            "إلى",
        'tip_title':     "💡 ملحوظة مهمة:",
        'tip_text':      "بعد تحميل الملف على الشاشة، إذا لم تظهر القنوات بشكل صحيح، اذهب إلى: إعدادات ← القنوات ← مدير القنوات ← تعديل كل القنوات ← تحديد الكل ← استعادة",
        'no_file':       "⬆️ ارفع ملف TLL أولاً للبدء.",
        'unknown':       "غير معروف",
        'keep_same':     "— الاحتفاظ بنفس القيمة —",
    },
    'en': {
        'title':         "🔄 RAMBO — TLL File Converter",
        'subtitle':      "⚡ Convert your channel file to any model or country in seconds",
        'upload_label':  "📂 Upload your TLL file:",
        'step1_title':   "📋 Step 1: Upload File",
        'step2_title':   "⚙️ Step 2: Choose Conversion",
        'step3_title':   "✅ Step 3: Download Converted File",
        'file_info':     "📊 Uploaded File Info:",
        'current_model': "Current Model",
        'current_country':"Current Country",
        'file_type':     "File Type",
        'ch_count':      "Channel Count",
        'modern':        "Modern (JSON)",
        'legacy':        "Legacy (XML)",
        'change_model':  "🖥️ Change Model",
        'change_country':"🌍 Change Country",
        'new_model_lbl': "Select new model:",
        'new_country_lbl':"Select new broadcast country:",
        'or_type_model': "Or type model manually:",
        'btn_convert':   "🔄 Convert Now",
        'btn_download':  "📥 Download Converted File",
        'btn_reset':     "🔄 Convert New File",
        'success':       "✅ Conversion successful! File ready to download.",
        'no_change':     "⚠️ No changes selected! Choose a new model or country.",
        'changes_made':  "📝 Changes Applied:",
        'model_changed': "Model",
        'country_changed':"Country",
        'from':          "from",
        'to':            "to",
        'tip_title':     "💡 Important Note:",
        'tip_text':      "After loading the file on your TV, if channels don't appear correctly, go to: Settings ← Channels ← Channel Manager ← Edit All Channels ← Select All ← Restore",
        'no_file':       "⬆️ Upload a TLL file first to start.",
        'unknown':       "Unknown",
        'keep_same':     "— Keep same value —",
    }
}

# ──────────────────────────────────────────────────────
# 4. دوال التحليل والتحويل
# ──────────────────────────────────────────────────────
def parse_tll_info(file_bytes):
    """استخراج معلومات الملف"""
    try:
        txt = file_bytes.decode('utf-8', errors='ignore')
    except:
        txt = file_bytes.decode('latin-1', errors='ignore')

    info = {}

    # الموديل
    m = re.search(r'<ModelName[^>]*>([^<]+)</ModelName>', txt)
    info['model'] = m.group(1).strip() if m else ""

    # نوع الملف
    info['is_modern'] = 'legacybroadcast' in txt

    # البلد
    if info['is_modern']:
        # Modern JSON
        m = re.search(r'"country"\s*:\s*"([^"]+)"', txt)
        info['country'] = m.group(1).strip() if m else ""
        m2 = re.search(r'<country[^>]*>([^<]+)</country>', txt)
        info['country_xml'] = m2.group(1).strip() if m2 else ""
    else:
        # Legacy XML
        m = re.search(r'<country[^>]*>([^<]+)</country>', txt)
        info['country'] = m.group(1).strip() if m else ""
        info['country_xml'] = info['country']

    # عدد القنوات
    if info['is_modern']:
        m = re.search(r'"channelList"\s*:\s*\[', txt)
        if m:
            # عدّ القنوات في JSON
            channel_matches = re.findall(r'"channelName"\s*:', txt)
            info['ch_count'] = len(channel_matches)
        else:
            info['ch_count'] = 0
    else:
        info['ch_count'] = len(re.findall(r'<ITEM>', txt))

    info['raw_text'] = txt
    return info


def convert_tll(file_bytes, new_model, new_country_name, current_info):
    """تحويل الملف"""
    try:
        txt = file_bytes.decode('utf-8', errors='ignore')
    except:
        txt = file_bytes.decode('latin-1', errors='ignore')

    changes = []
    is_modern = current_info.get('is_modern', False)

    # ── تغيير الموديل ──
    if new_model and new_model != current_info.get('model', ''):
        old_model = current_info.get('model', '')
        txt = re.sub(
            r'(<ModelName[^>]*>)([^<]+)(</ModelName>)',
            rf'\g<1>{new_model}\g<3>',
            txt
        )
        changes.append(('model', old_model, new_model))

    # ── تغيير البلد ──
    if new_country_name and new_country_name in COUNTRIES:
        country_data = COUNTRIES[new_country_name]
        old_country = current_info.get('country', '')

        if is_modern:
            # Modern JSON: غيّر في كلا المكانين
            # في XML
            old_xml = current_info.get('country_xml', old_country)
            # نحدد الكود الصح حسب الكود الحالي
            old_len = len(old_xml)
            new_code = country_data['code2'] if old_len <= 2 else country_data['code3']

            txt = re.sub(
                r'(<country[^>]*>)([^<]+)(</country>)',
                rf'\g<1>{new_code}\g<3>',
                txt
            )
            # في JSON داخل legacybroadcast
            txt = re.sub(
                r'("country"\s*:\s*")([^"]+)(")',
                rf'\g<1>{country_data["code3"]}\g<3>',
                txt
            )
            new_display = new_code
        else:
            # Legacy XML: كود 2 حروف أو 3 حسب الملف الأصلي
            old_len = len(old_country)
            new_code = country_data['code2'] if old_len <= 2 else country_data['code3']

            txt = re.sub(
                r'(<country[^>]*>)([^<]+)(</country>)',
                rf'\g<1>{new_code}\g<3>',
                txt
            )
            new_display = new_code

        if old_country != new_display:
            changes.append(('country', old_country, new_display))

    return txt.encode('utf-8'), changes


# ──────────────────────────────────────────────────────
# 5. إعداد الصفحة والـ CSS
# ──────────────────────────────────────────────────────
t = UI[st.session_state.lang]
st.set_page_config(page_title="RAMBO P4 — Converter", page_icon="🔄", layout="wide")

# أزرار اللغة والثيم
col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("🌐 English" if st.session_state.lang == 'ar' else "🌐 العربية"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
        st.rerun()
with col_theme:
    if st.button("☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

# CSS
if st.session_state.theme == 'dark':
    bg      = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)"
    tc      = "#00f0ff"
    box_bg  = "rgba(13,7,33,0.85)"
    bord    = "#00f0ff"
    bsh     = "rgba(0,240,255,0.35)"
    tsh     = "0 0 5px rgba(0,240,255,0.4)"
    th_bg   = "#0d0722"
else:
    bg      = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
    tc      = "#0d0722"
    box_bg  = "#ffffff"
    bord    = "#ff007f"
    bsh     = "rgba(255,0,127,0.15)"
    tsh     = "none"
    th_bg   = "#0d0722"

ff = "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
.main {{ background: {bg} !important; color: {tc} !important; font-family: {ff}; }}
h1 {{ color: #ff007f !important;
      text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.4) !important;
      text-align: center; font-weight: 900; margin-top: 5px; }}
h3, p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] p {{
    color: {tc} !important; text-shadow: {tsh}; }}
.stTextInput>div>div>input, .stSelectbox>div>div {{
    background-color: {box_bg} !important; color: {tc} !important;
    border: 2px solid {bord} !important; border-radius: 10px !important; }}
div[data-testid="stFileUploader"] {{
    background: {box_bg} !important; border: 2px solid {bord} !important;
    box-shadow: 0px 5px 15px {bsh} !important; border-radius: 14px !important;
    padding: 18px !important; margin-bottom: 20px !important; }}
.stButton>button {{
    background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
    color: #ffffff !important; border: 2px solid #ff007f !important;
    border-radius: 12px !important; font-weight: bold; width: 100%; }}
.stDownloadButton>button {{
    background: linear-gradient(135deg, #00b894 0%, #00695c 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; font-weight: bold; width: 100%; }}
.info-card {{
    background: {box_bg}; border: 2px solid {bord};
    box-shadow: 0 5px 15px {bsh}; border-radius: 14px;
    padding: 20px; margin-bottom: 18px; }}
.step-badge {{
    display: inline-block;
    background: linear-gradient(135deg, #ff007f, #aa0055);
    color: white; border-radius: 50%; width: 32px; height: 32px;
    text-align: center; line-height: 32px; font-weight: bold;
    margin-left: 8px; margin-right: 8px; font-size: 1rem; }}
.change-row {{
    background: rgba(0,240,255,0.08); border-left: 4px solid #00f0ff;
    border-radius: 8px; padding: 10px 16px; margin: 6px 0;
    font-size: 0.95rem; }}
.arrow {{ color: #ff007f; font-weight: bold; margin: 0 8px; }}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 6. العنوان
# ──────────────────────────────────────────────────────
st.title(t['title'])
st.markdown(f"<h3 style='text-align:center;'>{t['subtitle']}</h3>", unsafe_allow_html=True)
st.write("---")

# ──────────────────────────────────────────────────────
# 7. الخطوة 1 — رفع الملف
# ──────────────────────────────────────────────────────
st.markdown(f"### <span class='step-badge'>1</span> {t['step1_title']}", unsafe_allow_html=True)

col_up, col_reset = st.columns([5, 1])
with col_up:
    uploaded = st.file_uploader(
        t['upload_label'], type=["TLL"],
        key=f"p4_uploader_{st.session_state.p4_uploader_key}"
    )
with col_reset:
    st.write("")
    st.write("")
    if st.button(t['btn_reset'], key="p4_reset_top"):
        for k in ['p4_file_bytes','p4_file_name','p4_info','p4_result_bytes','p4_step']:
            st.session_state[k] = None if 'bytes' in k or 'info' in k else (1 if k == 'p4_step' else None)
        st.session_state.p4_info = {}
        st.session_state.p4_step = 1
        st.session_state.p4_uploader_key += 1
        st.rerun()

# معالجة الملف
if uploaded:
    file_bytes = uploaded.read()
    if st.session_state.p4_file_name != uploaded.name:
        st.session_state.p4_file_bytes = file_bytes
        st.session_state.p4_file_name  = uploaded.name
        st.session_state.p4_info       = parse_tll_info(file_bytes)
        st.session_state.p4_step       = 2
        st.session_state.p4_result_bytes = None

if not st.session_state.p4_file_bytes:
    st.info(t['no_file'])
    st.markdown("""
    <div style="background:#0f172a;border:2px solid #00f0ff;color:white;padding:30px;
    text-align:center;border-radius:15px;margin-top:50px;font-family:Arial;">
    <b>🛠️ DEVELOPER ENG: RAFIK RAMBO</b><br><br>
    📱 +201280339779<br>✉️ rafikrambo113@gmail.com<br><br>
    <a href="https://api.whatsapp.com/send?phone=201280339779" style="color:#25d366;">WhatsApp</a>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── عرض معلومات الملف ──
info = st.session_state.p4_info
current_country_name = CODE_TO_COUNTRY.get(info.get('country',''), info.get('country', t['unknown']))
file_type_label = t['modern'] if info.get('is_modern') else t['legacy']

st.markdown(f"<div class='info-card'>", unsafe_allow_html=True)
st.markdown(f"**{t['file_info']}**")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric(t['current_model'],   info.get('model', t['unknown']))
with c2:
    st.metric(t['current_country'], f"{current_country_name} ({info.get('country','')})")
with c3:
    st.metric(t['file_type'],       file_type_label)
with c4:
    st.metric(t['ch_count'],        f"{info.get('ch_count', 0):,}")
st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# ──────────────────────────────────────────────────────
# 8. الخطوة 2 — اختيارات التحويل
# ──────────────────────────────────────────────────────
st.markdown(f"### <span class='step-badge'>2</span> {t['step2_title']}", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

# ── تغيير الموديل ──
with col_left:
    st.markdown(f"#### {t['change_model']}")
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)

    # اختيار من القائمة
    model_options = [t['keep_same']] + sorted(LG_MODELS)
    selected_model_dropdown = st.selectbox(
        t['new_model_lbl'],
        options=model_options,
        key="p4_model_select"
    )

    # أو كتابة يدوي
    manual_model = st.text_input(
        t['or_type_model'],
        placeholder="مثال: 55UN7340PVA" if st.session_state.lang == 'ar' else "e.g. 55UN7340PVA",
        key="p4_model_manual"
    ).strip()

    # أولوية: اليدوي على الـ dropdown
    final_model = manual_model if manual_model else (
        selected_model_dropdown if selected_model_dropdown != t['keep_same'] else ""
    )

    if final_model and final_model != info.get('model', ''):
        st.success(f"✅ {'سيتم التغيير إلى' if st.session_state.lang == 'ar' else 'Will change to'}: **{final_model}**")
    elif final_model == info.get('model', ''):
        st.info(f"ℹ️ {'نفس الموديل الحالي' if st.session_state.lang == 'ar' else 'Same as current model'}")

    st.markdown("</div>", unsafe_allow_html=True)

# ── تغيير البلد ──
with col_right:
    st.markdown(f"#### {t['change_country']}")
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)

    country_options = [t['keep_same']] + list(COUNTRIES.keys())
    selected_country = st.selectbox(
        t['new_country_lbl'],
        options=country_options,
        key="p4_country_select"
    )

    final_country = selected_country if selected_country != t['keep_same'] else ""

    if final_country:
        codes = COUNTRIES[final_country]
        # عرض الكودين المحتملين
        old_len = len(info.get('country', 'XX'))
        expected_code = codes['code2'] if old_len <= 2 else codes['code3']
        st.success(
            f"✅ {'سيتم التغيير إلى' if st.session_state.lang == 'ar' else 'Will change to'}: "
            f"**{final_country}** `({expected_code})`"
        )

    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ── زر التحويل ──
col_btn, _, _ = st.columns([2, 1, 1])
with col_btn:
    if st.button(t['btn_convert'], use_container_width=True, key="p4_convert_btn"):
        if not final_model and not final_country:
            st.warning(t['no_change'])
        else:
            result_bytes, changes = convert_tll(
                st.session_state.p4_file_bytes,
                final_model,
                final_country,
                info
            )
            st.session_state.p4_result_bytes = result_bytes
            st.session_state.p4_changes      = changes
            st.session_state.p4_step         = 3
            st.rerun()

# ──────────────────────────────────────────────────────
# 9. الخطوة 3 — النتيجة والتحميل
# ──────────────────────────────────────────────────────
if st.session_state.p4_step == 3 and st.session_state.p4_result_bytes:
    st.write("---")
    st.markdown(f"### <span class='step-badge'>3</span> {t['step3_title']}", unsafe_allow_html=True)

    st.success(t['success'])

    # ── عرض التغييرات ──
    changes = st.session_state.get('p4_changes', [])
    if changes:
        st.markdown(f"**{t['changes_made']}**")
        for ch_type, old_val, new_val in changes:
            label = t['model_changed'] if ch_type == 'model' else t['country_changed']
            st.markdown(
                f"<div class='change-row'>"
                f"🔧 <b>{label}</b>: "
                f"<code>{old_val}</code>"
                f"<span class='arrow'>➜</span>"
                f"<code style='color:#00f0ff;'>{new_val}</code>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.write("")

    # ── زر التحميل ──
    col_d1, col_d2 = st.columns([3, 1])
    with col_d1:
        st.download_button(
            label=t['btn_download'],
            data=st.session_state.p4_result_bytes,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream",
            use_container_width=True,
        )
    with col_d2:
        if st.button(t['btn_reset'], key="p4_reset_bottom", use_container_width=True):
            for k in ['p4_file_bytes','p4_file_name','p4_info','p4_result_bytes']:
                st.session_state[k] = None
            st.session_state.p4_info    = {}
            st.session_state.p4_step    = 1
            st.session_state.p4_uploader_key += 1
            st.rerun()

    # ── ملحوظة LG ──
    st.markdown(f"""
<div style="background:rgba(255,193,7,0.1);border:2px solid #ffc107;border-radius:14px;
padding:22px;margin-top:20px;">
<div style="color:#ffc107;font-size:1.1rem;font-weight:bold;margin-bottom:10px;">
{t['tip_title']}</div>
<div style="line-height:1.8;">{t['tip_text']}</div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 10. FOOTER
# ──────────────────────────────────────────────────────
whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"
st.markdown(f"""
<div style="background:#0f172a;border:2px solid #00f0ff;color:#ffffff;
padding:35px;text-align:center;border-radius:20px;margin-top:65px;font-family:Arial;">
<div style="color:#ff007f;font-size:26px;font-weight:bold;">🛠️ DEVELOPER ENG: RAFIK NATHAN</div>
<div style="margin-top:10px;">📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
<div style="margin-top:10px;">✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com</div>
<a href="{whatsapp_url}" target="_blank"
style="color:#25d366;padding:14px 35px;border-radius:35px;display:inline-block;
font-weight:bold;border:2px solid #25d366;text-decoration:none;margin-top:20px;">
WhatsApp</a>
</div>
""", unsafe_allow_html=True)
