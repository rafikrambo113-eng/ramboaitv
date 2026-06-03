# صفحة 3: توليد ملف قنوات جديد
if page == t['page3_title']:
    st.markdown(f"## {t['page3_title']}")
    st.markdown("---")
    st.markdown("📝 **أدخل بيانات القمر الصناعي لتوليد ملف قنوات جديد**")
    
    # حقول الإدخال
    col1, col2 = st.columns(2)
    
    with col1:
        satellite = st.text_input(f"📡 {t['satellite']} *", 
                                  placeholder="مثال: NILESAT 201",
                                  key="page3_satellite")
        country = st.text_input(f"🌍 {t['country']} *", 
                                placeholder="مثال: Egypt, Saudi Arabia",
                                key="page3_country")
        compass = st.text_input(f"🧭 {t['compass']}", 
                                placeholder="مثال: 23.5E (اختياري)",
                                key="page3_compass")
    
    with col2:
        model = st.text_input(f"📺 {t['model']}", 
                              placeholder="مثال: 55UP7500PUA (اختياري)",
                              key="page3_model")
        year = st.number_input(f"📅 {t['year']} *", 
                               min_value=2009, 
                               max_value=2026, 
                               value=2024,
                               step=1,
                               key="page3_year")
        st.info("💡 سنة الصنع تحدد نوع الملف: 2018 فأحدث = ملف جديد (webOS), قبل 2018 = ملف قديم (NetCast)")
    
    st.markdown("---")
    
    # زر التوليد
    if st.button(f"⚡ {t['generate']}", key="page3_generate", use_container_width=True):
        if not satellite or not country or not year:
            st.error("❗ يرجى ملء جميع الحقول الإلزامية: القمر الصناعي، بلد البث، سنة الصنع")
        else:
            # تحديد نوع الملف بناءً على السنة
            is_new_file = year >= 2018  # webOS 4.0+ يعتبر جديد
            
            st.success(f"✅ تم تحديد نوع الملف: **{t['new_file'] if is_new_file else t['old_file']}**")
            
            # إنشاء محتوى الملف
            if is_new_file:
                # صيغة الملف الجديد (webOS 4.0+ مع JSON داخل legacybroadcast)
                st.markdown("### 📄 محتوى الملف الجديد (JSON Format - webOS)")
                
                channel_data = {
                    "version": "4.0",
                    "fileType": "GlobalClone",
                    "channelList": [
                        {
                            "name": "MBC 1",
                            "category": "🎬 مسلسلات ودراما",
                            "frequency": 10851,
                            "polarization": "H",
                            "majorNumber": 1,
                            "invisible": False,
                            "skipped": False
                        },
                        {
                            "name": "Al Jazeera",
                            "category": "📰 أخبار وسياسة",
                            "frequency": 10853,
                            "polarization": "H",
                            "majorNumber": 2,
                            "invisible": False,
                            "skipped": False
                        },
                        {
                            "name": "BeIN Sports",
                            "category": "⚽ رياضة",
                            "frequency": 10911,
                            "polarization": "V",
                            "majorNumber": 3,
                            "invisible": False,
                            "skipped": False
                        }
                    ],
                    "satellite": satellite,
                    "country": country,
                    "compass": compass if compass else "0.0",
                    "model": model if model else "Unknown",
                    "year": year
                }
                
                json_str = json.dumps(channel_data, ensure_ascii=False, indent=2)
                st.code(json_str, language="json")
                
                # زر التحميل للملف الجديد
                st.download_button(
                    label="💾 تنزيل ملف جديد (.TLL)",
                    data=json_str.encode('utf-8'),
                    file_name=f"GlobalClone_{satellite.replace(' ', '_')}_{country}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
            else:
                # صيغة الملف القديم (NetCast OS مع XML ITEM)
                st.markdown("### 📄 محتوى الملف القديم (XML Format - NetCast)")
                
                xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<LGTV_CONF>
    <HEADER>
        <VERSION>1.0</VERSION>
        <TYPE>SAT_DTV</TYPE>
        <SATELLITE>{satellite}</SATELLITE>
        <COUNTRY>{country}</COUNTRY>
        <COMPASS>{compass if compass else "0.0"}</COMPASS>
        <MODEL>{model if model else "Unknown"}</MODEL>
        <YEAR>{year}</YEAR>
    </HEADER>
    <ITEM>
        <prNum>1</prNum>
        <name>MBC 1</name>
        <frequency>10851</frequency>
        <polarization>H</polarization>
        <category>🎬 مسلسلات ودراما</category>
    </ITEM>
    <ITEM>
        <prNum>2</prNum>
        <name>Al Jazeera</name>
        <frequency>10853</frequency>
        <polarization>H</polarization>
        <category>📰 أخبار وسياسة</category>
    </ITEM>
    <ITEM>
        <prNum>3</prNum>
        <name>BeIN Sports</name>
        <frequency>10911</frequency>
        <polarization>V</polarization>
        <category>⚽ رياضة</category>
    </ITEM>
</LGTV_CONF>"""
                
                st.code(xml_content, language="xml")
                
                # زر التحميل للملف القديم
                st.download_button(
                    label="💾 تنزيل ملف قديم (.TLL)",
                    data=xml_content.encode('utf-8'),
                    file_name=f"ChannelList_{satellite.replace(' ', '_')}_{country}.xml",
                    mime="text/xml",
                    use_container_width=True
                )
            
            # ملخص الإعدادات
            st.markdown("---")
            st.markdown("### 📊 ملخص الإعدادات")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                - **القمر الصناعي**: `{satellite}`
                - **بلد البث**: `{country}`
                - **نوع الملف**: `{t['new_file'] if is_new_file else t['old_file']}`
                """)
            with col2:
                st.markdown(f"""
                - **البوصلة**: `{compass if compass else 'غير محدد'}`
                - **الموديل**: `{model if model else 'غير محدد'}`
                - **سنة الصنع**: `{year}`
                """)
