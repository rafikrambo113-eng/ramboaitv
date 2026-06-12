import streamlit as st
import json
import re
import base64
import xml.etree.ElementTree as ET
from io import BytesIO, StringIO
import zipfile

st.set_page_config(page_title="محول ملفات القنوات", page_icon="🔄", layout="wide")

# ─── CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Cairo:wght@400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
}

.main {
    background: radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%) !important;
}

section[data-testid="stSidebar"] { display: none !important; }

#MainMenu, header, footer { visibility: hidden !important; }

h1 {
    color: #ff007f !important;
    text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.5) !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900 !important;
    text-align: center !important;
    font-size: 40px !important;
}

h2, h3 {
    color: #00f0ff !important;
    text-shadow: 0 0 5px #00f0ff !important;
    font-family: 'Cairo', sans-serif !important;
    font-weight: 700 !important;
}

p, label, div, span {
    color: #e0e0e0 !important;
    font-size: 17px !important;
    line-height: 1.9 !important;
}

.stButton>button {
    background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
    color: #fff !important;
    border: 2px solid #ff007f !important;
    border-radius: 14px !important;
    font-weight: bold !important;
    font-size: 18px !important;
    padding: 12px 30px !important;
    box-shadow: 0 0 15px rgba(255,0,127,0.4) !important;
    font-family: 'Cairo' !important;
    width: 100% !important;
}

.stDownloadButton>button {
    background: linear-gradient(135deg, #00f0ff 0%, #0077aa 100%) !important;
    color: #000 !important;
    border: 2px solid #00f0ff !important;
    border-radius: 14px !important;
    font-weight: bold !important;
    font-size: 18px !important;
    padding: 12px 30px !important;
    box-shadow: 0 0 15px rgba(0,240,255,0.4) !important;
    font-family: 'Cairo' !important;
    width: 100% !important;
}

.stSelectbox>div>div, .stTextInput>div>div>input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid #00f0ff !important;
    color: #fff !important;
    border-radius: 10px !important;
}

.info-box {
    background: rgba(0,240,255,0.1);
    border: 1px solid #00f0ff;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 10px 0;
    direction: rtl;
}

.success-box {
    background: rgba(255,0,127,0.1);
    border: 1px solid #ff007f;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 10px 0;
    direction: rtl;
    text-align: center;
}

.step-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid #444;
    border-radius: 12px;
    padding: 14px 18px;
    margin: 8px 0;
}

