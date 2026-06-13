import streamlit as st
import re
import json

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
# 2. بيانات
# ──────────────────────────────────────────────────────
COUNTRIES = {
    "🇪🇬 مصر":        {"code3": "EGY", "full": "Egypt"},
    "🇸🇦 السعودية":   {"code3": "SAU", "full": "Saudi Arabia"},
    "🇦🇪 الإمارات":   {"code3": "ARE", "full": "United Arab Emirates"},
    "🇯🇴 الأردن":     {"code3": "JOR", "full": "Jordan"},
    "🇱🇧 لبنان":      {"code3": "LBN", "full": "Lebanon"},
    "🇸🇩 السودان":    {"code3": "SDN", "full": "Sudan"},
    "🇩🇿 الجزائر":    {"code3": "DZA", "full": "Algeria"},
    "🇲🇦 المغرب":     {"code3": "MAR", "full": "Morocco"},
    "🇹🇳 تونس":       {"code3": "TUN", "full": "Tunisia"},
    "🇱🇾 ليبيا":      {"code3": "LBY", "full": "Libya"},
    "🇮🇶 العراق":     {"code3": "IRQ", "full": "Iraq"},
    "🇸🇾 سوريا":      {"code3": "SYR", "full": "Syria"},
    "🇾🇪 اليمن":      {"code3": "YEM", "full": "Yemen"},
    "🇰🇼 الكويت":     {"code3": "KWT", "full": "Kuwait"},
    "🇶🇦 قطر":        {"code3": "QAT", "full": "Qatar"},
    "🇧🇭 البحرين":    {"code3": "BHR", "full": "Bahrain"},
    "🇴🇲 عُمان":      {"code3": "OMN", "full": "Oman"},
    "🇵🇸 فلسطين":     {"code3": "PSE", "full": "Palestine"},
    "🌐 عالمي (JA)":  {"code3": "JA",  "full": "Japan"},
}

CODE_TO_LABEL = {}
for label, d in COUNTRIES.items():
    CODE_TO_LABEL[d["code3"].upper()] = label
    CODE_TO_LABEL[d["full"].upper()]  = label

LG_MODELS = sorted([
    "65UR78006LL","65UR78006LK","55UR78006LK","43UR78006LK","75UR78006LK",
    "65UR80006LJ","55UR80006LJ","43UR80006LJ","50UR80006LJ","75UR80006LJ",
    "65UP80006LR","55UP80006LR","43UP80006LR","50UP80006LR","75UP80006LR",
    "OLED65G4PSA","OLED55C4PSA","OLED77C4PSA","OLED65C3PSA","OLED55C3PSA",
    "OLED65CX6LA","OLED55CX6LA","OLED65C2PSA","OLED55C2PSA",
    "65QNED85T6A","55QNED80T6A","65QNED85VPA","55QNED85VPA",
    "65UQ80006LB","55UQ80006LB","50UQ80006LB","43UQ80006LB",
    "65NANO86VPA","55NANO86VPA","65NANO75VPA","55NANO75VPA",
    "55UA85006LA.DFUYLWE","65UA80006LA","75UA80006LA",
    "32LQ63806LC","43LQ63006LA","50LQ63006LA","32LQ630BPSA","43LQ630BPSA",
    "65SM9010PLA","55SM9010PLA","65SK8500PLA","55SK8500PLA",
    "43UK6300PLB","49UK6300PLB","55UK6300PLB","65UK6300PLB",
    "32LK6100PLB","43LK6100PLB","49LK6100PLB","55LK6100PLB",
    "32LM550BPVA","43LM5500PLA","49LM5500PLA","55LM5500PLA",
    "32LH604U-TB","43LH604V","49LH604V","55LH604V",
    "32LH570U","43LH570V","49LH570V","55LH570V",
    "32LH530V","43LH530V","49LH530V",
    "65UH950V","55UH950V","49UH850V","43UH850V",
])

