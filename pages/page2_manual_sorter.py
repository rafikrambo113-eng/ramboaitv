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
    st.session_state.channels = []          # قائمة القنوات المحملة
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
# 2. نصوص الواجهة (عربي / إنجليزي)
# ─────────────────────────────────────────────
UI = {
    'ar': {
        'title':           "📺 RAMBO — المُرتِّب اليدوي للقنوات",
        'subtitle':        "⚡ تحكم كامل — رتّب كل قناة بنفسك، عدّل ترددها، أضف قنوات جديدة",
        'upload_label':    "🚀 ارفع ملف القنوات (GlobalClone00001.TLL):",
        'success_read':    "🛸 تم قراءة الملف بنجاح! الموديل: ",
        'search_ph':       "🔍 ابحث عن قناة بالاسم...",
        'tbl_num':         "رقم الترتيب",
        'tbl_name':        "اسم القناة",
        'tbl_freq':        "التردد (MHz)",
        'tbl_action':      "تعديل",
        'move_title':      "📌 نقل قناة لرقم محدد",
        'move_ch':         "اختر القناة المراد نقلها:",
        'move_to':         "انقلها إلى الرقم:",
        'move_btn':        "✅ تنفيذ النقل",
        'move_ok':         "✔️ تم نقل القناة بنجاح!",
        'edit_freq_title': "✏️ تعديل / إضافة تردد قناة",
        'edit_sel':        "اختر القناة:",
        'edit_new_freq':   "التردد الجديد (MHz):",
        'edit_pol':        "الاستقطاب (Polarization):",
        'edit_btn':        "💾 حفظ التردد",
        'edit_ok':         "✔️ تم تحديث التردد!",
        'add_title':       "➕ إضافة قناة جديدة غير موجودة في الملف",
        'add_name':        "اسم القناة الجديدة:",
        'add_freq':        "تردد القناة (MHz):",
        'add_pol':         "الاستقطاب:",
        'add_btn':         "🚀 إضافة القناة",
        'add_ok':          "✔️ تمت الإضافة!",
        'add_dup':         "⚠️ القناة موجودة بالفعل!",
        'preview_title':   "📊 الترتيب النهائي (جدول كامل):",
        'ready_msg':       "🌌 الملفات جاهزة للتحميل!",
        'btn_tll':         "📥 تحميل ملف الشاشة (GlobalClone00001.TLL)",
        'btn_txt':         "📄 تحميل تقرير الترتيب (Channels_List.txt)",
        'txt_header':      "📄 تقرير الترتيب اليدوي — RAMBO Page 2",
        'no_file':         "⬆️ ارفع ملف TLL أولاً لتبدأ.",
        'search_none':     "⚠️ لا توجد قنوات مطابقة.",
        'col_h':           "رقم",
        'col_n':           "اسم القناة",
        'col_f':           "التردد",
    },
    'en': {
        'title':           "📺 RAMBO — Manual Channel Sorter",
        'subtitle':        "⚡ Full Control — Reorder, Edit Frequency, Add New Channels",
        'upload_label':    "🚀 Upload Channel File (GlobalClone00001.TLL):",
        'success_read':    "🛸 File Parsed Successfully! Model: ",
        'search_ph':       "🔍 Search channel by name...",
        'tbl_num':         "Order No.",
        'tbl_name':        "Channel Name",
        'tbl_freq':        "Frequency (MHz)",
        'tbl_action':      "Action",
        'move_title':      "📌 Move Channel to Specific Position",
        'move_ch':         "Select channel to move:",
        'move_to':         "Move it to position No.:",
        'move_btn':        "✅ Apply Move",
        'move_ok':         "✔️ Channel moved successfully!",
        'edit_freq_title': "✏️ Edit / Add Channel Frequency",
        'edit_sel':        "Select Channel:",
        'edit_new_freq':   "New Frequency (MHz):",
        'edit_pol':        "Polarization:",
        'edit_btn':        "💾 Save Frequency",
        'edit_ok':         "✔️ Frequency Updated!",
        'add_title':       "➕ Add New Channel (Not in File)",
        'add_name':        "New Channel Name:",
        'add_freq':        "Frequency (MHz):",
        'add_pol':         "Polarization:",
        'add_btn':         "🚀 Add Channel",
        'add_ok':          "✔️ Channel Added!",
        'add_dup':         "⚠️ Channel already exists!",
        'preview_title':   "📊 Final Channel Order (Full Table):",
        'ready_msg':       "🌌 Files ready for download!",
        'btn_tll':         "📥 Download TV File (GlobalClone00001.TLL)",
        'btn_txt':         "📄 Download Report (Channels_List.txt)",
        'txt_header':      "📄 Manual Sorting Report — RAMBO Page 2",
        'no_file':         "⬆️ Upload a TLL file to start.",
        'search_none':     "⚠️ No matching channels found.",
        'col_h':           "No.",
        'col_n':           "Channel Name",
        'col_f':           "Frequency",
    }
}

