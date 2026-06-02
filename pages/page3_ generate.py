# ── زر التوليد (التعديل المطلوب هنا) ──
if st.button("🚀 توليد الملف النهائي"):
    # 1. تحضير قائمة القنوات بناءً على الترتيب المختار
    ordered_channels = []
    for cat in user_priority:
        for ch_name in NILESAT_GEN_DB.get(cat, []):
            # هنا نفترض تردد افتراضي 11000 أو يمكنك ربطه بقاعدة بيانات كاملة
            ordered_channels.append({"name": ch_name, "freq": "11000", "pol": "Vertical"})

    # 2. بناء الملف النهائي (البيانات الحقيقية)
    if system_type == "حديث":
        # هيكل JSON للموديلات الحديثة
        channel_list = []
        for i, ch in enumerate(ordered_channels, 1):
            channel_list.append({
                "channelName": ch["name"], "majorNumber": i, "minorNumber": 0,
                "frequency": int(ch["freq"]), "polarization": ch["pol"],
                "satelliteName": "Nilesat", "serviceType": 1
            })
        payload = json.dumps({"channelList": channel_list, "satelliteList": [{"satelliteName": "Nilesat"}]}, ensure_ascii=False)
        final_content = f'<?xml version="1.0" encoding="utf-8"?><TLLDATA><ModelName>{model or "RAMBO"}</ModelName><legacybroadcast><![CDATA[{payload}]]></legacybroadcast></TLLDATA>'
    else:
        # هيكل XML للموديلات القديمة
        items = "".join([f'<ITEM><prNum>{i}</prNum><vchName>{ch["name"]}</vchName><frequency>{ch["freq"]}</frequency><polarization>{ch["pol"]}</polarization></ITEM>' for i, ch in enumerate(ordered_channels, 1)])
        final_content = f'<?xml version="1.0" encoding="utf-8"?><TLLDATA><ModelName>{model or "RAMBO"}</ModelName>{items}</TLLDATA>'

    # 3. بناء ملف التقرير النصي (TXT)
    report_content = "تقرير ملف القنوات RAMBO\n" + "="*30 + "\n"
    for i, ch in enumerate(ordered_channels, 1):
        report_content += f"{i}. {ch['name']} | التردد: {ch['freq']}\n"

    st.success(f"✅ تم بناء ملف الـ {system_type} بنجاح!")
    
    # 4. أزرار التحميل بالبيانات الحقيقية
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button("📥 تحميل ملف القنوات TLL", final_content.encode('utf-8'), "GlobalClone00001.TLL", "application/octet-stream")
    with col_btn2:
        st.download_button("📄 تحميل تقرير القنوات TXT", report_content, "Channels_List.txt", "text/plain")

    st.warning("💡 بعد تنزيل الملف: ادخل مدير القنوات -> تعديل كل القنوات -> استعادة (Restore).")
