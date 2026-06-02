# ══════════════════════════════════════════════
# 🎛️ مصفوفة ترتيب الفئات (Category Sorting)
# ══════════════════════════════════════════════

st.write(f"### {t['config_title']}")
st.markdown(f"💡 *{t['config_tip']}*")

selected_categories = st.multiselect(
    t['multiselect_label'],
    options=ALL_AVAILABLE_CATEGORIES,
    default=ALL_AVAILABLE_CATEGORIES
)

if not selected_categories:
    st.warning(t['warning_no_priority'])
    selected_categories = ALL_AVAILABLE_CATEGORIES

# ══════════════════════════════════════════════
# 🚀 محرك التوليد (Generator Core)
# ══════════════════════════════════════════════

if st.button(t['btn_generate'], key="gen_btn_final"):
    
    # 1. ترتيب القنوات بناءً على اختيار المستخدم
    sorted_channels = []
    for cat in selected_categories:
        for ch in FULL_CHANNEL_DB:
            if ai_classify(ch["name"]) == cat:
                sorted_channels.append(ch)
    
    # 2. بناء الهيكل بناءً على النظام المختار
    if system_type == "Modern":
        # هيكل JSON للشاشات الحديثة
        data_payload = {
            "modelInfo": {"country": country_key.upper()},
            "channelList": [
                {
                    "channelName": ch["name"],
                    "majorNumber": i + 1,
                    "frequency": ch["frequency"],
                    "polarization": 0 if ch["polarization"] == "Vertical" else 1,
                    "serviceType": 1
                } for i, ch in enumerate(sorted_channels)
            ]
        }
        json_str = json.dumps(data_payload)
        final_file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<TLLDATA>
    <ModelInfo><ModelName>{selected_model}</ModelName></ModelInfo>
    <CHANNEL><legacybroadcast>{json_str}</legacybroadcast></CHANNEL>
</TLLDATA>"""
    else:
        # هيكل XML بسيط للشاشات القديمة (Legacy)
        root = ET.Element("TLLDATA")
        ch_list = ET.SubElement(root, "CHANNEL")
        for i, ch in enumerate(sorted_channels):
            chan_node = ET.SubElement(ch_list, "Channel")
            chan_node.set("name", ch["name"])
            chan_node.set("number", str(i + 1))
            chan_node.set("frequency", str(ch["frequency"]))
        final_file_content = ET.tostring(root, encoding='utf-8').decode('utf-8')

    # 3. توفير التحميل
    st.success(t['ready_msg'])
    st.download_button(t['btn_download_tll'], final_file_content, "GlobalClone00001.TLL", "application/octet-stream")
    
    # تقرير نصي
    report = f"{t['txt_header']}\n{'-'*30}\n{t['txt_system']} {system_type}\n{t['txt_country']} {country_display}\n\n"
    for i, ch in enumerate(sorted_channels):
        report += f"{i+1}. {ch['name']} - {ch['frequency']}\n"
    st.download_button(t['btn_download_txt'], report, "Channels_List.txt")

# 💡 نصيحة LG
with st.expander(f"💡 {t['lg_trick_title']}"):
    st.write(t['lg_trick_text'])

st.markdown('<div class="futuristic-cyber-footer">RAMBO Generator v3.0<br><div class="footer-dev">Advanced TV Logic</div></div>', unsafe_allow_html=True)
