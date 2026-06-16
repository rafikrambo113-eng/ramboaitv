import streamlit as st
import json
import re
import time

st.set_page_config(page_title="RAMBO — محوّل LG الشامل", layout="centered")

# تهيئة الجلسة
for k, v in {
    'ref_bytes': None, 'ref_name': None,
    'tar_bytes': None, 'tar_name': None,
    'ref_key': 0, 'tar_key': 0,
    'done': False, 'result': None,
    'stats': {}, 'match_detail': []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

bg   = "radial-gradient(circle at 50% 50%,#110926 0%,#05020d 100%)"
tc   = "#00f0ff"
bb   = "rgba(13,7,33,0.85)"
bord = "#00f0ff"
bsh  = "rgba(0,240,255,0.35)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
.main{{background:{bg}!important;color:{tc}!important;font-family:'Cairo',sans-serif;}}
h1{{color:#ff007f!important;text-shadow:0 0 10px #ff007f!important;text-align:center;font-weight:900;}}
h2,h3,p,label,.stMarkdown,div[data-testid="stMarkdownContainer"] p{{color:{tc}!important;}}
div[data-testid="stFileUploader"]{{background:{bb}!important;border:2px solid {bord}!important;box-shadow:0 5px 15px {bsh}!important;border-radius:14px!important;}}
.stButton>button{{background:linear-gradient(135deg,#ff007f,#aa0055)!important;color:#fff!important;border:2px solid #ff007f!important;border-radius:12px!important;font-weight:bold;width:100%;}}
.stDownloadButton>button{{background:linear-gradient(135deg,#00b894,#00695c)!important;color:#fff!important;border:none!important;border-radius:12px!important;font-weight:bold;width:100%;}}
.card-ref{{background:{bb};border:2px solid #00f0ff;border-radius:14px;padding:18px;margin-bottom:12px;}}
.card-tar{{background:{bb};border:2px solid #ff007f;border-radius:14px;padding:18px;margin-bottom:12px;}}
.info-box{{background:rgba(0,240,255,0.07);border:1px solid #00f0ff;border-radius:10px;padding:12px;margin:8px 0;}}
</style>
""", unsafe_allow_html=True)

st.title("🔄 RAMBO — محوّل LG الشامل")
st.markdown("<h3 style='text-align:center;'>⚡ تحديث الترتيب والترددات معاً من الملف المرجعي وحقنها بأمان جوه شاشتك</h3>", unsafe_allow_html=True)
st.write("---")

def super_clean_name(s):
    if not s: return ""
    s = str(s).upper().strip()
    s = re.sub(r'\b(HD|SD|TV|AC3|DIGITAL|AUDIO|NEW)\b', '', s)
    s = re.sub(r'[أإآٱ]', 'ا', s)
    s = re.sub(r'[ة]', 'ه', s)
    s = re.sub(r'[ى]', 'ي', s)
    s = re.sub(r'[^A-Z0-9ا-ي]', '', s) 
    return s

def extract_channels(file_bytes):
    try: txt = file_bytes.decode('utf-8', errors='ignore'); enc='utf-8'
    except: txt = file_bytes.decode('latin-1', errors='ignore'); enc='latin-1'
    info = {'txt':txt,'enc':enc,'raw_items':[],'json_data':{},'channels':[]}
    
    if 'legacybroadcast' in txt:
        info['type'] = 'modern'
        jm = re.search(r'<legacybroadcast>(.*?)</legacybroadcast>', txt, re.DOTALL)
        if jm:
            try:
                data = json.loads(jm.group(1))
                info['json_data'] = data
                for idx,ch in enumerate(data.get('channelList',[]),1):
                    info['channels'].append({
                        'name': ch.get('channelName','').strip().upper(),
                        'freq': str(ch.get('frequency','')),
                        'svcid': str(ch.get('SVCID','')),
                        'order': ch.get('majorNumber',idx),
                        'raw': ch,
                    })
            except: pass
    else:
        info['type'] = 'legacy'
        items = re.findall(r'<ITEM>.*?</ITEM>', txt, re.DOTALL)
        info['raw_items'] = items
        for idx,item in enumerate(items,1):
            nm = re.search(r'<vchName>([^<]+)</vchName>', item)
            fm = re.search(r'<frequency>([^<]+)</frequency>', item)
            pm = re.search(r'<prNum>([^<]+)</prNum>', item)
            sm = re.search(r'<service_id>([^<]+)</service_id>', item)
            info['channels'].append({
                'name': nm.group(1).strip().upper() if nm else '',
                'freq': fm.group(1).strip() if fm else '',
                'order': int(pm.group(1)) if pm else idx,
                'svcid': sm.group(1).strip() if sm else '1',
                'raw': item,
            })
    return info

# ─────────────────────────────────────────────
# 🔥 تحديث الترتيب + الترددات من ملف النت صب جوه قالب جهازك
# ─────────────────────────────────────────────
def apply_comprehensive_order(ref_chs, tar_info):
    txt = tar_info['txt']
    
    # 1. عمل خريطة كاملة من ملف النت تشمل (الترتيب، التردد، الـ Service ID)
    ref_map = {}
    for ch in ref_chs:
        clean_n = super_clean_name(ch['name'])
        if clean_n and clean_n not in ref_map:
            ref_map[clean_n] = {
                'order': ch['order'],
                'freq': ch['freq'],
                'svcid': ch['svcid']
            }
            
    # 2. معالجة وتحديث قنوات الشاشة الأصلية
    if tar_info['type'] == 'modern':
        data = dict(tar_info['json_data'])
        ch_list = list(data.get('channelList', []))
        
        stats = {'updated_all': 0, 'to_end': 0}
        
        for ch in ch_list:
            clean_tar_n = super_clean_name(ch.get('channelName', ''))
            if clean_tar_n in ref_map:
                # تحديث حقيقي للترتيب والتردد والـ Service ID من ملف النت المرجعي
                ch['_target_sort'] = ref_map[clean_tar_n]['order']
                if ref_map[clean_tar_n]['freq'].isdigit():
                    ch['frequency'] = int(ref_map[clean_tar_n]['freq'])
                if ref_map[clean_tar_n]['svcid'].isdigit():
                    ch['SVCID'] = int(ref_map[clean_tar_n]['svcid'])
                stats['updated_all'] += 1
            else:
                ch['_target_sort'] = 90000 + ch.get('majorNumber', 1)
                stats['to_end'] += 1
                
        # ترتيب الملف بناءً على الترتيب الجديد
        ch_list.sort(key=lambda x: x['_target_sort'])
        
        # إعادة ربط أرقام السورت المتسلسلة لـ LG لمنع الشاشة السوداء
        for seq_num, ch in enumerate(ch_list, 1):
            ch['majorNumber'] = seq_num
            ch['displayChannelNumber'] = str(seq_num)
            ch['chIndex'] = seq_num - 1
            if 'channelId' in ch and ch['channelId']:
                parts = ch['channelId'].split('_')
                if len(parts) >= 2:
                    ch['channelId'] = f"{parts[0]}_{seq_num}"
                    
            ch['userSelCHNo'] = True
            ch['userCustomize'] = True
            ch['userEditChNumber'] = True
            ch['visible'] = True
            ch['skipped'] = False
            ch['deleted'] = False
            ch.pop('_target_sort', None)
            
        data['channelList'] = ch_list
        new_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        new_txt  = re.sub(r'<legacybroadcast>.*?</legacybroadcast>',
                          f'<legacybroadcast>{new_json}</legacybroadcast>',
                          txt, flags=re.DOTALL)
        return new_txt.encode('utf-8'), stats
        
    else:
        # الشاشات القديمة Legacy
        paired = []
        stats = {'updated_all': 0, 'to_end': 0}
        for idx, ch in enumerate(tar_info['channels']):
            clean_tar_n = super_clean_name(ch['name'])
            item_xml = tar_info['raw_items'][idx]
            
            if clean_tar_n in ref_map:
                target_sort = ref_map[clean_tar_n]['order']
                new_freq = ref_map[clean_tar_n]['freq']
                new_svcid = ref_map[clean_tar_n]['svcid']
                
                # حقن التردد الجديد والـ Service ID جوه الـ XML
                item_xml = re.sub(r'<frequency>[^<]*</frequency>', f'<frequency>{new_freq}</frequency>', item_xml)
                item_xml = re.sub(r'<service_id>[^<]*</service_id>', f'<service_id>{new_svcid}</service_id>', item_xml)
                stats['updated_all'] += 1
            else:
                target_sort = 90000 + ch['order']
                stats['to_end'] += 1
                
            paired.append((target_sort, item_xml))
            
        paired.sort(key=lambda x: x[0])
        
        new_items = []
        for seq_num, (_, item_xml) in enumerate(paired, 1):
            item_xml = re.sub(r'<prNum>[^<]+</prNum>', f'<prNum>{seq_num}</prNum>', item_xml)
            if '<isUserSelCHNo>' in item_xml:
                item_xml = re.sub(r'<isUserSelCHNo>[^<]+</isUserSelCHNo>', '<isUserSelCHNo>1</isUserSelCHNo>', item_xml)
            else:
                item_xml = item_xml.replace('</ITEM>', '<isUserSelCHNo>1</isUserSelCHNo></ITEM>')
            new_items.append(item_xml)
            
        combined = '\r\n'.join(new_items)
        first_idx = txt.find('<ITEM>')
        last_idx  = txt.rfind('</ITEM>') + len('</ITEM>')
        new_txt   = txt[:first_idx] + combined + txt[last_idx:] if first_idx != -1 else txt
        return new_txt.encode(tar_info['enc'], errors='ignore'), stats

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
st.markdown("### 1️⃣ ارفع الملفين")

col_r, col_t = st.columns(2)
with col_r:
    st.markdown("<div class='card-ref'>", unsafe_allow_html=True)
    st.markdown("**📡 ملف النت المُرتب والمحدث (المرجع)**")
    up_ref = st.file_uploader("", type=["tll","bak","TLL"], key=f"ref_{st.session_state.ref_key}", label_visibility="collapsed")
    if up_ref:
        b = up_ref.read()
        if st.session_state.ref_name != up_ref.name:
            st.session_state.ref_bytes = b; st.session_state.ref_name = up_ref.name
            st.session_state.done = False; st.session_state.result = None
    st.markdown("</div>", unsafe_allow_html=True)

with col_t:
    st.markdown("<div class='card-tar'>", unsafe_allow_html=True)
    st.markdown("**📺 ملف شاشتك الأصلي**")
    up_tar = st.file_uploader("", type=["tll","bak","TLL"], key=f"tar_{st.session_state.tar_key}", label_visibility="collapsed")
    if up_tar:
        b = up_tar.read()
        if st.session_state.tar_name != up_tar.name:
            st.session_state.tar_bytes = b; st.session_state.tar_name = up_tar.name
            st.session_state.done = False; st.session_state.result = None
    st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.ref_bytes or not st.session_state.tar_bytes:
    st.stop()

st.write("---")
st.markdown("### 2️⃣ المعالجة الشاملة")

if st.button("🚀 ابدأ تحديث الترتيب والترددات معاً", use_container_width=True):
    pb = st.progress(0); st_txt = st.empty()
    
    st_txt.markdown("⏳ **جاري تحليل الملفات ومطابقة الأسماء الذكية... (40%)**"); pb.progress(40); time.sleep(0.2)
    ri = extract_channels(st.session_state.ref_bytes)
    ti = extract_channels(st.session_state.tar_bytes)
    
    st_txt.markdown("⚙️ **جاري تحديث الترددات ونقل الترتيب وقفل الـ Hardware... (80%)**"); pb.progress(80); time.sleep(0.3)
    result_bytes, stats = apply_comprehensive_order(ri['channels'], ti)
    
    st_txt.markdown("✅ **تم التحويل بنجاح! (100%)**"); pb.progress(100); time.sleep(0.2)
    st_txt.empty(); pb.empty()
    
    st.session_state.result = result_bytes
    st.session_state.stats = stats
    st.session_state.done   = True
    st.rerun()

if st.session_state.done and st.session_state.result:
    st.success("🎉 مبروك يا فنان! تم تحديث قنواتك بالترتيب والترددات الجديدة المستخرجة بنجاح تـام!")
    
    st.markdown(f"""
    <div class='info-box'>
    📊 <b>ملخص التحديث المدمج:</b><br>
    • قنوات تم تحديث مكانها وترددها بالكامل: <b style='color:#00b894;'>{st.session_state.stats.get('updated_all')}</b> قناة.<br>
    • قنوات متبقية (تم الحفاظ عليها و ترحيلها للآخر بأمان): <b>{st.session_state.stats.get('to_end')}</b> قناة.
    </div>
    """, unsafe_allow_html=True)
    
    st.download_button(
        "📥 تحميل ملف القنوات النهائي (GlobalClone00001.TLL)",
        data=st.session_state.result,
        file_name="GlobalClone00001.TLL",
        mime="application/octet-stream",
        use_container_width=True,
    )
