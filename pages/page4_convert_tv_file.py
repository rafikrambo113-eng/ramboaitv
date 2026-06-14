import streamlit as st
import re
import json
import base64

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
    'p4_preview': [],
    'p4_skipped': [],
    'p4_done': False,
    'p4_src_key': 0,
    'p4_ref_key': 0,
    'p4_mode': 'simple',
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ──────────────────────────────────────────────────────
# 2. FALLBACK FREQ DB — ترددات NileSat الحقيقية
# ──────────────────────────────────────────────────────
FALLBACK_FREQ_DB = {
    # التردد → (onid, tsid, physicalNum, special_data, nitVersion, videoStreamType, serviceId, satHandle)
    "10727": ("65535", "2",   "160", "81189034", "11", "2",  "1",    "5"),
    "10815": ("65535", "1",   "162", "81189034", "11", "2",  "4",    "5"),
    "10834": ("65535", "3",   "163", "81189034", "11", "2",  "5",    "5"),
    "10853": ("65535", "4",   "164", "81189034", "11", "2",  "6",    "5"),
    "10873": ("65535", "5",   "165", "81189034", "11", "2",  "7",    "5"),
    "10892": ("65535", "6",   "166", "81189034", "11", "2",  "8",    "5"),
    "10921": ("65535", "7",   "167", "81189034", "11", "2",  "9",    "5"),
    "10971": ("65535", "9",   "169", "81189034", "11", "2",  "10",   "5"),
    "11013": ("65535", "10",  "170", "81189034", "11", "2",  "11",   "5"),
    "11054": ("65535", "11",  "171", "81189034", "11", "2",  "12",   "5"),
    "11096": ("65535", "12",  "168", "81189034", "11", "2",  "2",    "5"),
    "11137": ("65535", "13",  "172", "81189034", "11", "2",  "13",   "5"),
    "11177": ("65535", "14",  "173", "81189034", "11", "2",  "14",   "5"),
    "11178": ("65535", "15",  "174", "81189034", "11", "2",  "15",   "5"),
    "11179": ("65535", "16",  "175", "81189034", "11", "2",  "16",   "5"),
    "11219": ("65535", "17",  "176", "81189034", "11", "27", "17",   "5"),
    "11221": ("65535", "18",  "177", "81189034", "11", "27", "18",   "5"),
    "11258": ("65535", "19",  "178", "81189034", "11", "2",  "19",   "5"),
    "11277": ("65535", "20",  "179", "81189034", "11", "2",  "20",   "5"),
    "11296": ("65535", "21",  "180", "81189034", "11", "2",  "21",   "5"),
    "11315": ("65535", "22",  "181", "81189034", "11", "2",  "22",   "5"),
    "11334": ("65535", "23",  "182", "81189034", "11", "2",  "23",   "5"),
    "11354": ("2048",  "800", "223", "282515498","22", "27", "1015", "5"),
    "11373": ("65535", "24",  "183", "81189034", "11", "2",  "24",   "5"),
    "11392": ("110",   "23",  "135", "81188906", "2",  "2",  "7006", "5"),
    "11411": ("65535", "25",  "184", "81189034", "11", "27", "25",   "5"),
    "11430": ("65535", "26",  "185", "81189034", "11", "2",  "26",   "5"),
    "11449": ("65535", "27",  "186", "81189034", "11", "2",  "27",   "5"),
    "11471": ("65535", "28",  "187", "81189034", "11", "27", "28",   "5"),
    "11488": ("65535", "29",  "188", "81189034", "11", "2",  "29",   "5"),
    "11554": ("65535", "30",  "189", "81189034", "11", "2",  "30",   "5"),
    "11564": ("65535", "31",  "190", "81189034", "11", "27", "31",   "5"),
    "11602": ("65535", "32",  "191", "81189034", "11", "2",  "32",   "5"),
    "11637": ("65535", "33",  "192", "81189034", "11", "27", "33",   "5"),
    "11641": ("65535", "34",  "193", "81189034", "11", "27", "34",   "5"),
    "11678": ("65535", "35",  "194", "81189034", "11", "27", "35",   "5"),
    "11680": ("65535", "36",  "195", "81189034", "11", "27", "36",   "5"),
    "11727": ("65535", "37",  "196", "81189034", "11", "2",  "37",   "5"),
    "11747": ("65535", "38",  "197", "81189034", "11", "27", "38",   "5"),
    "11766": ("65535", "39",  "198", "81189034", "11", "2",  "39",   "5"),
    "11785": ("65535", "40",  "199", "81189034", "11", "27", "40",   "5"),
    "11804": ("65535", "41",  "200", "81189034", "11", "27", "41",   "5"),
    "11823": ("65535", "42",  "201", "81189034", "11", "27", "42",   "5"),
    "11842": ("65535", "43",  "202", "81189034", "11", "27", "43",   "5"),
    "11861": ("65535", "44",  "203", "81189034", "11", "27", "44",   "5"),
    "11900": ("65535", "45",  "204", "81189034", "11", "27", "45",   "5"),
    "11919": ("65535", "46",  "205", "81189034", "11", "27", "46",   "5"),
    "11938": ("65535", "47",  "206", "81189034", "11", "27", "47",   "5"),
    "11957": ("65535", "48",  "207", "81189034", "11", "27", "48",   "5"),
    "11976": ("65535", "49",  "208", "81189034", "11", "27", "49",   "5"),
    "12015": ("65535", "50",  "209", "81189034", "11", "27", "50",   "5"),
    "12034": ("65535", "51",  "210", "81189034", "11", "27", "51",   "5"),
    "12053": ("65535", "52",  "211", "81189034", "11", "27", "52",   "5"),
    "12072": ("65535", "53",  "212", "81189034", "11", "27", "53",   "5"),
    "12091": ("65535", "54",  "213", "81189034", "11", "27", "54",   "5"),
    "12092": ("65535", "55",  "214", "81189034", "11", "27", "55",   "5"),
    "12130": ("65535", "56",  "215", "81189034", "11", "27", "56",   "5"),
    "12149": ("65535", "57",  "216", "81189034", "11", "27", "57",   "5"),
    "12187": ("65535", "58",  "217", "81189034", "11", "27", "58",   "5"),
    "12206": ("65535", "59",  "218", "81189034", "11", "27", "59",   "5"),
    "12226": ("65535", "60",  "219", "81189034", "11", "27", "60",   "5"),
    "12245": ("65535", "61",  "220", "81189034", "11", "27", "61",   "5"),
    "12284": ("65535", "62",  "221", "81189034", "11", "27", "62",   "5"),
    "12303": ("65535", "63",  "222", "81189034", "11", "27", "63",   "5"),
    "12322": ("65535", "64",  "224", "81189034", "11", "27", "64",   "5"),
    "12360": ("65535", "65",  "225", "81189034", "11", "27", "65",   "5"),
    "12399": ("65535", "66",  "226", "81189034", "11", "27", "66",   "5"),
    "12418": ("65535", "67",  "227", "81189034", "11", "27", "67",   "5"),
    "12521": ("65535", "68",  "228", "81189034", "11", "27", "68",   "5"),
    "12562": ("65535", "69",  "229", "81189034", "11", "27", "69",   "5"),
    "12604": ("65535", "70",  "230", "81189034", "11", "27", "70",   "5"),
    "12646": ("65535", "71",  "231", "81189034", "11", "27", "71",   "5"),
    "12687": ("65535", "72",  "232", "81189034", "11", "27", "72",   "5"),
    "12688": ("65535", "73",  "233", "81189034", "11", "27", "73",   "5"),
    "12728": ("65535", "74",  "234", "81189034", "11", "27", "74",   "5"),
}

