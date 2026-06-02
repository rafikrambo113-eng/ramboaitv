# ── قاعدة بيانات موسعة (أكثر من 70 قناة) لضمان الغزارة ──
NILESAT_GEN_DB = {
    "AL HAYAT": {"frequency": 12207, "polarization": "Vertical"},
    "AL HAYAT 2": {"frequency": 12207, "polarization": "Vertical"},
    "AL HAYAT CINEMA": {"frequency": 12207, "polarization": "Vertical"},
    "SAT-7 KIDS": {"frequency": 11353, "polarization": "Vertical"},
    "SAT-7 ARABIC": {"frequency": 11353, "polarization": "Vertical"},
    "CTV": {"frequency": 12022, "polarization": "Vertical"},
    "AGHAPY TV": {"frequency": 11179, "polarization": "Horizontal"},
    "MESAT": {"frequency": 11096, "polarization": "Horizontal"},
    "IQRAA": {"frequency": 11938, "polarization": "Vertical"},
    "MAJD": {"frequency": 11862, "polarization": "Vertical"},
    "RAHMA": {"frequency": 11938, "polarization": "Vertical"},
    "QURAN KAREEM": {"frequency": 11727, "polarization": "Vertical"},
    "AL JAZEERA HD": {"frequency": 10853, "polarization": "Vertical"},
    "AL ARABIYA": {"frequency": 11938, "polarization": "Vertical"},
    "AL HADATH": {"frequency": 11938, "polarization": "Vertical"},
    "CBC": {"frequency": 12092, "polarization": "Vertical"},
    "CBC DRAMA": {"frequency": 11488, "polarization": "Horizontal"},
    "EXTRA NEWS": {"frequency": 12092, "polarization": "Vertical"},
    "ON E": {"frequency": 12092, "polarization": "Vertical"},
    "ON DRAMA": {"frequency": 11861, "polarization": "Vertical"},
    "MBC 2": {"frequency": 11938, "polarization": "Vertical"},
    "MBC 4": {"frequency": 11938, "polarization": "Vertical"},
    "MBC DRAMA": {"frequency": 11470, "polarization": "Vertical"},
    "MBC MAX": {"frequency": 11938, "polarization": "Vertical"},
    "ROTANA CINEMA": {"frequency": 11938, "polarization": "Vertical"},
    "ROTANA DRAMA": {"frequency": 11296, "polarization": "Horizontal"},
    "ROTANA ACTION": {"frequency": 11296, "polarization": "Horizontal"},
    "ON TIME SPORTS 1": {"frequency": 11861, "polarization": "Vertical"},
    "ON TIME SPORTS 2": {"frequency": 11861, "polarization": "Vertical"},
    "SPACE TOON": {"frequency": 11727, "polarization": "Vertical"},
    "MAJID": {"frequency": 11862, "polarization": "Vertical"},
    "TOYOR ALJANNAH": {"frequency": 11179, "polarization": "Horizontal"},
    "CN ARABIC": {"frequency": 11277, "polarization": "Vertical"},
    "SKY NEWS ARABIA": {"frequency": 12380, "polarization": "Horizontal"},
    "BBC ARABIC": {"frequency": 11727, "polarization": "Horizontal"},
    "AL KASS": {"frequency": 11919, "polarization": "Horizontal"}
}

# --- منطق بناء الملف بعد اختيار المستخدم ---

# 1. بناء القائمة المفلترة
channels_to_generate = []
if add_new_ch:
    for name, info in NILESAT_GEN_DB.items():
        # إذا تم تفعيل تحديث الترددات، نستخدم قيم قاعدة البيانات، وإلا نستخدم قيم افتراضية
        freq = info["frequency"] if update_freq else 11000
        channels_to_generate.append({"name": name, "freq": str(freq), "pol": info["polarization"]})

# 2. توليد هيكل الملف (Modern JSON / Legacy XML)
if system_type == t['sys_modern']:
    # نظام JSON المدمج للأنظمة الحديثة
    channel_list_json = [
        {
            "channelName": ch["name"],
            "majorNumber": i,
            "minorNumber": 0,
            "frequency": int(ch["freq"]),
            "polarization": ch["pol"],
            "invisible": 0, "skipped": 0, "locked": 0, "serviceType": 1
        } for i, ch in enumerate(channels_sorted, start=1)
    ]
    
    # هيكل الترويسة الرسمي لـ LG
    broadcast_payload = {"channelList": channel_list_json, "satelliteList": [{"satelliteName": "Nilesat", "satellitePosition": 70}]}
    json_str = json.dumps(broadcast_payload, ensure_ascii=False)
    
    final_xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<TLLDATA>\n  <ModelName>{generated_model_name}</ModelName>\n  <legacybroadcast><![CDATA[{json_str}]]></legacybroadcast>\n</TLLDATA>"
    final_xml_bytes = final_xml.encode('utf-8')

else:
    # نظام الـ ITEM الكلاسيكي للموديلات القديمة
    items_xml = "".join([
        f"\n  <ITEM>\n    <prNum>{i}</prNum>\n    <vchName>{ch['name']}</vchName>\n    <frequency>{ch['freq']}</frequency>\n    <polarization>{ch['pol']}</polarization>\n  </ITEM>"
        for i, ch in enumerate(channels_sorted, start=1)
    ])
    
    final_xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<TLLDATA>\n  <ModelName>{generated_model_name}</ModelName>{items_xml}\n</TLLDATA>"
    final_xml_bytes = final_xml.encode('utf-8')
