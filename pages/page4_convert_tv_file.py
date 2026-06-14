
import streamlit as st
import re, json, base64

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for k, v in {
    'lang':'ar','theme':'dark',
    'net_bytes':None,'net_name':None,'net_info':{},
    'my_bytes':None,'my_name':None,'my_info':{},
    'result_bytes':None,'done':False,
    'preview':[],'skipped':[],
    'net_key':0,'my_key':0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# البلدان والموديلات
# ─────────────────────────────────────────────
COUNTRIES = {
    "🇪🇬 مصر":       {"c3":"EGY","full":"Egypt"},
    "🇸🇦 السعودية":  {"c3":"SAU","full":"Saudi Arabia"},
    "🇦🇪 الإمارات":  {"c3":"ARE","full":"United Arab Emirates"},
    "🇯🇴 الأردن":    {"c3":"JOR","full":"Jordan"},
    "🇱🇧 لبنان":     {"c3":"LBN","full":"Lebanon"},
    "🇸🇩 السودان":   {"c3":"SDN","full":"Sudan"},
    "🇩🇿 الجزائر":   {"c3":"DZA","full":"Algeria"},
    "🇲🇦 المغرب":    {"c3":"MAR","full":"Morocco"},
    "🇹🇳 تونس":      {"c3":"TUN","full":"Tunisia"},
    "🇱🇾 ليبيا":     {"c3":"LBY","full":"Libya"},
    "🇮🇶 العراق":    {"c3":"IRQ","full":"Iraq"},
    "🇸🇾 سوريا":     {"c3":"SYR","full":"Syria"},
    "🇾🇪 اليمن":     {"c3":"YEM","full":"Yemen"},
    "🇰🇼 الكويت":    {"c3":"KWT","full":"Kuwait"},
    "🇶🇦 قطر":       {"c3":"QAT","full":"Qatar"},
    "🇧🇭 البحرين":   {"c3":"BHR","full":"Bahrain"},
    "🇴🇲 عُمان":     {"c3":"OMN","full":"Oman"},
    "🌐 عالمي (JA)": {"c3":"JA", "full":"Japan"},
}

LG_MODELS = sorted([
    "65UR78006LL","65UR78006LK","55UR78006LK","43UR78006LK","75UR78006LK",
    "65UR80006LJ","55UR80006LJ","43UR80006LJ","50UR80006LJ","75UR80006LJ",
    "65UP80006LR","55UP80006LR","43UP80006LR","50UP80006LR","75UP80006LR",
    "OLED65G4PSA","OLED55C4PSA","OLED77C4PSA","OLED65C3PSA","OLED55C3PSA",
    "OLED65CX6LA","OLED55CX6LA","65QNED85T6A","55QNED80T6A",
    "65UQ80006LB","55UQ80006LB","50UQ80006LB","43UQ80006LB",
    "55UA85006LA.DFUYLWE","65UA80006LA","65NANO86VPA","55NANO86VPA",
    "32LQ63806LC","43LQ63006LA","50LQ63006LA","32LQ630BPSA",
    "65SM9010PLA","55SM9010PLA","43UK6300PLB","49UK6300PLB","55UK6300PLB","65UK6300PLB",
    "32LK6100PLB","43LK6100PLB","49LK6100PLB","55LK6100PLB",
    "32LM550BPVA","43LM5500PLA","49LM5500PLA","55LM5500PLA",
    "32LH604U-TB","43LH604V","49LH604V","55LH604V","43LJ510V-TD",
    "32LH570U","43LH570V","49LH570V","55LH570V","32LH530V",
    "65UH950V","55UH950V","49UH850V","43UH850V",
])

# ─────────────────────────────────────────────
# PARSE
# ─────────────────────────────────────────────
def parse_tll(b):
    try: txt = b.decode('utf-8','ignore')
    except: txt = b.decode('latin-1','ignore')
    info = {'txt':txt, 'is_modern':'legacybroadcast' in txt}
    m = re.search(r'<ModelName[^>]*>([^<]+)</ModelName>', txt)
    info['model'] = m.group(1).strip() if m else ''
    m = re.search(r'<BroadcastCountrySetting[^>]*>([^<]+)</BroadcastCountrySetting>', txt)
    info['bc'] = m.group(1).strip() if m else ''
    m = re.search(r'<country[^>]*>([^<]+)</country>', txt)
    info['cx'] = m.group(1).strip() if m else ''
    info['cj'] = ''
    if info['is_modern']:
        jm = re.search(r'<legacybroadcast>(.*?)</legacybroadcast>', txt, re.DOTALL)
        if jm:
            try:
                d = json.loads(jm.group(1))
                info['cj']       = d.get('modelInfo',{}).get('country','')
                info['channels'] = d.get('channelList',[])
                info['ch_count'] = len(info['channels'])
                info['jdata']    = d
            except:
                info['channels'] = []; info['ch_count'] = 0; info['jdata'] = {}
        else:
            info['channels'] = []; info['ch_count'] = 0; info['jdata'] = {}
    else:
        info['channels']  = re.findall(r'<ITEM>(.*?)</ITEM>', txt, re.DOTALL)
        info['ch_count']  = len(info['channels'])
        info['jdata']     = {}
    info['display'] = info['bc'] or info['cj'] or info['cx']
    return info

# ─────────────────────────────────────────────
# FALLBACK: أقرب تردد
# ─────────────────────────────────────────────
def find_closest_freq(target_freq, available_freqs):
    """يرجع أقرب تردد متاح"""
    try:
        tf = int(target_freq)
        closest = min(available_freqs, key=lambda f: abs(int(f)-tf))
        return closest
    except:
        return list(available_freqs)[0] if available_freqs else None

def build_item_from_template(idx, name, freq, template_item):
    """يبني ITEM جديد من template بس بتردد واسم مختلفين"""
    item = template_item
    # غير التردد
    item = re.sub(r'<frequency>[^<]+</frequency>', f'<frequency>{freq}</frequency>', item)
    # غير الرقم
    item = re.sub(r'<prNum>[^<]+</prNum>', f'<prNum>{idx}</prNum>', item)
    # غير الاسم
    nh = name.encode('utf-8').hex()
    nl = len(name)
    item = re.sub(r'<hexVchName>[^<]+</hexVchName>', f'<hexVchName>{nh}</hexVchName>', item)
    item = re.sub(r'<notConvertedLengthOfVchName>[^<]+</notConvertedLengthOfVchName>',
                  f'<notConvertedLengthOfVchName>{nl}</notConvertedLengthOfVchName>', item)
    item = re.sub(r'<vchName>[^<]+</vchName>', f'<vchName>{name}</vchName>', item)
    item = re.sub(r'<lengthOfVchName>[^<]+</lengthOfVchName>',
                  f'<lengthOfVchName>{nl}</lengthOfVchName>', item)
    return item

# ─────────────────────────────────────────────
# CORE CONVERT
# ─────────────────────────────────────────────
def do_convert(net_info, my_info, new_model, new_country):
    net_modern = net_info['is_modern']
    my_modern  = my_info['is_modern']
    txt_my     = my_info['txt']
    net_chs    = net_info['channels']

    # الموديل والبلد النهائيين
    target_model = new_model.strip() if new_model.strip() else net_info['model']
    target_c3    = my_info['bc'] or my_info['cx'] or 'JA'
    target_full  = my_info['cj'] or 'Japan'
    target_cx    = my_info['cx'] or 'JA'
    if new_country and new_country in COUNTRIES:
        target_c3   = COUNTRIES[new_country]['c3']
        target_full = COUNTRIES[new_country]['full']

    preview = []
    skipped = []

    # ══════════════════════════════════════════
    # حالة: ملف النت Legacy، ملفي Legacy
    # ══════════════════════════════════════════
    if not net_modern and not my_modern:
        # بناء map تردد → ITEM من ملفي
        freq_to_item = {}
        for item in my_info['channels']:
            fm = re.search(r'<frequency>([^<]+)</frequency>', item)
            if fm:
                f = fm.group(1).strip()
                if f not in freq_to_item:
                    freq_to_item[f] = item

        available_freqs = list(freq_to_item.keys())
        new_items = []

        for idx, item_net in enumerate(net_chs, 1):
            nm = re.search(r'<vchName>([^<]+)</vchName>', item_net)
            fm = re.search(r'<frequency>([^<]+)</frequency>', item_net)
            name = nm.group(1) if nm else 'Unknown'
            freq = fm.group(1).strip() if fm else ''

            if freq in freq_to_item:
                # تردد مطابق — استخدم الـ template مباشرة
                new_item = build_item_from_template(idx, name, freq, freq_to_item[freq])
                new_items.append('<ITEM>' + new_item + '</ITEM>')
                preview.append((idx, name, freq, '✅ مطابق'))
            elif available_freqs:
                # Fallback: أقرب تردد
                closest = find_closest_freq(freq, available_freqs)
                new_item = build_item_from_template(idx, name, freq, freq_to_item[closest])
                new_items.append('<ITEM>' + new_item + '</ITEM>')
                preview.append((idx, name, freq, f'🔄 fallback ({closest})'))
            else:
                skipped.append((name, freq))

        # دمج في ملفي
        combined = '\r\n'.join(new_items)
        si = txt_my.find('<ITEM>')
        ei = txt_my.rfind('</ITEM>') + len('</ITEM>')
        new_txt = txt_my[:si] + combined + txt_my[ei:]

        # الموديل
        new_txt = re.sub(r'(<ModelName[^>]*>)([^<]+)(</ModelName>)',
                         lambda m: m.group(1)+target_model+m.group(3), new_txt)
        # BroadcastCountry
        if re.search(r'<BroadcastCountrySetting', new_txt):
            new_txt = re.sub(r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                             lambda m: m.group(1)+target_c3+m.group(3), new_txt)
        else:
            new_txt = new_txt.replace('</ModelInfo>',
                f'<BroadcastCountrySetting type="0">{target_c3}</BroadcastCountrySetting>\n</ModelInfo>')
        # country XML
        new_txt = re.sub(r'(<country[^>]*>)([^<]+)(</country>)',
                         lambda m: m.group(1)+target_cx+m.group(3), new_txt)

        return new_txt.encode('utf-8'), preview, skipped, 'Legacy→Legacy'

    # ══════════════════════════════════════════
    # حالة: ملف النت Modern، ملفي Legacy
    # ══════════════════════════════════════════
    elif net_modern and not my_modern:
        freq_to_item = {}
        for item in my_info['channels']:
            fm = re.search(r'<frequency>([^<]+)</frequency>', item)
            if fm:
                f = fm.group(1).strip()
                if f not in freq_to_item:
                    freq_to_item[f] = item

        available_freqs = list(freq_to_item.keys())
        new_items = []

        for idx, ch in enumerate(net_chs, 1):
            name = ch.get('channelName','Unknown')
            freq = str(ch.get('frequency',''))

            if freq in freq_to_item:
                new_item = build_item_from_template(idx, name, freq, freq_to_item[freq])
                new_items.append('<ITEM>' + new_item + '</ITEM>')
                preview.append((idx, name, freq, '✅ مطابق'))
            elif available_freqs:
                closest = find_closest_freq(freq, available_freqs)
                new_item = build_item_from_template(idx, name, freq, freq_to_item[closest])
                new_items.append('<ITEM>' + new_item + '</ITEM>')
                preview.append((idx, name, freq, f'🔄 fallback ({closest})'))
            else:
                skipped.append((name, freq))

        combined = '\r\n'.join(new_items)
        si = txt_my.find('<ITEM>'); ei = txt_my.rfind('</ITEM>') + len('</ITEM>')
        new_txt = txt_my[:si] + combined + txt_my[ei:]
        new_txt = re.sub(r'(<ModelName[^>]*>)([^<]+)(</ModelName>)',
                         lambda m: m.group(1)+target_model+m.group(3), new_txt)
        if re.search(r'<BroadcastCountrySetting', new_txt):
            new_txt = re.sub(r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                             lambda m: m.group(1)+target_c3+m.group(3), new_txt)
        else:
            new_txt = new_txt.replace('</ModelInfo>',
                f'<BroadcastCountrySetting type="0">{target_c3}</BroadcastCountrySetting>\n</ModelInfo>')
        new_txt = re.sub(r'(<country[^>]*>)([^<]+)(</country>)',
                         lambda m: m.group(1)+target_cx+m.group(3), new_txt)

        return new_txt.encode('utf-8'), preview, skipped, 'Modern→Legacy'

    # ══════════════════════════════════════════
    # حالة: ملف النت Legacy، ملفي Modern
    # ══════════════════════════════════════════
    elif not net_modern and my_modern:
        data_my  = dict(my_info['jdata'])
        ref_chs  = data_my.get('channelList', [])
        freq_to_ch = {}
        for ch in ref_chs:
            f = str(ch.get('frequency',''))
            if f not in freq_to_ch: freq_to_ch[f] = ch
        available_freqs = list(freq_to_ch.keys())
        base_ch = ref_chs[0] if ref_chs else {}

        new_channels = []
        for idx, item in enumerate(net_chs, 1):
            nm = re.search(r'<vchName>([^<]+)</vchName>', item)
            fm = re.search(r'<frequency>([^<]+)</frequency>', item)
            name = nm.group(1) if nm else 'Unknown'
            freq = fm.group(1).strip() if fm else ''

            if freq in freq_to_ch:
                template = dict(freq_to_ch[freq])
                src = '✅ مطابق'
            elif available_freqs:
                closest = find_closest_freq(freq, available_freqs)
                template = dict(freq_to_ch[closest])
                try: template['frequency'] = int(freq)
                except: pass
                src = f'🔄 fallback ({closest})'
            else:
                template = dict(base_ch)
                try: template['frequency'] = int(freq)
                except: pass
                src = '🔄 fallback (base)'

            template.update({
                'channelName':name,'majorNumber':idx,'programNum':idx,
                'SVCID':idx,'userSelCHNo':True,'userCustomize':True,
                'userEditChNumber':True,'skipped':False,'deleted':False,'Invisible':False,
            })
            try:
                template['chNameBase64'] = base64.b64encode(
                    name.ljust(40,'\x00').encode('utf-8')).decode()
            except: pass
            new_channels.append(template)
            preview.append((idx, name, freq, src))

        data_my['channelList'] = new_channels
        if 'modelInfo' not in data_my: data_my['modelInfo'] = {}
        data_my['modelInfo']['country'] = target_full

        new_json = json.dumps(data_my, ensure_ascii=False, separators=(',',':'))
        new_txt = re.sub(r'<legacybroadcast>.*?</legacybroadcast>',
                         f'<legacybroadcast>{new_json}</legacybroadcast>',
                         txt_my, flags=re.DOTALL)
        new_txt = re.sub(r'(<ModelName[^>]*>)([^<]+)(</ModelName>)',
                         lambda m: m.group(1)+target_model+m.group(3), new_txt)
        if re.search(r'<BroadcastCountrySetting', new_txt):
            new_txt = re.sub(r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                             lambda m: m.group(1)+target_c3+m.group(3), new_txt)
        else:
            new_txt = new_txt.replace('</ModelInfo>',
                f'<BroadcastCountrySetting type="0">{target_c3}</BroadcastCountrySetting>\n</ModelInfo>')

        return new_txt.encode('utf-8'), preview, skipped, 'Legacy→Modern'

    # ══════════════════════════════════════════
    # حالة: كلاهما Modern
    # ══════════════════════════════════════════
    else:
        data_my = dict(my_info['jdata'])
        ref_chs = data_my.get('channelList', [])
        freq_to_ch = {}
        for ch in ref_chs:
            f = str(ch.get('frequency',''))
            if f not in freq_to_ch: freq_to_ch[f] = ch
        available_freqs = list(freq_to_ch.keys())
        base_ch = ref_chs[0] if ref_chs else {}

        new_channels = []
        for idx, ch_net in enumerate(net_chs, 1):
            name = ch_net.get('channelName','Unknown')
            freq = str(ch_net.get('frequency',''))

            if freq in freq_to_ch:
                template = dict(freq_to_ch[freq])
                src = '✅ مطابق'
            elif available_freqs:
                closest = find_closest_freq(freq, available_freqs)
                template = dict(freq_to_ch[closest])
                try: template['frequency'] = int(freq)
                except: pass
                src = f'🔄 fallback ({closest})'
            else:
                template = dict(base_ch)
                try: template['frequency'] = int(freq)
                except: pass
                src = '🔄 fallback (base)'

            template.update({
                'channelName':name,'majorNumber':idx,'programNum':idx,
                'SVCID':idx,'userSelCHNo':True,'userCustomize':True,
                'userEditChNumber':True,'skipped':False,'deleted':False,'Invisible':False,
            })
            try:
                template['chNameBase64'] = base64.b64encode(
                    name.ljust(40,'\x00').encode('utf-8')).decode()
            except: pass
            new_channels.append(template)
            preview.append((idx, name, freq, src))

        data_my['channelList'] = new_channels
        if 'modelInfo' not in data_my: data_my['modelInfo'] = {}
        data_my['modelInfo']['country'] = target_full

        new_json = json.dumps(data_my, ensure_ascii=False, separators=(',',':'))
        new_txt = re.sub(r'<legacybroadcast>.*?</legacybroadcast>',
                         f'<legacybroadcast>{new_json}</legacybroadcast>',
                         txt_my, flags=re.DOTALL)
        new_txt = re.sub(r'(<ModelName[^>]*>)([^<]+)(</ModelName>)',
                         lambda m: m.group(1)+target_model+m.group(3), new_txt)
        if re.search(r'<BroadcastCountrySetting', new_txt):
            new_txt = re.sub(r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                             lambda m: m.group(1)+target_c3+m.group(3), new_txt)
        else:
            new_txt = new_txt.replace('</ModelInfo>',
                f'<BroadcastCountrySetting type="0">{target_c3}</BroadcastCountrySetting>\n</ModelInfo>')

        return new_txt.encode('utf-8'), preview, skipped, 'Modern→Modern'

# ─────────────────────────────────────────────
# CSS & PAGE
# ─────────────────────────────────────────────
st.set_page_config(page_title="RAMBO P4", page_icon="🔄", layout="wide")

cl, ct, _ = st.columns([1.2,1.5,8])
with cl:
    if st.button("🌐 English" if st.session_state.lang=='ar' else "🌐 العربية"):
        st.session_state.lang='en' if st.session_state.lang=='ar' else 'ar'; st.rerun()
with ct:
    if st.button("☀️ Light" if st.session_state.theme=='dark' else "🌙 Dark"):
        st.session_state.theme='light' if st.session_state.theme=='dark' else 'dark'; st.rerun()

ar = st.session_state.lang=='ar'
dk = st.session_state.theme=='dark'
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
h1{{color:#ff007f!important;text-shadow:0 0 10px #ff007f,0 0 25px rgba(255,0,127,0.4)!important;text-align:center;font-weight:900;}}
h3,p,label,.stMarkdown,div[data-testid="stMarkdownContainer"] p{{color:{tc}!important;text-shadow:{tsh};}}
.stTextInput>div>div>input,.stSelectbox>div>div{{background:{bb}!important;color:{tc}!important;border:2px solid {bord}!important;border-radius:10px!important;}}
div[data-testid="stFileUploader"]{{background:{bb}!important;border:2px solid {bord}!important;box-shadow:0 5px 15px {bsh}!important;border-radius:14px!important;padding:18px!important;}}
.stButton>button{{background:linear-gradient(135deg,#ff007f,#aa0055)!important;color:#fff!important;border:2px solid #ff007f!important;border-radius:12px!important;font-weight:bold;width:100%;}}
.stDownloadButton>button{{background:linear-gradient(135deg,#00b894,#00695c)!important;color:#fff!important;border:none!important;border-radius:12px!important;font-weight:bold;width:100%;}}
.card{{background:{bb};border:2px solid {bord};box-shadow:0 5px 15px {bsh};border-radius:14px;padding:20px;margin-bottom:14px;}}
.badge{{display:inline-block;background:linear-gradient(135deg,#ff007f,#aa0055);color:white;border-radius:50%;width:32px;height:32px;text-align:center;line-height:32px;font-weight:bold;margin:0 8px;}}
.file-net{{border:2px solid #00f0ff;background:rgba(0,240,255,0.05);border-radius:14px;padding:18px;margin-bottom:12px;}}
.file-my{{border:2px solid #ff007f;background:rgba(255,0,127,0.05);border-radius:14px;padding:18px;margin-bottom:12px;}}
.stat{{border-radius:12px;padding:14px;text-align:center;border:2px solid;}}
.sg{{border-color:#00b894;background:rgba(0,184,148,0.1);color:#00b894;}}
.sb{{border-color:#00f0ff;background:rgba(0,240,255,0.1);color:#00f0ff;}}
.tag{{display:inline-block;padding:2px 10px;border-radius:6px;font-size:0.82rem;font-weight:bold;}}
.tm{{background:rgba(0,240,255,0.15);border:1px solid #00f0ff;color:#00f0ff;}}
.tl{{background:rgba(255,165,0,0.15);border:1px solid orange;color:orange;}}
.warn{{background:rgba(255,193,7,0.1);border:2px solid #ffc107;border-radius:12px;padding:14px;margin-top:10px;}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────
st.title("🔄 RAMBO — محوّل ملفات TLL" if ar else "🔄 RAMBO — TLL File Converter")
st.markdown(f"<h3 style='text-align:center;'>{'⚡ ارفع ملف النت المرتب + ملفك الشغال ← يولّد ملف لشاشتك بنفس الترتيب' if ar else '⚡ Upload sorted net file + your working file → sorted file for your TV'}</h3>", unsafe_allow_html=True)
st.write("---")

# ─────────────────────────────────────────────
# STEP 1: رفع الملفين
# ─────────────────────────────────────────────
st.markdown(f"### <span class='badge'>1</span> {'ارفع الملفين' if ar else 'Upload Both Files'}", unsafe_allow_html=True)

col_n, col_arr, col_m = st.columns([5,1,5])

with col_n:
    st.markdown("<div class='file-net'>", unsafe_allow_html=True)
    st.markdown(f"**{'📡 ملف النت المرتب' if ar else '📡 Sorted Net File'}**")
    st.caption("مرتب بس مش لموديلك — هنأخذ منه الترتيب والقنوات" if ar else "Sorted but not your model — we take channels & order from it")
    up_net = st.file_uploader("", type=["TLL","bak"], key=f"net_{st.session_state.net_key}", label_visibility="collapsed")
    if up_net:
        b = up_net.read()
        if st.session_state.net_name != up_net.name:
            st.session_state.net_bytes = b; st.session_state.net_name = up_net.name
            st.session_state.net_info = parse_tll(b)
            st.session_state.done = False; st.session_state.result_bytes = None
    ni = st.session_state.net_info
    if ni:
        t = "<span class='tag tm'>Modern</span>" if ni['is_modern'] else "<span class='tag tl'>Legacy</span>"
        st.markdown(f"✅ **{ni['model']}** | {ni['ch_count']:,} ch | {t}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_arr:
    st.markdown("<div style='text-align:center;font-size:2.5rem;color:#ff007f;margin-top:70px;'>➜</div>", unsafe_allow_html=True)

with col_m:
    st.markdown("<div class='file-my'>", unsafe_allow_html=True)
    st.markdown(f"**{'📺 ملفك الشغال على شاشتك' if ar else '📺 Your Working TV File'}**")
    st.caption("شغال على شاشتك — هنأخذ منه الهيكل التقني والبلد" if ar else "Works on your TV — we take technical structure & country from it")
    up_my = st.file_uploader("", type=["TLL","bak"], key=f"my_{st.session_state.my_key}", label_visibility="collapsed")
    if up_my:
        b = up_my.read()
        if st.session_state.my_name != up_my.name:
            st.session_state.my_bytes = b; st.session_state.my_name = up_my.name
            st.session_state.my_info = parse_tll(b)
            st.session_state.done = False; st.session_state.result_bytes = None
    mi = st.session_state.my_info
    if mi:
        t = "<span class='tag tm'>Modern</span>" if mi['is_modern'] else "<span class='tag tl'>Legacy</span>"
        st.markdown(f"✅ **{mi['model']}** | {mi['ch_count']:,} ch | {t}", unsafe_allow_html=True)
        st.markdown(f"🌍 `{mi.get('display','')}`")
    st.markdown("</div>", unsafe_allow_html=True)

ni = st.session_state.net_info
mi = st.session_state.my_info

if ni and mi:
    nm, mm = ni['is_modern'], mi['is_modern']
    ctype = f"{'Modern' if nm else 'Legacy'} ➜ {'Modern' if mm else 'Legacy'}"
    st.info(f"**{'نوع التحويل:' if ar else 'Conversion type:'}** {ctype} {'(مع Fallback للترددات المختلفة ✅)' if ar else '(with Fallback for different frequencies ✅)'}")

if not ni or not mi:
    st.info("⬆️ " + ("ارفع الملفين للبدء." if ar else "Upload both files to start."))
    st.stop()

st.write("---")

# ─────────────────────────────────────────────
# STEP 2: الموديل والبلد
# ─────────────────────────────────────────────
st.markdown(f"### <span class='badge'>2</span> {'اضبط الموديل وبلد البث' if ar else 'Set Model & Country'}", unsafe_allow_html=True)

col_mod, col_ctr = st.columns(2)

with col_mod:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**🖥️ {'الموديل النهائي للملف' if ar else 'Final Model'}**")
    st.caption(f"{'من ملف النت:' if ar else 'From net file:'} `{ni['model']}` | {'من ملفك:' if ar else 'From your file:'} `{mi['model']}`")
    keep_m = "— " + ("استخدم موديل ملف النت" if ar else "Use net file model") + " —"
    sel_m = st.selectbox("", [keep_m]+LG_MODELS, key="selm", label_visibility="collapsed")
    man_m = st.text_input("", placeholder="أو اكتب موديلك يدوياً / Or type manually", key="manm", label_visibility="collapsed").strip()
    final_model = man_m if man_m else ("" if sel_m==keep_m else sel_m)
    st.markdown(f"**{'✅ الموديل النهائي:' if ar else '✅ Final model:'} `{final_model or ni['model']}`**")
    st.markdown("</div>", unsafe_allow_html=True)

with col_ctr:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**🌍 {'بلد البث' if ar else 'Broadcast Country'}**")
    st.caption(f"{'البلد الحالي في ملفك:' if ar else 'Current in your file:'} `{mi.get('display','')}`")
    keep_c = "— " + ("استخدم بلد ملفك الشغال" if ar else "Use working file country") + " —"
    sel_c = st.selectbox("", [keep_c]+list(COUNTRIES.keys()), key="selc", label_visibility="collapsed")
    final_country = "" if sel_c==keep_c else sel_c
    if final_country:
        st.success(f"✅ **{final_country}** → `{COUNTRIES[final_country]['c3']}`")
    else:
        st.info(f"{'✅ سيستخدم:' if ar else '✅ Will use:'} `{mi.get('display','')}`")
    st.markdown(f"<div class='warn'>⚠️ {'اختر نفس البلد المضبوط على شاشتك لتجنب Cloning Error 8' if ar else 'Select same country as your TV to avoid Cloning Error 8'}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
cb, _, _ = st.columns([2,1,1])
with cb:
    if st.button("🔄 " + ("تحويل الآن" if ar else "Convert Now"), use_container_width=True):
        with st.spinner("⏳ " + ("جاري التحويل..." if ar else "Converting...")):
            res, preview, skipped, ctype = do_convert(
                st.session_state.net_info, st.session_state.my_info,
                final_model, final_country
            )
        st.session_state.result_bytes = res
        st.session_state.preview      = preview
        st.session_state.skipped      = skipped
        st.session_state.done         = True
        st.rerun()

# ─────────────────────────────────────────────
# STEP 3: النتيجة
# ─────────────────────────────────────────────
if st.session_state.done and st.session_state.result_bytes:
    st.write("---")
    st.markdown(f"### <span class='badge'>3</span> {'النتيجة' if ar else 'Result'}", unsafe_allow_html=True)
    st.success("🎉 " + ("تم التحويل بنجاح!" if ar else "Conversion successful!"))

    preview = st.session_state.preview
    skipped = st.session_state.skipped
    matched  = len([p for p in preview if '✅' in p[3]])
    fallback = len([p for p in preview if '🔄' in p[3]])

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='stat sg'><b style='font-size:1.6rem;'>{len(preview)}</b><br>{'إجمالي القنوات' if ar else 'Total Channels'}</div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='stat sg'><b style='font-size:1.6rem;'>{matched}</b><br>{'تردد مطابق ✅' if ar else 'Exact Match ✅'}</div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='stat sb'><b style='font-size:1.6rem;'>{fallback}</b><br>{'Fallback 🔄' if ar else 'Fallback 🔄'}</div>", unsafe_allow_html=True)

    st.write("")

    if preview:
        with st.expander(f"📋 {'معاينة القنوات' if ar else 'Channel Preview'} ({len(preview)})", expanded=False):
            scroll = st.container(height=300)
            with scroll:
                h1,h2,h3,h4 = st.columns([1,4,2,3])
                h1.markdown("**#**"); h2.markdown(f"**{'القناة' if ar else 'Channel'}**")
                h3.markdown(f"**{'التردد' if ar else 'Freq'}**"); h4.markdown(f"**{'المصدر' if ar else 'Source'}**")
                for p in preview[:300]:
                    c1,c2,c3,c4 = st.columns([1,4,2,3])
                    c1.write(p[0]); c2.write(p[1]); c3.write(f"`{p[2]}`"); c4.write(p[3])

    st.write("")
    cd1, cd2 = st.columns([3,1])
    with cd1:
        st.download_button(
            "📥 " + ("تحميل الملف المحوّل (GlobalClone00001.TLL)" if ar else "Download Converted File"),
            data=st.session_state.result_bytes,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream",
            use_container_width=True,
        )
    with cd2:
        if st.button("🔄 " + ("من جديد" if ar else "Reset"), key="rst"):
            for k in ['net_bytes','net_name','net_info','my_bytes','my_name','my_info',
                      'result_bytes','done','preview','skipped']:
                st.session_state[k] = None if 'bytes' in k or 'name' in k else ({} if 'info' in k else ([] if k in ['preview','skipped'] else False))
            st.session_state.net_key+=1; st.session_state.my_key+=1; st.rerun()

    st.markdown(f"""<div class='warn'>
💡 <b>{'ملحوظة:' if ar else 'Note:'}</b>
{'إذا لم تظهر القنوات: إعدادات ← القنوات ← مدير القنوات ← تعديل كل القنوات ← تحديد الكل ← استعادة' if ar else 'If channels missing: Settings → Channels → Channel Manager → Edit All Channels → Select All → Restore'}
</div>""", unsafe_allow_html=True)
