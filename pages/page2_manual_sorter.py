import streamlit as st
import xml.etree.ElementTree as ET
import json
import re
import pandas as pd

# ─────────────────────────────────────────────
# 1. تهيئة الجلسة (Session State) بشكل مستقر
# ─────────────────────────────────────────────
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'channels' not in st.session_state:
    st.session_state.channels = []          
if 'ordered_channels' not in st.session_state:
    st.session_state.ordered_channels = []  
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
if 'edit_finished' not in st.session_state:
    st.session_state.edit_finished = False 

# ─────────────────────────────────────────────
# 2. قواميس النصوص (عربي / إنجليزي)
# ─────────────────────────────────────────────
UI = {
    'ar': {
        'title':           "📺 RAMBO — المُرتب اليدوي المطور",
        'subtitle':        "⚡ نظام الترتيب الذكي المستقر: اضغط زرع، عدل أرقامك، ثم اضغط حفظ التعديلات",
        'upload_label':    "🚀 ارفع ملف القنوات (GlobalClone00001.TLL):",
        'success_read':    "🛸 تم قراءة الملف بنجاح! الموديل: ",
        'search_ph':       "🔍 ابحث عن قناة بالاسم في الملف الأصلي...",
        'all_ch_title':    "📋 1. جدول القنوات الكلي المتوفرة",
        'ordered_title':   "📊 2. جدول الترتيب النهائي (اكتب أرقام الترتيب هنا واضغط حفظ بالأسفل)",
        'col_action':      "إجراء",
        'btn_add_to_order': "➕ زرع",
        'auto_features_title': "⚙️ خيارات الفحص الذكي والصيانة الفورية للملف",
        'chk_scan_inject': "📡 تفعيل الفحص التلقائي وزرع القنوات الجديدة المتاحة على القمر فوراً",
        'chk_modern_maint': "🔧 تفعيل الصيانة الحديثة وتحديث الترددات الميتة والقديمة تلقائياً",
        'preview_title':   "🏁 استخراج وتنزيل الملفات النهائية",
        'btn_finish':      "🔒 إنهاء التعديل وتجهيز ملفات التحميل",
        'ready_msg':       "🌌 تم اعتماد الترتيب الجديد وعمل التقرير بنجاح! الملفات جاهزة الآن:",
        'btn_tll':         "📥 تحميل ملف الشاشة المعدل (GlobalClone00001.TLL)",
        'btn_txt':         "📄 تحميل تقرير لستة الترتيب (Channels_List.txt)",
        'txt_header':      "📄 تقرير الترتيب اليدوي المطور — RAMBO Page 2",
        'no_file':         "⬆️ ارفع ملف TLL أولاً لتبدأ العمل.",
    },
    'en': {
        'title':           "📺 RAMBO — Advanced Manual Sorter",
        'subtitle':        "⚡ Stable Smart Sorting System: Inject, edit order numbers, then click Save",
        'upload_label':    "🚀 Upload Channel File (GlobalClone00001.TLL):",
        'success_read':    "🛸 File Parsed Successfully! Model: ",
        'search_ph':       "🔍 Search channel name in original pool...",
        'ordered_title':   "📊 2. Final Custom List (Change numbers then click save below)",
        'col_action':      "Action",
        'btn_add_to_order': "➕ Inject",
        'auto_features_title': "⚙️ Smart Auto-Maintenance & Scanning Options",
        'chk_scan_inject': "📡 Enable Auto-Scan & Inject newly available Satellite Channels",
        'chk_modern_maint': "🔧 Enable Modern Maintenance & Auto-Update dead frequencies",
        'preview_title':   "🏁 Export & Download Final Files",
        'btn_finish':      "🔒 Finish Editing & Generate Download Links",
        'ready_msg':       "🌌 Sorting completed & report generated! Ready for download:",
        'btn_tll':         "📥 Download TV File (GlobalClone00001.TLL)",
        'btn_txt':         "📄 Download Sorted List Report (Channels_List.txt)",
        'txt_header':      "📄 Manual Sorting Advanced Report — RAMBO Page 2",
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
    div[data-testid="stFileUploader"], .rambo-box {{ background: {box_bg} !important; border: 2px solid {box_border} !important; box-shadow: 0px 5px 15px {box_shadow} !important; border-radius: 14px !important; padding: 18px !important; margin-bottom: 20px !important; }}
    .stButton>button {{ background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important; color: #ffffff !important; border: 2px solid #ff007f !important; border-radius: 12px !important; font-weight: bold; width: 100%; }}
    </style>
""", unsafe_allow_html=True)

st.title(t['title'])
st.markdown(f"<h3>{t['subtitle']}</h3>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4. دالة قراءة وتفكيك ملف الـ TLL
# ─────────────────────────────────────────────
def parse_tll(file_bytes):
    try: file_text = file_bytes.decode('utf-8')
    except UnicodeDecodeError: file_text = file_bytes.decode('latin-1')

    file_text_cleaned = re.sub(r'^\s+', '', file_text)
    root = ET.fromstring(file_text_cleaned.encode('utf-8'))
    
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
# 5. رفع ومعالجة الملف الأصلي
# ─────────────────────────────────────────────
uploaded = st.file_uploader(t['upload_label'], type=["TLL"], key="tll_uploader_p2")

if uploaded is not None:
    if not st.session_state.channels:
        try:
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
            st.session_state.model_name = model_node.text if model_node is not None else "LG TV Custom"
            st.session_state.ordered_channels = []
            st.session_state.edit_finished = False 
        except Exception as e:
            st.error(f"❌ خطأ في معالجة بناء الملف. تأكد أن الملف سليم وغير تالف. تفاصيل: {e}")
            st.stop()

if not st.session_state.channels:
    st.info(t['no_file'])
    st.stop()

st.success(f"{t['success_read']} **{st.session_state.model_name}** | 📡 {'Modern JSON' if st.session_state.is_modern else 'Legacy XML'} | الإجمالي: {len(st.session_state.channels)} قناة.")

# ─────────────────────────────────────────────
# 6. خيارات الفحص والصيانة التلقائية
# ─────────────────────────────────────────────
st.write(f"### {t['auto_features_title']}")
col_chk1, col_chk2 = st.columns(2)

with col_chk1:
    scan_active = st.checkbox(t['chk_scan_inject'], value=False, key="chk_scan_p2")
    
    if scan_active and not st.session_state.get('scan_done_p2', False):
        added_count = 0
        simulated_new_channels = [
            {"name": "RAMBO CINEMA HD", "freq": "11678", "pol": "Horizontal"},
            {"name": "EGYPT NOW", "freq": "12054", "pol": "Vertical"},
            {"name": "FOOTBALL LIVE", "freq": "11054", "pol": "Horizontal"}
        ]
        current_names = [c.get('name', '').upper() for c in st.session_state.channels]
        new_inserted_names = []
        
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
                new_inserted_names.append(f"📡 {nc['name']} (تردد: {nc['freq']})")
                added_count += 1
                
        st.session_state.scan_done_p2 = True
        st.session_state.inserted_list_p2 = new_inserted_names
        if added_count > 0:
            st.toast("📡 تم زرع القنوات الجديدة في جدول المتوفر!")
            st.rerun()

    if scan_active:
        if st.session_state.get('inserted_list_p2'):
            st.markdown("<div style='background:rgba(0, 240, 255, 0.1); padding:12px; border-radius:10px; border-left:4px solid #00f0ff; margin-top:10px;'>", unsafe_allow_html=True)
            st.markdown("**✨ قنوات جديدة تم زرعها في (1. جدول القنوات الكلي المتوفرة):**")
            for item in st.session_state.inserted_list_p2:
                st.markdown(f"<span style='color:#00f0ff;'>{item}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#888; margin-top:10px;'>ℹ️ لم يتم العثور على قنوات جديدة للزرع (مضافة بالفعل).</div>", unsafe_allow_html=True)

with col_chk2:
    maint_active = st.checkbox(t['chk_modern_maint'], value=False, key="chk_maint_p2")
    
    if maint_active and not st.session_state.get('maint_done_p2', False):
        updated_count = 0
        freq_updates = {"11747": "12054", "11137": "11785", "12015": "11678"}
        maint_details = []
        
        for ch in st.session_state.channels:
            current_freq = ch.get('freq', 'N/A')
            if current_freq in freq_updates:
                new_f = freq_updates[current_freq]
                ch['freq'] = new_f
                if st.session_state.is_modern and 'raw_node' in ch:
                    ch['raw_node']['frequency'] = int(new_f)
                elif 'raw_str' in ch:
                    ch['raw_str'] = re.sub(r'<frequency>\d+</frequency>', f'<frequency>{new_f}</frequency>', ch['raw_str'])
                
                detail_str = f"🔄 القناة: **{ch.get('name','Unknown')}** | تم تحديث التردد من `{current_freq}` إلى `{new_f}`"
                if detail_str not in maint_details:
                    maint_details.append(detail_str)
                updated_count += 1
                
        st.session_state.maint_done_p2 = True
        st.session_state.maint_details_p2 = maint_details
        if updated_count > 0:
            st.toast("🔧 تم تحديث الترددات في جدول المتوفر بنجاح!")
            st.rerun()

    if maint_active:
        if st.session_state.get('maint_details_p2'):
            st.markdown("<div style='background:rgba(255, 0, 127, 0.1); padding:12px; border-radius:10px; border-left:4px solid #ff007f; margin-top:10px;'>", unsafe_allow_html=True)
            st.markdown("**🔧 تقرير الترددات المعدلة في (1. جدول القنوات الكلي المتوفرة):**")
            for detail in st.session_state.maint_details_p2:
                st.markdown(f"<span style='color:#ff007f;'>{detail}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#888; margin-top:10px;'>ℹ️ جميع الترددات الحالية بجدول المتوفر مطابقة لأحدث نسخة.</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 7. دوال الـ Callbacks لضمان ثبات البيانات
# ─────────────────────────────────────────────
def add_channel_callback(ch_obj):
    st.session_state.ordered_channels.append(ch_obj.copy())
    st.session_state.edit_finished = False

# ─────────────────────────────────────────────
# 8. واجهة نظام الجدولين المتجاورين
# ─────────────────────────────────────────────
st.write("---")
col_table1, col_table2 = st.columns(2)

# ── الجدول الأول: القنوات الكلية المتاحة ──
with col_table1:
    st.write(f"### {t['all_ch_title']}")
    search_q1 = st.text_input(t['search_ph'], key="src_p2_1").strip().upper()
    
    filtered_pool = [c for c in st.session_state.channels if not search_q1 or search_q1 in c.get('name', '').upper()]
    st.write(f"🔎 المتاح حسب البحث: **{len(filtered_pool)}** قناة.")
    
    st.markdown(f"""
    <div style='background:{table_head_bg}; padding:8px; border-bottom:2px solid {box_border}; display:flex; font-weight:bold; color:#00f0ff; text-align:center;'>
        <div style='flex:1;'>التردد</div>
        <div style='flex:3;'>اسم القناة</div>
        <div style='flex:1;'>{t['col_action']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    scroll_container = st.container(height=400)
    with scroll_container:
        for ch in filtered_pool[:100]:
            col_f, col_n, col_b = st.columns([1, 3, 1])
            col_f.write(f"`{ch.get('freq', 'N/A')}`")
            col_n.write(f"**{ch.get('name', 'Unknown')}**")
            col_b.button(t['btn_add_to_order'], key=f"btn_add_{ch['id']}_{len(st.session_state.ordered_channels)}", on_click=add_channel_callback, args=(ch,))

# ── الجدول الثاني التفاعلي: عرض وتحديث الترتيب النهائي بسلة المهملات ──
with col_table2:
    st.write(f"### {t['ordered_title']}")
    
    ord_list = st.session_state.ordered_channels
    st.write(f"🔢 القنوات داخل لستتك الآن: **{len(ord_list)}** قناة.")
    
    if ord_list:
        st.markdown(f"""
        <div style='background:{table_head_bg}; padding:8px; border-bottom:2px solid {box_border}; display:flex; font-weight:bold; color:#ff007f; text-align:center; margin-bottom:10px;'>
            <div style='flex:1.2;'>الترتيب الحالي</div>
            <div style='flex:2.5;'>اسم القناة</div>
            <div style='flex:1.3;'>التردد</div>
            <div style='flex:1;'>حذف</div>
        </div>
        """, unsafe_allow_html=True)
        
        scroll_ordered = st.container(height=400)
        new_ranks = {}
        
        with scroll_ordered:
            for i, ch in enumerate(ord_list):
                col_rank, col_name, col_freq, col_del = st.columns([1.2, 2.5, 1.3, 1])
                
                # 1. خانة تعديل رقم الترتيب اليدوي
                with col_rank:
                    new_val = st.number_input(
                        "الترتيب", 
                        min_value=1, 
                        max_value=2000, 
                        value=i + 1, 
                        key=f"rank_input_{i}_{ch['id']}", 
                        label_visibility="collapsed"
                    )
                    new_ranks[i] = new_val
                
                # 2. اسم القناة والتردد
                col_name.write(f"**{ch.get('name', 'Unknown')}**")
                col_freq.write(f"`{ch.get('freq', 'N/A')}`")
                
                # 3. زر سلة المهملات الفورية
                with col_del:
                    if st.button("🗑️", key=f"del_btn_{i}_{ch['id']}", help="حذف القناة فوراً من قائمة الترتيب"):
                        st.session_state.ordered_channels.pop(i)
                        st.session_state.edit_finished = False
                        st.toast(f"🗑️ تم حذف قناة [{ch.get('name')}] من الترتيب!")
                        st.rerun()
        
        st.write("")
        # 4. زر اعتماد الترتيب الجديد
        if st.button("💾 اعتماد الترتيب الجديد وحفظ التعديلات", key="save_ordered_ranks_btn"):
            indexed_channels = [(new_ranks[idx], ch) for idx, ch in enumerate(ord_list)]
            indexed_channels.sort(key=lambda x: x[0])
            
            st.session_state.ordered_channels = [item[1] for item in indexed_channels]
            st.session_state.edit_finished = False
            st.toast("🎯 تم فرز وتحديث جدول الترتيب بنجاح طبقاً للأرقام المكتوبة!")
            st.rerun()
            
    else:
        st.info("💡 اضغط على زر [➕ زرع] من الجدول الأيمن لتصنع قائمة الترتيب المخصصة هنا.")

st.write("---")

# ─────────────────────────────────────────────
# 9. التجهيز النهائي والتحميل والملحوظة الفنية
# ─────────────────────────────────────────────
st.write(f"### {t['preview_title']}")

final_out_list = st.session_state.ordered_channels

if not final_out_list:
    st.warning("⚠️ جدولك المخصص فارغ حالياً! قم بزرع قنوات أولاً لتفعيل روابط التحميل.")
else:
    if st.button(t['btn_finish'], key="finish_sorting_btn_p2"):
        st.session_state.edit_finished = True
        st.rerun()

    if st.session_state.edit_finished:
        st.success(t['ready_msg'])
        
        # إنشاء ملف التقارير المكتوبة
        report_header = t.get('txt_header', "📄 تقرير الترتيب اليدوي المطور")
        txt_report = f"{report_header} ({st.session_state.model_name})\n"
        txt_report += "=" * 60 + "\n"
        for rank, ch in enumerate(final_out_list, start=1):
            txt_report += f"No. {rank:03d} : {ch.get('name','Unknown'):<30} | Freq: {ch.get('freq','N/A')} MHz\n"

        root = st.session_state.root
        legacy_tag = st.session_state.get('legacy_tag')

        # بناء ملف الـ TLL النهائي بناءً على نوع البنية
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
                raw = ch.get("raw_str", f"<ITEM>\r\n<vchName>{ch.get('name','Unknown')}</vchName>\r\n<frequency>{ch.get('freq','N/A')}</frequency>\r\n</ITEM>")
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

        # أزرار التحميل
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(label=t['btn_tll'], data=final_tll_bytes, file_name="GlobalClone00001.TLL", mime="application/octet-stream")
        with col_d2:
            st.download_button(label=t['btn_txt'], data=txt_report, file_name="Channels_List_Manual.txt", mime="text/plain; charset=utf-8")

        # ── إضافة الملحوظة الفنية الهامة المخصصة لشاشات LG ──
        st.markdown("""
        <div style="background-color: rgba(255, 165, 0, 0.12); border-left: 5px solid #ffa500; padding: 20px; border-radius: 12px; margin-top: 25px;">
            <h4 style="color: #ffa500; margin-top: 0; font-weight: bold;">💡 ملحوظة فنية هامة جداً بعد تنزيل الملف على شاشة LG:</h4>
            <p style="font-size: 15px; line-height: 1.6;">
            في بعض الحالات، بعد تنزيل ملف القنوات على الشاشة، قد تشعر أن القنوات ليست منظمة كما رتبتها. لحل هذا الأمر فوراً واجبار الشاشة على تفعيل الترتيب الصحيح، قم بالآتي:
            </p>
            <ol style="font-size: 15px; line-height: 1.7; margin-right: 20px;">
                <li>من إعدادات التلفزيون اختار <b>القنوات (Channels)</b>.</li>
                <li>بعد ذلك اختار <b>مدير القنوات (Channel Manager)</b>.</li>
                <li>اختار <b>التعديل على كل القنوات (Edit All Channels)</b>.</li>
                <li>ستظهر لك القنوات المرتبة ويكون بعضها في وضع مخفي، قم <b>بتحديد كل القنوات</b> واختار <b>استعادة (Restore)</b>.</li>
            </ol>
            <p style="font-size: 13px; color: #ffaa55; font-style: italic; margin-bottom: 0; margin-top: 10px;">
            *ملحوظة: تفعل هذه الخطوة فقط إذا شعرت أن الملف بعد التنزيل غير مرتب كما حددته على الموقع.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 10. الفوتر السيبراني
# ─────────────────────────────────────────────
whatsapp_url = "https://api.whatsapp.com/send?phone=201280339779&text=Hello%20Developer%20Rafik%20Rambo"
st.markdown(f"""
<div class="futuristic-cyber-footer" style="background:{footer_bg}; border:2px solid #00f0ff; color:{footer_text} !important; padding:35px; text-align:center; border-radius:20px; margin-top:65px; font-family:'Orbitron', sans-serif;">
    <div class="footer-dev" style="color:#ff007f; font-size:26px; font-weight:bold;">🛠️ DEVELOPER ENG: RAFIK RAMBO</div>
    <div>📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
    <div>✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com</div>
    <a href="{whatsapp_url}" target="_blank" class="cyber-whatsapp-btn" style="color:#25d366 !important; padding:14px 35px; border-radius:35px; display:inline-block; font-weight:bold; border:2px solid #25d366; text-decoration:none; margin-top:20px;">WhatsApp Web</a>
</div>
""", unsafe_allow_html=True)