def make_item_from_fallback(idx, name, freq):
    """بناء ITEM كامل من الـ fallback DB"""
    freq_str = str(freq)
    if freq_str in FALLBACK_FREQ_DB:
        onid, tsid, phys, spec, nit, vst, svc, sat = FALLBACK_FREQ_DB[freq_str]
    else:
        onid, tsid, phys, spec, nit, vst, svc, sat = ("65535","99","200","81189034","11","27",str(7000+idx),"5")

    name_hex = name.encode('utf-8').hex()
    name_len = len(name)
    return f"""<ITEM>
<prNum>{idx}</prNum>
<minorNum>0</minorNum>
<original_network_id>{onid}</original_network_id>
<transport_id>{tsid}</transport_id>
<network_id>{onid}</network_id>
<service_id>{svc}</service_id>
<physicalNum>{phys}</physicalNum>
<sourceIndex>7</sourceIndex>
<serviceType>1</serviceType>
<special_data>{spec}</special_data>
<frequency>{freq}</frequency>
<nitVersion>{nit}</nitVersion>
<mapType>1</mapType>
<mapAttr>0</mapAttr>
<programNo>{svc}</programNo>
<favoriteIdxA>250</favoriteIdxA>
<favoriteIdxB>250</favoriteIdxB>
<favoriteIdxC>250</favoriteIdxC>
<favoriteIdxD>250</favoriteIdxD>
<favoriteIdxE>250</favoriteIdxE>
<favoriteIdxF>250</favoriteIdxF>
<favoriteIdxG>250</favoriteIdxG>
<favoriteIdxH>250</favoriteIdxH>
<isInvisable>0</isInvisable>
<isBlocked>0</isBlocked>
<isSkipped>0</isSkipped>
<isNumUnSel>0</isNumUnSel>
<isDeleted>0</isDeleted>
<chNameByte>0</chNameByte>
<isDisabled>0</isDisabled>
<hexVchName>{name_hex}</hexVchName>
<notConvertedLengthOfVchName>{name_len}</notConvertedLengthOfVchName>
<vchName>{name}</vchName>
<lengthOfVchName>{name_len}</lengthOfVchName>
<hSettingIDHandle>1</hSettingIDHandle>
<usSatelliteHandle>{sat}</usSatelliteHandle>
<isUserSelCHNo>1</isUserSelCHNo>
<videoStreamType>{vst}</videoStreamType>
</ITEM>"""