hr { border-color: #00f0ff !important; opacity: 0.4 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Helper Functions ───

COUNTRIES = {
    "مصر 🇪🇬": "EGY",
    "السعودية 🇸🇦": "SAU",
    "الإمارات 🇦🇪": "ARE",
    "الكويت 🇰🇼": "KWT",
    "قطر 🇶🇦": "QAT",
    "البحرين 🇧🇭": "BHR",
    "عُمان 🇴🇲": "OMN",
    "الأردن 🇯🇴": "JOR",
    "لبنان 🇱🇧": "LBN",
    "العراق 🇮🇶": "IRQ",
    "سوريا 🇸🇾": "SYR",
    "ليبيا 🇱🇾": "LBY",
    "تونس 🇹🇳": "TUN",
    "الجزائر 🇩🇿": "DZA",
    "المغرب 🇲🇦": "MAR",
    "السودان 🇸🇩": "SDN",
}

COUNTRY_NAMES_EN = {
    "EGY": "Egypt", "SAU": "Saudi Arabia", "ARE": "United Arab Emirates",
    "KWT": "Kuwait", "QAT": "Qatar", "BHR": "Bahrain", "OMN": "Oman",
    "JOR": "Jordan", "LBN": "Lebanon", "IRQ": "Iraq", "SYR": "Syria",
    "LBY": "Libya", "TUN": "Tunisia", "DZA": "Algeria", "MAR": "Morocco",
    "SDN": "Sudan",
}

def detect_format(content: str) -> str:
    """اكتشاف صيغة الملف"""
    if '<legacybroadcast>' in content:
        return 'modern'
    elif '<ITEM>' in content or '<item>' in content:
        return 'legacy'
    else:
        return 'unknown'

def extract_model_info(content: str) -> dict:
    """استخراج معلومات الموديل"""
    info = {}
    m = re.search(r'<ModelName[^>]*>([^<]+)</ModelName>', content)
    if m: info['model'] = m.group(1)
    m = re.search(r'<BroadcastCountrySetting[^>]*>([^<]+)</BroadcastCountrySetting>', content)
    if m: info['country'] = m.group(1)
    m = re.search(r'<PlatformVersion>([^<]+)</PlatformVersion>', content)
    if m: info['platform'] = m.group(1)
    m = re.search(r'<DTVInfo[^>]*>([^<]+)</DTVInfo>', content)
    if m: info['dtv'] = m.group(1)
    return info

def decode_channel_name(b64_name: str) -> str:
    """فك تشفير اسم القناة"""
    try:
        decoded = base64.b64decode(b64_name).decode('utf-8').rstrip('\x00').strip()
        return decoded if decoded else "Unknown"
    except:
        return "Unknown"

def extract_modern_channels(content: str) -> list:
    """استخراج القنوات من الصيغة الحديثة JSON"""
    lb_match = re.search(r'<legacybroadcast>(.*?)</legacybroadcast>', content, re.DOTALL)
    if not lb_match:
        return []
    try:
        lb_data = json.loads(lb_match.group(1))
        channels = lb_data.get('channelList', [])
        result = []
        for ch in channels:
            if ch.get('deleted') or ch.get('disabled'):
                continue
            name = ch.get('channelName', '')
            if not name:
                name = decode_channel_name(ch.get('chNameBase64', ''))
            result.append({
                'major': ch.get('majorNumber', 0),
                'minor': ch.get('minorNumber', 0),
                'physicalNum': ch.get('physicalNumber', 0),
                'chName': name,
                'sourceIndex': ch.get('sourceIndex', 'SATELLITE DIGITAL'),
                'frequency': ch.get('frequency', 0),
                'symbolRate': ch.get('symbolRate', 27500) if ch.get('symbolRate') else 27500,
                'isSkipped': 1 if ch.get('skipped') else 0,
                'isLocked': 1 if ch.get('locked') else 0,
                'isBlocked': 0,
                'satelliteId': ch.get('satelliteId', '3530'),
                'programNum': ch.get('programNum', 0),
                'TSID': ch.get('TSID', 0),
                'ONID': ch.get('ONID', 0),
                'scrambled': 1 if ch.get('scrambled') else 0,
                'hdStatus': ch.get('hdStatus', 0),
                'transSystem': ch.get('transSystem', 'DVBS'),
            })
        return result
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        return []

def extract_legacy_channels(content: str) -> list:
    """استخراج القنوات من الصيغة القديمة XML"""
    channels = []
    try:
        root = ET.fromstring(content)
        channel_section = root.find('.//CHANNEL')
        if channel_section is None:
            return []
        for item in channel_section.findall('ITEM'):
            def g(tag, default=''):
                el = item.find(tag)
                return el.text if el is not None else default
            channels.append({
                'major': int(g('major', '0')),
                'minor': int(g('minor', '0')),
                'physicalNum': int(g('PhysicalNum', '0')),
                'chName': g('chName', 'Unknown'),
                'sourceIndex': g('sourceIndex', 'SATELLITE DIGITAL'),
                'frequency': int(g('frequency', '0')),
                'symbolRate': int(g('symbolRate', '27500')),
                'isSkipped': int(g('isSkipped', '0')),
                'isLocked': int(g('isLocked', '0')),
                'isBlocked': 0,
                'satelliteId': g('satelliteId', '3530'),
                'programNum': int(g('programNum', '0')),
                'TSID': int(g('TSID', '0')),
                'ONID': int(g('ONID', '0')),
                'scrambled': int(g('scrambled', '0')),
                'hdStatus': int(g('hdStatus', '0')),
                'transSystem': g('transSystem', 'DVBS'),
            })
    except Exception as e:
        st.error(f"خطأ في قراءة الملف القديم: {e}")
    return channels

def build_legacy_xml(channels: list, model_name: str, country_code: str) -> str:
    """بناء ملف XML قديم"""
    country_en = COUNTRY_NAMES_EN.get(country_code, country_code)
    lines = []
    lines.append('<?xml version="1.0"?>')
    lines.append('<TLLDATA>')
    lines.append('\t<ModelInfo>')
    lines.append(f'\t\t<ModelName type="0">{model_name}</ModelName>')
    lines.append('\t\t<DTVInfo type="0">DTV_DVB</DTVInfo>')
    lines.append(f'\t\t<BroadcastCountrySetting type="0">{country_code}</BroadcastCountrySetting>')
    lines.append('\t\t<country type="0">JA</country>')
    lines.append('\t</ModelInfo>')
    lines.append('\t<CHANNEL>')
    
    for i, ch in enumerate(channels):
        lines.append('\t\t<ITEM>')
        lines.append(f'\t\t\t<major>{ch["major"]}</major>')
        lines.append(f'\t\t\t<minor>{ch["minor"]}</minor>')
        lines.append(f'\t\t\t<PhysicalNum>{ch["physicalNum"]}</PhysicalNum>')
        lines.append(f'\t\t\t<chName>{ch["chName"]}</chName>')
        lines.append(f'\t\t\t<sourceIndex>{ch["sourceIndex"]}</sourceIndex>')
        lines.append(f'\t\t\t<frequency>{ch["frequency"]}</frequency>')
        lines.append(f'\t\t\t<symbolRate>{ch["symbolRate"]}</symbolRate>')
        lines.append(f'\t\t\t<isSkipped>{ch["isSkipped"]}</isSkipped>')
        lines.append(f'\t\t\t<isLocked>{ch["isLocked"]}</isLocked>')
        lines.append(f'\t\t\t<isBlocked>0</isBlocked>')
        lines.append(f'\t\t\t<satelliteId>{ch["satelliteId"]}</satelliteId>')
        lines.append(f'\t\t\t<programNum>{ch["programNum"]}</programNum>')
        lines.append(f'\t\t\t<TSID>{ch["TSID"]}</TSID>')
        lines.append(f'\t\t\t<ONID>{ch["ONID"]}</ONID>')
        lines.append(f'\t\t\t<scrambled>{ch["scrambled"]}</scrambled>')
        lines.append(f'\t\t\t<hdStatus>{ch["hdStatus"]}</hdStatus>')
        lines.append(f'\t\t\t<transSystem>{ch["transSystem"]}</transSystem>')
        lines.append('\t\t</ITEM>')
    
    lines.append('\t</CHANNEL>')
    lines.append('</TLLDATA>')
    return '\n'.join(lines)

def build_modern_json(channels: list, model_name: str, country_code: str) -> str:
    """بناء ملف حديث JSON"""
    country_en = COUNTRY_NAMES_EN.get(country_code, country_code)
    
    channel_list = []
    for ch in channels:
        name_bytes = ch['chName'].encode('utf-8')
        padded = name_bytes + b'\x00' * (40 - len(name_bytes))
        b64_name = base64.b64encode(padded[:40]).decode('ascii')
        
        channel_list.append({
            "disabled": False,
            "cellID": 0,
            "videoStreamType": 27,
            "specialData": 0,
            "pcrPid": 8191,
            "sourceIndex": ch['sourceIndex'],
            "regionId": 0,
            "audioDesc": False,
            "signalLossDay": 0,
            "homeTP": False,
            "primaryCh": False,
            "userSelCHNo": True,
            "altPhysicalNum": 0,
            "isDVBI": False,
            "userSubtitleLangCode": 0,
            "virtualChannel": False,
            "majorNumber": ch['major'],
            "physicalNumber": ch['physicalNum'],
            "skipped": ch['isSkipped'] == 1,
            "minorNumber": ch['minor'],
            "videoPid": 8191,
            "transSystem": ch['transSystem'],
            "deleted": False,
            "validLCN": False,
            "isFVP": False,
            "conflict": False,
            "setIdHandle": 0,
            "locked": ch['isLocked'] == 1,
            "satelliteId": str(ch['satelliteId']),
            "hdStatus": ch['hdStatus'],
            "scrambled": ch['scrambled'] == 1,
            "programNum": ch['programNum'],
            "TSID": ch['TSID'],
            "ONID": ch['ONID'],
            "frequency": ch['frequency'],
            "channelName": ch['chName'],
            "chNameBase64": b64_name,
            "serviceType": 1,
            "bandwidth": "BW_8M",
        })
    
    lb_data = {
        "modelInfo": {"country": country_en},
        "bouquetList": [],
        "settingIdList": [],
        "channelList": channel_list
    }
    
    iepg_data = {"favoriteChList": [], "modelInfo": {"country": country_code}}
    
    xml_lines = []
    xml_lines.append('<?xml version="1.0"?>')
    xml_lines.append('<TLLDATA>')
    xml_lines.append('\t<ModelInfo>')
    xml_lines.append(f'\t\t<ModelName type="0">{model_name}</ModelName>')
    xml_lines.append('\t\t<DTVInfo type="0">DTV_DVB</DTVInfo>')
    xml_lines.append(f'\t\t<BroadcastCountrySetting type="0">{country_code}</BroadcastCountrySetting>')
    xml_lines.append('\t\t<country type="0">JA</country>')
    xml_lines.append('\t\t<CloneVersion type="1">')
    xml_lines.append('\t\t\t<MajorVersion>200</MajorVersion>')
    xml_lines.append('\t\t\t<MinorVersion>000</MinorVersion>')
    xml_lines.append('\t\t\t<SatelliteDBVersion>500</SatelliteDBVersion>')
    xml_lines.append('\t\t\t<PlatformVersion>webOSTV 25</PlatformVersion>')
    xml_lines.append('\t\t</CloneVersion>')
    xml_lines.append('\t</ModelInfo>')
    xml_lines.append('\t<CHANNEL>')
    xml_lines.append(f'\t\t<iepg>{json.dumps(iepg_data, ensure_ascii=False)}</iepg>')
    xml_lines.append(f'\t\t<legacybroadcast>{json.dumps(lb_data, ensure_ascii=False)}</legacybroadcast>')
    xml_lines.append('\t</CHANNEL>')
    xml_lines.append('</TLLDATA>')
    return '\n'.join(xml_lines)

# ─────────────────────────────────────────────
# واجهة المستخدم
# ─────────────────────────────────────────────

st.markdown("<h1>🔄 محول ملفات القنوات</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00f0ff; font-size:20px; font-weight:700;'>حوّل أي ملف TLL بين الصيغة القديمة والجديدة بضغطة زر</p>", unsafe_allow_html=True)

st.markdown("---")

# ─── الخطوات ───
st.markdown("### 📋 خطوات التحويل")

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.markdown('<div class="step-box"><p style="text-align:center">📁 <b>الخطوة 1</b><br>ارفع ملف TLL من النت</p></div>', unsafe_allow_html=True)
with col_s2:
    st.markdown('<div class="step-box"><p style="text-align:center">⚙️ <b>الخطوة 2</b><br>اختار إعدادات جهازك</p></div>', unsafe_allow_html=True)
with col_s3:
    st.markdown('<div class="step-box"><p style="text-align:center">⬇️ <b>الخطوة 3</b><br>حمّل الملف المحوّل</p></div>', unsafe_allow_html=True)

st.markdown("---")

# ─── رفع الملف ───
st.markdown("### 📁 الخطوة 1: ارفع الملف")
st.markdown('<div class="info-box"><p>ارفع ملف <b>TLL</b> أو <b>BAK</b> اللي لقيته على النت — الموقع هيكتشف صيغته تلقائياً</p></div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "اختار ملف TLL أو BAK",
    type=['tll', 'bak', 'TLL', 'BAK'],
    help="ارفع ملف قنوات إل جي بأي صيغة"
)

if uploaded_file:
    content = uploaded_file.read().decode('utf-8', errors='ignore')
    fmt = detect_format(content)
    model_info = extract_model_info(content)
    
    col_inf1, col_inf2, col_inf3 = st.columns(3)
    with col_inf1:
        fmt_label = "🆕 حديث (JSON/webOS)" if fmt == 'modern' else "📼 قديم (XML)" if fmt == 'legacy' else "❓ غير معروف"
        st.metric("صيغة الملف", fmt_label)
    with col_inf2:
        st.metric("بلد البث الأصلي", model_info.get('country', '?'))
    with col_inf3:
        if fmt == 'modern':
            chs = extract_modern_channels(content)
        elif fmt == 'legacy':
            chs = extract_legacy_channels(content)
        else:
            chs = []
        st.metric("عدد القنوات", f"{len(chs)} قناة")
    
    if fmt == 'unknown':
        st.error("❌ الملف ده مش صيغة TLL معروفة!")
        st.stop()
    
    st.success(f"✅ تم قراءة الملف بنجاح — {len(chs)} قناة")
    
    # عرض عينة
    if chs:
        with st.expander("👁️ شوف أول 10 قنوات من الملف"):
            for i, ch in enumerate(chs[:10]):
                st.write(f"**{i+1}.** {ch['chName']} | رقم: {ch['major']} | تردد: {ch['frequency']}")
    
    st.markdown("---")
    
    # ─── إعدادات التحويل ───
    st.markdown("### ⚙️ الخطوة 2: إعدادات جهازك")
    
    col_opt1, col_opt2 = st.columns(2)
    
    with col_opt1:
        st.markdown("**📺 صيغة جهازك (الناتج)**")
        if fmt == 'modern':
            target_label = "📼 قديم XML (قبل 2018) — موصى به لجهازك"
            target_format = 'legacy'
            st.info("✅ الملف حديث → سيتم تحويله لصيغة قديمة تناسب جهازك")
        else:
            target_label = "🆕 حديث JSON (webOS 2018+)"
            target_format = 'modern'
            st.info("✅ الملف قديم → سيتم تحويله لصيغة حديثة")
        st.markdown(f"**الصيغة الناتجة:** {target_label}")
    
    with col_opt2:
        st.markdown("**🌍 بلد البث في جهازك**")
        selected_country_ar = st.selectbox(
            "اختار بلدك",
            options=list(COUNTRIES.keys()),
            index=0,
            help="اختار نفس البلد اللي جهازك مضبوط عليه"
        )
        target_country = COUNTRIES[selected_country_ar]
    
    st.markdown("**📺 موديل جهازك (اختياري)**")
    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        custom_model = st.text_input(
            "اكتب موديل جهازك — أو اتركه فاضي يستخدم موديل الملف",
            value="",
            placeholder="مثال: 43LM6300PLA.AFUQLWE",
            help="الموديل موجود على ستيكر في ظهر الشاشة"
        )
    with col_m2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="info-box"><p style="font-size:14px">💡 لو مش عارف الموديل، اتركه فاضي</p></div>', unsafe_allow_html=True)
    
    final_model = custom_model.strip() if custom_model.strip() else model_info.get('model', 'LG_TV_MODEL')
    
    st.markdown("---")
    
    # ─── تحويل وتحميل ───
    st.markdown("### ⬇️ الخطوة 3: حوّل وحمّل")
    
    col_conv1, col_conv2, col_conv3 = st.columns([1, 2, 1])
    with col_conv2:
        if st.button("🔄 ابدأ التحويل الآن", use_container_width=True):
            with st.spinner("⚙️ جاري التحويل..."):
                if target_format == 'legacy':
                    output_content = build_legacy_xml(chs, final_model, target_country)
                else:
                    output_content = build_modern_json(chs, final_model, target_country)
                
                st.session_state['converted'] = output_content
                st.session_state['target_format'] = target_format
                st.session_state['channel_count'] = len(chs)
            st.success("✅ تم التحويل بنجاح!")
    
    if 'converted' in st.session_state and st.session_state.get('converted'):
        output_bytes = st.session_state['converted'].encode('utf-8')
        ch_count = st.session_state.get('channel_count', 0)
        
        st.markdown(f"""
        <div class="success-box">
            <p style="font-size:22px; color:#ff007f; font-weight:bold;">🎉 الملف جاهز!</p>
            <p>✅ {ch_count} قناة تم تحويلها</p>
            <p>✅ بلد البث: {selected_country_ar}</p>
            <p>✅ الموديل: {final_model}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
        with col_d2:
            st.download_button(
                label="⬇️ تحميل GlobalClone00001.TLL",
                data=output_bytes,
                file_name="GlobalClone00001.TLL",
                mime="application/octet-stream",
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("### 📖 طريقة تشغيل الملف على شاشتك")
        st.markdown("""
        <div class="info-box">
        <p>1️⃣ <b>انسخ الملف</b> على فلاشة USB فاضية</p>
        <p>2️⃣ <b>الاسم لازم يكون:</b> <code>GlobalClone00001.TLL</code></p>
        <p>3️⃣ <b>حط الفلاشة</b> في البورت الجنبي للشاشة</p>
        <p>4️⃣ <b>روح Settings</b> ← Channel ← Channel Manager ← Channel Update / Clone</p>
        <p>5️⃣ <b>اختار "Load from USB"</b> أو "Import from USB"</p>
        <p>6️⃣ <b>انتظر</b> لحد ما يخلص ويعمل Restart تلقائياً</p>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="info-box">
    <p style="text-align:center; font-size:19px;">
    ⬆️ ارفع ملف TLL أو BAK من فوق وابدأ التحويل<br><br>
    <b>الموقع بيدعم:</b><br>
    ✅ تحويل ملف <b>حديث (webOS/JSON)</b> → ملف <b>قديم (XML)</b> لجهازك<br>
    ✅ تحويل ملف <b>قديم (XML)</b> → ملف <b>حديث (JSON)</b><br>
    ✅ تغيير بلد البث<br>
    ✅ تغيير موديل الجهاز
    </p>
    </div>
    """, unsafe_allow_html=True)

# ─── الفوتر ───
st.markdown("---")
st.markdown("<p style='text-align:center; font-size:20px; color:#ff007f; font-weight:bold;'>🛠️ DEVELOPER ENG: RAFIK NATHAN</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#e0e0e0;'>📱 +201280339779 &nbsp;|&nbsp; ✉️ rafikrambo113@gmail.com</p>", unsafe_allow_html=True)
whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"
st.link_button("WhatsApp 💬", whatsapp_url)
