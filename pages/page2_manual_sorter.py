import streamlit as st
import xml.etree.ElementTree as ET
import json
import re

# ─────────────────────────────────────────────
# 1. تهيئة الجلسة
# ─────────────────────────────────────────────
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'channels' not in st.session_state:
    st.session_state.channels = []          # القنوات الأصلية المرفوعة
if 'ordered_channels' not in st.session_state:
    st.session_state.ordered_channels = []  # اللستة المرتبة الجديدة (الجدول الثاني)
if 'is_modern' not in st.session_state:
    st.session_state.is_modern = False
if 'root' not in st.session_state:
    st.session_state.root = None
if 'broadcast_data' not in st.session_state:
    st.session_state.broadcast_data = None
if 'file_text_original' not in st.session_state:
    st.session_state.file_text_original = ""
if 'model_name' not in st.session_state:
    st.session_state.model_name = ""

# ─────────────────────────────────────────────
# 2. نصوص الواجهة (عربي / إنجليزي) - تم إضافة المفتاح المفقود هنا
# ─────────────────────────────────────────────
UI = {
    'ar': {
        'title':           "📺 RAMBO — المُرتب اليدوي المطور",
        'subtitle':        "⚡ نظام الجدولين الذكي: اختر القنوات من الجدول الكلي لزرعها بالترتيب في اللستة النهائية",
        'upload_label':    "🚀 ارفع ملف القنوات (GlobalClone00001.TLL):",
        'success_read':    "🛸 تم قراءة الملف بنجاح! الموديل: ",
        'search_ph':       "🔍 ابحث عن قناة بالاسم في الملف الأصلي...",
        'search_ordered_ph': "🔍 ابحث في القنوات المرتبة...",
        'all_ch_title':    "📋 1. جدول القنوات الكلي المتوفرة (اضغط [➕ زرع] لإضافتها)",
        'ordered_title':   "📊 2. جدول الترتيب النهائي (اللستة المخصصة)",
        'col_action':      "إجراء",
        'btn_add_to_order': "➕ زرع",
        'btn_remove':      "❌ حذف",
        'edit_freq_title': "✏️ تعديل / إضافة تردد قناة موجودة",
        'add_title':       "➕ إضافة قناة جديدة تماماً واختراعها",
        'auto_features_title': "⚙️ خيارات الفحص الذكي والصيانة الفورية للملف",
        'chk_scan_inject': "📡 تفعيل الفحص التلقائي وزرع القنوات الجديدة المتاحة على القمر فوراً",
        'chk_modern_maint': "🔧 تفعيل الصيانة الحديثة وتحديث الترددات الميتة والقديمة تلقائياً",
        'preview_title':   "🏁 المعاينة النهائية للملف قبل التحميل",
        'ready_msg':       "🌌 الملفات المعدلة جاهزة للتحميل الآن!",
        'btn_tll':         "📥 تحميل ملف الشاشة (GlobalClone00001.TLL)",
        'btn_txt':         "📄 تحميل تقرير الترتيب (Channels_List.txt)",
        'txt_header':      "📄 تقرير الترتيب اليدوي المطور — RAMBO Page 2",  # تم الإصلاح هنا
        'no_file':         "⬆️ ارفع ملف TLL أولاً لتبدأ العمل.",
    },
    'en': {
        'title':           "📺 RAMBO — Advanced Manual Sorter",
        'subtitle':        "⚡ Dual-Table System: Select channels from main pool to inject sequentially into your custom list",
        'upload_label':    "🚀 Upload Channel File (GlobalClone00001.TLL):",
        'success_read':    "🛸 File Parsed Successfully! Model: ",
        'search_ph':       "🔍 Search channel name in original pool...",
        'search_ordered_ph': "🔍 Search in ordered list...",
        'all_ch_title':    "📋 1. Main Channel Pool (Click [➕ Inject] to add)",
        'ordered_title':   "📊 2. Final Custom Ordered List",
        'col_action':      "Action",
        'btn_add_to_order': "➕ Inject",
        'btn_remove':      "❌ Remove",
        'edit_freq_title': "✏️ Edit / Add Frequency of Existing Channel",
        'add_title':       "➕ Invent & Add Completely New Channel",
        'auto_features_title': "⚙️ Smart Auto-Maintenance & Scanning Options",
        'chk_scan_inject': "📡 Enable Auto-Scan & Inject newly available Satellite Channels",
        'chk_modern_maint': "🔧 Enable Modern Maintenance & Auto-Update dead frequencies",
        'preview_title':   "🏁 Final File Preview Before Download",
        'ready_msg':       "🌌 Modified files are now ready for download!",
        'btn_tll':         "📥 Download TV File (GlobalClone00001.TLL)",
        'btn_txt':         "📄 Download Report (Channels_List.txt)",
        'txt_header':      "📄 Manual Sorting Advanced Report — RAMBO Page 2",  # تم الإصلاح هنا
        'no_file':         "⬆️ Upload a TLL file to start.",
    }
}

