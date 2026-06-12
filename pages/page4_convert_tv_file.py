import streamlit as st
import re
import json
from datetime import datetime

# ──────────────────────────────────────────────────────
# 1. SESSION STATE
# ──────────────────────────────────────────────────────
for key, val in {
    'lang': 'ar',
    'theme': 'dark',
    'p4_file_bytes': None,
    'p4_file_name': None,
    'p4_info': {},
    'p4_result_bytes': None,
    'p4_changes': [],
    'p4_done': False,
    'p4_uploader_key': 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ──────────────────────────────────────────────────────
# 2. بيانات البلدان
# ──────────────────────────────────────────────────────
COUNTRIES = {
    "🇪🇬 مصر / Egypt":           {"code2": "EG",  "code3": "EGY", "full": "Egypt"},
    "🇸🇦 السعودية / Saudi":       {"code2": "SA",  "code3": "SAU", "full": "Saudi Arabia"},
    "🇦🇪 الإمارات / UAE":          {"code2": "AE",  "code3": "ARE", "full": "United Arab Emirates"},
    "🇯🇴 الأردن / Jordan":         {"code2": "JO",  "code3": "JOR", "full": "Jordan"},
    "🇱🇧 لبنان / Lebanon":         {"code2": "LB",  "code3": "LBN", "full": "Lebanon"},
    "🇸🇩 السودان / Sudan":         {"code2": "SD",  "code3": "SDN", "full": "Sudan"},
    "🇩🇿 الجزائر / Algeria":       {"code2": "DZ",  "code3": "DZA", "full": "Algeria"},
    "🇲🇦 المغرب / Morocco":        {"code2": "MA",  "code3": "MAR", "full": "Morocco"},
    "🇹🇳 تونس / Tunisia":          {"code2": "TN",  "code3": "TUN", "full": "Tunisia"},
    "🇱🇾 ليبيا / Libya":           {"code2": "LY",  "code3": "LBY", "full": "Libya"},
    "🇮🇶 العراق / Iraq":           {"code2": "IQ",  "code3": "IRQ", "full": "Iraq"},
    "🇸🇾 سوريا / Syria":           {"code2": "SY",  "code3": "SYR", "full": "Syria"},
    "🇾🇪 اليمن / Yemen":           {"code2": "YE",  "code3": "YEM", "full": "Yemen"},
    "🇰🇼 الكويت / Kuwait":         {"code2": "KW",  "code3": "KWT", "full": "Kuwait"},
    "🇶🇦 قطر / Qatar":             {"code2": "QA",  "code3": "QAT", "full": "Qatar"},
    "🇧🇭 البحرين / Bahrain":       {"code2": "BH",  "code3": "BHR", "full": "Bahrain"},
    "🇴🇲 عُمان / Oman":            {"code2": "OM",  "code3": "OMN", "full": "Oman"},
    "🇵🇸 فلسطين / Palestine":      {"code2": "PS",  "code3": "PSE", "full": "Palestine"},
    "🌐 عالمي / Global (JA)":      {"code2": "JA",  "code3": "JA",  "full": "Japan"},
}

# عكس للبحث عن اسم البلد من الكود
CODE_TO_NAME = {}
for name, d in COUNTRIES.items():
    CODE_TO_NAME[d["code2"].upper()] = name
    CODE_TO_NAME[d["code3"].upper()] = name
    CODE_TO_NAME[d["full"].upper()]  = name

# موديلات LG
LG_MODELS = sorted([
    # 2024/2025
    "OLED65G4PSA","OLED55C4PSA","OLED77C4PSA","65QNED85T6A","55QNED80T6A",
    "75UR78006LK","65UR78006LK","65UR78006LL","55UR78006LK","43UR78006LK",
    "32LQ63806LC","43LQ63006LA","50LQ63006LA",
    # 2022/2023
    "OLED65C3PSA","OLED55C3PSA","65QNED85VPA","55QNED85VPA",
    "75UR80006LJ","65UR80006LJ","55UR80006LJ","43UR80006LJ","50UR80006LJ",
    "32LQ630BPSA","43LQ630BPSA","50LQ630BPSA",
    "65UQ80006LB","55UQ80006LB","50UQ80006LB","43UQ80006LB",
    # 2020/2021
    "OLED65CX6LA","OLED55CX6LA","65NANO86VPA","55NANO86VPA",
    "75UP80006LR","65UP80006LR","55UP80006LR","43UP80006LR","50UP80006LR",
    "43UP75006LF","50UP75006LF",
    # 2018/2019
    "65SM9010PLA","55SM9010PLA","65SK8500PLA","55SK8500PLA",
    "43UK6300PLB","49UK6300PLB","55UK6300PLB","65UK6300PLB",
    "32LK6100PLB","43LK6100PLB","49LK6100PLB","55LK6100PLB",
    "32LM550BPVA","43LM5500PLA","49LM5500PLA","55LM5500PLA",
    # 2016/2017
    "65UH950V","55UH950V","49UH850V","43UH850V",
    "32LH604U-TB","43LH604V","49LH604V","55LH604V",
    "32LH570U","43LH570V","49LH570V","55LH570V",
    "32LH530V","43LH530V","49LH530V",
    "55UA85006LA.DFUYLWE","65UA80006LA",
])

# ──────────────────────────────────────────────────────
# 3. دوال التحليل والتحويل
# ──────────────────────────────────────────────────────
def parse_tll(file_bytes):
    try:
        txt = file_bytes.decode('utf-8', errors='ignore')
    except:
        txt = file_bytes.decode('latin-1', errors='ignore')

    info = {}
    info['txt'] = txt
    info['is_modern'] = 'legacybroadcast' in txt

    # الموديل
    m = re.search(r'<ModelName[^>]*>([^<]+)</ModelName>', txt)
    info['model'] = m.group(1).strip() if m else ""

    if info['is_modern']:
        # ── Modern JSON ──
        # BroadcastCountrySetting (code3)
        m = re.search(r'<BroadcastCountrySetting[^>]*>([^<]+)</BroadcastCountrySetting>', txt)
        info['broadcast_country'] = m.group(1).strip() if m else ""

        # country XML (عادةً JA)
        m = re.search(r'<country[^>]*>([^<]+)</country>', txt)
        info['country_xml'] = m.group(1).strip() if m else ""

        # country في JSON (الاسم الكامل)
        jm = re.search(r'<legacybroadcast>(.*?)</legacybroadcast>', txt, re.DOTALL)
        if jm:
            try:
                data = json.loads(jm.group(1))
                info['country_json'] = data.get('modelInfo', {}).get('country', '')
                info['ch_count'] = len(data.get('channelList', []))
            except:
                info['country_json'] = ''
                info['ch_count'] = len(re.findall(r'"channelName"', txt))
        else:
            info['country_json'] = ''
            info['ch_count'] = 0

        # البلد المعروض = BroadcastCountrySetting أو country_json
        info['display_country'] = info['broadcast_country'] or info['country_json']

    else:
        # ── Legacy XML ──
        m = re.search(r'<BroadcastCountrySetting[^>]*>([^<]+)</BroadcastCountrySetting>', txt)
        info['broadcast_country'] = m.group(1).strip() if m else ""

        m = re.search(r'<country[^>]*>([^<]+)</country>', txt)
        info['country_xml'] = m.group(1).strip() if m else ""

        info['country_json'] = ''
        info['display_country'] = info['country_xml'] or info['broadcast_country']
        info['ch_count'] = len(re.findall(r'<ITEM>', txt))

    # اسم البلد بالعربي
    dc = info['display_country'].upper()
    info['country_label'] = CODE_TO_NAME.get(dc, info['display_country'])

    return info


def convert_tll(info, new_model, new_country_name):
    txt = info['txt']
    changes = []
    is_modern = info['is_modern']

    # ══════════════════════════════════
    # تغيير الموديل
    # ══════════════════════════════════
    if new_model and new_model.strip() and new_model.strip() != info['model']:
        old = info['model']
        new = new_model.strip()
        txt = re.sub(
            r'(<ModelName[^>]*>)([^<]+)(</ModelName>)',
            lambda m: m.group(1) + new + m.group(3),
            txt
        )
        changes.append(('model', old, new))

    # ══════════════════════════════════
    # تغيير البلد
    # ══════════════════════════════════
    if new_country_name and new_country_name in COUNTRIES:
        cd = COUNTRIES[new_country_name]

        if is_modern:
            # ── Modern: غيّر في 3 أماكن ──

            # 1. BroadcastCountrySetting → code3
            old_bc = info['broadcast_country']
            if old_bc:
                txt = re.sub(
                    r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                    lambda m: m.group(1) + cd['code3'] + m.group(3),
                    txt
                )
            else:
                # أضفها لو مش موجودة
                txt = txt.replace(
                    '</ModelInfo>',
                    f'<BroadcastCountrySetting type="0">{cd["code3"]}</BroadcastCountrySetting>\n</ModelInfo>'
                )

            # 2. country XML → اتركها JA (ده بيخلي الشاشة تقبل الملف)
            # مش بنغيرها عشان دي بتتحكم في قبول الملف

            # 3. country في JSON → full name
            def replace_json_country(match):
                try:
                    data = json.loads(match.group(1))
                    data['modelInfo']['country'] = cd['full']
                    return '<legacybroadcast>' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '</legacybroadcast>'
                except:
                    return match.group(0)
            txt = re.sub(
                r'<legacybroadcast>(.*?)</legacybroadcast>',
                replace_json_country,
                txt,
                flags=re.DOTALL
            )

            old_display = info['broadcast_country'] or info['country_json']
            new_display = cd['code3']

        else:
            # ── Legacy XML: غيّر country ──
            old_display = info['country_xml'] or info['broadcast_country']

            # BroadcastCountrySetting لو موجود
            if info['broadcast_country']:
                txt = re.sub(
                    r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                    lambda m: m.group(1) + cd['code3'] + m.group(3),
                    txt
                )

            # country tag - نحدد الطول المناسب
            old_len = len(info['country_xml'])
            new_code = cd['code2'] if old_len <= 2 else cd['code3']
            txt = re.sub(
                r'(<country[^>]*>)([^<]+)(</country>)',
                lambda m: m.group(1) + new_code + m.group(3),
                txt
            )
            new_display = new_code

        if old_display != new_display:
            changes.append(('country', old_display, new_display, new_country_name))

    return txt.encode('utf-8'), changes


# ──────────────────────────────────────────────────────
# 4. إعداد الصفحة والـ CSS
# ──────────────────────────────────────────────────────
t_lang = st.session_state.lang
st.set_page_config(page_title="RAMBO P4 — Converter", page_icon="🔄", layout="wide")

col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("🌐 English" if t_lang == 'ar' else "🌐 العربية"):
        st.session_state.lang = 'en' if t_lang == 'ar' else 'ar'
        st.rerun()
with col_theme:
    if st.button("☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

dk = st.session_state.theme == 'dark'
bg    = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)" if dk else "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
tc    = "#00f0ff" if dk else "#0d0722"
bb    = "rgba(13,7,33,0.85)" if dk else "#ffffff"
bord  = "#00f0ff" if dk else "#ff007f"
bsh   = "rgba(0,240,255,0.35)" if dk else "rgba(255,0,127,0.15)"
tsh   = "0 0 5px rgba(0,240,255,0.4)" if dk else "none"
ff    = "'Cairo', sans-serif" if t_lang == 'ar' else "'Orbitron', sans-serif"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
.main {{ background: {bg} !important; color: {tc} !important; font-family: {ff}; }}
h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f,0 0 25px rgba(255,0,127,0.4) !important;
      text-align:center; font-weight:900; margin-top:5px; }}