# ──────────────────────────────────────────────────────
# 3. Parse + Convert
# ──────────────────────────────────────────────────────
def parse_tll(file_bytes):
    try:
        txt = file_bytes.decode('utf-8', errors='ignore')
    except:
        txt = file_bytes.decode('latin-1', errors='ignore')

    info = {'txt': txt}
    info['is_modern'] = 'legacybroadcast' in txt

    m = re.search(r'<ModelName[^>]*>([^<]+)</ModelName>', txt)
    info['model'] = m.group(1).strip() if m else ""

    m = re.search(r'<BroadcastCountrySetting[^>]*>([^<]+)</BroadcastCountrySetting>', txt)
    info['broadcast'] = m.group(1).strip() if m else ""

    m = re.search(r'<country[^>]*>([^<]+)</country>', txt)
    info['country_xml'] = m.group(1).strip() if m else ""

    info['country_json'] = ""
    if info['is_modern']:
        jm = re.search(r'<legacybroadcast>(.*?)</legacybroadcast>', txt, re.DOTALL)
        if jm:
            try:
                data = json.loads(jm.group(1))
                info['country_json'] = data.get('modelInfo', {}).get('country', '')
                info['ch_count'] = len(data.get('channelList', []))
            except:
                info['ch_count'] = len(re.findall(r'"channelName"', txt))
        else:
            info['ch_count'] = 0
    else:
        info['ch_count'] = len(re.findall(r'<ITEM>', txt))

    # البلد المعروض
    display = info['broadcast'] or info['country_json'] or info['country_xml']
    info['display_country'] = display
    info['country_label'] = CODE_TO_LABEL.get(display.upper(), display)

    # MajorVersion
    m = re.search(r'<MajorVersion>([^<]+)</MajorVersion>', txt)
    info['major_ver'] = m.group(1).strip() if m else "?"

    return info


def convert_tll(info, new_model, new_country_name):
    txt = info['txt']
    changes = []
    is_modern = info['is_modern']

    # ── تغيير الموديل ──
    if new_model and new_model.strip() and new_model.strip() != info['model']:
        old = info['model']
        new = new_model.strip()
        txt = re.sub(
            r'(<ModelName[^>]*>)([^<]+)(</ModelName>)',
            lambda m: m.group(1) + new + m.group(3), txt
        )
        changes.append(('model', old, new))

    # ── تغيير البلد ──
    if new_country_name and new_country_name in COUNTRIES:
        cd = COUNTRIES[new_country_name]
        old_display = info['display_country']

        if is_modern:
            # 1. BroadcastCountrySetting → code3
            if info['broadcast']:
                txt = re.sub(
                    r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                    lambda m: m.group(1) + cd['code3'] + m.group(3), txt
                )
            else:
                txt = txt.replace(
                    '</ModelInfo>',
                    f'<BroadcastCountrySetting type="0">{cd["code3"]}</BroadcastCountrySetting>\n</ModelInfo>'
                )

            # 2. country JSON → full name
            def fix_json(match):
                try:
                    data = json.loads(match.group(1))
                    if 'modelInfo' not in data:
                        data['modelInfo'] = {}
                    data['modelInfo']['country'] = cd['full']
                    return '<legacybroadcast>' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '</legacybroadcast>'
                except:
                    return match.group(0)
            txt = re.sub(r'<legacybroadcast>(.*?)</legacybroadcast>', fix_json, txt, flags=re.DOTALL)

            # 3. country XML → نسيبها JA (مهم جداً لقبول الشاشة للملف)

            new_display = cd['code3']

        else:
            # Legacy XML
            if info['broadcast']:
                txt = re.sub(
                    r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                    lambda m: m.group(1) + cd['code3'] + m.group(3), txt
                )
            # country XML
            old_len = len(info['country_xml'])
            new_code = cd['code3'][:2] if old_len <= 2 and len(cd['code3']) > 2 else cd['code3']
            txt = re.sub(
                r'(<country[^>]*>)([^<]+)(</country>)',
                lambda m: m.group(1) + new_code + m.group(3), txt
            )
            new_display = new_code

        if old_display.upper() != new_display.upper():
            changes.append(('country', old_display, new_display, new_country_name))

    return txt.encode('utf-8'), changes

# ──────────────────────────────────────────────────────
# 4. CSS & Page Config
# ──────────────────────────────────────────────────────
st.set_page_config(page_title="RAMBO P4 — Converter", page_icon="🔄", layout="wide")

