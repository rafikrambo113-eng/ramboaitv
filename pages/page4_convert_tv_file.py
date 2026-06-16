import streamlit as st
import json
import re
import time

st.set_page_config(page_title="RAMBO — محوّل TLL الذكي", layout="centered")

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

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
.main{{background:{bg}!important;color:{tc}!important;font-family:'Cairo',sans-serif;}}
h1{{color:#ff007f!important;text-shadow:0 0 10px #ff007f!important;text-align:center;font-weight:900;}}
h2,h3,p,label,.stMarkdown,div[data-testid="stMarkdownContainer"] p{{color:{tc}!important;text-shadow:{tsh};}}
div[data-testid="stFileUploader"]{{background:{bb}!important;border:2px solid {bord}!important;box-shadow:0 5px 15px {bsh}!important;border-radius:14px!important;padding:18px!important;}}
.stButton>button{{background:linear-gradient(135deg,#ff007f,#aa0055)!important;color:#fff!important;border:2px solid #ff007f!important;border-radius:12px!important;font-weight:bold;width:100%;font-size:1.05rem;padding:0.6rem;}}
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

cl, ct, _ = st.columns([1.2, 1.5, 8])
with cl:
    if st.button("🌐 English" if ar else "🌐 العربية"):
        st.session_state.lang = 'en' if ar else 'ar'; st.rerun()
with ct:
    if st.button("☀️ Light" if dk else "🌙 Dark"):
        st.session_state.theme = 'light' if dk else 'dark'; st.rerun()

st.title("🔄 RAMBO — محوّل TLL الذكي" if ar else "🔄 RAMBO — Smart TLL Converter")
st.markdown(f"<h3 style='text-align:center;'>{'⚡ انقل ترتيب أي ملف مرجعي لشاشتك — يدعم قديم↔حديث' if ar else '⚡ Transfer channel order — supports Legacy↔Modern'}</h3>", unsafe_allow_html=True)
st.write("---")

# ─────────────────────────────────────────────
# EXTRACT
# ─────────────────────────────────────────────
def extract_channels(file_bytes):
    try:
        txt = file_bytes.decode('cp1256')
        enc = 'cp1256'
    except:
        try:
            txt = file_bytes.decode('utf-8', errors='ignore')
            enc = 'utf-8'
        except:
            txt = file_bytes.decode('latin-1', errors='ignore')
            enc = 'latin-1'

    info = {'txt': txt, 'enc': enc, 'raw_items': [], 'json_data': {}, 'channels': []}
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
        items = re.findall(r'<ITEM>.*?</ITEM>', txt, re.DOTALL)
        info['raw_items'] = items
        for idx, item in enumerate(items, 1):
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

# ─────────────────────────────────────────────
# MATCH
# ─────────────────────────────────────────────
def normalize(s):
    return re.sub(r'\s+', ' ', s.upper().strip())

def smart_match(ref_chs, tar_chs):
    ref_by_name  = {}
    ref_by_freq  = {}

    for ch in ref_chs:
        n = normalize(ch['name'])
        f = ch['freq']
        o = ch['order']
        if n and n not in ref_by_name:
            ref_by_name[n] = o
        if f and f not in ref_by_freq:
            ref_by_freq[f] = o

    results = []
    stats   = {'exact': 0, 'partial': 0, 'freq': 0, 'none': 0}
    max_ref_order = max((ch['order'] for ch in ref_chs), default=9999)

    for tar_idx, ch in enumerate(tar_chs):
        n = normalize(ch['name'])
        f = ch['freq']

        # مستوى 1: اسم مطابق تماماً
        if n in ref_by_name:
            results.append((tar_idx, ref_by_name[n], '✅ اسم مطابق'))
            stats['exact'] += 1
            continue

        # مستوى 2: اسم متشابه
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

        # مستوى 3: تردد مطابق
        if f and f in ref_by_freq:
            results.append((tar_idx, ref_by_freq[f], '🔄 تردد مطابق'))
            stats['freq'] += 1
            continue

        # لم يُطابَق — يُوضع في النهاية
        results.append((tar_idx, max_ref_order + tar_idx + 1, '⬜ في النهاية'))
        stats['none'] += 1

    return results, stats

# ─────────────────────────────────────────────
# APPLY — الترتيب الفعلي بإعادة ترتيب القائمة
# ─────────────────────────────────────────────
def apply_order(tar_info, matches):
    txt = tar_info['txt']

    # ── Legacy XML ──
    if tar_info['type'] == 'legacy':
        # أولاً: نرتب الـ ITEMs حسب الترتيب المطلوب
        paired = []
        for tar_idx, target_order, mtype in matches:
            if tar_idx < len(tar_info['raw_items']):
                paired.append((target_order, tar_idx, tar_info['raw_items'][tar_idx]))

        # الترتيب الفعلي
        paired.sort(key=lambda x: x[0])

        # بناء الـ ITEMs بأرقام تسلسلية جديدة
        new_items = []
        for seq_num, (_, tar_idx, item_xml) in enumerate(paired, 1):
            # تحديث prNum
            item_xml = re.sub(r'<prNum>[^<]+</prNum>',
                              f'<prNum>{seq_num}</prNum>', item_xml)
            # تفعيل isUserSelCHNo
            if '<isUserSelCHNo>' in item_xml:
                item_xml = re.sub(r'<isUserSelCHNo>[^<]+</isUserSelCHNo>',
                                  '<isUserSelCHNo>1</isUserSelCHNo>', item_xml)
            else:
                item_xml = item_xml.replace('</ITEM>', '<isUserSelCHNo>1</isUserSelCHNo></ITEM>')
            # إظهار القناة
            if '<isInvisable>' in item_xml:
                item_xml = re.sub(r'<isInvisable>[^<]+</isInvisable>',
                                  '<isInvisable>0</isInvisable>', item_xml)
            new_items.append(item_xml)

        # دمج في الملف
        combined  = '\r\n'.join(new_items)
        first_idx = txt.find('<ITEM>')
        last_idx  = txt.rfind('</ITEM>') + len('</ITEM>')
        if first_idx != -1 and last_idx != -1:
            new_txt = txt[:first_idx] + combined + txt[last_idx:]
        else:
            new_txt = txt

        return new_txt.encode(tar_info['enc'], errors='ignore')

    # ── Modern JSON ──
    else:
        data    = dict(tar_info['json_data'])
        ch_list = list(data.get('channelList', []))

        # وضع الترتيب المطلوب كـ temp key
        for tar_idx, target_order, _ in matches:
            if tar_idx < len(ch_list):
                ch_list[tar_idx]['_sort'] = target_order

        # الترتيب الفعلي للقائمة
        ch_list.sort(key=lambda x: x.get('_sort', 999999))

        # تعيين majorNumber تسلسلي بعد الترتيب
        for seq_num, ch in enumerate(ch_list, 1):
            ch['majorNumber']      = seq_num
            ch['userSelCHNo']      = True
            ch['userCustomize']    = True
            ch['userEditChNumber'] = True
            ch['skipped']          = False
            ch['deleted']          = False
            ch['Invisible']        = False
            # حذف الـ temp key
            ch.pop('_sort', None)

        data['channelList'] = ch_list
        new_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        new_txt  = re.sub(r'<legacybroadcast>.*?</legacybroadcast>',
                          f'<legacybroadcast>{new_json}</legacybroadcast>',
                          txt, flags=re.DOTALL)
        return new_txt.encode('utf-8')

# ─────────────────────────────────────────────
# UI — رفع الملفات
# ─────────────────────────────────────────────
st.markdown(f"## {'1️⃣ ارفع الملفين' if ar else '1️⃣ Upload Both Files'}")

col_r, col_t = st.columns(2)

with col_r:
    st.markdown("<div class='card-ref'>", unsafe_allow_html=True)
    st.markdown(f"**{'📡 الملف المرجعي المرتب' if ar else '📡 Sorted Reference File'}**")
    st.caption("الملف المرتب من النت — سنأخذ منه الترتيب فقط" if ar else "Sorted file — order will be taken from it")
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
        st.markdown(f"✅ **{ri['model']}** | {len(ri['channels']):,} {'قناة' if ar else 'ch'} | {t}", unsafe_allow_html=True)
        st.caption(f"🌍 {ri.get('display','')}")
    st.markdown("</div>", unsafe_allow_html=True)

with col_t:
    st.markdown("<div class='card-tar'>", unsafe_allow_html=True)
    st.markdown(f"**{'📺 ملف شاشتك الشغال' if ar else '📺 Your Working TV File'}**")
    st.caption("الملف الشغال على شاشتك — سيُحدَّث ترتيبه" if ar else "The file that works — its order will be updated")
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
        st.markdown(f"✅ **{ti['model']}** | {len(ti['channels']):,} {'قناة' if ar else 'ch'} | {t}", unsafe_allow_html=True)
        st.caption(f"🌍 {ti.get('display','')}")
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.ref_bytes and st.session_state.tar_bytes:
    ri = extract_channels(st.session_state.ref_bytes)
    ti = extract_channels(st.session_state.tar_bytes)
    rt = 'Modern' if ri['type']=='modern' else 'Legacy'
    tt = 'Modern' if ti['type']=='modern' else 'Legacy'
    st.info(f"**{rt} ➜ {tt}** | {'المطابقة: اسم دقيق → اسم متشابه → تردد مطابق | القنوات غير المطابقة تُوضع في النهاية' if ar else 'Matching: Exact → Similar → Frequency | Unmatched go to end'}")

if not st.session_state.ref_bytes or not st.session_state.tar_bytes:
    st.info("⬆️ " + ("ارفع الملفين للبدء." if ar else "Upload both files to start."))
    st.stop()

st.write("---")

# ─────────────────────────────────────────────
# UI — التحويل
# ─────────────────────────────────────────────
st.markdown(f"## {'2️⃣ ابدأ نقل الترتيب' if ar else '2️⃣ Start Transfer'}")

if st.button("✨ " + ("بدء نقل الترتيب الذكي" if ar else "Start Smart Order Transfer"), use_container_width=True):
    progress_bar = st.progress(0)
    status_text  = st.empty()

    status_text.markdown("⏳ **جاري قراءة الملفين... (20%)**" if ar else "⏳ **Reading files... (20%)**")
    progress_bar.progress(20)
    time.sleep(0.3)

    ri = extract_channels(st.session_state.ref_bytes)
    ti = extract_channels(st.session_state.tar_bytes)

    status_text.markdown("🔍 **جاري مطابقة القنوات... (55%)**" if ar else "🔍 **Matching channels... (55%)**")
    progress_bar.progress(55)
    time.sleep(0.3)

    matches, stats = smart_match(ri['channels'], ti['channels'])

    status_text.markdown("⚙️ **جاري إعادة ترتيب وبناء الملف... (85%)**" if ar else "⚙️ **Rebuilding file... (85%)**")
    progress_bar.progress(85)
    time.sleep(0.3)

    result_bytes = apply_order(ti, matches)

    status_text.markdown("✅ **تم! جاري التجهيز... (100%)**" if ar else "✅ **Done! Finalizing... (100%)**")
    progress_bar.progress(100)
    time.sleep(0.2)

    status_text.empty()
    progress_bar.empty()

    # بناء تفاصيل المعاينة بالترتيب الصحيح
    paired_detail = []
    for tar_idx, target_order, mtype in matches:
        name = ti['channels'][tar_idx]['name'].title() if tar_idx < len(ti['channels']) else '?'
        paired_detail.append((target_order, name, mtype))
    paired_detail.sort(key=lambda x: x[0])
    detail = [(name, seq+1, mtype) for seq, (_, name, mtype) in enumerate(paired_detail)]

    st.session_state.result       = result_bytes
    st.session_state.stats        = stats
    st.session_state.match_detail = detail
    st.session_state.done         = True
    st.rerun()

# ─────────────────────────────────────────────
# UI — النتيجة
# ─────────────────────────────────────────────
if st.session_state.done and st.session_state.result:
    st.write("---")
    st.markdown(f"## {'3️⃣ النتيجة' if ar else '3️⃣ Result'}")
    st.success("🎉 " + ("تم نقل الترتيب بنجاح!" if ar else "Order transferred successfully!"))

    stats = st.session_state.stats
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='stat sg'><b style='font-size:1.5rem;'>{stats.get('exact',0)}</b><br>{'اسم مطابق ✅' if ar else 'Exact ✅'}</div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='stat sb'><b style='font-size:1.5rem;'>{stats.get('partial',0)}</b><br>{'متشابه 🔍' if ar else 'Similar 🔍'}</div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='stat so'><b style='font-size:1.5rem;'>{stats.get('freq',0)}</b><br>{'تردد 🔄' if ar else 'Freq 🔄'}</div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='stat sn'><b style='font-size:1.5rem;'>{stats.get('none',0)}</b><br>{'في النهاية ⬜' if ar else 'End ⬜'}</div>", unsafe_allow_html=True)

    st.write("")

    detail = st.session_state.match_detail
    if detail:
        with st.expander(f"📋 {'معاينة الترتيب الجديد' if ar else 'Preview New Order'} ({len(detail)})", expanded=False):
            scroll = st.container(height=300)
            with scroll:
                h1, h2, h3 = st.columns([4, 2, 3])
                h1.markdown(f"**{'القناة' if ar else 'Channel'}**")
                h2.markdown(f"**{'الترتيب' if ar else 'Order'}**")
                h3.markdown(f"**{'المطابقة' if ar else 'Match'}**")
                for name, order, mtype in detail[:400]:
                    c1, c2, c3 = st.columns([4, 2, 3])
                    c1.write(name); c2.write(f"#{order}"); c3.write(mtype)

    st.write("")
    cd1, cd2 = st.columns([3, 1])
    with cd1:
        st.download_button(
            "📥 " + ("تحميل الملف المحوّل (GlobalClone00001.TLL)" if ar else "Download Converted File"),
            data=st.session_state.result,
            file_name="GlobalClone00001.TLL",
            mime="application/octet-stream",
            use_container_width=True,
        )
    with cd2:
        if st.button("🔄 " + ("من جديد" if ar else "Reset"), key="rst"):
            for k in ['ref_bytes','ref_name','tar_bytes','tar_name','result','done','stats','match_detail']:
                st.session_state[k] = (None if k in ['ref_bytes','ref_name','tar_bytes','tar_name','result']
                                       else (False if k=='done' else ({} if k=='stats' else [])))
            st.session_state.ref_key += 1
            st.session_state.tar_key += 1
            st.rerun()

    st.markdown(f"""<div class='warn'>
💡 <b>{'ملحوظة:' if ar else 'Note:'}</b><br>
{'إذا لم تظهر القنوات مرتبة: إعدادات ← القنوات ← مدير القنوات ← تعديل كل القنوات ← تحديد الكل ← استعادة' if ar else 'If channels not sorted: Settings → Channels → Channel Manager → Edit All Channels → Select All → Restore'}
</div>""", unsafe_allow_html=True)