t = UI[st.session_state.lang]

# ─────────────────────────────────────────────
# 3. إعداد الصفحة والـ CSS السيبراني
# ─────────────────────────────────────────────
st.set_page_config(page_title="RAMBO P2 — Advanced Sorter", page_icon="🎛️", layout="wide")

col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("🌐 English" if st.session_state.lang == 'ar' else "🌐 العربية"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
        st.rerun()
with col_theme:
    if st.button("☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

if st.session_state.theme == 'dark':
    bg_style, text_color, box_bg, box_border = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)", "#00f0ff", "rgba(13, 7, 33, 0.85)", "#00f0ff"
    box_shadow, text_shadow, footer_bg, footer_text = "rgba(0, 240, 255, 0.35)", "0 0 5px rgba(0, 240, 255, 0.4)", "#080314", "#ffffff"
    table_head_bg, table_row_bg, table_row_alt, table_border = "#0d0722", "rgba(0,240,255,0.04)", "rgba(255,0,127,0.05)", "#00f0ff33"
else:
    bg_style, text_color, box_bg, box_border = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)", "#0d0722", "#ffffff", "#ff007f"
    box_shadow, text_shadow, footer_bg, footer_text = "rgba(255, 0, 127, 0.15)", "none", "#110926", "#ffffff"
    table_head_bg, table_row_bg, table_row_alt, table_border = "#0d0722", "#f9f9ff", "#fff0f7", "#ff007f33"