# ──────────────────────────────────────────────────────
# 3. بيانات البلدان والموديلات
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
# 4. دوال التحليل والتحويل
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
    display = info['broadcast'] or info['country_json'] or info['country_xml']
    info['display_country'] = display
    info['country_label'] = CODE_TO_LABEL.get(display.upper(), display)
    return info


def apply_country_model(txt, is_modern, new_model, new_country_name, old_model, old_display):
    """تطبيق تغيير الموديل والبلد"""
    changes = []
    if new_model and new_model.strip() and new_model.strip() != old_model:
        txt = re.sub(r'(<ModelName[^>]*>)([^<]+)(</ModelName>)',
                     lambda m: m.group(1) + new_model.strip() + m.group(3), txt)
        changes.append(('model', old_model, new_model.strip()))

    if new_country_name and new_country_name in COUNTRIES:
        cd = COUNTRIES[new_country_name]
        if is_modern:
            txt = re.sub(r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                         lambda m: m.group(1) + cd['code3'] + m.group(3), txt)
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
            txt = re.sub(r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                         lambda m: m.group(1) + cd['code3'] + m.group(3), txt)
            old_len = len(old_display)
            new_code = cd['code3'][:2] if old_len <= 2 and len(cd['code3']) > 2 else cd['code3']
            txt = re.sub(r'(<country[^>]*>)([^<]+)(</country>)',
                         lambda m: m.group(1) + new_code + m.group(3), txt)
            new_display = new_code
        if old_display.upper() != new_display.upper():
            changes.append(('country', old_display, new_display, new_country_name))
    return txt, changes


def convert_modern_to_legacy(src_info, ref_info, new_model, new_country_name):
    """Modern JSON → Legacy XML مع fallback كامل"""
    txt_ref = ref_info['txt']

    # القنوات من المصدر
    jm = re.search(r'<legacybroadcast>(.*?)</legacybroadcast>', src_info['txt'], re.DOTALL)
    channels = json.loads(jm.group(1))['channelList']

    # templates من المرجع
    items_ref = re.findall(r'<ITEM>(.*?)</ITEM>', txt_ref, re.DOTALL)
    freq_to_item = {}
    for item in items_ref:
        fm = re.search(r'<frequency>([^<]+)</frequency>', item)
        if fm:
            f = fm.group(1).strip()
            if f not in freq_to_item:
                freq_to_item[f] = item

    new_items = []
    preview = []
    skipped_list = []

    for idx, ch in enumerate(channels, start=1):
        name = ch.get('channelName', 'Unknown')
        freq = str(ch.get('frequency', ''))

        if freq in freq_to_item:
            # من المرجع
            item = freq_to_item[freq]
            item = re.sub(r'<prNum>[^<]+</prNum>', f'<prNum>{idx}</prNum>', item)
            nh = name.encode('utf-8').hex()
            nl = len(name)
            item = re.sub(r'<hexVchName>[^<]+</hexVchName>', f'<hexVchName>{nh}</hexVchName>', item)
            item = re.sub(r'<notConvertedLengthOfVchName>[^<]+</notConvertedLengthOfVchName>', f'<notConvertedLengthOfVchName>{nl}</notConvertedLengthOfVchName>', item)
            item = re.sub(r'<vchName>[^<]+</vchName>', f'<vchName>{name}</vchName>', item)
            item = re.sub(r'<lengthOfVchName>[^<]+</lengthOfVchName>', f'<lengthOfVchName>{nl}</lengthOfVchName>', item)
            new_items.append('<ITEM>' + item + '</ITEM>')
            preview.append({'num': idx, 'name': name, 'freq': freq, 'src': '✅ مرجع'})
        elif freq in FALLBACK_FREQ_DB:
            # من الـ fallback
            item_str = make_item_from_fallback(idx, name, freq)
            new_items.append(item_str)
            preview.append({'num': idx, 'name': name, 'freq': freq, 'src': '🔄 fallback'})
        else:
            skipped_list.append({'name': name, 'freq': freq})

    # دمج
    combined = '\r\n'.join(new_items)
    start_i = txt_ref.find('<ITEM>')
    end_i   = txt_ref.rfind('</ITEM>') + len('</ITEM>')
    new_txt = txt_ref[:start_i] + combined + txt_ref[end_i:]

    # موديل وبلد
    target_model = new_model.strip() if new_model and new_model.strip() else src_info['model']
    new_txt, changes = apply_country_model(
        new_txt, False, target_model, new_country_name,
        ref_info['model'], ref_info.get('display_country','')
    )
    changes.append(('stats', len(new_items), len(skipped_list), len([p for p in preview if 'fallback' in p['src']])))
    return new_txt.encode('utf-8'), changes, preview, skipped_list