t = UI[st.session_state.lang]

# ─────────────────────────────────────────────
# 3. إعداد الصفحة
# ─────────────────────────────────────────────
st.set_page_config(page_title="RAMBO P2 — Manual Sorter", page_icon="🎛️", layout="wide")

# أزرار اللغة والثيم
col_lang, col_theme, _ = st.columns([1.2, 1.5, 8])
with col_lang:
    if st.button("🌐 English" if st.session_state.lang == 'ar' else "🌐 العربية"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
        st.rerun()
with col_theme:
    if st.button("☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

# ─────────────────────────────────────────────
# 4. CSS السيبراني (نفس ستايل صفحة 1)
# ─────────────────────────────────────────────
if st.session_state.theme == 'dark':
    bg_style       = "radial-gradient(circle at 50% 50%, #110926 0%, #05020d 100%)"
    text_color     = "#00f0ff"
    box_bg         = "rgba(13, 7, 33, 0.85)"
    box_border     = "#00f0ff"
    box_shadow     = "rgba(0, 240, 255, 0.35)"
    text_shadow    = "0 0 5px rgba(0, 240, 255, 0.4)"
    footer_bg      = "#080314"
    footer_text    = "#ffffff"
    table_head_bg  = "#0d0722"
    table_row_bg   = "rgba(0,240,255,0.04)"
    table_row_alt  = "rgba(255,0,127,0.05)"
    table_border   = "#00f0ff33"
else:
    bg_style       = "radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e4e7eb 100%)"
    text_color     = "#0d0722"
    box_bg         = "#ffffff"
    box_border     = "#ff007f"
    box_shadow     = "rgba(255, 0, 127, 0.15)"
    text_shadow    = "none"
    footer_bg      = "#110926"
    footer_text    = "#ffffff"
    table_head_bg  = "#0d0722"
    table_row_bg   = "#f9f9ff"
    table_row_alt  = "#fff0f7"
    table_border   = "#ff007f33"

font_family = "'Cairo', sans-serif" if st.session_state.lang == 'ar' else "'Orbitron', sans-serif"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Cairo:wght@400;700&display=swap');
    .main {{ background: {bg_style} !important; color: {text_color} !important; font-family: {font_family}; }}
    h1 {{ color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 25px rgba(255,0,127,0.4) !important; text-align: center; font-weight: 900; margin-top: 5px; }}
    h3, p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] p {{ color: {text_color} !important; text-shadow: {text_shadow}; }}
    .stTextInput>div>div>input, .stNumberInput>div>div>input {{
        background-color: {box_bg} !important; color: {text_color} !important;
        border: 2px solid {box_border} !important; border-radius: 10px !important;
    }}
    .stSelectbox>div>div, .stMultiSelect>div>div {{
        background-color: {box_bg} !important; border: 2px solid {box_border} !important;
        border-radius: 10px !important;
    }}
    .stCheckbox, .stMultiSelect, div[data-testid="stExpander"],
    div[data-testid="stFileUploader"], .rambo-box {{
        background: {box_bg} !important;
        border: 2px solid {box_border} !important;
        box-shadow: 0px 5px 15px {box_shadow} !important;
        border-radius: 14px !important;
        padding: 18px !important;
        margin-bottom: 20px !important;
    }}
    .stButton>button {{
        background: linear-gradient(135deg, #ff007f 0%, #aa0055 100%) !important;
        color: #ffffff !important; border: 2px solid #ff007f !important;
        border-radius: 12px !important; font-weight: bold;
    }}
    /* جدول القنوات */
    .rambo-table {{ width:100%; border-collapse:collapse; font-family:{font_family}; font-size:13px; }}
    .rambo-table th {{
        background:{table_head_bg}; color:#00f0ff;
        padding:10px 14px; text-align:center;
        border-bottom: 2px solid {box_border};
        position: sticky; top: 0;
    }}
    .rambo-table td {{ padding:8px 14px; text-align:center; border-bottom:1px solid {table_border}; color:{text_color}; }}
    .rambo-table tr:nth-child(even) td {{ background:{table_row_alt}; }}
    .rambo-table tr:nth-child(odd)  td {{ background:{table_row_bg}; }}
    .rambo-table tr:hover td {{ background: rgba(255,0,127,0.12) !important; }}
    .rambo-table .ch-name {{ text-align:{'right' if st.session_state.lang == 'ar' else 'left'}; font-weight:600; }}
    .table-scroll {{ max-height:420px; overflow-y:auto; border: 2px solid {box_border}; border-radius:12px; }}
    .futuristic-cyber-footer {{
        background:{footer_bg}; border:2px solid #00f0ff; color:{footer_text} !important;
        padding:35px; text-align:center; border-radius:20px; margin-top:65px;
        font-family:'Orbitron', sans-serif;
    }}
    .footer-dev {{ color:#ff007f; font-size:26px; font-weight:bold; }}
    .cyber-whatsapp-btn {{
        color:#25d366 !important; padding:14px 35px; border-radius:35px;
        display:inline-block; font-weight:bold; border:2px solid #25d366;
        text-decoration:none; margin-top:20px;
    }}
    </style>
""", unsafe_allow_html=True)

st.title(t['title'])
st.markdown(f"<h3>{t['subtitle']}</h3>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 5. دالة تحويل القنوات من الملف
# ─────────────────────────────────────────────
def parse_tll(file_bytes):
    """يقرأ ملف TLL ويرجع (channels_list, is_modern, root, broadcast_data, file_text)"""
    try:
        file_text = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        file_text = file_bytes.decode('latin-1')

    root = ET.fromstring(file_bytes)
    legacy_tag = root.find(".//legacybroadcast")
    is_modern  = legacy_tag is not None and legacy_tag.text

    channels = []
    if is_modern:
        bdata = json.loads(legacy_tag.text)
        for idx, ch in enumerate(bdata.get("channelList", [])):
            channels.append({
                "id":   idx,
                "name": ch.get("channelName", "Unknown"),
                "freq": str(ch.get("frequency", "N/A")),
                "pol":  ch.get("polarization", "Vertical"),
                "raw_node": ch
            })
        return channels, True, root, bdata, file_text, legacy_tag
    else:
        items = re.findall(r'(<ITEM>.*?</ITEM>)', file_text, re.DOTALL)
        for idx, item_str in enumerate(items):
            nm = re.search(r'<vchName>(.*?)</vchName>', item_str)
            fq = re.search(r'<frequency>(.*?)</frequency>', item_str)
            channels.append({
                "id":      idx,
                "name":    nm.group(1) if nm else "Unknown",
                "freq":    fq.group(1) if fq else "N/A",
                "pol":     "Vertical",
                "raw_str": item_str
            })
        return channels, False, root, None, file_text, None

# ─────────────────────────────────────────────
# 6. رفع الملف
# ─────────────────────────────────────────────
uploaded = st.file_uploader(t['upload_label'], type=["TLL"])

if uploaded is not None:
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

if not st.session_state.channels:
    st.info(t['no_file'])
    st.stop()

# مرجع سريع
channels       = st.session_state.channels
is_modern      = st.session_state.is_modern
model_name     = st.session_state.model_name

st.info(f"{t['success_read']} **{model_name}**  |  📡 {'Modern JSON' if is_modern else 'Legacy XML'}")
st.write("---")

# ─────────────────────────────────────────────
# 7. سيرش بار
# ─────────────────────────────────────────────
st.write(f"### 🔍 {t['search_ph']}")
search_q = st.text_input("", placeholder=t['search_ph'], label_visibility="collapsed").strip().upper()

def filtered_channels():
    if not search_q:
        return channels
    return [c for c in channels if search_q in c['name'].upper()]

# ─────────────────────────────────────────────
# 8. عرض الجدول الحالي (مع سكرول)
# ─────────────────────────────────────────────
visible = filtered_channels()
rows_html = ""
for rank, ch in enumerate(channels, start=1):
    if ch not in visible:
        continue
    rows_html += f"""
    <tr>
        <td><b style="color:#ff007f;">{rank}</b></td>
        <td class="ch-name">{ch['name']}</td>
        <td>{ch['freq']}</td>
    </tr>"""

table_html = f"""
<div class="table-scroll">
<table class="rambo-table">
<thead><tr>
  <th>{t['col_h']}</th>
  <th>{t['col_n']}</th>
  <th>{t['col_f']}</th>
</tr></thead>
<tbody>{rows_html}</tbody>
</table>
</div>"""
st.markdown(table_html, unsafe_allow_html=True)
st.write(f"**{len(visible)} / {len(channels)}** {'قناة ظاهرة' if st.session_state.lang=='ar' else 'channels shown'}")
st.write("---")

# ─────────────────────────────────────────────
# 9. نقل قناة لرقم محدد
# ─────────────────────────────────────────────
st.write(f"### {t['move_title']}")
ch_names = [f"{i+1}. {c['name']}" for i, c in enumerate(channels)]

col_m1, col_m2, col_m3 = st.columns([3, 1.5, 1])
with col_m1:
    chosen_label = st.selectbox(t['move_ch'], ch_names, key="move_sel")
with col_m2:
    target_pos = st.number_input(t['move_to'], min_value=1, max_value=len(channels), value=1, step=1, key="move_pos")
with col_m3:
    st.write("")
    st.write("")
    if st.button(t['move_btn']):
        chosen_idx  = ch_names.index(chosen_label)
        target_idx  = int(target_pos) - 1
        item        = channels.pop(chosen_idx)
        channels.insert(target_idx, item)
        st.session_state.channels = channels
        st.success(t['move_ok'])
        st.rerun()

st.write("---")

# ─────────────────────────────────────────────
# 10. تعديل / إضافة تردد لقناة موجودة
# ─────────────────────────────────────────────
st.write(f"### {t['edit_freq_title']}")
col_e1, col_e2, col_e3, col_e4 = st.columns([3, 1.5, 1.5, 1])
with col_e1:
    edit_label = st.selectbox(t['edit_sel'], ch_names, key="edit_sel")
with col_e2:
    edit_freq  = st.number_input(t['edit_new_freq'], min_value=1, max_value=99999,
                                  value=11000, step=1, key="edit_freq")
with col_e3:
    edit_pol   = st.selectbox(t['edit_pol'], ["Vertical", "Horizontal"], key="edit_pol")
with col_e4:
    st.write("")
    st.write("")
    if st.button(t['edit_btn']):
        idx = ch_names.index(edit_label)
        channels[idx]['freq'] = str(edit_freq)
        channels[idx]['pol']  = edit_pol
        # تحديث الـ raw_node / raw_str أيضاً
        if is_modern:
            channels[idx]['raw_node']['frequency']    = edit_freq
            channels[idx]['raw_node']['polarization'] = edit_pol
        else:
            raw = channels[idx]['raw_str']
            raw = re.sub(r'<frequency>\d+</frequency>', f'<frequency>{edit_freq}</frequency>', raw)
            channels[idx]['raw_str'] = raw
        st.session_state.channels = channels
        st.success(t['edit_ok'])
        st.rerun()

st.write("---")

# ─────────────────────────────────────────────
# 11. إضافة قناة جديدة غير موجودة
# ─────────────────────────────────────────────
st.write(f"### {t['add_title']}")
col_a1, col_a2, col_a3, col_a4 = st.columns([3, 1.5, 1.5, 1])
with col_a1:
    new_name = st.text_input(t['add_name'], key="add_name", placeholder="e.g. MY CHANNEL HD")
with col_a2:
    new_freq = st.number_input(t['add_freq'], min_value=1, max_value=99999,
                                value=11000, step=1, key="add_freq")
with col_a3:
    new_pol  = st.selectbox(t['add_pol'], ["Vertical", "Horizontal"], key="add_pol")
with col_a4:
    st.write("")
    st.write("")
    if st.button(t['add_btn']):
        name_clean = new_name.strip().upper()
        existing   = [c['name'].upper() for c in channels]
        if name_clean in existing:
            st.warning(t['add_dup'])
        elif name_clean:
            new_idx = len(channels)
            if is_modern:
                new_node = {
                    "channelName": name_clean, "frequency": new_freq,
                    "polarization": new_pol, "majorNumber": new_idx + 1,
                    "serviceType": "1", "scrambled": "false", "symbolRate": "27500"
                }
                channels.append({"id": new_idx, "name": name_clean,
                                  "freq": str(new_freq), "pol": new_pol,
                                  "raw_node": new_node})
            else:
                raw_str = (f"<ITEM>\r\n<prNum>{new_idx+1}</prNum>\r\n"
                           f"<vchName>{name_clean}</vchName>\r\n"
                           f"<frequency>{new_freq}</frequency>\r\n"
                           f"<serviceType>1</serviceType>\r\n</ITEM>")
                channels.append({"id": new_idx, "name": name_clean,
                                  "freq": str(new_freq), "pol": new_pol,
                                  "raw_str": raw_str})
            st.session_state.channels = channels
            st.success(t['add_ok'])
            st.rerun()

st.write("---")

# ─────────────────────────────────────────────
# 12. جدول المعاينة النهائي الكامل
# ─────────────────────────────────────────────
st.write(f"### {t['preview_title']}")
preview_rows = ""
for rank, ch in enumerate(channels, start=1):
    preview_rows += f"""
    <tr>
        <td><b style="color:#ff007f;">{rank}</b></td>
        <td class="ch-name">{ch['name']}</td>
        <td>{ch['freq']}</td>
        <td style="color:#aaa; font-size:11px;">{ch.get('pol','—')}</td>
    </tr>"""

preview_table = f"""
<div class="table-scroll">
<table class="rambo-table">
<thead><tr>
  <th>{t['col_h']}</th><th>{t['col_n']}</th><th>{t['col_f']}</th>
  <th>{'الاستقطاب' if st.session_state.lang=='ar' else 'Pol.'}</th>
</tr></thead>
<tbody>{preview_rows}</tbody>
</table>
</div>"""
st.markdown(preview_table, unsafe_allow_html=True)
st.write("---")

# ─────────────────────────────────────────────
# 13. بناء الملفات النهائية وتحميلها
# ─────────────────────────────────────────────
st.success(t['ready_msg'])

# ── بناء نص التقرير ──
txt_report = f"{t['txt_header']} ({model_name})\n"
txt_report += "=" * 50 + "\n"
for rank, ch in enumerate(channels, start=1):
    txt_report += f"No. {rank:03d} : {ch['name']:<30} | Freq: {ch['freq']} MHz | Pol: {ch.get('pol','—')}\n"

# ── بناء ملف TLL ──
root       = st.session_state.root
legacy_tag = st.session_state.get('legacy_tag')

if is_modern:
    bdata = st.session_state.broadcast_data
    final_list = []
    for rank, ch in enumerate(channels, start=1):
        node = ch["raw_node"]
        node["majorNumber"] = rank
        final_list.append(node)
    bdata["channelList"] = final_list
    legacy_tag.text = json.dumps(bdata, ensure_ascii=False)
    final_tll_bytes = ET.tostring(root, encoding="utf-8")
else:
    file_text = st.session_state.file_text_original
    item_strings = []
    for rank, ch in enumerate(channels, start=1):
        raw = ch["raw_str"]
        if "<prNum>" in raw:
            raw = re.sub(r'<prNum>\d+</prNum>', f'<prNum>{rank}</prNum>', raw)
        else:
            raw = raw.replace("<ITEM>", f"<ITEM>\r\n<prNum>{rank}</prNum>")
        item_strings.append(raw)

    combined = "\r\n".join(item_strings)
    start_i  = file_text.find("<ITEM>")
    end_i    = file_text.rfind("</ITEM>") + len("</ITEM>")
    if start_i != -1 and end_i != -1:
        final_text = file_text[:start_i] + combined + file_text[end_i:]
    else:
        final_text = combined
    try:
        final_tll_bytes = final_text.encode('utf-8')
    except UnicodeEncodeError:
        final_tll_bytes = final_text.encode('latin-1')

col_d1, col_d2 = st.columns(2)
with col_d1:
    st.download_button(
        label=t['btn_tll'],
        data=final_tll_bytes,
        file_name="GlobalClone00001.TLL",
        mime="application/octet-stream"
    )
with col_d2:
    st.download_button(
        label=t['btn_txt'],
        data=txt_report,
        file_name="Channels_List_Manual.txt",
        mime="text/plain; charset=utf-8"
    )

# ─────────────────────────────────────────────
# 14. الفوتر السيبراني
# ─────────────────────────────────────────────
whatsapp_url = ("https://api.whatsapp.com/send?phone=201280339779"
                "&text=Hello%20Developer%20Rafik%20Rambo%2C%20"
                "I%20have%20an%20inquiry%20about%20the%20LG%20Sorter%3A")

st.markdown(f"""
<div class="futuristic-cyber-footer">
    <div class="footer-dev">🛠️ DEVELOPER ENG: RAFIK RAMBO</div>
    <div>📱 <b>MOBILE / الموبايل:</b> +201280339779</div>
    <div>✉️ <b>E-MAIL:</b> rafikrambo113@gmail.com</div>
    <a href="{whatsapp_url}" target="_blank" class="cyber-whatsapp-btn">WhatsApp Web</a>
</div>
""", unsafe_allow_html=True)