h3,p,label,.stMarkdown,div[data-testid="stMarkdownContainer"] p {{
    color:{tc} !important; text-shadow:{tsh}; }}
.stTextInput>div>div>input,.stSelectbox>div>div {{
    background-color:{bb} !important; color:{tc} !important;
    border:2px solid {bord} !important; border-radius:10px !important; }}
div[data-testid="stFileUploader"] {{
    background:{bb} !important; border:2px solid {bord} !important;
    box-shadow:0 5px 15px {bsh} !important; border-radius:14px !important;
    padding:18px !important; margin-bottom:20px !important; }}
.stButton>button {{
    background:linear-gradient(135deg,#ff007f 0%,#aa0055 100%) !important;
    color:#fff !important; border:2px solid #ff007f !important;
    border-radius:12px !important; font-weight:bold; width:100%; }}
.stDownloadButton>button {{
    background:linear-gradient(135deg,#00b894 0%,#00695c 100%) !important;
    color:#fff !important; border:none !important;
    border-radius:12px !important; font-weight:bold; width:100%; }}
.card {{
    background:{bb}; border:2px solid {bord};
    box-shadow:0 5px 15px {bsh}; border-radius:14px;
    padding:20px; margin-bottom:16px; }}
.badge {{
    display:inline-block; background:linear-gradient(135deg,#ff007f,#aa0055);
    color:white; border-radius:50%; width:30px; height:30px;
    text-align:center; line-height:30px; font-weight:bold;
    margin-left:8px; margin-right:8px; }}
.change-row {{
    background:rgba(0,240,255,0.08); border-left:4px solid #00f0ff;
    border-radius:8px; padding:10px 16px; margin:6px 0; }}
.tag {{
    display:inline-block; border-radius:6px; padding:3px 10px;
    font-size:0.85rem; font-weight:bold; margin:2px; }}
.tag-modern {{ background:rgba(0,240,255,0.15); border:1px solid #00f0ff; color:#00f0ff; }}
.tag-legacy {{ background:rgba(255,165,0,0.15); border:1px solid orange; color:orange; }}
.tag-country {{ background:rgba(255,0,127,0.15); border:1px solid #ff007f; color:#ff007f; }}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 5. العنوان
# ──────────────────────────────────────────────────────
title_ar = "🔄 RAMBO — محوّل ملفات TLL"
title_en = "🔄 RAMBO — TLL File Converter"
sub_ar   = "⚡ غيّر الموديل أو بلد البث لأي شاشة LG في ثوانٍ"
sub_en   = "⚡ Change model or broadcast country for any LG TV in seconds"

st.title(title_ar if t_lang == 'ar' else title_en)
st.markdown(f"<h3 style='text-align:center;'>{sub_ar if t_lang == 'ar' else sub_en}</h3>", unsafe_allow_html=True)
st.write("---")

# ──────────────────────────────────────────────────────
# 6. رفع الملف
# ──────────────────────────────────────────────────────
lbl_ar = "📂 ارفع ملف TLL هنا:"
lbl_en = "📂 Upload your TLL file here:"
rst_ar = "🔄 ملف جديد"
rst_en = "🔄 New File"

col_up, col_rst = st.columns([5, 1])
with col_up:
    uploaded = st.file_uploader(
        lbl_ar if t_lang == 'ar' else lbl_en,
        type=["TLL", "bak"],
        key=f"p4_up_{st.session_state.p4_uploader_key}"
    )
with col_rst:
    st.write(""); st.write("")
    if st.button(rst_ar if t_lang == 'ar' else rst_en, key="p4_rst"):
        for k in ['p4_file_bytes','p4_file_name','p4_info','p4_result_bytes','p4_changes','p4_done']:
            st.session_state[k] = None if 'bytes' in k else ({} if k == 'p4_info' else ([] if k == 'p4_changes' else False))
        st.session_state.p4_uploader_key += 1
        st.rerun()

# معالجة الملف
if uploaded:
    fbytes = uploaded.read()
    if st.session_state.p4_file_name != uploaded.name:
        st.session_state.p4_file_bytes  = fbytes
        st.session_state.p4_file_name   = uploaded.name
        st.session_state.p4_info        = parse_tll(fbytes)
        st.session_state.p4_result_bytes = None
        st.session_state.p4_done        = False
        st.session_state.p4_changes     = []

if not st.session_state.p4_file_bytes:
    nf_ar = "⬆️ ارفع ملف TLL للبدء."
    nf_en = "⬆️ Upload a TLL file to start."
    st.info(nf_ar if t_lang == 'ar' else nf_en)
    st.markdown("""<div style="background:#0f172a;border:2px solid #00f0ff;color:white;
    padding:30px;text-align:center;border-radius:15px;margin-top:50px;font-family:Arial;">
    <b>🛠️ DEVELOPER ENG: RAFIK RAMBO</b><br><br>
    📱 +201280339779<br>✉️ rafikrambo113@gmail.com<br><br>
    <a href="https://api.whatsapp.com/send?phone=201280339779" style="color:#25d366;">WhatsApp</a>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ──────────────────────────────────────────────────────
# 7. معلومات الملف
# ──────────────────────────────────────────────────────
info = st.session_state.p4_info
is_modern = info.get('is_modern', False)
type_tag = f"<span class='tag tag-modern'>{'حديث' if t_lang=='ar' else 'Modern'} JSON</span>" if is_modern else f"<span class='tag tag-legacy'>{'قديم' if t_lang=='ar' else 'Legacy'} XML</span>"
country_label = info.get('country_label', info.get('display_country', '?'))

st.markdown("<div class='card'>", unsafe_allow_html=True)
fi_ar = "📊 معلومات الملف الحالي:"
fi_en = "📊 Current File Info:"
st.markdown(f"**{fi_ar if t_lang=='ar' else fi_en}**")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("الموديل" if t_lang=='ar' else "Model", info.get('model','?'))
with c2:
    st.markdown(f"**{'بلد البث' if t_lang=='ar' else 'Country'}**")
    st.markdown(f"<span class='tag tag-country'>{country_label}</span>", unsafe_allow_html=True)
with c3:
    st.markdown(f"**{'نوع الملف' if t_lang=='ar' else 'File Type'}**")
    st.markdown(type_tag, unsafe_allow_html=True)
with c4:
    st.metric("القنوات" if t_lang=='ar' else "Channels", f"{info.get('ch_count',0):,}")

# تفاصيل البلد للملف الحديث
if is_modern:
    st.markdown("---")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f"**BroadcastCountry:** `{info.get('broadcast_country','—')}`")
    with d2:
        st.markdown(f"**country (XML):** `{info.get('country_xml','—')}`")
    with d3:
        st.markdown(f"**country (JSON):** `{info.get('country_json','—')}`")

st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# ──────────────────────────────────────────────────────
# 8. خيارات التحويل
# ──────────────────────────────────────────────────────
sec_ar = "⚙️ اختر التحويل المطلوب"
sec_en = "⚙️ Choose Conversion"
st.markdown(f"### <span class='badge'>2</span> {sec_ar if t_lang=='ar' else sec_en}", unsafe_allow_html=True)

col_m, col_c = st.columns(2)

# ── تغيير الموديل ──
with col_m:
    mod_ar = "🖥️ تغيير الموديل"
    mod_en = "🖥️ Change Model"
    st.markdown(f"#### {mod_ar if t_lang=='ar' else mod_en}")
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    model_opts = ["— " + ("الاحتفاظ بنفس الموديل" if t_lang=='ar' else "Keep same model") + " —"] + LG_MODELS
    sel_model = st.selectbox(
        "اختر من القائمة:" if t_lang=='ar' else "Select from list:",
        options=model_opts, key="p4_sel_model"
    )
    manual_model = st.text_input(
        "أو اكتب يدوياً:" if t_lang=='ar' else "Or type manually:",
        placeholder="مثال: 55UN7340PVA",
        key="p4_man_model"
    ).strip()

    final_model = manual_model if manual_model else (
        sel_model if not sel_model.startswith("—") else ""
    )
    if final_model:
        if final_model == info.get('model',''):
            st.info("ℹ️ " + ("نفس الموديل الحالي" if t_lang=='ar' else "Same as current"))
        else:
            st.success(f"✅ {'سيتغير إلى' if t_lang=='ar' else 'Will change to'}: **{final_model}**")
    st.markdown("</div>", unsafe_allow_html=True)

# ── تغيير البلد ──
with col_c:
    ctr_ar = "🌍 تغيير بلد البث"
    ctr_en = "🌍 Change Broadcast Country"
    st.markdown(f"#### {ctr_ar if t_lang=='ar' else ctr_en}")
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    country_opts = ["— " + ("الاحتفاظ بنفس البلد" if t_lang=='ar' else "Keep same country") + " —"] + list(COUNTRIES.keys())
    sel_country = st.selectbox(
        "اختر البلد الجديد:" if t_lang=='ar' else "Select new country:",
        options=country_opts, key="p4_sel_country"
    )
    final_country = sel_country if not sel_country.startswith("—") else ""

    if final_country and final_country in COUNTRIES:
        cd = COUNTRIES[final_country]
        if is_modern:
            st.success(
                f"✅ **{final_country}**\n\n"
                f"BroadcastCountry → `{cd['code3']}`  |  JSON → `{cd['full']}`"
            )
        else:
            old_len = len(info.get('country_xml', 'XX'))
            nc = cd['code2'] if old_len <= 2 else cd['code3']
            st.success(f"✅ **{final_country}** → `{nc}`")

    # ملحوظة مهمة
    if is_modern:
        st.markdown(
            f"<div style='color:#ffc107;font-size:0.82rem;margin-top:8px;'>"
            f"{'⚠️ في الملفات الحديثة: country(XML) ستبقى JA — هذا طبيعي ويضمن قبول الملف' if t_lang=='ar' else '⚠️ Modern files: country(XML) stays JA — this is correct and ensures TV accepts the file'}"
            f"</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ── زر التحويل ──
col_btn, _, _ = st.columns([2,1,1])
with col_btn:
    btn_ar = "🔄 تحويل الآن"
    btn_en = "🔄 Convert Now"
    warn_ar = "⚠️ اختر تغيير الموديل أو البلد أولاً!"
    warn_en = "⚠️ Please select a model or country change first!"

    if st.button(btn_ar if t_lang=='ar' else btn_en, use_container_width=True):
        if not final_model and not final_country:
            st.warning(warn_ar if t_lang=='ar' else warn_en)
        else:
            res_bytes, changes = convert_tll(info, final_model, final_country)
            st.session_state.p4_result_bytes = res_bytes
            st.session_state.p4_changes      = changes
            st.session_state.p4_done         = True
            st.rerun()

# ──────────────────────────────────────────────────────
# 9. النتيجة والتحميل
# ──────────────────────────────────────────────────────
if st.session_state.p4_done and st.session_state.p4_result_bytes:
    st.write("---")
    done_ar = "✅ الخطوة 3: تحميل الملف المحوّل"
    done_en = "✅ Step 3: Download Converted File"
    st.markdown(f"### <span class='badge'>3</span> {done_ar if t_lang=='ar' else done_en}", unsafe_allow_html=True)

    suc_ar = "🎉 تم التحويل بنجاح! الملف جاهز."
    suc_en = "🎉 Conversion successful! File ready."
    st.success(suc_ar if t_lang=='ar' else suc_en)

    # التغييرات
    changes = st.session_state.p4_changes
    if changes:
        ch_ar = "📝 التغييرات المطبّقة:"
        ch_en = "📝 Changes Applied:"
        st.markdown(f"**{ch_ar if t_lang=='ar' else ch_en}**")
        for ch in changes:
            if ch[0] == 'model':
                label = "🖥️ الموديل" if t_lang=='ar' else "🖥️ Model"
                st.markdown(
                    f"<div class='change-row'>{label}: "
                    f"<code>{ch[1]}</code> <span style='color:#ff007f;font-weight:bold;'>➜</span> "
                    f"<code style='color:#00f0ff;'>{ch[2]}</code></div>",
                    unsafe_allow_html=True
                )
            elif ch[0] == 'country':
                label = "🌍 بلد البث" if t_lang=='ar' else "🌍 Country"
                country_name = ch[3] if len(ch) > 3 else ch[2]
                st.markdown(
                    f"<div class='change-row'>{label}: "
                    f"<code>{ch[1]}</code> <span style='color:#ff007f;font-weight:bold;'>➜</span> "
                    f"<code style='color:#00f0ff;'>{ch[2]}</code> ({country_name})</div>",
                    unsafe_allow_html=True
                )
    else:
        nc_ar = "ℹ️ لم يتم تغيير أي قيمة (القيم الجديدة مطابقة للقديمة)."
        nc_en = "ℹ️ No values changed (new values match existing ones)."
        st.info(nc_ar if t_lang=='ar' else nc_en)

    st.write("")

    # أزرار التحميل
    col_d1, col_d2 = st.columns([3,1])
    with col_d1:
        dl_ar = "📥 تحميل الملف المحوّل (GlobalClone00001.TLL)"
        dl_en = "📥 Download Converted File (GlobalClone00001.TLL)"
        st.download_button(
            label=dl_ar if t_lang=='ar' else dl_en,
            data=st.session_state.p4_result_bytes,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream",
            use_container_width=True,
        )
    with col_d2:
        nr_ar = "🔄 ملف جديد"
        nr_en = "🔄 New File"
        if st.button(nr_ar if t_lang=='ar' else nr_en, key="p4_rst2"):
            for k in ['p4_file_bytes','p4_file_name','p4_result_bytes','p4_changes','p4_done']:
                st.session_state[k] = None if 'bytes' in k else ([] if k == 'p4_changes' else False)
            st.session_state.p4_info = {}
            st.session_state.p4_uploader_key += 1
            st.rerun()

    # ملحوظة LG
    tip_title_ar = "💡 ملحوظة مهمة بعد تحميل الملف على الشاشة:"
    tip_title_en = "💡 Important note after loading file on TV:"
    tip_text_ar  = "إذا لم تظهر القنوات بشكل صحيح، اذهب إلى: إعدادات ← القنوات ← مدير القنوات ← تعديل كل القنوات ← تحديد الكل ← استعادة"
    tip_text_en  = "If channels don't appear correctly: Settings → Channels → Channel Manager → Edit All Channels → Select All → Restore"
    st.markdown(f"""
<div style="background:rgba(255,193,7,0.1);border:2px solid #ffc107;border-radius:14px;
padding:20px;margin-top:20px;">
<b style="color:#ffc107;">{tip_title_ar if t_lang=='ar' else tip_title_en}</b><br><br>
<span style="line-height:1.8;">{tip_text_ar if t_lang=='ar' else tip_text_en}</span>
</div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 10. FOOTER
# ──────────────────────────────────────────────────────
st.markdown("""
<div style="background:#0f172a;border:2px solid #00f0ff;color:#ffffff;
padding:35px;text-align:center;border-radius:20px;margin-top:65px;font-family:Arial;">
<div style="color:#ff007f;font-size:26px;font-weight:bold;">🛠️ DEVELOPER ENG: RAFIK NATHAN</div>
<div style="margin-top:10px;">📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
<div style="margin-top:10px;">✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com</div>
<a href="https://api.whatsapp.com/send?phone=201280339779" target="_blank"
style="color:#25d366;padding:14px 35px;border-radius:35px;display:inline-block;
font-weight:bold;border:2px solid #25d366;text-decoration:none;margin-top:20px;">
WhatsApp</a>
</div>
""", unsafe_allow_html=True)
