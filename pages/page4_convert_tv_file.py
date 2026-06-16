import streamlit as st
import json
import re
import time
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="RAMBO — محوّل TLL الحي", layout="centered")

# تهيئة الجلسة
for k, v in {
    'lang': 'ar', 'theme': 'dark',
    'ref_bytes': None, 'ref_name': None,
    'tar_bytes': None, 'tar_name': None,
    'ref_key': 0, 'tar_key': 0,
    'done': False, 'result': None,
    'stats': {}, 'match_detail': [],
    'live_channels': None
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

dk = st.session_state.theme == 'dark'
ar = st.session_state.lang == 'ar'
bg   = "radial-gradient(circle at 50% 50%,#110926 0%,#05020d 100%)" if dk else "#f4f5f7"
tc   = "#00f0ff" if dk else "#0d0722"
bb   = "rgba(13,7,33,0.85)" if dk else "#ffffff"
bord = "#00f0ff" if dk else "#ff007f"
bsh  = "rgba(0,240,255,0.35)" if dk else "rgba(255,0,127,0.15)"
tsh  = "0 0 5px rgba(0,240,255,0.4)" if dk else "none"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
.main{{background:{bg}!important;color:{tc}!important;font-family:'Cairo',sans-serif;}}
h1{{color:#ff007f!important;text-shadow:0 0 10px #ff007f!important;text-align:center;font-weight:900;}}
h2,h3,p,label,.stMarkdown,div[data-testid="stMarkdownContainer"] p{{color:{tc}!important;text-shadow:{tsh};}}
div[data-testid="stFileUploader"]{{background:{bb}!important;border:2px solid {bord}!important;box-shadow:0 5px 15px {bsh}!important;border-radius:14px!important;padding:18px!important;}}
.stButton>button{{background:linear-gradient(135deg,#ff007f,#aa0055)!important;color:#fff!important;border:2px solid #ff007f!important;border-radius:12px!important;font-weight:bold;width:100%;font-size:1.05rem;padding:0.6rem;}}
.stButton>button:hover{{border:2px solid #00f0ff!important;box-shadow:0 0 15px #00f0ff!important;}}
.stDownloadButton>button{{background:linear-gradient(135deg,#00b894,#00695c)!important;color:#fff!important;border:none!important;border-radius:12px!important;font-weight:bold;width:100%;}}
.card-ref{{background:{bb};border:2px solid #00f0ff;border-radius:14px;padding:18px;margin-bottom:12px;}}
.card-tar{{background:{bb};border:2px solid #ff007f;border-radius:14px;padding:18px;margin-bottom:12px;}}
.stat{{border-radius:12px;padding:14px;text-align:center;border:2px solid;}}
.sg{{border-color:#00b894;background:rgba(0,184,148,0.1);color:#00b894;}}
.sb{{border-color:#00f0ff;background:rgba(0,240,255,0.1);color:#00f0ff;}}
.sn{{border-color:#888;background:rgba(128,128,128,0.1);color:#888;}}
.warn{{background:rgba(255,193,7,0.1);border:2px solid #ffc107;border-radius:12px;padding:14px;margin-top:10px;}}
.info-box{{background:rgba(0,240,255,0.07);border:1px solid #00f0ff;border-radius:10px;padding:12px;margin:8px 0;font-size:0.88rem;}}
</style>
""", unsafe_allow_html=True)

st.title("🔄 RAMBO — محوّل TLL الحي الذكي")
st.markdown("<h3 style='text-align:center;'>🌐 جلب الترددات حياً وتحديث ملف شاشتك تلقائياً</h3>", unsafe_allow_html=True)
st.write("---")

def norm(s):
    return re.sub(r'\s+', ' ', str(s).upper().strip())

# ─────────────────────────────────────────────
# 🚀 محرك الجلب الحي المتطور (تخطي الحظر)
# ─────────────────────────────────────────────
def fetch_live_nilesat():
    url = "https://www.flysat.com/en/satellite/nilesat-201-eutelsat-7-west-a"
    # تزوير هيدرز كاملة لتبدو كمتصفح طبيعي 100%
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive"
    }
    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code != 200: 
            return None
        soup = BeautifulSoup(res.text, 'html.parser')
        
        channels_db = {}
        current_freq = "11747"
        current_pol  = "V"
        current_sr   = "27500"
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                if len(tds) >= 3:
                    text_all = "".join([td.get_text() for td in tds])
                    m_freq = re.search(r'(\d{5})\s+([HV])\s+(\d{5})', text_all)
                    if m_freq:
                        current_freq = m_freq.group(1)
                        current_pol  = m_freq.group(2)
                        current_sr   = m_freq.group(3)
                        continue
                    
                    ch_name = tds[0].get_text().strip()
                    svcid_text = tds[2].get_text().strip() if len(tds) > 2 else ""
                    m_id = re.search(r'\b\d+\b', svcid_text)
                    svc_id = m_id.group(0) if m_id else "1"
                    
                    if ch_name and len(ch_name) > 2 and not ch_name.isdigit():
                        n_name = norm(ch_name)
                        channels_db[n_name] = {
                            'freq': current_freq,
                            'pol': current_pol,
                            'sr': current_sr,
                            'svcid': svc_id
                        }
        return channels_db if len(channels_db) > 10 else None
    except:
        return None

# ─────────────────────────────────────────────
# EXTRACT FILE CHANNELS
# ─────────────────────────────────────────────
def extract_channels(file_bytes):
    try: txt = file_bytes.decode('utf-8', errors='ignore'); enc='utf-8'
    except: txt = file_bytes.decode('latin-1', errors='ignore'); enc='latin-1'
    info = {'txt':txt,'enc':enc,'raw_items':[],'json_data':{},'channels':[]}
    
    m = re.search(r'<ModelName[^>]*>([^<]+)</ModelName>', txt)
    info['model'] = m.group(1).strip() if m else 'LG TV'

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
                        'order': ch.get('majorNumber',idx),
                        'svcid': str(ch.get('SVCID','')),
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
# الحقن المباشر
# ─────────────────────────────────────────────
def apply_live_order(ref_chs, tar_info, live_db):
    txt = tar_info['txt']
    stats = {'updated_live': 0, 'kept': 0}
    final_channels_pool = []
    
    for idx, ref_ch in enumerate(ref_chs, 1):
        r_name = norm(ref_ch['name'])
        
        freq = ref_ch['freq']
        svcid = ref_ch['svcid']
        pol = "V"
        sr = "27500"
        
        if live_db and r_name in live_db:
            freq = live_db[r_name]['freq']
            svcid = live_db[r_name]['svcid']
            pol = live_db[r_name]['pol']
            sr = live_db[r_name]['sr']
            stats['updated_live'] += 1
        else:
            stats['kept'] += 1
            
        final_channels_pool.append({
            'name': ref_ch['name'],
            'order': idx,
            'freq': freq,
            'svcid': svcid,
            'pol': pol,
            'sr': sr
        })

    if tar_info['type'] == 'legacy':
        new_items = []
        base_xml = tar_info['raw_items'][0] if tar_info['raw_items'] else "<ITEM><vchName></vchName><frequency></frequency><prNum></prNum><service_id></service_id></ITEM>"
        for ch in final_channels_pool:
            item_xml = base_xml
            item_xml = re.sub(r'<vchName>[^<]*</vchName>', f'<vchName>{ch["name"]}</vchName>', item_xml)
            item_xml = re.sub(r'<frequency>[^<]*</frequency>', f'<frequency>{ch["freq"]}</frequency>', item_xml)
            item_xml = re.sub(r'<prNum>[^<]*</prNum>', f'<prNum>{ch["order"]}</prNum>', item_xml)
            item_xml = re.sub(r'<service_id>[^<]*</service_id>', f'<service_id>{ch["svcid"]}</service_id>', item_xml)
            if '<isUserSelCHNo>' in item_xml: item_xml = re.sub(r'<isUserSelCHNo>[^<]+</isUserSelCHNo>', '<isUserSelCHNo>1</isUserSelCHNo>', item_xml)
            new_items.append(item_xml)
            
        combined = '\r\n'.join(new_items)
        first_idx = txt.find('<ITEM>')
        last_idx  = txt.rfind('</ITEM>') + len('</ITEM>')
        new_txt   = txt[:first_idx] + combined + txt[last_idx:] if first_idx != -1 else txt
        return new_txt.encode(tar_info['enc'], errors='ignore'), stats
    else:
        data = dict(tar_info['json_data'])
        base_ch = data.get('channelList', [{}])[0] if data.get('channelList') else {}
        
        new_ch_list = []
        for ch in final_channels_pool:
            ch_obj = dict(base_ch)
            ch_obj['channelName'] = ch['name']
            ch_obj['majorNumber'] = ch['order']
            ch_obj['displayChannelNumber'] = str(ch['order'])
            ch_obj['frequency'] = int(ch['freq']) if ch['freq'].isdigit() else 11747
            ch_obj['SVCID'] = int(ch['svcid']) if ch['svcid'].isdigit() else 1
            ch_obj['userSelCHNo'] = True
            ch_obj['userCustomize'] = True
            ch_obj['visible'] = True
            ch_obj['skipped'] = False
            ch_obj['deleted'] = False
            ch_obj['chIndex'] = ch['order'] - 1
            ch_obj['channelId'] = f"0_{ch['order']}"
            new_ch_list.append(ch_obj)
            
        data['channelList'] = new_ch_list
        new_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        new_txt  = re.sub(r'<legacybroadcast>.*?</legacybroadcast>',
                          f'<legacybroadcast>{new_json}</legacybroadcast>',
                          txt, flags=re.DOTALL)
        return new_txt.encode('utf-8'), stats

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
st.markdown("### 🌐 الخطوة 0: جلب الترددات الحية من الإنترنت (اختياري)")
c_btn, c_status = st.columns([2, 1])

with c_btn:
    if st.button("📡 تحديث قاعدة الترددات حياً من موقع FlySat", use_container_width=True):
        with st.spinner("جاري محاكاة متصفح حقيقي وجلب أحدث البيانات الحية..."):
            db = fetch_live_nilesat()
            if db:
                st.session_state.live_channels = db
                st.success(f"🎉 تم جلب {len(db)} قناة بنجاح من النت!")
            else:
                st.session_state.live_channels = "FAILED"

with c_status:
    if st.session_state.live_channels == "FAILED":
        st.warning("⚠️ حظر مؤقت من الموقع! (شغالين بالخطة ب المباشرة)")
    elif st.session_state.live_channels and st.session_state.live_channels != "FAILED":
        st.info(f"✅ نشط: {len(st.session_state.live_channels)} قناة")
    else:
        st.write("💤 بانتظار الجلب...")

st.write("---")
st.markdown("### 1️⃣ ارفع الملفين")

col_r, col_t = st.columns(2)
with col_r:
    st.markdown("<div class='card-ref'>", unsafe_allow_html=True)
    st.markdown("**📡 الملف المرجعي المُرتب بالأسماء**")
    st.caption("ملف النت اللي عاجبك ترتيبه وشكله")
    up_ref = st.file_uploader("", type=["tll","bak","TLL"], key=f"ref_{st.session_state.ref_key}", label_visibility="collapsed")
    if up_ref:
        b = up_ref.read()
        if st.session_state.ref_name != up_ref.name:
            st.session_state.ref_bytes = b; st.session_state.ref_name = up_ref.name
            st.session_state.done = False; st.session_state.result = None
    st.markdown("</div>", unsafe_allow_html=True)

with col_t:
    st.markdown("<div class='card-tar'>", unsafe_allow_html=True)
    st.markdown("**📺 ملف قنوات شاشتك الأصلي**")
    st.caption("ملف التلفزيون بتاعك (عشان قالب وشفرة جهازك)")
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
st.markdown("### 2️⃣ معالجة الكوبي بيست المباشر")

if st.button("🚀 ابدأ عملية الكوبي بيست للملف وحقن الترتيب فوراً", use_container_width=True):
    pb = st.progress(0); st_txt = st.empty()
    
    st_txt.markdown("⏳ **جاري قراءة هيكل وقالب ملف الشاشة... (30%)**"); pb.progress(30); time.sleep(0.2)
    ri = extract_channels(st.session_state.ref_bytes)
    ti = extract_channels(st.session_state.tar_bytes)
    
    st_txt.markdown("⚙️ **جاري تطبيق الـ الكوبي بيست المباشر وبناء الترتيب الإجباري... (70%)**"); pb.progress(70); time.sleep(0.3)
    
    # تمرير قاعدة البيانات فقط لو نجح الجلب، وإلا نمرر None ويشتغل كوبي بيست تلقائي بالبيانات المرجعية
    live_db = st.session_state.live_channels if (st.session_state.live_channels and st.session_state.live_channels != "FAILED") else None
    result_bytes, stats = apply_live_order(ri['channels'], ti, live_db)
    
    st_txt.markdown("✅ **اكتمل التحويل بنجاح! (100%)**"); pb.progress(100); time.sleep(0.2)
    st_txt.empty(); pb.empty()
    
    st.session_state.result = result_bytes
    st.session_state.stats  = stats
    st.session_state.done   = True
    st.rerun()

if st.session_state.done and st.session_state.result:
    st.success("🎉 مبروك يا فنان! تم نسخ الترتيب 100% كوبي بيست وحقنه في قالب شاشتك بنجاح تـام!")
    
    if st.session_state.stats.get('updated_live', 0) > 0:
        msg = f"• تم تحديث <b style='color:#00b894;'>{st.session_state.stats.get('updated_live')}</b> قناة حياً بالترددات الجديدة من النت.<br>• تم نسخ <b>{st.session_state.stats.get('kept')}</b> قناة بالترددات المخزنة."
    else:
        msg = f"• تم تطبيق الخطة (ب): نسخ وتحويل إجباري لـ <b>{st.session_state.stats.get('kept')}</b> قناة بالترتيب الجديد مباشرة من غير مطابقات ووجع قلب!"
        
    st.markdown(f"<div class='info-box'>📊 <b>ملخص العملية:</b><br>{msg}</div>", unsafe_allow_html=True)
    
    st.download_button(
        "📥 تحميل ملف القنوات النهائي المحدث (GlobalClone00001.TLL)",
        data=st.session_state.result,
        file_name="GlobalClone00001.TLL",
        mime="application/octet-stream",
        use_container_width=True,
    )
