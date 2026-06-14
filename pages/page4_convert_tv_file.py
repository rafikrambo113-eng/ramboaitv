import streamlit as st
import re
import json

# ──────────────────────────────────────────────────────
# 1. SESSION STATE
# ──────────────────────────────────────────────────────
for key, val in {
    'lang': 'ar',
    'theme': 'dark',
    'p4_src_bytes': None,
    'p4_src_name': None,
    'p4_src_info': {},
    'p4_ref_bytes': None,
    'p4_ref_name': None,
    'p4_ref_info': {},
    'p4_result_bytes': None,
    'p4_changes': [],
    'p4_done': False,
    'p4_src_key': 0,
    'p4_ref_key': 0,
    'p4_mode': 'simple',  # simple = بلد/موديل فقط | convert = تحويل قديم/حديث
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
    "65NANO86VPA","55NANO86VPA",
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
# 3. دوال
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

    m = re.search(r'<MajorVersion>([^<]+)</MajorVersion>', txt)
    info['major_ver'] = m.group(1).strip() if m else "?"

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
        info['ch_count'] = len(re.findall(r'<ITEM>', txt))

    display = info['broadcast'] or info['country_json'] or info['country_xml']
    info['display_country'] = display
    info['country_label'] = CODE_TO_LABEL.get(display.upper(), display)
    return info


def change_country_model(info, new_model, new_country_name):
    """تغيير الموديل و/أو البلد فقط"""
    txt = info['txt']
    changes = []
    is_modern = info['is_modern']

    if new_model and new_model.strip() and new_model.strip() != info['model']:
        old = info['model']
        txt = re.sub(r'(<ModelName[^>]*>)([^<]+)(</ModelName>)',
                     lambda m: m.group(1) + new_model.strip() + m.group(3), txt)
        changes.append(('model', old, new_model.strip()))

    if new_country_name and new_country_name in COUNTRIES:
        cd = COUNTRIES[new_country_name]
        old_display = info['display_country']

        if is_modern:
            if info['broadcast']:
                txt = re.sub(r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                             lambda m: m.group(1) + cd['code3'] + m.group(3), txt)
            else:
                txt = txt.replace('</ModelInfo>',
                    f'<BroadcastCountrySetting type="0">{cd["code3"]}</BroadcastCountrySetting>\n</ModelInfo>')

            def fix_json(match):
                try:
                    data = json.loads(match.group(1))
                    if 'modelInfo' not in data: data['modelInfo'] = {}
                    data['modelInfo']['country'] = cd['full']
                    return '<legacybroadcast>' + json.dumps(data, ensure_ascii=False, separators=(',',':')) + '</legacybroadcast>'
                except: return match.group(0)
            txt = re.sub(r'<legacybroadcast>(.*?)</legacybroadcast>', fix_json, txt, flags=re.DOTALL)
            new_display = cd['code3']
        else:
            if info['broadcast']:
                txt = re.sub(r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                             lambda m: m.group(1) + cd['code3'] + m.group(3), txt)
            old_len = len(info['country_xml'])
            new_code = cd['code3'][:2] if old_len <= 2 and len(cd['code3']) > 2 else cd['code3']
            txt = re.sub(r'(<country[^>]*>)([^<]+)(</country>)',
                         lambda m: m.group(1) + new_code + m.group(3), txt)
            new_display = new_code

        if old_display.upper() != new_display.upper():
            changes.append(('country', old_display, new_display, new_country_name))

    return txt.encode('utf-8'), changes


def convert_modern_to_legacy(src_info, ref_info, new_model, new_country_name):
    """تحويل ملف حديث Modern لـ Legacy باستخدام ملف مرجعي شغال"""
    txt_ref = ref_info['txt']
    changes = []

    # القنوات من الملف الحديث
    jm = re.search(r'<legacybroadcast>(.*?)</legacybroadcast>', src_info['txt'], re.DOTALL)
    data = json.loads(jm.group(1))
    channels = data['channelList']

    # الـ ITEMs الشغالة من الملف المرجعي
    items_ref = re.findall(r'<ITEM>(.*?)</ITEM>', txt_ref, re.DOTALL)

    # map تردد → ITEM template
    freq_to_item = {}
    for item in items_ref:
        freq_m = re.search(r'<frequency>([^<]+)</frequency>', item)
        if freq_m:
            freq = freq_m.group(1).strip()
            if freq not in freq_to_item:
                freq_to_item[freq] = item

    # بناء القنوات
    new_items = []
    skipped = 0
    for idx, ch in enumerate(channels, start=1):
        name = ch.get('channelName', 'Unknown')
        freq = str(ch.get('frequency', ''))

        if freq in freq_to_item:
            item = freq_to_item[freq]
            item = re.sub(r'<prNum>[^<]+</prNum>', f'<prNum>{idx}</prNum>', item)
            name_hex = name.encode('utf-8').hex()
            name_len = len(name)
            item = re.sub(r'<hexVchName>[^<]+</hexVchName>', f'<hexVchName>{name_hex}</hexVchName>', item)
            item = re.sub(r'<notConvertedLengthOfVchName>[^<]+</notConvertedLengthOfVchName>',
                          f'<notConvertedLengthOfVchName>{name_len}</notConvertedLengthOfVchName>', item)
            item = re.sub(r'<vchName>[^<]+</vchName>', f'<vchName>{name}</vchName>', item)
            item = re.sub(r'<lengthOfVchName>[^<]+</lengthOfVchName>',
                          f'<lengthOfVchName>{name_len}</lengthOfVchName>', item)
            new_items.append('<ITEM>' + item + '</ITEM>')
        else:
            skipped += 1

    # دمج في الملف المرجعي
    combined = '\r\n'.join(new_items)
    start_i = txt_ref.find('<ITEM>')
    end_i   = txt_ref.rfind('</ITEM>') + len('</ITEM>')
    new_txt = txt_ref[:start_i] + combined + txt_ref[end_i:]

    # تغيير الموديل
    target_model = new_model.strip() if new_model and new_model.strip() else src_info['model']
    new_txt = re.sub(r'(<ModelName[^>]*>)([^<]+)(</ModelName>)',
                     lambda m: m.group(1) + target_model + m.group(3), new_txt)
    changes.append(('model', ref_info['model'], target_model))

    # تغيير البلد
    if new_country_name and new_country_name in COUNTRIES:
        cd = COUNTRIES[new_country_name]
        new_txt = re.sub(r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                         lambda m: m.group(1) + cd['code3'] + m.group(3), new_txt)
        old_bc = re.search(r'<BroadcastCountrySetting[^>]*>([^<]+)</BroadcastCountrySetting>', txt_ref)
        old_code = old_bc.group(1) if old_bc else '?'
        changes.append(('country', old_code, cd['code3'], new_country_name))
    
    changes.append(('converted', len(new_items), skipped))

    return new_txt.encode('utf-8'), changes


def convert_legacy_to_modern(src_info, ref_info, new_model, new_country_name):
    """تحويل ملف قديم Legacy لـ Modern باستخدام ملف مرجعي شغال"""
    txt_ref = ref_info['txt']
    changes = []

    # القنوات من الملف القديم
    items_src = re.findall(r'<ITEM>(.*?)</ITEM>', src_info['txt'], re.DOTALL)

    # JSON من الملف المرجعي الحديث
    jm = re.search(r'<legacybroadcast>(.*?)</legacybroadcast>', txt_ref, re.DOTALL)
    data_ref = json.loads(jm.group(1))
    ref_channels = data_ref.get('channelList', [])

    # map تردد → channel template من المرجعي
    freq_to_ch = {}
    for ch in ref_channels:
        freq = str(ch.get('frequency', ''))
        if freq not in freq_to_ch:
            freq_to_ch[freq] = ch

    # بناء القنوات الجديدة
    new_channels = []
    skipped = 0
    import base64

    for idx, item in enumerate(items_src, start=1):
        name_m = re.search(r'<vchName>([^<]+)</vchName>', item)
        freq_m = re.search(r'<frequency>([^<]+)</frequency>', item)
        name = name_m.group(1) if name_m else 'Unknown'
        freq = freq_m.group(1).strip() if freq_m else ''

        if freq in freq_to_ch:
            template = dict(freq_to_ch[freq])
            template['channelName'] = name
            template['majorNumber'] = idx
            template['programNum']  = idx
            template['SVCID']       = idx
            template['userSelCHNo'] = True
            template['userCustomize'] = True
            template['userEditChNumber'] = True
            template['skipped'] = False
            template['deleted'] = False
            template['Invisible'] = False
            try:
                name_b64 = base64.b64encode(name.ljust(40, '\x00').encode('utf-8')).decode()
                template['chNameBase64'] = name_b64
            except: pass
            new_channels.append(template)
        else:
            skipped += 1

    # حقن القنوات في JSON المرجعي
    data_ref['channelList'] = new_channels

    # تغيير البلد في JSON
    target_country_full = 'Japan'
    target_code3 = 'JA'
    if new_country_name and new_country_name in COUNTRIES:
        cd = COUNTRIES[new_country_name]
        target_country_full = cd['full']
        target_code3 = cd['code3']

    if 'modelInfo' not in data_ref: data_ref['modelInfo'] = {}
    data_ref['modelInfo']['country'] = target_country_full

    # تجميع الملف
    new_json = json.dumps(data_ref, ensure_ascii=False, separators=(',', ':'))
    new_txt = re.sub(r'<legacybroadcast>.*?</legacybroadcast>',
                     f'<legacybroadcast>{new_json}</legacybroadcast>',
                     txt_ref, flags=re.DOTALL)

    # تغيير الموديل
    target_model = new_model.strip() if new_model and new_model.strip() else src_info['model']
    new_txt = re.sub(r'(<ModelName[^>]*>)([^<]+)(</ModelName>)',
                     lambda m: m.group(1) + target_model + m.group(3), new_txt)

    # تغيير BroadcastCountrySetting
    new_txt = re.sub(r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                     lambda m: m.group(1) + target_code3 + m.group(3), new_txt)

    old_bc = re.search(r'<BroadcastCountrySetting[^>]*>([^<]+)</BroadcastCountrySetting>', txt_ref)
    changes.append(('model', ref_info['model'], target_model))
    if new_country_name and new_country_name in COUNTRIES:
        changes.append(('country', old_bc.group(1) if old_bc else '?', target_code3, new_country_name))
    changes.append(('converted', len(new_channels), skipped))

    return new_txt.encode('utf-8'), changes


# ──────────────────────────────────────────────────────
# 4. CSS & Config
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

ar = st.session_state.lang == 'ar'
dk = st.session_state.theme == 'dark'
bg   = "radial-gradient(circle at 50% 50%,#110926 0%,#05020d 100%)" if dk else "radial-gradient(circle at 50% 50%,#f4f5f7 0%,#e4e7eb 100%)"
tc   = "#00f0ff" if dk else "#0d0722"
bb   = "rgba(13,7,33,0.85)" if dk else "#ffffff"
bord = "#00f0ff" if dk else "#ff007f"
bsh  = "rgba(0,240,255,0.35)" if dk else "rgba(255,0,127,0.15)"
tsh  = "0 0 5px rgba(0,240,255,0.4)" if dk else "none"
ff   = "'Cairo',sans-serif" if ar else "'Orbitron',sans-serif"

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
    padding:18px!important;margin-bottom:16px!important;}}
