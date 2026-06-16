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
    'live_channels': None # لحفظ البيانات الحية بعد جلبها
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
.tag{{display:inline-block;padding:2px 10px;border-radius:6px;font-size:0.82rem;font-weight:bold;}}
</style>
""", unsafe_allow_html=True)

st.title("🔄 RAMBO — محوّل TLL الحي الذكي")
st.markdown("<h3 style='text-align:center;'>🌐 جلب الترددات حياً من FlySat وتحديث ملف شاشتك تلقائياً</h3>", unsafe_allow_html=True)
st.write("---")

def norm(s):
    return re.sub(r'\s+', ' ', str(s).upper().strip())

# ─────────────────────────────────────────────
# 🚀 محرك الجلب الحي (FLY SATS SCRAPER)
# ─────────────────────────────────────────────
def fetch_live_nilesat():
    url = "https://www.flysat.com/en/satellite/nilesat-201-eutelsat-7-west-a"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200: return None
        soup = BeautifulSoup(res.text, 'html.parser')
        
        channels_db = {}
        current_freq = "11747"
        current_pol  = "V"
        current_sr   = "27500"
        
        # قشط الجداول وتحليل الترددات وقنواتها
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                if len(tds) >= 3:
                    text_all = "".join([td.get_text() for td in tds])
                    # كشف سطر التردد الجديد
                    m_freq = re.search(r'(\d{5})\s+([HV])\s+(\d{5})', text_all)
                    if m_freq:
                        current_freq = m_freq.group(1)
                        current_pol  = m_freq.group(2)
                        current_sr   = m_freq.group(3)
                        continue
                    
                    # استخراج اسم القناة والـ Service ID (عادة يكون رقم في أحد الأعمدة)
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
        return channels_db
    except Exception as e:
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
# ⚡ الـ صياعة البرمجية: الحقن والدمج الحي بدون مطابقة معقدة
# ─────────────────────────────────────────────
def apply_live_order(ref_chs, tar_info, live_db):
    txt = tar_info['txt']
    stats = {'updated_live': 0, 'kept': 0}
    
    # بناء القائمة النهائية بناءً على ترتيب ملف النت (المرجع)
    final_channels_pool = []
    
    for idx, ref_ch in enumerate(ref_chs, 1):
        r_name = norm(ref_ch['name'])
        
        # الافتراض الأساسي: نأخذ قيم القناة من ملف المرجع
        freq = ref_ch['freq']
        svcid = ref_ch['svcid']
        pol = "V"
        sr = "27500"
        
        # التحديث الحي الحقيقي: لو القناة موجودة في FlySat نحدث بياناتها فوراً طازة!
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

    # بناء ملف الـ TLL النهائي بناءً على نوع الشاشة القديم أو الحديث
    if tar_info['type'] == 'legacy':
        new_items = []
        # استخدام قالب أول عنصر أو عنصر افتراضي لبناء الـ XML
        base_xml = tar_info['raw_items'][0] if tar_info['raw_items'] else "<ITEM><vchName></vchName><frequency></frequency><prNum></prNum><service_id></service_id></ITEM>"
        
        for ch in final_channels_pool:
            item_xml = base_xml
            item_xml = re.sub(r'<vchName>[^<]*</vchName>', f'<vchName>{ch["name"]}</vchName>', item_xml)
            item_xml = re.sub(r'<frequency>[^<]*</frequency>', f'<frequency>{ch["freq"]}</frequency>', item_xml)
            item_xml = re.sub(r'<prNum>[^<]*</prNum>', f'<prNum>{ch["order"]}</prNum>', item_xml)
            item_xml = re.sub(r'<service_id>[^<]*</service_id>', f'<service_id>{ch["svcid"]}</service_id>', item_xml)
            # تصفير شفرات التيونر الإضافية لإجبار التلفزيون على لقط الإشارة حياً
            if '<isUserSelCHNo>' in item_xml: item_xml = re.sub(r'<isUserSelCHNo>[^<]+</isUserSelCHNo>', '<isUserSelCHNo>1</isUserSelCHNo>', item_xml)
            new_items.append(item_xml)
            
        combined = '\r\n'.join(new_items)
        first_idx = txt.find('<ITEM>')
        last_idx  = txt.rfind('</ITEM>') + len('</ITEM>')
        new_txt   = txt[:first_idx] + combined + txt[last_idx:] if first_idx != -1 else txt
        return new_txt.encode(tar_info['enc'], errors='ignore'), stats
    else:
        # الشاشات الحديثة (webOS)
        data = dict(tar_info['json_data'])
        base_ch = data.get('channelList', [{}])[0] if data.get('channelList') else {}
        
        new_ch_list = []
        for ch in final_channels_pool:
            ch_obj = dict(base_ch) # نسخ قالب الهاردوير النظيف من ملفك
            ch_obj['channelName'] = ch['name']
            ch_obj['majorNumber'] = ch['order']
            ch_obj['displayChannelNumber'] = str(ch['order'])
            ch_obj['frequency'] = int(ch['freq']) if ch['freq'].isdigit() else 11747
            ch_obj['SVCID'] = int(ch['svcid']) if ch['svcid'].isdigit() else 1
            
            # تصفير وضبط قيم الهاردوير لعدم البرش أو حدوث شاشة سوداء
            ch_obj['userSelCHNo'] = True
            ch_obj['userCustomize'] = True
            ch_obj['visible'] = True
            ch_obj['skipped'] = False
            ch_obj['deleted'] = False
            
            # ربط الفهرس الداخلي بشكل متسلسل إجباري للشاشة
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
# الواجهة الرسومية (UI)
# ─────────────────────────────────────────────
st.markdown("### 🌐 الخطوة 0: جلب الترددات الحية من الإنترنت")
if st.button("📡 اضغط هنا لتحديث قاعدة بيانات الترددات حياً من موقع FlySat", use_container_width=True):
    with st.spinner("جاري سحب جداول قمر نايل سات الحية وتحديث الـ Service IDs الحالية..."):
        db = fetch_live_nilesat()
        if db:
            st.session_state.live_channels = db
            st.success(f"🎉 رائع! تم جلب {len(db)} قناة بنجاح تام وبأحدث الترددات الحالية من موقع FlySat المعتمد!")
        else:
            st.error("⚠️ فشل الاتصال بالموقع أو قام بحظر الطلب مؤقتاً، سيتم استخدام الترددات الافتراضية المخزنة بالملف المرجعي.")

if st.session_state.live_channels:
    st.info(f"📊 قاعدة البيانات الحية النشطة تحتوي على: {len(st.session_state.live_channels)} قناة جاهزة للحقن التلقائي.")

st.write("---")
st.markdown("### 1️⃣ ارفع الملفين")

col_r, col_t = st.columns(2)
with col_r:
    st.markdown("<div class='card-ref'>", unsafe_allow_html=True)
    st.markdown("**📡 الملف المرجعي المُرتب بالأسماء**")
    st.caption("ملف النت اللي عاجبك ترتيبه وشكله (سنأخذ الأسماء والترتيب فقط)")
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
    st.caption("ملف التلفزيون بتاعك (عشان ناخد منه قالب وشفرة جهازك فقط)")
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
st.markdown("### 2️⃣ معالجة الكوبي بيست الذكي بالترددات الحية")

if st.button("🚀 ابدأ عملية مسح القنوات وحقن الترددات الحية بنسبة 100%", use_container_width=True):
    pb = st.progress(0); st_txt = st.empty()
    
    st_txt.markdown("⏳ **جاري قراءة هيكل وقالب ملف الشاشة... (30%)**"); pb.progress(30); time.sleep(0.3)
    ri = extract_channels(st.session_state.ref_bytes)
    ti = extract_channels(st.session_state.tar_bytes)
    
    st_txt.markdown("⚙️ **جاري دمج الأسماء وحقن أحدث الترددات المجلوبة من FlySat... (70%)**"); pb.progress(70); time.sleep(0.4)
    result_bytes, stats = apply_live_order(ri['channels'], ti, st.session_state.live_channels)
    
    st_txt.markdown("✅ **اكتمل التحويل بنجاح! (100%)**"); pb.progress(100); time.sleep(0.2)
    st_txt.empty(); pb.empty()
    
    st.session_state.result = result_bytes
    st.session_state.stats  = stats
    st.session_state.done   = True
    st.rerun()

if st.session_state.done and st.session_state.result:
    st.success("🎉 مبروك يا فنان! تم تحويل الملف بنظام الـ 'كوبي بيست' الإجباري لترتيب ملف النت، مع ترقية الترددات حياً وتصفير الهاردوير!")
    
    # عرض إحصائيات التحديث الحي
    st.markdown(f"""
    <div class='info-box'>
    📊 <b>ملخص التحديث المباشر للترددات:</b><br>
    • قنوات تم ترقية ترددها والـ Service ID حياً من موقع FlySat: <b style='color:#00b894;'>{st.session_state.stats.get('updated_live', 0)}</b> قناة.<br>
    • قنوات تم الحفاظ على بياناتها الافتراضية المرجعية: <b>{st.session_state.stats.get('kept', 0)}</b> قناة.
    </div>
    """, unsafe_allow_html=True)
    
    st.download_button(
        "📥 تحميل ملف القنوات النهائي المحدث (GlobalClone00001.TLL)",
        data=st.session_state.result,
        file_name="GlobalClone00001.TLL",
        mime="application/octet-stream",
        use_container_width=True,
    )