def convert_legacy_to_modern(src_info, ref_info, new_model, new_country_name):
    """Legacy XML → Modern JSON مع fallback"""
    txt_ref = ref_info['txt']

    items_src = re.findall(r'<ITEM>(.*?)</ITEM>', src_info['txt'], re.DOTALL)

    jm = re.search(r'<legacybroadcast>(.*?)</legacybroadcast>', txt_ref, re.DOTALL)
    data_ref = json.loads(jm.group(1))
    ref_channels = data_ref.get('channelList', [])

    # template حديث من المرجع
    freq_to_ch = {}
    for ch in ref_channels:
        f = str(ch.get('frequency',''))
        if f not in freq_to_ch:
            freq_to_ch[f] = ch

    # template افتراضي
    base_ch = ref_channels[0] if ref_channels else {}

    new_channels = []
    preview = []
    skipped_list = []

    for idx, item in enumerate(items_src, start=1):
        nm = re.search(r'<vchName>([^<]+)</vchName>', item)
        fm = re.search(r'<frequency>([^<]+)</frequency>', item)
        name = nm.group(1) if nm else 'Unknown'
        freq = fm.group(1).strip() if fm else ''

        if freq in freq_to_ch:
            template = dict(freq_to_ch[freq])
            src_label = '✅ مرجع'
        elif freq:
            template = dict(base_ch) if base_ch else {}
            template['frequency'] = int(freq)
            src_label = '🔄 fallback'
        else:
            skipped_list.append({'name': name, 'freq': freq})
            continue

        template['channelName']       = name
        template['majorNumber']       = idx
        template['programNum']        = idx
        template['SVCID']             = idx
        template['userSelCHNo']       = True
        template['userCustomize']     = True
        template['userEditChNumber']  = True
        template['skipped']           = False
        template['deleted']           = False
        template['Invisible']         = False
        try:
            nb64 = base64.b64encode(name.ljust(40,'\x00').encode('utf-8')).decode()
            template['chNameBase64'] = nb64
        except: pass

        new_channels.append(template)
        preview.append({'num': idx, 'name': name, 'freq': freq, 'src': src_label})

    data_ref['channelList'] = new_channels

    # بلد JSON
    target_full = 'Japan'
    target_code = 'JA'
    if new_country_name and new_country_name in COUNTRIES:
        target_full = COUNTRIES[new_country_name]['full']
        target_code = COUNTRIES[new_country_name]['code3']
    if 'modelInfo' not in data_ref: data_ref['modelInfo'] = {}
    data_ref['modelInfo']['country'] = target_full

    new_json = json.dumps(data_ref, ensure_ascii=False, separators=(',',':'))
    new_txt = re.sub(r'<legacybroadcast>.*?</legacybroadcast>',
                     f'<legacybroadcast>{new_json}</legacybroadcast>',
                     txt_ref, flags=re.DOTALL)

    target_model = new_model.strip() if new_model and new_model.strip() else src_info['model']
    new_txt, changes = apply_country_model(
        new_txt, True, target_model, new_country_name,
        ref_info['model'], ref_info.get('display_country','')
    )
    new_txt = re.sub(r'(<BroadcastCountrySetting[^>]*>)([^<]+)(</BroadcastCountrySetting>)',
                     lambda m: m.group(1) + target_code + m.group(3), new_txt)

    changes.append(('stats', len(new_channels), len(skipped_list),
                    len([p for p in preview if 'fallback' in p['src']])))
    return new_txt.encode('utf-8'), changes, preview, skipped_list


def change_country_model_only(info, new_model, new_country_name):
    txt = info['txt']
    txt, changes = apply_country_model(
        txt, info['is_modern'], new_model, new_country_name,
        info['model'], info.get('display_country','')
    )
    return txt.encode('utf-8'), changes, [], []

