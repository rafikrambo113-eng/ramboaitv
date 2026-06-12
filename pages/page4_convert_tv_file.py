import streamlit as st
import json
import re
import base64
import xml.etree.ElementTree as ET

st.set_page_config(page_title="محول ملفات القنوات", page_icon="🔄", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Cairo:wght@400;600;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; direction: rtl !important; }
.main { background: radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%) !important; }
section[data-testid="stSidebar"] { display: none !important; }
#MainMenu, header, footer { visibility: hidden !important; }
h1 {
    color: #ff007f !important;
    text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.5) !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900 !important; text-align: center !important; font-size: 38px !important;
}
h2, h3 { color: #00f0ff !important; font-family: 'Cairo', sans-serif !important; font-weight: 700 !important; }
p, label, div, span { color: #e0e0e0 !important; font-size: 16px !important; line-height: 1.8 !important; }
.stButton>button {
    background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
    color: #fff !important; border: 2px solid #ff007f !important; border-radius: 14px !important;
    font-weight: bold !important; font-size: 17px !important; padding: 12px 30px !important;
    box-shadow: 0 0 15px rgba(255,0,127,0.4) !important; font-family: 'Cairo' !important; width: 100% !important;
}
.stDownloadButton>button {
    background: linear-gradient(135deg, #00f0ff 0%, #0077aa 100%) !important;
    color: #000 !important; border: 2px solid #00f0ff !important; border-radius: 14px !important;
    font-weight: bold !important; font-size: 17px !important; padding: 12px 30px !important;
    box-shadow: 0 0 15px rgba(0,240,255,0.4) !important; font-family: 'Cairo' !important; width: 100% !important;
}
.info-box {
    background: rgba(0,240,255,0.08); border: 1px solid #00f0ff;
    border-radius: 12px; padding: 14px 18px; margin: 8px 0; direction: rtl;
}
.warn-box {
    background: rgba(255,200,0,0.08); border: 1px solid #ffc800;
    border-radius: 12px; padding: 14px 18px; margin: 8px 0; direction: rtl;
}
.success-box {
    background: rgba(0,255,100,0.08); border: 1px solid #00ff64;
    border-radius: 12px; padding: 16px 20px; margin: 10px 0; direction: rtl; text-align: center;
}
.step-box {
    background: rgba(255,255,255,0.04); border: 1px solid #333;
    border-radius: 12px; padding: 14px 18px; margin: 8px 0; text-align: center;
}
hr { border-color: #00f0ff !important; opacity: 0.3 !important; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════
# البيانات الثابتة
# ════════════════════════════════════════════

COUNTRIES = {
    "مصر 🇪🇬": ("EGY", "Egypt"),
    "السعودية 🇸🇦": ("SAU", "Saudi Arabia"),
    "الإمارات 🇦🇪": ("ARE", "United Arab Emirates"),
    "الكويت 🇰🇼": ("KWT", "Kuwait"),
    "قطر 🇶🇦": ("QAT", "Qatar"),
    "البحرين 🇧🇭": ("BHR", "Bahrain"),
    "عُمان 🇴🇲": ("OMN", "Oman"),
    "الأردن 🇯🇴": ("JOR", "Jordan"),
    "لبنان 🇱🇧": ("LBN", "Lebanon"),
    "العراق 🇮🇶": ("IRQ", "Iraq"),
    "سوريا 🇸🇾": ("SYR", "Syria"),
    "ليبيا 🇱🇾": ("LBY", "Libya"),
    "تونس 🇹🇳": ("TUN", "Tunisia"),
    "الجزائر 🇩🇿": ("DZA", "Algeria"),
    "المغرب 🇲🇦": ("MAR", "Morocco"),
    "السودان 🇸🇩": ("SDN", "Sudan"),
}

# الموديلات مرتبة حسب الحجم
LG_MODELS = {
    "━━━ 32 بوصة ━━━": [],
    "32LM6300PLA.AFUQLWE": ["32LM6300PLA.AFUQLWE", "32 بوصة - LM6300 (2020)"],
    "32LQ63006LA.AFUQLWE": ["32LQ63006LA.AFUQLWE", "32 بوصة - LQ6300 (2022)"],
    "32LQ570B6LA.AFUQLWE": ["32LQ570B6LA.AFUQLWE", "32 بوصة - LQ570B (2022)"],
    "32LK500BPLA.AFUQLWE": ["32LK500BPLA.AFUQLWE", "32 بوصة - LK500 (2018)"],
    "32LK610BPLA.AFUQLWE": ["32LK610BPLA.AFUQLWE", "32 بوصة - LK610 (2018)"],
    "━━━ 43 بوصة ━━━ ": [],
    "43LM6300PLA.AFUQLWE": ["43LM6300PLA.AFUQLWE", "43 بوصة - LM6300 (2020)"],
    "43LQ63006LA.AFUQLWE": ["43LQ63006LA.AFUQLWE", "43 بوصة - LQ6300 (2022)"],
    "43UQ75006LF.AFUQLWE": ["43UQ75006LF.AFUQLWE", "43 بوصة - UQ7500 (2022)"],
    "43UR78006LK.AFUQLWE": ["43UR78006LK.AFUQLWE", "43 بوصة - UR7800 (2023)"],
    "43UK6300PLB.AFUQLWE": ["43UK6300PLB.AFUQLWE", "43 بوصة - UK6300 (2018)"],
    "43LK5900PLA.AFUQLWE": ["43LK5900PLA.AFUQLWE", "43 بوصة - LK5900 (2018)"],
    "43UJ634V.AFU": ["43UJ634V.AFU", "43 بوصة - UJ634V (2017)"],
    "━━━ 49 بوصة ━━━  ": [],
    "49UJ634V.AFU": ["49UJ634V.AFU", "49 بوصة - UJ634V (2017)"],
    "49UK6300PLB.AFUQLWE": ["49UK6300PLB.AFUQLWE", "49 بوصة - UK6300 (2018)"],
    "49SM8600PLA.AFUQLWE": ["49SM8600PLA.AFUQLWE", "49 بوصة - SM8600 (2019)"],
    "━━━ 50 بوصة ━━━   ": [],
    "50UQ80006LJ.AFUQLWE": ["50UQ80006LJ.AFUQLWE", "50 بوصة - UQ8000 (2022)"],
    "50UR78006LK.AFUQLWE": ["50UR78006LK.AFUQLWE", "50 بوصة - UR7800 (2023)"],
    "50UP75006LF.AFUQLWE": ["50UP75006LF.AFUQLWE", "50 بوصة - UP7500 (2021)"],
    "50NANO756PA.AFUQLWE": ["50NANO756PA.AFUQLWE", "50 بوصة - NANO75 (2021)"],
    "━━━ 55 بوصة ━━━    ": [],
    "55UA85006LA.DFUYLWE": ["55UA85006LA.DFUYLWE", "55 بوصة - UA8500 (2024)"],
    "55UQ80006LJ.AFUQLWE": ["55UQ80006LJ.AFUQLWE", "55 بوصة - UQ8000 (2022)"],
    "55UR78006LK.AFUQLWE": ["55UR78006LK.AFUQLWE", "55 بوصة - UR7800 (2023)"],
    "55NANO756PA.AFUQLWE": ["55NANO756PA.AFUQLWE", "55 بوصة - NANO75 (2021)"],
    "55SM8600PLA.AFUQLWE": ["55SM8600PLA.AFUQLWE", "55 بوصة - SM8600 (2019)"],
    "55UK6300PLB.AFUQLWE": ["55UK6300PLB.AFUQLWE", "55 بوصة - UK6300 (2018)"],
    "55UJ634V.AFU": ["55UJ634V.AFU", "55 بوصة - UJ634V (2017)"],
    "━━━ 65 بوصة ━━━     ": [],
    "65UQ80006LJ.AFUQLWE": ["65UQ80006LJ.AFUQLWE", "65 بوصة - UQ8000 (2022)"],
    "65UR78006LK.AFUQLWE": ["65UR78006LK.AFUQLWE", "65 بوصة - UR7800 (2023)"],
    "65NANO756PA.AFUQLWE": ["65NANO756PA.AFUQLWE", "65 بوصة - NANO75 (2021)"],
    "65SM9000PLA.AFUQLWE": ["65SM9000PLA.AFUQLWE", "65 بوصة - SM9000 (2019)"],
    "━━━ 75 بوصة ━━━      ": [],
    "75UQ80006LJ.AFUQLWE": ["75UQ80006LJ.AFUQLWE", "75 بوصة - UQ8000 (2022)"],
    "75UR78006LK.AFUQLWE": ["75UR78006LK.AFUQLWE", "75 بوصة - UR7800 (2023)"],
    "75NANO756PA.AFUQLWE": ["75NANO756PA.AFUQLWE", "75 بوصة - NANO75 (2021)"],
}

# قائمة الاختيارات للـ selectbox
MODEL_OPTIONS = ["✏️ اكتب موديلك يدوياً"]
for k, v in LG_MODELS.items():
    if not v:  # separator
        MODEL_OPTIONS.append(k)
    else:
        MODEL_OPTIONS.append(f"{v[1]}  [{v[0]}]")

# ════════════════════════════════════════════
# دوال المعالجة
# ════════════════════════════════════════════

def detect_format(content):
    if '<legacybroadcast>' in content:
        return 'modern'
    elif '<ITEM>' in content or '<item>' in content:
        return 'legacy'
    return 'unknown'

def extract_model_info(content):
    info = {}
    for tag, key in [('ModelName', 'model'), ('BroadcastCountrySetting', 'country'), 
                      ('PlatformVersion', 'platform')]:
        m = re.search(rf'<{tag}[^>]*>([^<]+)</{tag}>', content)
        if m: info[key] = m.group(1)
    return info

def decode_b64_name(b64):
    try:
        return base64.b64decode(b64).decode('utf-8').rstrip('\x00').strip() or "Unknown"
    except:
        return "Unknown"

def extract_modern_channels(content):
    lb_match = re.search(r'<legacybroadcast>(.*?)</legacybroadcast>', content, re.DOTALL)
    if not lb_match:
        return [], []
    lb_data = json.loads(lb_match.group(1))
    all_chs = lb_data.get('channelList', [])
    
    result = []
    for ch in all_chs:
        if ch.get('deleted') or ch.get('disabled'):
            continue
        name = ch.get('channelName', '') or decode_b64_name(ch.get('chNameBase64', ''))
        
        # تحويل القناة مع الاحتفاظ بكل الحقول المهمة
        result.append({
            'majorNumber':    ch.get('majorNumber', 0),
            'minorNumber':    ch.get('minorNumber', 0),
            'physicalNumber': ch.get('physicalNumber', 0),
            'channelName':    name,
            'sourceIndex':    ch.get('sourceIndex', 'SATELLITE DIGITAL'),
            'frequency':      ch.get('frequency', 0),
            'symbolRate':     ch.get('symbolRate', 27500) or 27500,
            'skipped':        ch.get('skipped', False),
            'locked':         ch.get('locked', False),
            'satelliteId':    str(ch.get('satelliteId', '3530')),
            'programNum':     ch.get('programNum', 0),
            'TSID':           ch.get('TSID', 0),
            'ONID':           ch.get('ONID', 0),
            'SVCID':          ch.get('SVCID', 0),
            'scrambled':      ch.get('scrambled', False),
            'hdStatus':       ch.get('hdStatus', 0),
            'transSystem':    ch.get('transSystem', 'DVBS'),
            'serviceType':    ch.get('serviceType', 1),
            'tpId':           ch.get('tpId', ''),
            'networkId':      ch.get('networkId', 0),
            'videoStreamType':ch.get('videoStreamType', 27),
            'specialData':    ch.get('specialData', 0),
            'mapType':        ch.get('mapType', 'CUSTOMIZED'),
            'setIdHandle':    ch.get('setIdHandle', 0),
            'Invisible':      ch.get('Invisible', False),
            'factoryDefault': ch.get('factoryDefault', False),
            'pcrPid':         ch.get('pcrPid', 8191),
            'videoPid':       ch.get('videoPid', 8191),
            'audioPid':       ch.get('audioPid', 8191),
            'dvbss2':         ch.get('dvbss2', 0),
            'coderate':       ch.get('coderate', 0),
            'chNameBase64':   ch.get('chNameBase64', ''),
        })
    
    setting_list = lb_data.get('settingIdList', [])
    return result, setting_list

def extract_legacy_channels(content):
    channels = []
    try:
        root = ET.fromstring(content)
        ch_sec = root.find('.//CHANNEL')
        if ch_sec is None:
            return [], []
        for item in ch_sec.findall('ITEM'):
            def g(tag, default=''):
                el = item.find(tag)
                return el.text if el is not None and el.text else default
            channels.append({
                'majorNumber':    int(g('major', '0')),
                'minorNumber':    int(g('minor', '0')),
                'physicalNumber': int(g('PhysicalNum', '0')),
                'channelName':    g('chName', 'Unknown'),
                'sourceIndex':    g('sourceIndex', 'SATELLITE DIGITAL'),
                'frequency':      int(g('frequency', '0')),
                'symbolRate':     int(g('symbolRate', '27500')),
                'skipped':        g('isSkipped', '0') == '1',
                'locked':         g('isLocked', '0') == '1',
                'satelliteId':    g('satelliteId', '3530'),
                'programNum':     int(g('programNum', '0')),
                'TSID':           int(g('TSID', '0')),
                'ONID':           int(g('ONID', '0')),
                'SVCID':          int(g('SVCID', '0')),
                'scrambled':      g('scrambled', '0') == '1',
                'hdStatus':       int(g('hdStatus', '0')),
                'transSystem':    g('transSystem', 'DVBS'),
                'serviceType':    int(g('serviceType', '1')),
                'tpId':           g('tpId', ''),
                'networkId':      int(g('networkId', '0')),
                'videoStreamType':int(g('videoStreamType', '27')),
                'specialData':    int(g('specialData', '0')),
                'mapType':        'CUSTOMIZED',
                'setIdHandle':    0,
                'Invisible':      False,
                'factoryDefault': False,
                'pcrPid':         8191,
                'videoPid':       8191,
                'audioPid':       8191,
                'dvbss2':         0,
                'coderate':       0,
                'chNameBase64':   '',
            })
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
    return channels, []

def build_b64_name(name):
    try:
        nb = name.encode('utf-8')
        padded = nb + b'\x00' * max(0, 40 - len(nb))
        return base64.b64encode(padded[:40]).decode('ascii')
    except:
        return ''

def build_modern_tll(channels, setting_list, model_name, country_code, country_en, fix_invisible):
    """بناء ملف حديث JSON - مع إصلاح Invisible و skipped"""
    channel_list = []
    for i, ch in enumerate(channels):
        b64 = ch.get('chNameBase64') or build_b64_name(ch['channelName'])
        
        invisible = ch.get('Invisible', False)
        skipped   = ch.get('skipped', False)
        maptype   = ch.get('mapType', 'CUSTOMIZED')
        
        # إصلاح المشكلة الأساسية
        if fix_invisible:
            invisible = False
            skipped   = False
            maptype   = 'CUSTOMIZED'

        channel_list.append({
            "disabled":          False,
            "cellID":            0,
            "videoStreamType":   ch.get('videoStreamType', 27),
            "specialData":       ch.get('specialData', 0),
            "pcrPid":            ch.get('pcrPid', 8191),
            "sourceIndex":       ch.get('sourceIndex', 'SATELLITE DIGITAL'),
            "regionId":          0,
            "audioDesc":         False,
            "signalLossDay":     0,
            "homeTP":            False,
            "primaryCh":         False,
            "userSelCHNo":       True,
            "altPhysicalNum":    0,
            "isDVBI":            False,
            "userSubtitleLangCode": 0,
            "virtualChannel":    False,
            "majorNumber":       ch['majorNumber'],
            "physicalNumber":    ch['physicalNumber'],
            "skipped":           skipped,
            "minorNumber":       ch['minorNumber'],
            "videoPid":          ch.get('videoPid', 8191),
            "transSystem":       ch.get('transSystem', 'DVBS'),
            "deleted":           False,
            "validLCN":          False,
            "isFVP":             False,
            "conflict":          False,
            "setIdHandle":       ch.get('setIdHandle', 0),
            "astraMfCh":         False,
            "optrBlocked":       False,
            "factoryDefault":    ch.get('factoryDefault', False),
            "Invisible":         invisible,
            "networkId":         ch.get('networkId', 0),
            "locked":            ch.get('locked', False),
            "satelliteId":       ch['satelliteId'],
            "hdStatus":          ch.get('hdStatus', 0),
            "coderate":          ch.get('coderate', 0),
            "serviceIdentifier": 0,
            "dvbss2":            ch.get('dvbss2', 0),
            "chNameByte":        False,
            "solveNeed":         False,
            "prev_tsId":         ch.get('TSID', 0),
            "LCNPriority":       0,
            "userDualmonoType":  0,
            "audioPid":          ch.get('audioPid', 8191),
            "chNameBase64":      b64,
            "nitVersion":        0,
            "ipChannel":         False,
            "userCustomize":     False,
            "frequency":         ch.get('frequency', 0),
            "channelName":       ch['channelName'],
            "discarded":         False,
            "orgPhysicalNum":    0,
            "disableUpdate":     False,
            "prev_onId":         ch.get('ONID', 0),
            "adultChannel":      0,
            "mapType":           maptype,
            "audioSetbyUser":    False,
            "fineTuned":         False,
            "conflictNumber":    0,
            "programNum":        ch.get('programNum', 0),
            "subtitleSetbyUser": False,
            "userEditChNumber":  True,
            "bandwidth":         "BW_8M",
            "rfIpChannel":       False,
            "userAudio":         8191,
            "SVCID":             ch.get('SVCID', 0),
            "TSID":              ch.get('TSID', 0),
            "isMultipleLCN":     False,
            "numUnSel":          False,
            "scrambled":         ch.get('scrambled', False),
            "stillPicture":      False,
            "tpId":              ch.get('tpId', ''),
            "usedChName":        False,
            "altChannel":        False,
            "serviceType":       ch.get('serviceType', 1),
            "ac3AudioType":      False,
            "isOtherBroadcast":  False,
            "ONID":              ch.get('ONID', 0),
            "userSubtitle":      8191,
            "profileV2":         0,
        })

    lb_data = {
        "modelInfo":    {"country": country_en},
        "bouquetList":  [],
        "settingIdList": setting_list,
        "channelList":  channel_list,
    }
    iepg_data = {"favoriteChList": [], "modelInfo": {"country": country_code}}

    lines = ['<?xml version="1.0"?>', '<TLLDATA>', '\t<ModelInfo>',
             f'\t\t<ModelName type="0">{model_name}</ModelName>',
             '\t\t<DTVInfo type="0">DTV_DVB</DTVInfo>',
             f'\t\t<BroadcastCountrySetting type="0">{country_code}</BroadcastCountrySetting>',
             '\t\t<country type="0">JA</country>',
             '\t\t<CloneVersion type="1">',
             '\t\t\t<MajorVersion>200</MajorVersion>',
             '\t\t\t<MinorVersion>000</MinorVersion>',
             '\t\t\t<SatelliteDBVersion>500</SatelliteDBVersion>',
             '\t\t\t<PlatformVersion>webOSTV 25</PlatformVersion>',
             '\t\t</CloneVersion>', '\t</ModelInfo>', '\t<CHANNEL>',
             f'\t\t<iepg>{json.dumps(iepg_data, ensure_ascii=False)}</iepg>',
             f'\t\t<legacybroadcast>{json.dumps(lb_data, ensure_ascii=False, separators=(",",":"))}</legacybroadcast>',
             '\t</CHANNEL>', '</TLLDATA>']
    return '\n'.join(lines)

def build_legacy_tll(channels, model_name, country_code):
    """بناء ملف قديم XML"""
    lines = ['<?xml version="1.0"?>', '<TLLDATA>', '\t<ModelInfo>',
             f'\t\t<ModelName type="0">{model_name}</ModelName>',
             '\t\t<DTVInfo type="0">DTV_DVB</DTVInfo>',
             f'\t\t<BroadcastCountrySetting type="0">{country_code}</BroadcastCountrySetting>',
             '\t\t<country type="0">JA</country>', '\t</ModelInfo>', '\t<CHANNEL>']
    
    for ch in channels:
        # في الصيغة القديمة: مش skipped ومش invisible
        lines += [
            '\t\t<ITEM>',
            f'\t\t\t<major>{ch["majorNumber"]}</major>',
            f'\t\t\t<minor>{ch["minorNumber"]}</minor>',
            f'\t\t\t<PhysicalNum>{ch["physicalNumber"]}</PhysicalNum>',
            f'\t\t\t<chName>{ch["channelName"]}</chName>',
            f'\t\t\t<sourceIndex>{ch["sourceIndex"]}</sourceIndex>',
            f'\t\t\t<frequency>{ch["frequency"]}</frequency>',
            f'\t\t\t<symbolRate>{ch.get("symbolRate", 27500)}</symbolRate>',
            f'\t\t\t<isSkipped>{"1" if ch.get("skipped") else "0"}</isSkipped>',
            f'\t\t\t<isLocked>{"1" if ch.get("locked") else "0"}</isLocked>',
            '\t\t\t<isBlocked>0</isBlocked>',
            f'\t\t\t<satelliteId>{ch["satelliteId"]}</satelliteId>',
            f'\t\t\t<programNum>{ch["programNum"]}</programNum>',
            f'\t\t\t<TSID>{ch["TSID"]}</TSID>',
            f'\t\t\t<ONID>{ch["ONID"]}</ONID>',
            f'\t\t\t<SVCID>{ch.get("SVCID", 0)}</SVCID>',
            f'\t\t\t<scrambled>{"1" if ch.get("scrambled") else "0"}</scrambled>',
            f'\t\t\t<hdStatus>{ch.get("hdStatus", 0)}</hdStatus>',
            f'\t\t\t<transSystem>{ch.get("transSystem", "DVBS")}</transSystem>',
            f'\t\t\t<serviceType>{ch.get("serviceType", 1)}</serviceType>',
            f'\t\t\t<networkId>{ch.get("networkId", 0)}</networkId>',
            f'\t\t\t<tpId>{ch.get("tpId", "")}</tpId>',
            '\t\t</ITEM>',
        ]
    
    lines += ['\t</CHANNEL>', '</TLLDATA>']
    return '\n'.join(lines)

# ════════════════════════════════════════════
# الواجهة
# ════════════════════════════════════════════

st.markdown("<h1>🔄 محول ملفات TLL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#00f0ff;font-size:19px;font-weight:700;'>حوّل ملف القنوات بين أي موديل أو دولة أو صيغة</p>", unsafe_allow_html=True)
st.markdown("---")

# الخطوات
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="step-box"><p>📁 <b>خطوة 1</b><br>ارفع ملف TLL</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="step-box"><p>⚙️ <b>خطوة 2</b><br>اختار إعدادات جهازك</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="step-box"><p>⬇️ <b>خطوة 3</b><br>حمّل الملف المحوّل</p></div>', unsafe_allow_html=True)

st.markdown("---")

# ── خطوة 1: رفع الملف ──
st.markdown("### 📁 خطوة 1 — ارفع ملف TLL")
st.markdown('<div class="info-box"><p>ارفع ملف <b>TLL</b> أو <b>BAK</b> — الموقع هيكتشف صيغته تلقائياً (قديم أو حديث)</p></div>', unsafe_allow_html=True)

uploaded = st.file_uploader("اختار الملف", type=['tll','bak','TLL','BAK'])

if uploaded:
    content = uploaded.read().decode('utf-8', errors='ignore')
    fmt = detect_format(content)
    minfo = extract_model_info(content)

    if fmt == 'modern':
        chs, setting_list = extract_modern_channels(content)
    elif fmt == 'legacy':
        chs, setting_list = extract_legacy_channels(content)
    else:
        chs, setting_list = [], []

    # إحصائيات الملف
    all_count   = len(chs)
    invisible   = sum(1 for c in chs if c.get('Invisible'))
    visible_chs = [c for c in chs if not c.get('Invisible') and c.get('mapType') != 'NONE']
    skipped_n   = sum(1 for c in visible_chs if c.get('skipped'))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        fmt_lbl = "🆕 حديث JSON" if fmt=='modern' else "📼 قديم XML" if fmt=='legacy' else "❓"
        st.metric("صيغة الملف", fmt_lbl)
    with col2:
        st.metric("بلد الملف الأصلي", minfo.get('country','?'))
    with col3:
        st.metric("إجمالي القنوات", f"{all_count}")
    with col4:
        st.metric("قنوات مرئية فعلاً", f"{len(visible_chs)}")

    if fmt == 'unknown':
        st.error("❌ صيغة غير معروفة!")
        st.stop()

    # تحذير إذا في مشكلة Invisible
    if invisible > 0:
        st.markdown(f"""
        <div class="warn-box">
        <p>⚠️ <b>تنبيه:</b> الملف ده فيه <b>{invisible} قناة مخفية</b> (Invisible) من أصل {all_count}<br>
        ده السبب اللي بيخلي Chan Sort يقول "No Channel" — فعّل خيار <b>إصلاح المخفيات</b> تحت لحل المشكلة</p>
        </div>
        """, unsafe_allow_html=True)

    with st.expander(f"👁️ شوف أول 10 قنوات مرئية ({len(visible_chs)} قناة مرئية)"):
        for i, ch in enumerate(visible_chs[:10]):
            skip_lbl = "⏭️ مخطي" if ch.get('skipped') else "✅ فعال"
            st.write(f"**{i+1}.** {ch['channelName']} | رقم: {ch['majorNumber']} | {skip_lbl} | تردد: {ch['frequency']}")

    st.markdown("---")

    # ── خطوة 2: إعدادات جهازك ──
    st.markdown("### ⚙️ خطوة 2 — إعدادات جهازك")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**🌍 بلد البث**")
        country_choice = st.selectbox("اختار البلد", list(COUNTRIES.keys()), index=0)
        target_country_code, target_country_en = COUNTRIES[country_choice]

        st.markdown("**📺 صيغة الجهاز**")
        fmt_options = ["🔄 نفس صيغة الملف (بدون تغيير)", "🆕 حوّل لحديث JSON (webOS 2018+)", "📼 حوّل لقديم XML (قبل 2018)"]
        fmt_choice = st.selectbox("اختار صيغة الجهاز", fmt_options)

        if fmt_choice == fmt_options[0]:
            target_fmt = fmt
        elif fmt_choice == fmt_options[1]:
            target_fmt = 'modern'
        else:
            target_fmt = 'legacy'

    with col_b:
        st.markdown("**📺 موديل جهازك**")
        model_choice = st.selectbox(
            "اختار من القائمة أو اكتب يدوياً",
            MODEL_OPTIONS,
            index=0,
            help="اختار حجم شاشتك ثم الموديل"
        )

        # لو اختار من القائمة
        manual_model = ""
        if model_choice == "✏️ اكتب موديلك يدوياً" or model_choice.startswith("━"):
            manual_model = st.text_input(
                "اكتب موديلك",
                placeholder="مثال: 43LM6300PLA.AFUQLWE",
                help="موجود على ستيكر ظهر الشاشة"
            )

        # استخراج الموديل الفعلي
        if manual_model.strip():
            final_model = manual_model.strip()
        elif model_choice.startswith("━") or model_choice == "✏️ اكتب موديلك يدوياً":
            final_model = minfo.get('model', 'LG_TV_MODEL')
        else:
            # استخراج الموديل من النص [model_name]
            m = re.search(r'\[([^\]]+)\]', model_choice)
            final_model = m.group(1) if m else minfo.get('model', 'LG_TV_MODEL')

        st.markdown(f"<div class='info-box'><p>📺 الموديل المختار: <b>{final_model}</b></p></div>", unsafe_allow_html=True)

    # إصلاح Invisible
    st.markdown("**🔧 خيارات إضافية**")
    fix_invisible = st.toggle(
        "✅ إصلاح القنوات المخفية (Invisible/Skipped) — موصى به لو Chan Sort بيقول No Channel",
        value=True if invisible > 0 else False
    )

    st.markdown("---")

    # ── خطوة 3: تحويل وتحميل ──
    st.markdown("### ⬇️ خطوة 3 — حوّل وحمّل")

    cc1, cc2, cc3 = st.columns([1, 2, 1])
    with cc2:
        if st.button("🔄 ابدأ التحويل الآن", use_container_width=True):
            with st.spinner("⚙️ جاري التحويل..."):
                if target_fmt == 'modern':
                    out = build_modern_tll(chs, setting_list, final_model, target_country_code, target_country_en, fix_invisible)
                else:
                    # للقديم: لو fix_invisible فعّل، ارجع skipped=False لكل القنوات
                    out_chs = chs
                    if fix_invisible:
                        out_chs = [{**c, 'skipped': False, 'Invisible': False} for c in chs]
                    out = build_legacy_tll(out_chs, final_model, target_country_code)

                st.session_state['conv_out'] = out
                st.session_state['conv_count'] = len(chs)
                st.session_state['conv_visible'] = len(visible_chs)
                st.session_state['conv_fmt'] = target_fmt

    if st.session_state.get('conv_out'):
        out_bytes = st.session_state['conv_out'].encode('utf-8')
        total = st.session_state['conv_count']
        vis   = st.session_state['conv_visible']

        st.markdown(f"""
        <div class="success-box">
            <p style="font-size:22px;color:#00ff64;font-weight:bold;">🎉 الملف جاهز للتحميل!</p>
            <p>✅ {total} قناة تم تحويلها</p>
            <p>✅ بلد البث: {country_choice}</p>
            <p>✅ الموديل: {final_model}</p>
            <p>✅ الصيغة: {"حديث JSON" if st.session_state["conv_fmt"]=="modern" else "قديم XML"}</p>
            {"<p>✅ تم إصلاح القنوات المخفية</p>" if fix_invisible else ""}
        </div>
        """, unsafe_allow_html=True)

        cd1, cd2, cd3 = st.columns([1, 2, 1])
        with cd2:
            st.download_button(
                "⬇️ تحميل GlobalClone00001.TLL",
                data=out_bytes,
                file_name="GlobalClone00001.TLL",
                mime="application/octet-stream",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("### 📖 طريقة تشغيل الملف على شاشتك")
        st.markdown("""
        <div class="info-box">
        <p>1️⃣ <b>انسخ الملف</b> على فلاشة USB فاضية (FAT32)</p>
        <p>2️⃣ <b>الاسم لازم يكون بالظبط:</b> <code>GlobalClone00001.TLL</code></p>
        <p>3️⃣ <b>حط الفلاشة</b> في البورت الجنبي للشاشة</p>
        <p>4️⃣ <b>روح:</b> Settings ← Channel ← Channel Manager ← Clone TV</p>
        <p>5️⃣ <b>اختار:</b> "Load from USB" أو "USB → TV"</p>
        <p>6️⃣ <b>انتظر</b> الشاشة تعمل Restart تلقائياً</p>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="info-box">
    <p style="text-align:center;font-size:18px;">
    ⬆️ ارفع ملف TLL أو BAK وابدأ التحويل<br><br>
    ✅ تحويل <b>حديث → قديم</b> (لأجهزة قبل 2018)<br>
    ✅ تحويل <b>قديم → حديث</b> (لأجهزة webOS)<br>
    ✅ تغيير <b>بلد البث</b><br>
    ✅ تغيير <b>موديل الجهاز</b><br>
    ✅ إصلاح مشكلة <b>"No Channel"</b> في Chan Sort
    </p>
    </div>
    """, unsafe_allow_html=True)

# ── الفوتر ──
st.markdown("---")
st.markdown("<p style='text-align:center;font-size:20px;color:#ff007f;font-weight:bold;'>🛠️ DEVELOPER ENG: RAFIK NATHAN</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>📱 +201280339779 &nbsp;|&nbsp; ✉️ rafikrambo113@gmail.com</p>", unsafe_allow_html=True)
st.link_button("WhatsApp 💬", "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo")