col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("🌐 English" if st.session_state.lang == 'ar' else "🌐 العربية"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
        st.rerun()
with col_theme:
    if st.button("☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

dk = st.session_state.theme == 'dark'
bg   = "radial-gradient(circle at 50% 50%,#110926 0%,#05020d 100%)" if dk else "radial-gradient(circle at 50% 50%,#f4f5f7 0%,#e4e7eb 100%)"
tc   = "#00f0ff" if dk else "#0d0722"
bb   = "rgba(13,7,33,0.85)" if dk else "#ffffff"
bord = "#00f0ff" if dk else "#ff007f"
bsh  = "rgba(0,240,255,0.35)" if dk else "rgba(255,0,127,0.15)"
tsh  = "0 0 5px rgba(0,240,255,0.4)" if dk else "none"
ff   = "'Cairo',sans-serif" if st.session_state.lang == 'ar' else "'Orbitron',sans-serif"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
.main{{background:{bg}!important;color:{tc}!important;font-family:{ff};}}
h1{{color:#ff007f!important;text-shadow:0 0 10px #ff007f,0 0 25px rgba(255,0,127,0.4)!important;
    text-align:center;font-weight:900;margin-top:5px;}}
h3,p,label,.stMarkdown,div[data-testid="stMarkdownContainer"] p{{color:{tc}!important;text-shadow:{tsh};}}
.stTextInput>div>div>input,.stSelectbox>div>div{{
    background-color:{bb}!important;color:{tc}!important;
    border:2px solid {bord}!important;border-radius:10px!important;}}
div[data-testid="stFileUploader"]{{
    background:{bb}!important;border:2px solid {bord}!important;
    box-shadow:0 5px 15px {bsh}!important;border-radius:14px!important;
    padding:18px!important;margin-bottom:20px!important;}}
.stButton>button{{
    background:linear-gradient(135deg,#ff007f 0%,#aa0055 100%)!important;
    color:#fff!important;border:2px solid #ff007f!important;
    border-radius:12px!important;font-weight:bold;width:100%;}}
.stDownloadButton>button{{
    background:linear-gradient(135deg,#00b894 0%,#00695c 100%)!important;
    color:#fff!important;border:none!important;border-radius:12px!important;
    font-weight:bold;width:100%;}}
.card{{background:{bb};border:2px solid {bord};box-shadow:0 5px 15px {bsh};
       border-radius:14px;padding:20px;margin-bottom:16px;}}
.badge{{display:inline-block;background:linear-gradient(135deg,#ff007f,#aa0055);
        color:white;border-radius:50%;width:30px;height:30px;text-align:center;
        line-height:30px;font-weight:bold;margin:0 8px;}}
.change-box{{background:rgba(0,240,255,0.08);border-left:4px solid #00f0ff;
             border-radius:8px;padding:12px 16px;margin:6px 0;}}
.warn-box{{background:rgba(255,193,7,0.1);border:2px solid #ffc107;
           border-radius:12px;padding:16px;margin-top:16px;}}
.info-tag{{display:inline-block;padding:3px 10px;border-radius:6px;font-size:0.85rem;
           font-weight:bold;margin:2px;}}
.t-modern{{background:rgba(0,240,255,0.15);border:1px solid #00f0ff;color:#00f0ff;}}
.t-legacy{{background:rgba(255,165,0,0.15);border:1px solid orange;color:orange;}}
.t-country{{background:rgba(255,0,127,0.15);border:1px solid #ff007f;color:#ff007f;}}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 5. العنوان
# ──────────────────────────────────────────────────────
ar = st.session_state.lang == 'ar'
st.title("🔄 RAMBO — محوّل ملفات TLL" if ar else "🔄 RAMBO — TLL File Converter")
st.markdown(f"<h3 style='text-align:center;'>{'⚡ غيّر الموديل أو بلد البث — يحل مشكلة Cloning Error 8' if ar else '⚡ Change model or broadcast country — fixes Cloning Error 8'}</h3>", unsafe_allow_html=True)
st.write("---")

# ──────────────────────────────────────────────────────
# 6. رفع الملف
# ──────────────────────────────────────────────────────
col_up, col_rst = st.columns([5, 1])
with col_up:
    uploaded = st.file_uploader(
        "📂 ارفع ملف TLL هنا:" if ar else "📂 Upload TLL file:",
        type=["TLL","bak"],
        key=f"p4_up_{st.session_state.p4_uploader_key}"
    )
with col_rst:
    st.write(""); st.write("")
    if st.button("🔄 ملف جديد" if ar else "🔄 New File", key="p4_rst_top"):
        for k in ['p4_file_bytes','p4_file_name','p4_result_bytes','p4_changes','p4_done']:
            st.session_state[k] = None if 'bytes' in k else ([] if 'changes' in k else False)
        st.session_state.p4_info = {}
        st.session_state.p4_uploader_key += 1
        st.rerun()

if uploaded:
    fbytes = uploaded.read()
    if st.session_state.p4_file_name != uploaded.name:
        st.session_state.p4_file_bytes   = fbytes
        st.session_state.p4_file_name    = uploaded.name
        st.session_state.p4_info         = parse_tll(fbytes)
        st.session_state.p4_result_bytes = None
        st.session_state.p4_done         = False
        st.session_state.p4_changes      = []

if not st.session_state.p4_file_bytes:
    st.info("⬆️ ارفع ملف TLL للبدء." if ar else "⬆️ Upload a TLL file to start.")
    st.markdown("""<div style="background:#0f172a;border:2px solid #00f0ff;color:white;
    padding:30px;text-align:center;border-radius:15px;margin-top:40px;font-family:Arial;">
    <b>🛠️ DEVELOPER ENG: RAFIK RAMBO</b><br><br>
    📱 +201280339779 | ✉️ rafikrambo113@gmail.com<br><br>
    <a href="https://api.whatsapp.com/send?phone=201280339779" style="color:#25d366;">WhatsApp</a>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ──────────────────────────────────────────────────────
# 7. معلومات الملف
# ──────────────────────────────────────────────────────
info = st.session_state.p4_info
is_modern = info.get('is_modern', False)

type_tag = f"<span class='info-tag t-modern'>{'حديث' if ar else 'Modern'} JSON</span>" if is_modern else f"<span class='info-tag t-legacy'>{'قديم' if ar else 'Legacy'} XML</span>"
country_label = info.get('country_label', info.get('display_country','?'))

st.markdown(f"### <span class='badge'>1</span> {'معلومات الملف الحالي' if ar else 'Current File Info'}", unsafe_allow_html=True)
st.markdown("<div class='card'>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("الموديل" if ar else "Model", info.get('model','?'))
with c2:
    st.markdown(f"**{'بلد البث' if ar else 'Country'}**")
    st.markdown(f"<span class='info-tag t-country'>{country_label} ({info.get('display_country','')})</span>", unsafe_allow_html=True)
with c3:
    st.markdown(f"**{'نوع الملف' if ar else 'File Type'}**")
    st.markdown(type_tag, unsafe_allow_html=True)
with c4:
    st.metric("القنوات" if ar else "Channels", f"{info.get('ch_count',0):,}")

# تفاصيل الأماكن الثلاثة
if is_modern:
    st.markdown("---")
    st.markdown(f"**{'📍 أماكن البلد في الملف (3 أماكن):' if ar else '📍 Country locations in file (3 places):'}**")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f"**BroadcastCountrySetting:**  \n`{info.get('broadcast','—')}`")
    with d2:
        st.markdown(f"**country (XML):**  \n`{info.get('country_xml','—')}` ← {'يبقى JA دائماً' if ar else 'stays JA always'}")
    with d3:
        st.markdown(f"**country (JSON):**  \n`{info.get('country_json','—')}`")
else:
    st.markdown("---")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"**BroadcastCountrySetting:**  \n`{info.get('broadcast','—')}`")
    with d2:
        st.markdown(f"**country (XML):**  \n`{info.get('country_xml','—')}`")

st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# ──────────────────────────────────────────────────────
# 8. خيارات التحويل
# ──────────────────────────────────────────────────────
st.markdown(f"### <span class='badge'>2</span> {'اختر التحويل' if ar else 'Choose Conversion'}", unsafe_allow_html=True)

col_m, col_c = st.columns(2)

with col_m:
    st.markdown(f"#### {'🖥️ تغيير الموديل' if ar else '🖥️ Change Model'}")
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    keep_model = "— " + ("الاحتفاظ بالموديل الحالي" if ar else "Keep current model") + " —"
    sel_model = st.selectbox(
        "اختر من القائمة:" if ar else "Select from list:",
        options=[keep_model] + LG_MODELS, key="p4_sel_model"
    )
    manual_model = st.text_input(
        "أو اكتب الموديل يدوياً:" if ar else "Or type model manually:",
        placeholder="e.g. 55UN7340PVA", key="p4_man_model"
    ).strip()

    final_model = manual_model if manual_model else (
        "" if sel_model == keep_model else sel_model
    )

    if final_model:
        if final_model == info.get('model',''):
            st.info("ℹ️ " + ("نفس الموديل الحالي" if ar else "Same as current model"))
        else:
            st.success(f"✅ {'سيتغير إلى' if ar else 'Will change to'}: **{final_model}**")

    st.markdown("</div>", unsafe_allow_html=True)

with col_c:
    st.markdown(f"#### {'🌍 تغيير بلد البث' if ar else '🌍 Change Broadcast Country'}")
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    keep_country = "— " + ("الاحتفاظ ببلد البث الحالي" if ar else "Keep current country") + " —"
    sel_country = st.selectbox(
        "اختر البلد الجديد:" if ar else "Select new country:",
        options=[keep_country] + list(COUNTRIES.keys()), key="p4_sel_country"
    )
    final_country = "" if sel_country == keep_country else sel_country

    if final_country and final_country in COUNTRIES:
        cd = COUNTRIES[final_country]
        if is_modern:
            st.success(
                f"✅ **{final_country}**\n\n"
                f"• BroadcastCountrySetting → `{cd['code3']}`\n\n"
                f"• country JSON → `{cd['full']}`\n\n"
                f"• country XML → `JA` ({'يبقى كما هو' if ar else 'stays as is'})"
            )
        else:
            st.success(f"✅ **{final_country}** → `{cd['code3']}`")

    # تحذير Cloning Error
    st.markdown(
        f"<div class='warn-box'>"
        f"<b style='color:#ffc107;'>⚠️ {'حل مشكلة Cloning Error 8:' if ar else 'Fix Cloning Error 8:'}</b><br>"
        f"<span style='font-size:0.88rem;'>"
        f"{'اختر نفس بلد البث المضبوط على شاشتك.' if ar else 'Select the same country set on your TV.'}"
        f"</span></div>",
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
col_btn, _, _ = st.columns([2,1,1])
with col_btn:
    if st.button("🔄 " + ("تحويل الآن" if ar else "Convert Now"), use_container_width=True):
        if not final_model and not final_country:
            st.warning("⚠️ " + ("اختر تغيير الموديل أو البلد أولاً!" if ar else "Select a model or country change first!"))
        else:
            res_bytes, changes = convert_tll(info, final_model, final_country)
            st.session_state.p4_result_bytes = res_bytes
            st.session_state.p4_changes      = changes
            st.session_state.p4_done         = True
            st.rerun()

# ──────────────────────────────────────────────────────
# 9. النتيجة
# ──────────────────────────────────────────────────────
if st.session_state.p4_done and st.session_state.p4_result_bytes:
    st.write("---")
    st.markdown(f"### <span class='badge'>3</span> {'تحميل الملف المحوّل' if ar else 'Download Converted File'}", unsafe_allow_html=True)
    st.success("🎉 " + ("تم التحويل بنجاح! الملف جاهز." if ar else "Conversion successful! File ready."))

    changes = st.session_state.p4_changes
    if changes:
        st.markdown(f"**{'📝 التغييرات:' if ar else '📝 Changes:'}**")
        for ch in changes:
            if ch[0] == 'model':
                st.markdown(
                    f"<div class='change-box'>🖥️ {'الموديل' if ar else 'Model'}: "
                    f"<code>{ch[1]}</code> <b style='color:#ff007f;'>➜</b> "
                    f"<code style='color:#00f0ff;'>{ch[2]}</code></div>",
                    unsafe_allow_html=True
                )
            elif ch[0] == 'country':
                st.markdown(
                    f"<div class='change-box'>🌍 {'بلد البث' if ar else 'Country'}: "
                    f"<code>{ch[1]}</code> <b style='color:#ff007f;'>➜</b> "
                    f"<code style='color:#00f0ff;'>{ch[2]}</code> ({ch[3] if len(ch)>3 else ''})</div>",
                    unsafe_allow_html=True
                )
    else:
        st.info("ℹ️ " + ("لم يتم تغيير أي قيمة." if ar else "No values changed."))

    st.write("")
    col_d1, col_d2 = st.columns([3,1])
    with col_d1:
        st.download_button(
            label="📥 " + ("تحميل الملف المحوّل (GlobalClone00001.TLL)" if ar else "Download Converted File (GlobalClone00001.TLL)"),
            data=st.session_state.p4_result_bytes,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream",
            use_container_width=True,
        )
    with col_d2:
        if st.button("🔄 " + ("ملف جديد" if ar else "New File"), key="p4_rst_bot"):
            for k in ['p4_file_bytes','p4_file_name','p4_result_bytes','p4_changes','p4_done']:
                st.session_state[k] = None if 'bytes' in k else ([] if 'changes' in k else False)
            st.session_state.p4_info = {}
            st.session_state.p4_uploader_key += 1
            st.rerun()

    st.markdown(f"""
<div class='warn-box'>
<b style='color:#ffc107;'>💡 {'ملحوظة مهمة بعد التحميل على الشاشة:' if ar else 'Important note after loading on TV:'}</b><br>
<span style='font-size:0.88rem;line-height:1.8;'>
{'إذا ظهر خطأ أو لم تظهر القنوات: اذهب إلى إعدادات ← القنوات ← مدير القنوات ← تعديل كل القنوات ← تحديد الكل ← استعادة' if ar else 'If error appears or channels missing: Settings → Channels → Channel Manager → Edit All Channels → Select All → Restore'}
</span></div>""", unsafe_allow_html=True)

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
font-weight:bold;border:2px solid #25d366;text-decoration:none;margin-top:20px;">WhatsApp</a>
</div>""", unsafe_allow_html=True)