# ──────────────────────────────────────────────────────
# 5. CSS & Config
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
h1{{color:#ff007f!important;text-shadow:0 0 10px #ff007f,0 0 25px rgba(255,0,127,0.4)!important;text-align:center;font-weight:900;margin-top:5px;}}
h3,p,label,.stMarkdown,div[data-testid="stMarkdownContainer"] p{{color:{tc}!important;text-shadow:{tsh};}}
.stTextInput>div>div>input,.stSelectbox>div>div{{background-color:{bb}!important;color:{tc}!important;border:2px solid {bord}!important;border-radius:10px!important;}}
div[data-testid="stFileUploader"]{{background:{bb}!important;border:2px solid {bord}!important;box-shadow:0 5px 15px {bsh}!important;border-radius:14px!important;padding:18px!important;margin-bottom:16px!important;}}
.stButton>button{{background:linear-gradient(135deg,#ff007f 0%,#aa0055 100%)!important;color:#fff!important;border:2px solid #ff007f!important;border-radius:12px!important;font-weight:bold;width:100%;}}
.stDownloadButton>button{{background:linear-gradient(135deg,#00b894 0%,#00695c 100%)!important;color:#fff!important;border:none!important;border-radius:12px!important;font-weight:bold;width:100%;}}
.card{{background:{bb};border:2px solid {bord};box-shadow:0 5px 15px {bsh};border-radius:14px;padding:20px;margin-bottom:14px;}}
.badge{{display:inline-block;background:linear-gradient(135deg,#ff007f,#aa0055);color:white;border-radius:50%;width:30px;height:30px;text-align:center;line-height:30px;font-weight:bold;margin:0 8px;}}
.mode-card{{border-radius:14px;padding:18px;margin-bottom:10px;border:2px solid;text-align:center;}}
.mode-on{{border-color:#ff007f;background:rgba(255,0,127,0.12);}}
.mode-off{{border-color:#444;background:rgba(255,255,255,0.03);}}
.change-box{{background:rgba(0,240,255,0.08);border-left:4px solid #00f0ff;border-radius:8px;padding:10px 16px;margin:5px 0;}}
.warn-box{{background:rgba(255,193,7,0.1);border:2px solid #ffc107;border-radius:12px;padding:14px;margin-top:12px;}}
.stat-box{{border-radius:12px;padding:14px;text-align:center;border:2px solid;margin:4px;}}
.stat-green{{border-color:#00b894;background:rgba(0,184,148,0.1);color:#00b894;}}
.stat-blue{{border-color:#00f0ff;background:rgba(0,240,255,0.1);color:#00f0ff;}}
.stat-red{{border-color:#ff6b6b;background:rgba(255,107,107,0.1);color:#ff6b6b;}}
.tag{{display:inline-block;padding:3px 10px;border-radius:6px;font-size:0.82rem;font-weight:bold;margin:2px;}}
.t-m{{background:rgba(0,240,255,0.15);border:1px solid #00f0ff;color:#00f0ff;}}
.t-l{{background:rgba(255,165,0,0.15);border:1px solid orange;color:orange;}}
.t-c{{background:rgba(255,0,127,0.15);border:1px solid #ff007f;color:#ff007f;}}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 6. العنوان
# ──────────────────────────────────────────────────────
st.title("🔄 RAMBO — محوّل ملفات TLL" if ar else "🔄 RAMBO — TLL File Converter")
st.markdown(f"<h3 style='text-align:center;'>{'⚡ غيّر البلد | الموديل | حوّل قديم↔حديث — يحل Cloning Error 8' if ar else '⚡ Change Country | Model | Legacy↔Modern — Fixes Cloning Error 8'}</h3>", unsafe_allow_html=True)
st.write("---")

# ──────────────────────────────────────────────────────
# 7. اختيار الوضع
# ──────────────────────────────────────────────────────
st.markdown(f"### <span class='badge'>1</span> {'اختر نوع التحويل' if ar else 'Select Conversion Type'}", unsafe_allow_html=True)
col_m1, col_m2 = st.columns(2)
with col_m1:
    cls = 'mode-on' if st.session_state.p4_mode == 'simple' else 'mode-off'
    st.markdown(f"<div class='mode-card {cls}'>{'🌍 تغيير البلد أو الموديل فقط' if ar else '🌍 Change Country or Model Only'}<br><small>{'ملف واحد — لا يحتاج مرجع' if ar else 'One file — no reference needed'}</small></div>", unsafe_allow_html=True)
    if st.button("✅ " + ("اختر" if ar else "Select"), key="ms", use_container_width=True):
        st.session_state.p4_mode = 'simple'; st.rerun()
with col_m2:
    cls = 'mode-on' if st.session_state.p4_mode == 'convert' else 'mode-off'
    st.markdown(f"<div class='mode-card {cls}'>{'🔁 تحويل قديم ↔ حديث' if ar else '🔁 Convert Legacy ↔ Modern'}<br><small>{'ملف المصدر + ملف مرجعي شغال' if ar else 'Source file + working reference file'}</small></div>", unsafe_allow_html=True)
    if st.button("✅ " + ("اختر" if ar else "Select"), key="mc", use_container_width=True):
        st.session_state.p4_mode = 'convert'; st.rerun()
st.write("---")

# ──────────────────────────────────────────────────────
# 8. رفع الملفات
# ──────────────────────────────────────────────────────
st.markdown(f"### <span class='badge'>2</span> {'ارفع الملف/الملفات' if ar else 'Upload File(s)'}", unsafe_allow_html=True)

if st.session_state.p4_mode == 'simple':
    col_up, col_rst = st.columns([5,1])
    with col_up:
        up_src = st.file_uploader("📂 " + ("ارفع ملف TLL:" if ar else "Upload TLL:"), type=["TLL","bak"], key=f"s1_{st.session_state.p4_src_key}")
    with col_rst:
        st.write(""); st.write("")
        if st.button("🔄", key="rs1", use_container_width=True):
            st.session_state.p4_src_bytes = None; st.session_state.p4_src_name = None
            st.session_state.p4_src_info = {}; st.session_state.p4_result_bytes = None
            st.session_state.p4_done = False; st.session_state.p4_src_key += 1; st.rerun()
    if up_src:
        b = up_src.read()
        if st.session_state.p4_src_name != up_src.name:
            st.session_state.p4_src_bytes = b; st.session_state.p4_src_name = up_src.name
            st.session_state.p4_src_info = parse_tll(b)
            st.session_state.p4_result_bytes = None; st.session_state.p4_done = False
else:
    col_s, col_r = st.columns(2)
    with col_s:
        st.markdown(f"**{'📂 الملف المراد تحويله:' if ar else '📂 File to convert:'}**")
        up_src = st.file_uploader("Modern أو Legacy", type=["TLL","bak"], key=f"s2_{st.session_state.p4_src_key}")
        if up_src:
            b = up_src.read()
            if st.session_state.p4_src_name != up_src.name:
                st.session_state.p4_src_bytes = b; st.session_state.p4_src_name = up_src.name
                st.session_state.p4_src_info = parse_tll(b)
                st.session_state.p4_result_bytes = None; st.session_state.p4_done = False
    with col_r:
        st.markdown(f"**{'📂 الملف المرجعي الشغال:' if ar else '📂 Working reference file:'}**")
        up_ref = st.file_uploader("الملف الشغال على شاشتك", type=["TLL","bak"], key=f"r2_{st.session_state.p4_ref_key}")
        if up_ref:
            b = up_ref.read()
            if st.session_state.p4_ref_name != up_ref.name:
                st.session_state.p4_ref_bytes = b; st.session_state.p4_ref_name = up_ref.name
                st.session_state.p4_ref_info = parse_tll(b)
                st.session_state.p4_result_bytes = None; st.session_state.p4_done = False
    if st.button("🔄 " + ("إعادة ضبط" if ar else "Reset"), key="rc"):
        for k in ['p4_src_bytes','p4_src_name','p4_ref_bytes','p4_ref_name','p4_result_bytes','p4_done']:
            st.session_state[k] = None if k != 'p4_done' else False
        st.session_state.p4_src_info = {}; st.session_state.p4_ref_info = {}
        st.session_state.p4_src_key += 1; st.session_state.p4_ref_key += 1; st.rerun()

# عرض معلومات الملفات
def show_info(info, label):
    if not info: return
    is_m = info.get('is_modern', False)
    tag = f"<span class='tag t-m'>{'حديث' if ar else 'Modern'} JSON</span>" if is_m else f"<span class='tag t-l'>{'قديم' if ar else 'Legacy'} XML</span>"
    st.markdown(f"<div class='card'><b>{label}</b><br><br>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Model", info.get('model','?'))
    with c2:
        st.markdown("**Country**")
        st.markdown(f"<span class='tag t-c'>{info.get('country_label','?')} ({info.get('display_country','')})</span>", unsafe_allow_html=True)
    with c3:
        st.markdown("**Type**"); st.markdown(tag, unsafe_allow_html=True)
    with c4: st.metric("Channels", f"{info.get('ch_count',0):,}")
    st.markdown("</div>", unsafe_allow_html=True)

src_info = st.session_state.p4_src_info
ref_info = st.session_state.p4_ref_info

if src_info: show_info(src_info, "📄 " + ("الملف المصدر" if ar else "Source File"))
if ref_info and st.session_state.p4_mode == 'convert':
    show_info(ref_info, "📋 " + ("الملف المرجعي" if ar else "Reference File"))
    # اكتشاف اتجاه التحويل
    src_m = src_info.get('is_modern', False)
    ref_m = ref_info.get('is_modern', False)
    if src_m and not ref_m:
        st.info("🔁 " + ("سيتم التحويل: Modern JSON ➜ Legacy XML" if ar else "Will convert: Modern JSON ➜ Legacy XML"))
    elif not src_m and ref_m:
        st.info("🔁 " + ("سيتم التحويل: Legacy XML ➜ Modern JSON" if ar else "Will convert: Legacy XML ➜ Modern JSON"))
    elif src_m == ref_m:
        st.warning("⚠️ " + ("الملفان من نفس النوع — سيتم تغيير البلد/الموديل فقط" if ar else "Same type — will only change country/model"))

if not src_info:
    st.info("⬆️ " + ("ارفع ملف TLL للبدء." if ar else "Upload a TLL file to start."))
    st.stop()

if st.session_state.p4_mode == 'convert' and not ref_info:
    st.warning("⚠️ " + ("ارفع الملف المرجعي الشغال على شاشتك!" if ar else "Upload the reference file that works on your TV!"))
    st.stop()

st.write("---")

# ──────────────────────────────────────────────────────
# 9. خيارات التحويل
# ──────────────────────────────────────────────────────
st.markdown(f"### <span class='badge'>3</span> {'خيارات التحويل' if ar else 'Conversion Options'}", unsafe_allow_html=True)

col_m, col_c = st.columns(2)
with col_m:
    st.markdown(f"#### {'🖥️ الموديل الجديد' if ar else '🖥️ New Model'}")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    keep_m = "— " + ("الاحتفاظ بالموديل الحالي" if ar else "Keep current model") + " —"
    sel_model = st.selectbox("", [keep_m]+LG_MODELS, key="sm", label_visibility="collapsed")
    man_model = st.text_input("", placeholder="أو اكتب يدوياً / Or type manually", key="mm", label_visibility="collapsed").strip()
    final_model = man_model if man_model else ("" if sel_model == keep_m else sel_model)
    if final_model and final_model != src_info.get('model',''): st.success(f"✅ → **{final_model}**")
    st.markdown("</div>", unsafe_allow_html=True)

with col_c:
    st.markdown(f"#### {'🌍 بلد البث الجديد' if ar else '🌍 New Country'}")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    keep_c = "— " + ("الاحتفاظ بالبلد الحالي" if ar else "Keep current country") + " —"
    sel_country = st.selectbox("", [keep_c]+list(COUNTRIES.keys()), key="sc", label_visibility="collapsed")
    final_country = "" if sel_country == keep_c else sel_country
    if final_country: st.success(f"✅ **{final_country}** → `{COUNTRIES[final_country]['code3']}`")
    st.markdown(f"<div class='warn-box'><b style='color:#ffc107;'>⚠️ {'حل Cloning Error 8:' if ar else 'Fix Cloning Error 8:'}</b><br><small>{'اختر نفس بلد البث المضبوط على شاشتك' if ar else 'Select the same country set on your TV'}</small></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
col_btn,_,_ = st.columns([2,1,1])
with col_btn:
    if st.button("🔄 " + ("تحويل الآن" if ar else "Convert Now"), use_container_width=True):
        mode = st.session_state.p4_mode
        if mode == 'simple':
            if not final_model and not final_country:
                st.warning("⚠️ " + ("اختر تغيير الموديل أو البلد!" if ar else "Select model or country change!")); st.stop()
            res, changes, preview, skipped = change_country_model_only(src_info, final_model, final_country)
        else:
            src_m = src_info.get('is_modern', False)
            ref_m = ref_info.get('is_modern', False)
            if src_m and not ref_m:
                res, changes, preview, skipped = convert_modern_to_legacy(src_info, ref_info, final_model, final_country)
            elif not src_m and ref_m:
                res, changes, preview, skipped = convert_legacy_to_modern(src_info, ref_info, final_model, final_country)
            else:
                res, changes, preview, skipped = change_country_model_only(src_info, final_model, final_country)

        st.session_state.p4_result_bytes = res
        st.session_state.p4_changes      = changes
        st.session_state.p4_preview      = preview
        st.session_state.p4_skipped      = skipped
        st.session_state.p4_done         = True
        st.rerun()

# ──────────────────────────────────────────────────────
# 10. النتيجة والمعاينة
# ──────────────────────────────────────────────────────
if st.session_state.p4_done and st.session_state.p4_result_bytes:
    st.write("---")
    st.markdown(f"### <span class='badge'>4</span> {'النتيجة والتحميل' if ar else 'Result & Download'}", unsafe_allow_html=True)
    st.success("🎉 " + ("تم التحويل بنجاح!" if ar else "Conversion successful!"))

    changes = st.session_state.p4_changes
    preview = st.session_state.p4_preview
    skipped = st.session_state.p4_skipped

    # إحصائيات
    stats_ch = next((c for c in changes if c[0]=='stats'), None)
    if stats_ch:
        s1,s2,s3 = st.columns(3)
        with s1: st.markdown(f"<div class='stat-box stat-green'><b style='font-size:1.5rem;'>{stats_ch[1]}</b><br>{'قناة تم تحويلها' if ar else 'Channels Converted'}</div>", unsafe_allow_html=True)
        with s2: st.markdown(f"<div class='stat-box stat-blue'><b style='font-size:1.5rem;'>{stats_ch[3]}</b><br>{'من الـ Fallback' if ar else 'From Fallback DB'}</div>", unsafe_allow_html=True)
        with s3: st.markdown(f"<div class='stat-box stat-red'><b style='font-size:1.5rem;'>{stats_ch[2]}</b><br>{'تم تجاهلها' if ar else 'Skipped'}</div>", unsafe_allow_html=True)
        st.write("")

    # التغييرات
    for ch in changes:
        if ch[0] == 'model':
            st.markdown(f"<div class='change-box'>🖥️ Model: <code>{ch[1]}</code> <b style='color:#ff007f;'>➜</b> <code style='color:#00f0ff;'>{ch[2]}</code></div>", unsafe_allow_html=True)
        elif ch[0] == 'country':
            st.markdown(f"<div class='change-box'>🌍 Country: <code>{ch[1]}</code> <b style='color:#ff007f;'>➜</b> <code style='color:#00f0ff;'>{ch[2]}</code> ({ch[3] if len(ch)>3 else ''})</div>", unsafe_allow_html=True)

    # معاينة القنوات
    if preview:
        st.write("")
        with st.expander(f"📋 {'معاينة القنوات المحوّلة' if ar else 'Preview Converted Channels'} ({len(preview)})", expanded=False):
            ref_count = len([p for p in preview if '✅' in p['src']])
            fb_count  = len([p for p in preview if '🔄' in p['src']])
            st.markdown(f"✅ {'من ملف مرجعي' if ar else 'From reference'}: **{ref_count}** | 🔄 {'من Fallback DB' if ar else 'From Fallback DB'}: **{fb_count}**")
            st.markdown("---")
            # عرض جدول
            col_h1,col_h2,col_h3,col_h4 = st.columns([1,4,2,2])
            col_h1.markdown("**#**"); col_h2.markdown("**" + ("القناة" if ar else "Channel") + "**")
            col_h3.markdown("**" + ("التردد" if ar else "Freq") + "**"); col_h4.markdown("**" + ("المصدر" if ar else "Source") + "**")
            scroll = st.container(height=300)
            with scroll:
                for p in preview[:200]:
                    c1,c2,c3,c4 = st.columns([1,4,2,2])
                    c1.write(p['num']); c2.write(p['name']); c3.write(f"`{p['freq']}`"); c4.write(p['src'])
            if len(preview) > 200:
                st.caption(f"... {'و' if ar else 'and'} {len(preview)-200} {'قناة أخرى' if ar else 'more channels'}")

    # القنوات المتجاهلة
    if skipped:
        with st.expander(f"⚠️ {'القنوات التي تم تجاهلها' if ar else 'Skipped Channels'} ({len(skipped)})", expanded=False):
            st.markdown("**" + ("هذه القنوات تردداتها غير موجودة في المرجع أو الـ Fallback DB:" if ar else "These channels have frequencies not in reference or Fallback DB:") + "**")
            for s in skipped:
                st.markdown(f"- {s['name']} | Freq: `{s['freq']}`")

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
        if st.button("🔄 " + ("ملف جديد" if ar else "New File"), key="rst_b"):
            for k in ['p4_src_bytes','p4_src_name','p4_ref_bytes','p4_ref_name','p4_result_bytes','p4_done']:
                st.session_state[k] = None if k != 'p4_done' else False
            st.session_state.p4_src_info={}; st.session_state.p4_ref_info={}
            st.session_state.p4_preview=[]; st.session_state.p4_skipped=[]
            st.session_state.p4_src_key+=1; st.session_state.p4_ref_key+=1; st.rerun()

    st.markdown(f"""<div class='warn-box'>
<b style='color:#ffc107;'>💡 {'ملحوظة:' if ar else 'Note:'}</b><br>
<span style='font-size:0.88rem;'>{'إذا لم تظهر القنوات: إعدادات ← القنوات ← مدير القنوات ← تعديل كل القنوات ← تحديد الكل ← استعادة' if ar else 'If channels missing: Settings → Channels → Channel Manager → Edit All Channels → Select All → Restore'}</span>
</div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 11. FOOTER
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