.stButton>button{{
    background:linear-gradient(135deg,#ff007f 0%,#aa0055 100%)!important;
    color:#fff!important;border:2px solid #ff007f!important;
    border-radius:12px!important;font-weight:bold;width:100%;}}
.stDownloadButton>button{{
    background:linear-gradient(135deg,#00b894 0%,#00695c 100%)!important;
    color:#fff!important;border:none!important;border-radius:12px!important;
    font-weight:bold;width:100%;}}
.card{{background:{bb};border:2px solid {bord};box-shadow:0 5px 15px {bsh};
       border-radius:14px;padding:20px;margin-bottom:14px;}}
.badge{{display:inline-block;background:linear-gradient(135deg,#ff007f,#aa0055);
        color:white;border-radius:50%;width:30px;height:30px;text-align:center;
        line-height:30px;font-weight:bold;margin:0 8px;font-size:0.95rem;}}
.mode-card{{border-radius:14px;padding:18px;margin-bottom:10px;cursor:pointer;
            border:2px solid;text-align:center;}}
.mode-active{{border-color:#ff007f;background:rgba(255,0,127,0.12);}}
.mode-inactive{{border-color:#444;background:rgba(255,255,255,0.03);}}
.change-box{{background:rgba(0,240,255,0.08);border-left:4px solid #00f0ff;
             border-radius:8px;padding:10px 16px;margin:5px 0;}}
.success-box{{background:rgba(0,184,148,0.12);border:2px solid #00b894;
              border-radius:12px;padding:14px;margin:8px 0;}}
.warn-box{{background:rgba(255,193,7,0.1);border:2px solid #ffc107;
           border-radius:12px;padding:14px;margin-top:12px;}}
.tag{{display:inline-block;padding:3px 10px;border-radius:6px;font-size:0.82rem;font-weight:bold;margin:2px;}}
.t-modern{{background:rgba(0,240,255,0.15);border:1px solid #00f0ff;color:#00f0ff;}}
.t-legacy{{background:rgba(255,165,0,0.15);border:1px solid orange;color:orange;}}
.t-c{{background:rgba(255,0,127,0.15);border:1px solid #ff007f;color:#ff007f;}}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 5. العنوان
# ──────────────────────────────────────────────────────
st.title("🔄 RAMBO — محوّل ملفات TLL" if ar else "🔄 RAMBO — TLL File Converter")
st.markdown(f"<h3 style='text-align:center;'>{'⚡ غيّر البلد | الموديل | حوّل قديم↔حديث — يحل Cloning Error 8' if ar else '⚡ Change Country | Model | Convert Legacy↔Modern — Fixes Cloning Error 8'}</h3>", unsafe_allow_html=True)
st.write("---")

# ──────────────────────────────────────────────────────
# 6. اختيار الوضع
# ──────────────────────────────────────────────────────
st.markdown(f"### <span class='badge'>1</span> {'اختر نوع التحويل' if ar else 'Select Conversion Type'}", unsafe_allow_html=True)

col_m1, col_m2 = st.columns(2)
with col_m1:
    is_simple = st.session_state.p4_mode == 'simple'
    cls = 'mode-active' if is_simple else 'mode-inactive'
    st.markdown(f"<div class='mode-card {cls}'>{'🌍 تغيير البلد أو الموديل فقط' if ar else '🌍 Change Country or Model Only'}<br><small>{'لا تحتاج ملف مرجعي' if ar else 'No reference file needed'}</small></div>", unsafe_allow_html=True)
    if st.button("✅ " + ("اختر هذا" if ar else "Select This"), key="mode_simple", use_container_width=True):
        st.session_state.p4_mode = 'simple'
        st.rerun()

with col_m2:
    is_convert = st.session_state.p4_mode == 'convert'
    cls = 'mode-active' if is_convert else 'mode-inactive'
    st.markdown(f"<div class='mode-card {cls}'>{'🔁 تحويل قديم ↔ حديث' if ar else '🔁 Convert Legacy ↔ Modern'}<br><small>{'تحتاج ملف مرجعي شغال على شاشتك' if ar else 'Needs a reference file that works on your TV'}</small></div>", unsafe_allow_html=True)
    if st.button("✅ " + ("اختر هذا" if ar else "Select This"), key="mode_convert", use_container_width=True):
        st.session_state.p4_mode = 'convert'
        st.rerun()

st.write("---")

# ──────────────────────────────────────────────────────
# 7. رفع الملفات
# ──────────────────────────────────────────────────────
st.markdown(f"### <span class='badge'>2</span> {'ارفع الملف/الملفات' if ar else 'Upload File(s)'}", unsafe_allow_html=True)

if st.session_state.p4_mode == 'simple':
    # ملف واحد فقط
    col_up, col_rst = st.columns([5,1])
    with col_up:
        up_src = st.file_uploader(
            "📂 " + ("ارفع ملف TLL:" if ar else "Upload TLL file:"),
            type=["TLL","bak"], key=f"src_{st.session_state.p4_src_key}"
        )
    with col_rst:
        st.write(""); st.write("")
        if st.button("🔄", key="rst_s", use_container_width=True):
            st.session_state.p4_src_bytes = None
            st.session_state.p4_src_name  = None
            st.session_state.p4_src_info  = {}
            st.session_state.p4_result_bytes = None
            st.session_state.p4_done = False
            st.session_state.p4_src_key += 1
            st.rerun()

    if up_src:
        b = up_src.read()
        if st.session_state.p4_src_name != up_src.name:
            st.session_state.p4_src_bytes = b
            st.session_state.p4_src_name  = up_src.name
            st.session_state.p4_src_info  = parse_tll(b)
            st.session_state.p4_result_bytes = None
            st.session_state.p4_done = False

else:
    # ملفين
    col_s, col_r = st.columns(2)
    with col_s:
        st.markdown(f"**{'📂 الملف المطلوب تحويله:' if ar else '📂 File to convert:'}**")
        up_src = st.file_uploader(
            "Modern JSON أو Legacy XML",
            type=["TLL","bak"], key=f"src2_{st.session_state.p4_src_key}"
        )
        if up_src:
            b = up_src.read()
            if st.session_state.p4_src_name != up_src.name:
                st.session_state.p4_src_bytes = b
                st.session_state.p4_src_name  = up_src.name
                st.session_state.p4_src_info  = parse_tll(b)
                st.session_state.p4_result_bytes = None
                st.session_state.p4_done = False

    with col_r:
        st.markdown(f"**{'📂 الملف المرجعي الشغال على شاشتك:' if ar else '📂 Reference file (works on your TV):'}**")
        up_ref = st.file_uploader(
            "الملف اللي بيشتغل على شاشتك",
            type=["TLL","bak"], key=f"ref_{st.session_state.p4_ref_key}"
        )
        if up_ref:
            b = up_ref.read()
            if st.session_state.p4_ref_name != up_ref.name:
                st.session_state.p4_ref_bytes = b
                st.session_state.p4_ref_name  = up_ref.name
                st.session_state.p4_ref_info  = parse_tll(b)
                st.session_state.p4_result_bytes = None
                st.session_state.p4_done = False

    if st.button("🔄 " + ("إعادة ضبط" if ar else "Reset"), key="rst_c"):
        for k in ['p4_src_bytes','p4_src_name','p4_ref_bytes','p4_ref_name',
                  'p4_result_bytes','p4_done','p4_changes']:
            st.session_state[k] = None if 'bytes' in k or 'name' in k else ([] if 'changes' in k else False)
        st.session_state.p4_src_info = {}
        st.session_state.p4_ref_info = {}
        st.session_state.p4_src_key += 1
        st.session_state.p4_ref_key += 1
        st.rerun()

# ── عرض معلومات الملفات ──
src_info = st.session_state.p4_src_info
ref_info = st.session_state.p4_ref_info

def show_file_info(info, label):
    if not info: return
    is_mod = info.get('is_modern', False)
    tag = f"<span class='tag t-modern'>{'حديث' if ar else 'Modern'} JSON</span>" if is_mod else f"<span class='tag t-legacy'>{'قديم' if ar else 'Legacy'} XML</span>"
    st.markdown(f"<div class='card'><b>{label}</b><br><br>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Model", info.get('model','?'))
    with c2:
        st.markdown("**Country**")
        st.markdown(f"<span class='tag t-c'>{info.get('country_label','?')} ({info.get('display_country','')})</span>", unsafe_allow_html=True)
    with c3:
        st.markdown("**Type**")
        st.markdown(tag, unsafe_allow_html=True)
    with c4: st.metric("Channels", f"{info.get('ch_count',0):,}")
    st.markdown("</div>", unsafe_allow_html=True)

if src_info:
    show_file_info(src_info, "📄 " + ("الملف المراد تحويله" if ar else "Source File"))
if ref_info and st.session_state.p4_mode == 'convert':
    show_file_info(ref_info, "📋 " + ("الملف المرجعي" if ar else "Reference File"))

if not src_info:
    st.info("⬆️ " + ("ارفع ملف TLL للبدء." if ar else "Upload a TLL file to start."))
    st.stop()

st.write("---")

# ──────────────────────────────────────────────────────
# 8. خيارات التحويل
# ──────────────────────────────────────────────────────
st.markdown(f"### <span class='badge'>3</span> {'خيارات التحويل' if ar else 'Conversion Options'}", unsafe_allow_html=True)

col_m, col_c = st.columns(2)

with col_m:
    st.markdown(f"#### {'🖥️ الموديل الجديد' if ar else '🖥️ New Model'}")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    keep_m = "— " + ("الاحتفاظ بالموديل الحالي" if ar else "Keep current model") + " —"
    sel_model = st.selectbox("", options=[keep_m]+LG_MODELS, key="p4_sel_model", label_visibility="collapsed")
    man_model = st.text_input("", placeholder="أو اكتب يدوياً / Or type manually", key="p4_man_model", label_visibility="collapsed").strip()
    final_model = man_model if man_model else ("" if sel_model == keep_m else sel_model)
    if final_model and final_model != src_info.get('model',''):
        st.success(f"✅ → **{final_model}**")
    st.markdown("</div>", unsafe_allow_html=True)

with col_c:
    st.markdown(f"#### {'🌍 بلد البث الجديد' if ar else '🌍 New Broadcast Country'}")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    keep_c = "— " + ("الاحتفاظ ببلد البث الحالي" if ar else "Keep current country") + " —"
    sel_country = st.selectbox("", options=[keep_c]+list(COUNTRIES.keys()), key="p4_sel_country", label_visibility="collapsed")
    final_country = "" if sel_country == keep_c else sel_country
    if final_country:
        cd = COUNTRIES[final_country]
        st.success(f"✅ **{final_country}** → `{cd['code3']}`")
    st.markdown(
        f"<div class='warn-box'><b style='color:#ffc107;'>⚠️ {'حل Cloning Error 8:' if ar else 'Fix Cloning Error 8:'}</b><br>"
        f"<span style='font-size:0.85rem;'>{'اختر نفس بلد البث المضبوط على شاشتك' if ar else 'Select the same country set on your TV'}</span></div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# تحذير للوضع convert
if st.session_state.p4_mode == 'convert' and not ref_info:
    st.warning("⚠️ " + ("ارفع الملف المرجعي الشغال على شاشتك أولاً!" if ar else "Upload the reference file that works on your TV first!"))
    st.stop()

st.write("")
col_btn, _, _ = st.columns([2,1,1])
with col_btn:
    btn_lbl = "🔄 " + ("تحويل الآن" if ar else "Convert Now")
    if st.button(btn_lbl, use_container_width=True):
        if not final_model and not final_country and st.session_state.p4_mode == 'simple':
            st.warning("⚠️ " + ("اختر تغيير الموديل أو البلد!" if ar else "Select a model or country change!"))
        else:
            if st.session_state.p4_mode == 'simple':
                res, changes = change_country_model(src_info, final_model, final_country)
            else:
                src_is_modern = src_info.get('is_modern', False)
                ref_is_modern = ref_info.get('is_modern', False)
                if src_is_modern and not ref_is_modern:
                    res, changes = convert_modern_to_legacy(src_info, ref_info, final_model, final_country)
                elif not src_is_modern and ref_is_modern:
                    res, changes = convert_legacy_to_modern(src_info, ref_info, final_model, final_country)
                else:
                    # نفس النوع - غير بلد/موديل بس
                    res, changes = change_country_model(src_info, final_model, final_country)

            st.session_state.p4_result_bytes = res
            st.session_state.p4_changes      = changes
            st.session_state.p4_done         = True
            st.rerun()

# ──────────────────────────────────────────────────────
# 9. النتيجة
# ──────────────────────────────────────────────────────
if st.session_state.p4_done and st.session_state.p4_result_bytes:
    st.write("---")
    st.markdown(f"### <span class='badge'>4</span> {'تحميل الملف المحوّل' if ar else 'Download Converted File'}", unsafe_allow_html=True)
    st.success("🎉 " + ("تم التحويل بنجاح!" if ar else "Conversion successful!"))

    for ch in st.session_state.p4_changes:
        if ch[0] == 'model':
            st.markdown(f"<div class='change-box'>🖥️ Model: <code>{ch[1]}</code> <b style='color:#ff007f;'>➜</b> <code style='color:#00f0ff;'>{ch[2]}</code></div>", unsafe_allow_html=True)
        elif ch[0] == 'country':
            st.markdown(f"<div class='change-box'>🌍 Country: <code>{ch[1]}</code> <b style='color:#ff007f;'>➜</b> <code style='color:#00f0ff;'>{ch[2]}</code> ({ch[3] if len(ch)>3 else ''})</div>", unsafe_allow_html=True)
        elif ch[0] == 'converted':
            st.markdown(f"<div class='change-box'>📡 {'القنوات المحوّلة' if ar else 'Converted channels'}: <b style='color:#00f0ff;'>{ch[1]}</b> | {'تجاهل' if ar else 'Skipped'}: {ch[2]}</div>", unsafe_allow_html=True)

    st.write("")
    col_d1, col_d2 = st.columns([3,1])
    with col_d1:
        st.download_button(
            label="📥 " + ("تحميل الملف المحوّل (GlobalClone00001.TLL)" if ar else "Download Converted File"),
            data=st.session_state.p4_result_bytes,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream",
            use_container_width=True,
        )
    with col_d2:
        if st.button("🔄 " + ("ملف جديد" if ar else "New File"), key="rst_bot"):
            for k in ['p4_src_bytes','p4_src_name','p4_ref_bytes','p4_ref_name',
                      'p4_result_bytes','p4_changes','p4_done']:
                st.session_state[k] = None if 'bytes' in k or 'name' in k else ([] if 'changes' in k else False)
            st.session_state.p4_src_info = {}
            st.session_state.p4_ref_info = {}
            st.session_state.p4_src_key += 1
            st.session_state.p4_ref_key += 1
            st.rerun()

    st.markdown(f"""<div class='warn-box'>
<b style='color:#ffc107;'>💡 {'ملحوظة:' if ar else 'Note:'}</b><br>
<span style='font-size:0.88rem;'>
{'إذا لم تظهر القنوات: إعدادات ← القنوات ← مدير القنوات ← تعديل كل القنوات ← تحديد الكل ← استعادة' if ar else 'If channels missing: Settings → Channels → Channel Manager → Edit All Channels → Select All → Restore'}
</span></div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 10. FOOTER
# ──────────────────────────────────────────────────────
st.markdown("""<div style="background:#0f172a;border:2px solid #00f0ff;color:#ffffff;
padding:35px;text-align:center;border-radius:20px;margin-top:65px;font-family:Arial;">
<div style="color:#ff007f;font-size:26px;font-weight:bold;">🛠️ DEVELOPER ENG: RAFIK NATHAN</div>
<div style="margin-top:10px;">📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
<div style="margin-top:10px;">✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com</div>
<a href="https://api.whatsapp.com/send?phone=201280339779" target="_blank"
style="color:#25d366;padding:14px 35px;border-radius:35px;display:inline-block;
font-weight:bold;border:2px solid #25d366;text-decoration:none;margin-top:20px;">WhatsApp</a>
</div>""", unsafe_allow_html=True)