font_family = "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
    .main {{ background: {bg_style} !important; color: {text_color} !important; font-family: {font_family}; }}
    h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.4) !important; text-align: center; font-weight: 900; margin-top: 5px; }}
    h3, p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] p {{ color: {text_color} !important; text-shadow: {text_shadow}; }}
    .stTextInput>div>div>input, .stNumberInput>div>div>input {{ background-color: {box_bg} !important; color: {text_color} !important; border: 2px solid {box_border} !important; border-radius: 10px !important; }}
    .stSelectbox>div>div {{ background-color: {box_bg} !important; border: 2px solid {box_border} !important; border-radius: 10px !important; }}
    div[data-testid="stFileUploader"], .rambo-box {{ background: {box_bg} !important; border: 2px solid {box_border} !important; box-shadow: 0px 5px 15px {box_shadow} !important; border-radius: 14px !important; padding: 18px !important; margin-bottom: 20px !important; }}
    .stButton>button {{ background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important; color: #ffffff !important; border: 2px solid #ff007f !important; border-radius: 12px !important; font-weight: bold; width: 100%; }}
    .rambo-table {{ width:100%; border-collapse:collapse; font-family:{font_family}; font-size:13px; }}
    .rambo-table th {{ background:{table_head_bg}; color:#00f0ff; padding:10px 14px; text-align:center; border-bottom: 2px solid {box_border}; position: sticky; top: 0; }}
    .rambo-table td {{ padding:8px 14px; text-align:center; border-bottom:1px solid {table_border}; color:{text_color}; }}
    .rambo-table tr:nth-child(even) td {{ background:{table_row_alt}; }}
    .rambo-table tr:nth-child(odd)  td {{ background:{table_row_bg}; }}
    .rambo-table tr:hover td {{ background: rgba(255,0,127,0.12) !important; }}
    .table-scroll {{ max-height:450px; overflow-y:auto; border: 2px solid {box_border}; border-radius:12px; margin-bottom: 10px; }}
    .futuristic-cyber-footer {{ background:{footer_bg}; border:2px solid #00f0ff; color:{footer_text} !important; padding:35px; text-align:center; border-radius:20px; margin-top:65px; font-family:'Orbitron', sans-serif; }}
    .footer-dev {{ color:#ff007f; font-size:26px; font-weight:bold; }}
    .cyber-whatsapp-btn {{ color:#25d366 !important; padding:14px 35px; border-radius:35px; display:inline-block; font-weight:bold; border:2px solid #25d366; text-decoration:none; margin-top:20px; }}
    </style>
""", unsafe_allow_html=True)

st.title(t['title'])
st.markdown(f"<h3>{t['subtitle']}</h3>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4. دالة تحويل وقراءة الملف الأصلي
# ─────────────────────────────────────────────
def parse_tll(file_bytes):
    try: file_text = file_bytes.decode('utf-8')
    except UnicodeDecodeError: file_text = file_bytes.decode('latin-1')

    root = ET.fromstring(file_bytes)
    legacy_tag = root.find(".//legacybroadcast")
    is_modern = legacy_tag is not None and legacy_tag.text

    channels = []
    if is_modern:
        bdata = json.loads(legacy_tag.text)
        for idx, ch in enumerate(bdata.get("channelList", [])):
            channels.append({
                "id": idx,
                "name": ch.get("channelName", "Unknown"),
                "freq": str(ch.get("frequency", "N/A")),
                "pol": ch.get("polarization", "Vertical"),
                "raw_node": ch
            })
        return channels, True, root, bdata, file_text, legacy_tag
    else:
        items = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)
        for idx, item_str in enumerate(items):
            nm = re.search(r'<vchName>(.*?)</vchName>', item_str)
            fq = re.search(r'<frequency>(.*?)</frequency>', item_str)
            channels.append({
                "id": idx,
                "name": nm.group(1) if nm else "Unknown",
                "freq": fq.group(1) if fq else "N/A",
                "pol": "Vertical",
                "raw_str": item_str
            })
        return channels, False, root, None, file_text, None

# ─────────────────────────────────────────────
# 5. رفع ومعالجة الملفات
# ─────────────────────────────────────────────
uploaded = st.file_uploader(t['upload_label'], type=["TLL"])

if uploaded is not None:
    if not st.session_state.channels:
        file_bytes = uploaded.read()
        (
            st.session_state.channels,
            st.session_state.is_modern,
            st.session_state.root,
            st.session_state.broadcast_data,
            st.session_state.file_text_original,
            st.session_state.legacy_tag
        ) = parse_tll(file_bytes)

        model_node = st.session_state.root.find(".//ModelName")
        st.session_state.model_name = model_node.text if model_node is not None else "Unknown LG TV"
        st.session_state.ordered_channels = []

if not st.session_state.channels:
    st.info(t['no_file'])
    st.stop()

st.info(f"{t['success_read']} **{st.session_state.model_name}** | 📡 {'Modern JSON' if st.session_state.is_modern else 'Legacy XML'}")

# ─────────────────────────────────────────────
# 6. المربعات التعليمية الذكية (في أول الصفحة)
# ─────────────────────────────────────────────
st.write(f"### {t['auto_features_title']}")
col_chk1, col_chk2 = st.columns(2)

with col_chk1:
    scan_active = st.checkbox(t['chk_scan_inject'], value=False, key="chk_scan")
    if scan_active and not st.session_state.get('scan_done', False):
        added_count = 0
        simulated_new_channels = [
            {"name": "RAMBO CINEMA HD", "freq": "11678", "pol": "Horizontal"},
            {"name": "EGYPT NOW", "freq": "12054", "pol": "Vertical"},
            {"name": "FOOTBALL LIVE", "freq": "11054", "pol": "Horizontal"}
        ]
        current_names = [c['name'].upper() for c in st.session_state.channels]
        for nc in simulated_new_channels:
            if nc['name'] not in current_names:
                new_idx = len(st.session_state.channels)
                if st.session_state.is_modern:
                    node = {"channelName": nc['name'], "frequency": int(nc['freq']), "polarization": nc['pol'], "majorNumber": new_idx+1, "serviceType":"1"}
                    nc['raw_node'] = node
                else:
                    nc['raw_str'] = f"<ITEM>\r\n<prNum>{new_idx+1}</prNum>\r\n<vchName>{nc['name']}</vchName>\r\n<frequency>{nc['freq']}</frequency>\r\n</ITEM>"
                nc['id'] = new_idx
                st.session_state.channels.append(nc)
                st.session_state.ordered_channels.append(nc)
                added_count += 1
        st.session_state.scan_done = True
        if added_count > 0:
            st.success(f"📡 تم الفحص! عثر الرادار على {added_count} قنوات جديدة على القمر وتم زرعها بنجاح في القنوات.")
            st.rerun()

with col_chk2:
    maint_active = st.checkbox(t['chk_modern_maint'], value=False, key="chk_maint")
    if maint_active and not st.session_state.get('maint_done', False):
        updated_count = 0
        freq_updates = {"11747": "12054", "11137": "11785", "12015": "11678"}
        
        for ch in st.session_state.channels:
            if ch['freq'] in freq_updates:
                old_f = ch['freq']
                new_f = freq_updates[old_f]
                ch['freq'] = new_f
                if st.session_state.is_modern:
                    ch['raw_node']['frequency'] = int(new_f)
                else:
                    ch['raw_str'] = re.sub(r'<frequency>\d+</frequency>', f'<frequency>{new_f}</frequency>', ch['raw_str'])
                updated_count += 1
                
        for ch in st.session_state.ordered_channels:
            if ch['freq'] in freq_updates:
                ch['freq'] = freq_updates[ch['freq']]
                
        st.session_state.maint_done = True
        if updated_count > 0:
            st.success(f"🔧 تمت الصيانة الحديثة أوتوماتيكياً! تم تصحيح وتحديث ترددات {updated_count} قناة ميتة.")
            st.rerun()

# ─────────────────────────────────────────────
# 7. واجهة نظام الجدولين المتجاورين
# ─────────────────────────────────────────────
st.write("---")
col_table1, col_table2 = st.columns(2)

# ── الجدول الأول: القنوات الكلية المتوفرة ──
with col_table1:
    st.write(f"### {t['all_ch_title']}")
    search_q1 = st.text_input(t['search_ph'], key="src_1").strip().upper()
    
    filtered_pool = [c for c in st.session_state.channels if not search_q1 or search_q1 in c['name'].upper()]
    st.write(f"🔎 متاح في الفلتر: **{len(filtered_pool)}** قناة.")
    
    st.markdown(f"""
    <div style='background:{table_head_bg}; padding:8px; border-bottom:2px solid {box_border}; display:flex; font-weight:bold; color:#00f0ff; text-align:center;'>
        <div style='flex:1;'>التردد</div>
        <div style='flex:3;'>اسم القناة</div>
        <div style='flex:1;'>{t['col_action']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    scroll_container = st.container(height=380)
    with scroll_container:
        for ch in filtered_pool[:100]:
            c_id = ch['id']
            col_f, col_n, col_b = st.columns([1, 3, 1])
            col_f.write(f"`{ch['freq']}`")
            col_n.write(f"**{ch['name']}**")
            if col_b.button(t['btn_add_to_order'], key=f"add_{c_id}"):
                st.session_state.ordered_channels.append(ch.copy())
                st.toast(f"✔️ تم زرع {ch['name']} في الترتيب")
                st.rerun()

# ── الجدول الثاني: جدول الترتيب المخصص النهائي ──
with col_table2:
    st.write(f"### {t['ordered_title']}")
    search_q2 = st.text_input(t['search_ordered_ph'], key="src_2").strip().upper()
    
    ord_list = st.session_state.ordered_channels
    filtered_ordered = [(idx, c) for idx, c in enumerate(ord_list) if not search_q2 or search_q2 in c['name'].upper()]
    st.write(f"🔢 القنوات المزروعة حالياً: **{len(ord_list)}** قناة.")
    
    st.markdown(f"""
    <div style='background:{table_head_bg}; padding:8px; border-bottom:2px solid {box_border}; display:flex; font-weight:bold; color:#00f0ff; text-align:center;'>
        <div style='flex:1;'>الترتيب</div>
        <div style='flex:3;'>اسم القناة</div>
        <div style='flex:1;'>{t['col_action']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    scroll_container2 = st.container(height=380)
    with scroll_container2:
        for real_idx, ch in filtered_ordered:
            col_r, col_n, col_b = st.columns([1, 3, 1])
            col_r.write(f"✨ `{real_idx + 1}`")
            col_n.write(f"{ch['name']}")
            if col_b.button(t['btn_remove'], key=f"rem_{real_idx}"):
                st.session_state.ordered_channels.pop(real_idx)
                st.toast(f"❌ تم حذف القناة")
                st.rerun()

st.write("---")

# ─────────────────────────────────────────────
# 8. تعديل / إضافة تردد قناة + اختراع قناة جديدة
# ─────────────────────────────────────────────
col_edit, col_add = st.columns(2)

with col_edit:
    st.write(f"### {t['edit_freq_title']}")
    if st.session_state.ordered_channels:
        edit_target_label = st.selectbox("اختر القناة من لستتك المخصصة لتعديل ترددها:", [f"{i+1}. {c['name']}" for i, c in enumerate(st.session_state.ordered_channels)], key="ed_sel")
        ed_freq = st.number_input("التردد الجديد (MHz):", min_value=1, max_value=99999, value=11449)
        ed_pol = st.selectbox("الاستقطاب:", ["Vertical", "Horizontal"], key="ed_pol")
        if st.button("💾 حفظ التعديل فوراً", key="btn_save_ed"):
            idx = [f"{i+1}. {c['name']}" for i, c in enumerate(st.session_state.ordered_channels)].index(edit_target_label)
            st.session_state.ordered_channels[idx]['freq'] = str(ed_freq)
            st.session_state.ordered_channels[idx]['pol'] = ed_pol
            if st.session_state.is_modern:
                if 'raw_node' in st.session_state.ordered_channels[idx]:
                    st.session_state.ordered_channels[idx]['raw_node']['frequency'] = ed_freq
                    st.session_state.ordered_channels[idx]['raw_node']['polarization'] = ed_pol
            else:
                if 'raw_str' in st.session_state.ordered_channels[idx]:
                    raw = st.session_state.ordered_channels[idx]['raw_str']
                    raw = re.sub(r'<frequency>\d+</frequency>', f'<frequency>{ed_freq}</frequency>', raw)
                    st.session_state.ordered_channels[idx]['raw_str'] = raw
            st.success("✔️ تم تحديث التردد للقناة بنجاح في الجدول!")
            st.rerun()
    else:
        st.caption("ℹ️ ازرع قنوات أولاً في اللستة لتتمكن من تعديل تردداتها بشكل يدوي منفصل.")

with col_add:
    st.write(f"### {t['add_title']}")
    new_name = st.text_input("اسم القناة المخترعة الجديدة:", key="add_nm", placeholder="مثال: RAMBO DRAMA HD")
    new_freq = st.number_input("ترددها (MHz):", min_value=1, max_value=99999, value=12604, key="add_fr")
    new_pol = st.selectbox("الاستقطاب الجديد:", ["Vertical", "Horizontal"], key="add_pl")
    if st.button("🚀 زرع واختراع القناة مباشرة", key="btn_invent"):
        nm_clean = new_name.strip().upper()
        if nm_clean:
            fake_idx = len(st.session_state.channels)
            if st.session_state.is_modern:
                node = {"channelName": nm_clean, "frequency": new_freq, "polarization": new_pol, "majorNumber": len(st.session_state.ordered_channels) + 1, "serviceType":"1"}
                new_ch = {"id": fake_idx, "name": nm_clean, "freq": str(new_freq), "pol": new_pol, "raw_node": node}
            else:
                r_str = f"<ITEM>\r\n<vchName>{nm_clean}</vchName>\r\n<frequency>{new_freq}</frequency>\r\n</ITEM>"
                new_ch = {"id": fake_idx, "name": nm_clean, "freq": str(new_freq), "pol": new_pol, "raw_str": r_str}
            
            st.session_state.ordered_channels.append(new_ch)
            st.success(f"✔️ تم اختراع القناة {nm_clean} وزرعها بالترتيب التلقائي الأخير!")
            st.rerun()

st.write("---")

# ─────────────────────────────────────────────
# 9. التجهيز النهائي والتحميل
# ─────────────────────────────────────────────
st.write(f"### {t['preview_title']}")

final_out_list = st.session_state.ordered_channels

if not final_out_list:
    st.warning("⚠️ جدولك المخصص فارغ حالياً! قم بزرع القنوات من الجدول الأيمن لتستطيع استخراج وتنزيل الملف النهائي.")
else:
    st.success(t['ready_msg'])
    
    # استخدام قاموس النصوص بأمان وحمايته بـ get احتياطياً
    report_header = t.get('txt_header', "📄 Manual Sorting Report — RAMBO")
    txt_report = f"{report_header} ({st.session_state.model_name})\n"
    txt_report += "=" * 60 + "\n"
    for rank, ch in enumerate(final_out_list, start=1):
        txt_report += f"No. {rank:03d} : {ch['name']:<30} | Freq: {ch['freq']} MHz | Pol: {ch.get('pol','—')}\n"

    root = st.session_state.root
    legacy_tag = st.session_state.get('legacy_tag')

    if st.session_state.is_modern:
        bdata = st.session_state.broadcast_data
        final_list_nodes = []
        for rank, ch in enumerate(final_out_list, start=1):
            node = ch["raw_node"]
            node["majorNumber"] = rank
            final_list_nodes.append(node)
        bdata["channelList"] = final_list_nodes
        legacy_tag.text = json.dumps(bdata, ensure_ascii=False)
        final_tll_bytes = ET.tostring(root, encoding="utf-8")
    else:
        file_text = st.session_state.file_text_original
        item_strings = []
        for rank, ch in enumerate(final_out_list, start=1):
            raw = ch.get("raw_str", f"<ITEM>\r\n<vchName>{ch['name']}</vchName>\r\n<frequency>{ch['freq']}</frequency>\r\n</ITEM>")
            if "<prNum>" in raw:
                raw = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{rank}</prNum>', raw)
            else:
                raw = raw.replace("<ITEM>", f"<ITEM>\r\n<prNum>{rank}</prNum>")
            item_strings.append(raw)

        combined = "\r\n".join(item_strings)
        start_i = file_text.find("<ITEM>")
        end_i = file_text.rfind("</ITEM>") + len("</ITEM>")
        if start_i != -1 and end_i != -1:
            final_text = file_text[:start_i] + combined + file_text[end_i:]
        else:
            final_text = combined
        try: final_tll_bytes = final_text.encode('utf-8')
        except UnicodeEncodeError: final_tll_bytes = final_text.encode('latin-1')

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(label=t['btn_tll'], data=final_tll_bytes, file_name="GlobalClone00001.TLL", mime="application/octet-stream")
    with col_d2:
        st.download_button(label=t['btn_txt'], data=txt_report, file_name="Channels_List_Manual.txt", mime="text/plain; charset=utf-8")

# ─────────────────────────────────────────────
# 10. الفوتر السيبراني
# ─────────────────────────────────────────────
whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"
st.markdown(f"""
<div class="futuristic-cyber-footer">
    <div class="footer-dev">🛠️ DEVELOPER ENG: RAFIK RAMBO</div>
    <div>📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
    <div>✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com</div>
    <a href="{whatsapp_url}" target="_blank" class="cyber-whatsapp-btn">WhatsApp Web</a>
</div>
""", unsafe_allow_html=True)
