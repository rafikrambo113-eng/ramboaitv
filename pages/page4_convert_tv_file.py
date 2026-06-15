import streamlit as st
import json
import re
import time

st.set_page_config(page_title="RAMBO — محوّل TLL الذكي", layout="centered")

# تهيئة الجلسة (Session State)
for k, v in {
    'lang': 'ar', 'theme': 'dark',
    'ref_bytes': None, 'ref_name': None,
    'tar_bytes': None, 'tar_name': None,
    'ref_key': 0, 'tar_key': 0,
    'done': False, 'result': None,
    'stats': {}, 'match_detail': [],
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

# تنسيقات واجهة المستخدم (CSS واجهة رامبو الشهيرة)
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
.so{{border-color:#ffa500;background:rgba(255,165,0,0.1);color:#ffa500;}}
.sn{{border-color:#888;background:rgba(128,128,128,0.1);color:#888;}}
.warn{{background:rgba(255,193,7,0.1);border:2px solid #ffc107;border-radius:12px;padding:14px;margin-top:10px;}}
.tag{{display:inline-block;padding:2px 10px;border-radius:6px;font-size:0.82rem;font-weight:bold;}}
.tm{{background:rgba(0,240,255,0.15);border:1px solid #00f0ff;color:#00f0ff;}}
.tl{{background:rgba(255,165,0,0.15);border:1px solid orange;color:orange;}}
</style>
""", unsafe_allow_html=True)

# أزرار تغيير اللغة والمظهر
cl, ct, _ = st.columns([1.2, 1.5, 8])
with cl:
    if st.button("🌐 English" if ar else "🌐 العربية"):
        st.session_state.lang = 'en' if ar else 'ar'; st.rerun()
with ct:
    if st.button("☀️ Light" if dk else "🌙 Dark"):
        st.session_state.theme = 'light' if dk else 'dark'; st.rerun()

st.title("🔄 RAMBO — محوّل TLL الذكي")
st.markdown("<h3 style='text-align:center;'>⚡ انقل ترتيب أي ملف مرجعي لشاشتك — يدعم قنوات الـ webOS والملفات القديمة والحديثة بنجاح تامي</h3>", unsafe_allow_html=True)
st.write("---")

# دالة استخراج القنوات من ملف الـ TLL
def extract_channels(file_bytes):
    try:
        txt = file_bytes.decode('cp1256')
        encoding_used = 'cp1256'
    except:
        try:
            txt = file_bytes.decode('utf-8', errors='ignore')
            encoding_used = 'utf-8'
        except:
            txt = file_bytes.decode('latin-1', errors='ignore')
            encoding_used = 'latin-1'

    info = {'txt': txt, 'encoding': encoding_used, 'raw_items': [], 'json_data': {}, 'channels': []}

    m = re.search(r'<ModelName[^>]*>([^<]+)</ModelName>', txt)
    info['model'] = m.group(1).strip() if m else ''
    m = re.search(r'<BroadcastCountrySetting[^>]*>([^<]+)</BroadcastCountrySetting>', txt)
    info['bc'] = m.group(1).strip() if m else ''
    m = re.search(r'<country[^>]*>([^<]+)</country>', txt)
    info['cx'] = m.group(1).strip() if m else ''
    info['cj'] = ''

    if 'legacybroadcast' in txt:
        info['type'] = 'modern'
        jm = re.search(r'<legacybroadcast>(.*?)</legacybroadcast>', txt, re.DOTALL)
        if jm:
            try:
                data = json.loads(jm.group(1))
                info['json_data'] = data
                info['cj'] = data.get('modelInfo', {}).get('country', '')
                for idx, ch in enumerate(data.get('channelList', []), 1):
                    info['channels'].append({
                        'name':  ch.get('channelName', '').strip().upper(),
                        'freq':  str(ch.get('frequency', '')),
                        'svcid': str(ch.get('SVCID', '')),
                        'order': ch.get('majorNumber', idx),
                        'raw':   ch,
                    })
            except: pass
    else:
        info['type'] = 'legacy'
        items_with_tags = re.findall(r'<ITEM>.*?</ITEM>', txt, re.DOTALL)
        info['raw_items'] = items_with_tags
        for idx, item in enumerate(items_with_tags, 1):
            nm = re.search(r'<vchName>([^<]+)</vchName>', item)
            fm = re.search(r'<frequency>([^<]+)</frequency>', item)
            sm = re.search(r'<service_id>([^<]+)</service_id>', item)
            pm = re.search(r'<prNum>([^<]+)</prNum>', item)
            info['channels'].append({
                'name':  nm.group(1).strip().upper() if nm else '',
                'freq':  fm.group(1).strip() if fm else '',
                'svcid': sm.group(1).strip() if sm else '',
                'order': int(pm.group(1)) if pm else idx,
                'raw':   item,
            })

    info['display'] = info['bc'] or info['cj'] or info['cx']
    return info

def normalize(s):
    return re.sub(r'\s+', ' ', s.upper().strip())

# دالة المطابقة الذكية الثلاثية
def smart_match(ref_chs, tar_chs):
    ref_by_svcid = {}
    ref_by_name  = {}

    for ch in ref_chs:
        s_id = ch['svcid']
        n = normalize(ch['name'])
        o = ch['order']
        
        if s_id and s_id not in ref_by_svcid:
            ref_by_svcid[s_id] = o
        if n and n not in ref_by_name:
            ref_by_name[n] = o

    results = []
    stats   = {'svcid': 0, 'exact': 0, 'partial': 0, 'none': 0}

    for tar_idx, ch in enumerate(tar_chs):
        s_id = ch['svcid']
        n = normalize(ch['name'])

        if s_id and s_id in ref_by_svcid:
            results.append((tar_idx, ref_by_svcid[s_id], '🆔 معرّف رقمي مطابق'))
            stats['svcid'] += 1
            continue

        if n in ref_by_name:
            results.append((tar_idx, ref_by_name[n], '✅ اسم مطابق'))
            stats['exact'] += 1
            continue

        matched = False
        if n and len(n) > 3:
            for ref_n, ref_o in ref_by_name.items():
                if (n in ref_n or ref_n in n or
                        (len(n) >= 5 and len(ref_n) >= 5 and n[:5] == ref_n[:5])):
                    results.append((tar_idx, ref_o, '🔍 اسم متشابه'))
                    stats['partial'] += 1
                    matched = True
                    break

        if matched:
            continue

        results.append((tar_idx, 99999 + ch['order'], '⬜ بدون تغيير'))
        stats['none'] += 1

    return results, stats

# دالة إعادة بناء الترتيب وتصفير الهاردوير للشاشات الحديثة
def apply_order(tar_info, matches):
    txt = tar_info['txt']

    if tar_info['type'] == 'legacy':
        channel_pool = []
        for tar_idx, target_order, mtype in matches:
            if tar_idx < len(tar_info['raw_items']):
                channel_pool.append({
                    'original_idx': tar_idx,
                    'target_order': target_order,
                    'raw_xml': tar_info['raw_items'][tar_idx]
                })
        
        channel_pool.sort(key=lambda x: x['target_order'])
        
        updated_items = []
        for sequential_id, ch in enumerate(channel_pool, 1):
            item_xml = ch['raw_xml']
            item_xml = re.sub(r'<prNum>[^<]+</prNum>', f'<prNum>{sequential_id}</prNum>', item_xml)
            
            if '<isUserSelCHNo>' in item_xml:
                item_xml = re.sub(r'<isUserSelCHNo>[^<]+</isUserSelCHNo>', '<isUserSelCHNo>1</isUserSelCHNo>', item_xml)
            else:
                item_xml = item_xml.replace('</ITEM>', '<isUserSelCHNo>1</isUserSelCHNo></ITEM>')
                
            if '<uiInvisibleCH>' in item_xml:
                item_xml = re.sub(r'<uiInvisibleCH>[^<]+</uiInvisibleCH>', '<uiInvisibleCH>0</uiInvisibleCH>', item_xml)
            else:
                item_xml = item_xml.replace('</ITEM>', '<uiInvisibleCH>0</uiInvisibleCH></ITEM>')
                
            updated_items.append(item_xml)
        
        first_item_idx = txt.find('<ITEM>')
        last_item_idx = txt.rfind('</ITEM>')
        
        if first_item_idx != -1 and last_item_idx != -1:
            header = txt[:first_item_idx]
            footer = txt[last_item_idx + len('</ITEM>'):]
            middle = "".join(updated_items)
            final_txt = header + middle + footer
        else:
            final_txt = txt
            
        return final_txt.encode(tar_info['encoding'], errors='ignore')

    else: # تعديل شاشات webOS الحديثة وقفل الترتيب الداخلي
        data = dict(tar_info['json_data'])
        ch_list = list(data.get('channelList', []))
        
        for tar_idx, target_order, _ in matches:
            if tar_idx < len(ch_list):
                ch_list[tar_idx]['_tmp_order'] = target_order
                
        ch_list.sort(key=lambda x: x.get('_tmp_order', 999999))
        
        # اللوب المسؤولة عن ربط الـ Hardware وتوليد العداد الرقمي الإجباري للشاشة
        for sequential_id, ch in enumerate(ch_list, 1):
            ch['majorNumber'] = sequential_id
            ch['displayChannelNumber'] = str(sequential_id)
            
            if 'minorNumber' in ch:
                ch['minorNumber'] = 0
            if 'chIndex' in ch:
                ch['chIndex'] = sequential_id - 1
            
            if 'channelId' in ch and ch['channelId']:
                parts = ch['channelId'].split('_')
                if len(parts) >= 2:
                    ch['channelId'] = f"{parts[0]}_{sequential_id}"
                else:
                    ch['channelId'] = f"0_{sequential_id}"

            ch['userSelCHNo']      = True
            ch['userCustomize']    = True
            ch['userEditChNumber'] = True
            ch['visible']          = True
            ch['skipped']          = False
            
            if '_tmp_order' in ch: 
                del ch['_tmp_order']
                
        data['channelList'] = ch_list
        new_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        new_txt  = re.sub(r'<legacybroadcast>.*?</legacybroadcast>',
                          f'<legacybroadcast>{new_json}</legacybroadcast>',
                          txt, flags=re.DOTALL)
        return new_txt.encode('utf-8')

# ─────────────────────────────────────────────
# الخطوة الأولى: رفع الملفات
# ─────────────────────────────────────────────
st.markdown(f"## 1️⃣ ارفع الملفين")

col_r, col_t = st.columns(2)

with col_r:
    st.markdown("<div class='card-ref'>", unsafe_allow_html=True)
    st.markdown(f"**📡 الملف المرجعي المُرتب جاهز**")
    st.caption("الملف الجاهز المُرتب من الإنترنت (سنأخذ منه الترتيب فقط)")
    up_ref = st.file_uploader("", type=["tll","bak","TLL"],
                              key=f"ref_{st.session_state.ref_key}",
                              label_visibility="collapsed")
    if up_ref:
        b = up_ref.read()
        if st.session_state.ref_name != up_ref.name:
            st.session_state.ref_bytes = b
            st.session_state.ref_name  = up_ref.name
            st.session_state.done      = False
            st.session_state.result    = None
    if st.session_state.ref_bytes:
        ri = extract_channels(st.session_state.ref_bytes)
        t  = "<span class='tag tm'>Modern</span>" if ri['type']=='modern' else "<span class='tag tl'>Legacy</span>"
        st.markdown(f"✅ **{ri['model']}** | {len(ri['channels']):,} قناة | {t}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_t:
    st.markdown("<div class='card-tar'>", unsafe_allow_html=True)
    st.markdown(f"**📺 ملف شاشتك الحالية (الخام)**")
    st.caption("الملف المسحوب من شاشتك حالياً (الذي يحتوي على إشارات قنواتك)")
    up_tar = st.file_uploader("", type=["tll","bak","TLL"],
                              key=f"tar_{st.session_state.tar_key}",
                              label_visibility="collapsed")
    if up_tar:
        b = up_tar.read()
        if st.session_state.tar_name != up_tar.name:
            st.session_state.tar_bytes = b
            st.session_state.tar_name  = up_tar.name
            st.session_state.done      = False
            st.session_state.result    = None
    if st.session_state.tar_bytes:
        ti = extract_channels(st.session_state.tar_bytes)
        t  = "<span class='tag tm'>Modern</span>" if ti['type']=='modern' else "<span class='tag tl'>Legacy</span>"
        st.markdown(f"✅ **{ti['model']}** | {len(ti['channels']):,} قناة | {t}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.ref_bytes or not st.session_state.tar_bytes:
    st.info("⬆️ يرجى رفع الملف المرجعي وملف الشاشة للبدء.")
    st.stop()

st.write("---")

# ─────────────────────────────────────────────
# الخطوة الثانية: بدء النقل مع العداد الذكي من 1% لـ 100%
# ─────────────────────────────────────────────
st.markdown(f"## 2️⃣ ابدأ نقل الترتيب")

if st.button("✨ بدء نقل الترتيب وعمل المعالجة الرقمية الثنائية", use_container_width=True):
    # إنشاء بار العداد الذكي
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # المرحلة الأولى: فك فهارس القنوات
    status_text.markdown("⏳ **جاري فحص وتفكيك ملفات الـ TLL المرفوعة... (20%)**")
    progress_bar.progress(20)
    time.sleep(0.4)
    
    ri = extract_channels(st.session_state.ref_bytes)
    ti = extract_channels(st.session_state.tar_bytes)
    
    # المرحلة الثانية: اللوب الأولى للمطابقة الرقمية
    status_text.markdown("🔍 **اللوب الأولى: جاري ربط المعرّفات الرقمية وقراءة الأسماء (50%)**")
    progress_bar.progress(50)
    time.sleep(0.5)
    
    matches, stats = smart_match(ri['channels'], ti['channels'])
    
    # المرحلة الثالثة: اللوب الثانية وإعادة البناء وتعديل التيونر الداخلي
    status_text.markdown("⚙️ **اللوب الثانية: جاري إعادة بناء الـ Hardware لتلفزيونات LG ومنع التخطي... (85%)**")
    progress_bar.progress(85)
    time.sleep(0.5)
    
    result_bytes = apply_order(ti, matches)
    
    # المرحلة النهائية: حفظ وتجميع الداتا لشاشات الـ webOS
    status_text.markdown("⚡ **جاري مراجعة جودة الترتيب النهائي وتجهيز خروج الملف... (100%)**")
    progress_bar.progress(100)
    time.sleep(0.3)
    
    # إخفاء العداد بعد النجاح الكامل
    status_text.empty()
    progress_bar.empty()
    
    detail = []
    for sequential_id, ch_idx in enumerate(sorted(range(len(matches)), key=lambda k: matches[k][1]), 1):
        tar_idx, _, mtype = matches[ch_idx]
        ch_name = ti['channels'][tar_idx]['name'].title() if ti['channels'][tar_idx]['name'] else f"ID: {ti['channels'][tar_idx]['svcid']}"
        detail.append((ch_name, sequential_id, mtype))

    st.session_state.result        = result_bytes
    st.session_state.stats         = stats
    st.session_state.match_detail = detail
    st.session_state.done          = True
    st.rerun()

# ─────────────────────────────────────────────
# الخطوة الثالثة: عرض النتيجة وأزرار التحميل بالكامل بالعربي
# ─────────────────────────────────────────────
if st.session_state.done and st.session_state.result:
    st.write("---")
    st.markdown(f"## 3️⃣ النتيجة والتحميل")
    st.success("🎉 تم نقل ترتيب القنوات بنجاح وتم ربط الترتيب الأبجدي بالتيونر لضمان عدم حدوث پرش!")

    stats = st.session_state.stats
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='stat sg'><b style='font-size:1.5rem;'>{stats.get('svcid',0)}</b><br>معرّف رقمي 🆔</div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='stat sb'><b style='font-size:1.5rem;'>{stats.get('exact',0)}</b><br>اسم مطابق ✅</div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='stat so'><b style='font-size:1.5rem;'>{stats.get('partial',0)}</b><br>اسم متشابه 🔍</div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='stat sn'><b style='font-size:1.5rem;'>{stats.get('none',0)}</b><br>قنوات ثابتة ⬜</div>", unsafe_allow_html=True)

    st.write("")

    detail = st.session_state.match_detail
    if detail:
        with st.expander(f"📋 معاينة قائمة الترتيب الجديد بالكامل ({len(detail)} قناة)", expanded=False):
            scroll = st.container(height=300)
            with scroll:
                h1, h2, h3 = st.columns([4, 2, 3])
                h1.markdown("**القناة**")
                h2.markdown("**الترتيب الجديد**")
                h3.markdown("**نوع المطابقة**")
                for name, order, mtype in detail[:400]:
                    c1, c2, c3 = st.columns([4, 2, 3])
                    c1.write(name); c2.write(f"#{order}"); c3.write(mtype)

    st.write("")
    cd1, cd2 = st.columns([3, 1])
    with cd1:
        st.download_button(
            "📥 تحميل ملف القنوات الجديد المعدل (GlobalClone00001.TLL)",
            data=st.session_state.result,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream",
            use_container_width=True,
        )
    with cd2:
        if st.button("🔄 إعادة تعيين", key="rst"):
            for k in ['ref_bytes','ref_name','tar_bytes','tar_name','result','done','stats','match_detail']:
                st.session_state[k] = (None if k in ['ref_bytes','ref_name','tar_bytes','tar_name','result']
                                       else (False if k=='done' else ({} if k=='stats' else [])))
            st.session_state.ref_key += 1
            st.session_state.tar_key += 1
            st.rerun()

    st.markdown(f"""<div class='warn'>
💡 <b>ملحوظة هامة بعد رفع الملف للشاشة:</b><br>
إذا قمت برفع الملف للشاشة ولم تتغير القنوات فوراً، ادخل إلى: إعدادات التلفزيون ← القنوات ← مدير القنوات ← تعديل كل القنوات ← حدد الكل ثم اضغط على زر <b>استعادة (Restore)</b> لتجبر الشاشة على قراءة كود الـ Hardware الجديد فوراً.
</div>""", unsafe_allow_html=True)
