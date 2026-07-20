import streamlit as st
import json
import xml.etree.ElementTree as ET
import base64
import re

# إعدادات الصفحة الأساسية وثيم الألوان الزيتي الفخم المتناسق مع HTML الأصلي
st.set_page_config(
    page_title="Rambo AI TV — مرتّب قنوات التليفزيون",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# كود CSS مخصص لحقن نفس شكل وألوان موقع RAMBO AI TV الأصلي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Ops+One&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #14150f !important;
        color: #eae7da !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    h1, h2, h3, h4, p, span, label {
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: #eae7da !important;
    }
    
    /* الستايل الخاص بالهيدر */
    .header-box {
        border-bottom: 1px solid #34372a;
        padding: 20px;
        background: linear-gradient(180deg, rgba(255,255,255,0.02), transparent);
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 25px;
    }
    .badge-r {
        width: 48px; height: 48px; border-radius: 50%;
        border: 2px solid #7a9a3f; display: flex; align-items: center; justify-content: center;
        background: #1c1e15; color: #d4820a; font-family: 'Black Ops One', sans-serif;
        font-size: 24px; font-weight: bold; margin-left: 15px;
    }
    .brand-title {
        font-family: 'Black Ops One', sans-serif !important;
        font-size: 26px; margin: 0; color: #eae7da;
    }
    .brand-title span { color: #d4820a; }
    
    /* صناديق العمل والفئات */
    .cat-section {
        background-color: #1c1e15 !important;
        border: 1px solid #34372a !important;
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 12px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1c1e15;
        padding: 10px;
        border-radius: 4px;
        border-bottom: 1px solid #34372a;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: #a3a08c !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #7a9a3f !important;
        border-bottom: 2px solid #7a9a3f !important;
    }
    
    /* تنبيهات الهينت */
    .hint-box {
        background-color: #1c1e15;
        border-right: 4px solid #d4820a;
        padding: 12px;
        margin: 15px 0;
        font-size: 13px;
        color: #a3a08c;
    }
</style>
""", unsafe_allow_value=True)

# --- دالات المساعدة والمعالجة لتنسيقات LG و M3U ---
def detect_and_parse(text):
    """يكتشف نوع الملف ويقوم بتحليله المبدئي"""
    if '<legacybroadcast>' in text and '</legacybroadcast>' in text:
        # LG webOS JSON
        start_tag, end_tag = '<legacybroadcast>', '</legacybroadcast>'
        start = text.find(start_tag)
        end = text.find(end_tag)
        prefix = text[:start + len(start_tag)]
        suffix = text[end:]
        json_raw = text[start + len(start_tag):end]
        
        # Unescape XML entities
        json_raw = json_raw.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        doc = json.loads(json_raw)
        
        channels = []
        for idx, node in enumerate(doc.get('channelList', [])):
            if node.get('deleted'): continue
            name = node.get('channelName', '')
            if not name and node.get('chNameBase64'):
                try:
                    name = base64.b64decode(node['chNameBase64']).decode('utf-8')
                except:
                    name = "(بدون اسم)"
            major = node.get('majorNumber', 0)
            is_radio = bool(major & 0x4000)
            
            channels.append({
                'id': idx,
                'name': name or "(بدون اسم)",
                'number': major & 0x3FFF,
                'radio': is_radio,
                'skipped': bool(node.get('skipped', False)),
                'locked': bool(node.get('locked', False)),
                'invisible': bool(node.get('Invisible', False)),
                'raw_node': node
            })
        return {'type': 'lg-json', 'channels': channels, 'prefix': prefix, 'suffix': suffix, 'doc': doc}
        
    elif '#EXTM3U' in text.strip()[:20]:
        # M3U Playlist
        lines = text.splitlines()
        channels = []
        pending = None
        idx = 0
        for line in lines:
            if line.startswith('#EXTINF'):
                comma_idx = line.rfind(',')
                name = line[comma_idx+1:].strip()
                group_match = re.search(r'group-title="([^"]*)"', line)
                group = group_match.group(1) if group_match else 'منوعات عامة'
                pending = {'name': name, 'group': group, 'extinf': line}
            elif line.strip() and not line.startswith('#'):
                if pending:
                    pending['url'] = line.strip()
                    channels.append({
                        'id': idx,
                        'name': pending['name'],
                        'number': idx + 1,
                        'radio': False,
                        'skipped': False,
                        'locked': False,
                        'invisible': False,
                        'group': pending['group'],
                        'extinf': pending['extinf'],
                        'url': pending['url']
                    })
                    idx += 1
                    pending = None
        return {'type': 'm3u', 'channels': channels}
    return None

def serialize_file(parsed_meta, updated_channels):
    """إعادة بناء الملف الأصلي بالتعديلات الجديدة للحفظ"""
    if parsed_meta['type'] == 'lg-json':
        doc = parsed_meta['doc']
        # تحديث النودز الأصلية بناءً على التعديلات في جدول ستريم ليت
        for ch in updated_channels:
            node = ch['raw_node']
            radio_bit = 0x4000 if ch['radio'] else 0
            node['majorNumber'] = (int(ch['number']) & 0x3FFF) | radio_bit
            node['skipped'] = ch['skipped']
            node['locked'] = ch['locked']
            node['Invisible'] = ch['invisible']
            node['channelName'] = ch['name']
            try:
                node['chNameBase64'] = base64.b64encode(ch['name'].encode('utf-8')).decode('utf-8')
            except:
                pass
        
        json_str = json.dumps(doc)
        json_str = json_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return parsed_meta['prefix'] + json_str + parsed_meta['suffix']
        
    elif parsed_meta['type'] == 'm3u':
        out = ["#EXTM3U"]
        # ترتيب حسب الرقم الجديد المكتوب
        sorted_ch = sorted(updated_channels, key=lambda x: int(x['number']))
        for ch in sorted_ch:
            extinf = ch['extinf']
            comma_idx = extinf.rfind(',')
            extinf = extinf[:comma_idx+1] + ch['name']
            # تحديث الجروب لو تغير
            if 'group' in ch:
                extinf = re.sub(r'group-title="[^"]*"', f'group-title="{ch["group"]}"', extinf)
            out.append(extinf)
            out.append(ch['url'])
        return "\n".join(out)
    return ""

def normalize_arabic(s):
    """توحيد الحروف العربية لتسهيل البحث والمطابقة الذكية"""
    s = str(s).lower()
    s = re.sub(r'[\u064B-\u0652]', '', s) # إزالة التشكيل
    s = re.sub(r'[أإآا]', 'ا', s)
    s = re.sub(r'ة', 'ه', s)
    s = re.sub(r'ى', 'ي', s)
    s = re.sub(r'\s+', '', s)
    return s.strip()

def auto_classify(name):
    """تصنيف تلقائي بناء على الكلمات المفتاحية الذكية وقواعد الموقع"""
    n = normalize_arabic(name)
    
    rules = {
        'ديني اسلامي': ['قران', 'المجد', 'الرحمه', 'الناس', 'huda', 'مكه', 'السنه', 'quran', 'afasy'],
        'ديني مسيحي': ['مسيحي', 'coptic', 'sat7', 'aghapy', 'اغابي', 'الكرمة', 'alkarma', 'ctv', 'سي تي في', 'koogi', 'كوجي', 'logos', 'mesat'],
        'رياضة': ['رياضة', 'رياضه', 'sport', 'bein', 'بي ان', 'الكاس', 'ssc', 'دبي الرياضية', 'ontime', 'kooora'],
        'اطفال': ['اطفال', 'kids', 'cartoon', 'كرتون', 'طيور الجنة', 'spacetoon', 'سبيستون', 'mbc3', 'ماجد', 'karameesh', 'كراميش', 'توم'],
        'اخبار': ['اخبار', 'إخبار', 'جزيرة', 'العربية', 'bbc', 'cnn', 'حدث', 'الحدث', 'الغد', 'الشرق', 'القاهرة الاخبارية', 'extra', 'اكسترا'],
        'مسلسلات ودراما': ['مسلسلات', 'مسلسل', 'دراما', 'drama', 'zee alwan', 'حكايات', 'hekayat'],
        'افلام عربي': ['سينما', 'روتانا سينما', 'aflam', 'افلام', 'افلام عربي', 'cima', 'زمن'],
        'افلام اجنبي': ['mbc2', 'mbc max', 'fox movies', 'movies', 'هوليوود', 'hollywood', 'action', 'mix'],
        'موسیقى وأغاني': ['اغاني', 'موسيقى', 'music', 'mazzika', 'مزيكا', 'melody', 'وناسة'],
        'راديو': ['radio', ' fm', 'راديو'],
        'تجريبي وفحص': ['test', 'spare', 'promo', 'feed', 'demo']
    }
    
    for cat, kws in rules.items():
        for kw in kws:
            if kw in n:
                return cat
    return 'منوعات عامة'

# --- واجهة التطبيق الرئيسية ---
st.markdown("""
<div class="header-box">
    <div class="badge-r">R</div>
    <div>
        <div class="brand-title">RAMBO <span>AI</span> TV</div>
        <div style="font-size: 13px; color: #a3a08c;">مرتّب قوائم القنوات // إل جي وصيغ M3U (نسخة Streamlit)</div>
    </div>
</div>
""", unsafe_allow_value=True)

# التنقل المعتمد على تابات الـ Sidebar أو تابات الصفحة العلوية
page_tab = st.radio("اختر نمط العمل:", ["🗂️ الترتيب الذكي بالفئات", "🔁 نقل الترتيب بين ملفين"], horizontal=True, label_visibility="collapsed")

if page_tab == "🗂️ الترتيب الذكي بالفئات":
    st.markdown('<p style="color:#a3a08c; font-size:14px;">ارفع ملف قنواتك وهنصنّفها تلقائيًا حسب المحتوى بناءً على اسم كل قناة. كل المعالجة أمنة تماماً ومحلية داخل التطبيق.</p>', unsafe_allow_value=True)
    
    uploaded_file = st.file_uploader("اسحب ملف القنوات هنا أو اختر من جهازك", type=["tll", "xml", "json", "m3u", "m3u8", "txt"])
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        try:
            file_text = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            file_text = file_bytes.decode('latin-1') # معالجة الملفات الثنائية التغليف أحياناً
            
        parsed_data = detect_and_parse(file_text)
        
        if not parsed_data:
            st.error("صيغة الملف مش مدعومة لسه — جرب ملف LG (.TLL/.xml) أو M3U")
        else:
            st.success(f"تم تحميل الملف بنجاح: {uploaded_file.name} | إجمالي القنوات: {len(parsed_data['channels'])}")
            
            # معالجة القنوات وتصنيفها تلقائياً
            processed_channels = []
            categories_set = set()
            
            for ch in parsed_data['channels']:
                # لو الملف M3U وجاي بجروب أصلي نستخدمه، وإلا تصنيف آلي للقنوات
                inferred_cat = ch.get('group', auto_classify(ch['name']))
                ch['category'] = inferred_cat
                categories_set.add(inferred_cat)
                processed_channels.append(ch)
                
            # محرك البحث
            search_query = st.text_input("🔎 بحث عن قناة بالاسم...", "")
            
            # فلترة القنوات بناء على البحث
            if search_query:
                filtered_channels = [c for c in processed_channels if search_query.lower() in c['name'].lower()]
            else:
                filtered_channels = processed_channels
                
            # تقسيم القنوات وعرضها في تابات تبسيطية حسب فئاتها لتسهيل فرزها وتعديلها
            unique_cats = sorted(list(categories_set))
            tabs = st.tabs([f"{cat} ({len([c for c in filtered_channels if c['category'] == cat])})" for cat in unique_cats])
            
            updated_all_channels = []
            
            for i, cat_tab in enumerate(tabs):
                with cat_tab:
                    cat_name = unique_cats[i]
                    cat_chans = [c for c in filtered_channels if c['category'] == cat_name]
                    
                    if not cat_chans:
                        st.info("مفيش قنوات مطابقة للبحث في الفئة دي.")
                        continue
                    
                    # تحويل البيانات لجدول تفاعلي قابل للتعديل يدوياً بالكامل في ستريم ليت
                    table_data = []
                    for c in cat_chans:
                        table_data.append({
                            "الرقم": c['number'],
                            "اسم القناة": c['name'],
                            "الفئة": c['category'],
                            "تخطي ⏭": c['skipped'],
                            "قفل 🔒": c['locked'],
                            "إخفاء 👁": c['invisible'],
                            "id": c['id'] # معرف داخلي خفي للربط
                        })
                        
                    edited_df = st.data_editor(
                        table_data,
                        column_config={
                            "الرقم": st.column_config.NumberColumn("الرقم", min_value=1, step=1),
                            "اسم القناة": st.column_config.TextColumn("اسم القناة"),
                            "الفئة": st.column_config.SelectboxColumn("الفئة", options=unique_cats),
                            "تخطي ⏭": st.column_config.CheckboxColumn("تخطي"),
                            "قفل 🔒": st.column_config.CheckboxColumn("قفل"),
                            "إخفاء 👁": st.column_config.CheckboxColumn("إخفاء"),
                            "id": None # إخفاء عمود المعرف عن المستخدم
                        },
                        disabled=[],
                        key=f"editor_{cat_name}"
                    )
                    
                    # إعادة دمج التعديلات المباشرة من المستخدم في المصفوفة الكلية
                    for edited_row in edited_df:
                        orig_ch = next(item for item in processed_channels if item["id"] == edited_row["id"])
                        orig_ch['number'] = edited_row["الرقم"]
                        orig_ch['name'] = edited_row["اسم القناة"]
                        orig_ch['category'] = edited_row["الفئة"]
                        orig_ch['skipped'] = edited_row["تخطي ⏭"]
                        orig_ch['locked'] = edited_row["قفل 🔒"]
                        orig_ch['invisible'] = edited_row["إخفاء 👁"]
            
            # شريط التحميل النهائي للملف المعدل
            st.markdown("---")
            st.subheader("⬇️ حفظ وتحميل الملف المعدّل")
            
            final_output = serialize_file(parsed_data, processed_channels)
            
            st.download_button(
                label="تنزيل الملف المرتّب والجاهز للشاشة ⚡",
                data=final_output,
                file_name=uploaded_file.name,
                mime="text/plain"
            )
            
            st.markdown("""
            <div class="hint-box">
                ⚠️ <b>مهم قبل ما ترفع الملف على التليفزيون:</b><br>
                1) لازم اسم الملف يفضل زي ما هو بالظبط ومن غير أي أرقام زيادة زي (1).<br>
                2) الفلاشة لازم تكون فورمات FAT32 مش NTFS ولا exFAT.<br>
                3) لو كان على الفلاشة أكتر من ملف قنوات، سيب ده بس وامسح الباقي.
            </div>
            """, unsafe_allow_value=True)

elif page_tab == "🔁 نقل الترتيب بين ملفين":
    st.markdown('<p style="color:#a3a08c; font-size:14px;">ارفع ملف قنوات جاهز ومرتب من النت (حتى لو مش نفس موديل شاشتك)، وارفع معاه ملف شاشتك الأصلي، وهيتم نقل أرقام القنوات المتطابقة بالاسم فوراً مع الحفاظ على البيانات التقنية لملفك.</p>', unsafe_allow_value=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1) الملف المرتّب (المرجع)")
        ref_file = st.file_uploader("ارفع الملف المرتب اللي هتاخد منه النظام", type=["tll", "xml", "m3u", "txt"], key="ref_file")
        
    with col2:
        st.subheader("2) ملف جهازك القديم (الهدف)")
        target_file = st.file_uploader("ارفع ملف قنوات شاشتك الأصلي اللي عايز ترتبه", type=["tll", "xml", "m3u", "txt"], key="target_file")
        
    if ref_file and target_file:
        try:
            ref_text = ref_file.read().decode('utf-8', errors='ignore')
            target_text = target_file.read().decode('utf-8', errors='ignore')
            
            ref_parsed = detect_and_parse(ref_text)
            target_parsed = detect_and_parse(target_text)
            
            if ref_parsed and target_parsed:
                if st.button("بدء نقل الترتيب الذكي الآن ⚡"):
                    # إنشاء خريطة بالأسماء الموحدة من الملف المرجعي
                    ref_map = {}
                    for ch in ref_parsed['channels']:
                        norm_k = normalize_arabic(ch['name'])
                        if norm_k and norm_k not in ref_map:
                            ref_map[norm_k] = ch['number']
                            
                    matched_count = 0
                    # تحديث أرقام قنوات الملف المستهدف
                    for ch in target_parsed['channels']:
                        norm_k = normalize_arabic(ch['name'])
                        if norm_k in ref_map:
                            ch['number'] = ref_map[norm_k]
                            matched_count += 1
                            
                    st.success(f"✅ تم نقل الترتيب لـ {matched_count} قناة مشتركة بالاسم بنجاح!")
                    
                    # تحويل وتجهيز الملف النهائي للتحميل
                    final_transfer_output = serialize_file(target_parsed, target_parsed['channels'])
                    
                    st.download_button(
                        label="تنزيل ملف جهازك بالترتيب الجديد ⬇️",
                        data=final_transfer_output,
                        file_name=target_file.name,
                        mime="text/plain"
                    )
            else:
                st.error("فشل التعرف على صيغة أحد الملفين المرفوعين. تأكد من رفع صيغ مدعومة.")
        except Exception as e:
            st.error(f"حصلت مشكلة أثناء المعالجة: {str(e)}")
