import streamlit as st
import xml.etree.ElementTree as ET
import io
import json

st.set_page_config(page_title="LG Ultimate Channel Converter", layout="centered")

st.title("🛠️ محول قنوات LG الشامل (يدعم UQ, UR, UA والملفات الحديثة)")
st.write("تم تحديث الكود ليدعم الأجيال الحديثة بدقة، مع الحفاظ على **بلد البث (السعودية/الخليج)** وتفعيل **الـ Fallback** لحماية القنوات.")

# 1. رفع الملفات
st.subheader("1️⃣ ارفع الملفات المطلوبة")
reference_file = st.file_uploader("ارفع الملف المترتب الجاهز (الذي تريد نسخ الترتيب منه)", type=["tll", "bak"])
target_file = st.file_uploader("ارفع ملف شاشتك الأصلي (السعودي المستهدف)", type=["tll", "bak"])

if reference_file and target_file:
    st.subheader("2️⃣ معالجة الترتيب الذكي")
    
    if st.button("بدء نقل الترتيب ودعم الشاشات الحديثة ✨"):
        try:
            # 1. قراءة وتحليل ملف المرجع (المترتب)
            ref_bytes = reference_file.read()
            ref_root = ET.fromstring(ref_bytes)
            
            # 2. قراءة وتحليل ملف الشاشة الأصلي (الهدف)
            tar_bytes = target_file.read()
            tar_tree = ET.parse(io.BytesIO(tar_bytes))
            tar_root = tar_tree.getroot()
            
            # الحفاظ على إعدادات الموديل والبلد من الملف الأصلي (XML)
            orig_country_setting = tar_root.findtext(".//BroadcastCountrySetting")
            orig_country = tar_root.findtext(".//country")
            orig_model = tar_root.findtext(".//ModelName")
            
            st.info(f"🌍 تم قراءة وتثبيت هوية شاشتك الأصلية: {orig_model} | بلد البث: {orig_country_setting if orig_country_setting else 'السعودية/الخليج'}")
            
            # قاموس الترتيب المرجعي
            ref_channels_order = {}
            
            # [المرجع] استخراج القنوات من الـ XML الكلاسيكي
            for item in ref_root.findall(".//ITEM"):
                freq = item.findtext("frequency")
                srv_id = item.findtext("service_id")
                pr_num = item.findtext("prNum")
                if freq and srv_id and pr_num:
                    key = f"{int(freq)}_{int(srv_id)}"
                    ref_channels_order[key] = int(pr_num)
            
            # [المرجع] استخراج القنوات من الـ JSON لشاشات (UQ/UR/UA)
            for channel_tag in ref_root.findall(".//CHANNEL"):
                if channel_tag.text:
                    try:
                        js_data = json.loads(channel_tag.text)
                        # فحص مصفوفة القنوات في الأجهزة الحديثة
                        ch_list = js_data.get("legacybroadcast", {}).get("channelList", [])
                        for ch in ch_list:
                            freq = ch.get("frequency")
                            srv_id = ch.get("SVCID")
                            pr_num = ch.get("programNumber")
                            if freq and srv_id and pr_num:
                                key = f"{int(freq)}_{int(srv_id)}"
                                ref_channels_order[key] = int(pr_num)
                    except:
                        pass

            if not ref_channels_order:
                st.error("❌ لم نتمكن من استخراج قنوات من الملف المترتب المرجعي.")
            else:
                updated_count = 0
                fallback_count = 0
                
                # [الهدف] 1. تحديث الملف إذا كان شاشة كلاسيكية (XML ITEM)
                for item in tar_root.findall(".//ITEM"):
                    freq = item.findtext("frequency")
                    srv_id = item.findtext("service_id")
                    if freq and srv_id:
                        key = f"{int(freq)}_{int(srv_id)}"
                        pr_num_tag = item.find("prNum")
                        if key in ref_channels_order:
                            pr_num_tag.text = str(ref_channels_order[key])
                            updated_count += 1
                        else:
                            fallback_count += 1 # تفعيل الـ Fallback (تركها كما هي)

                # [الهدف] 2. تحديث الملف إذا كان شاشة حديثة (UQ, UR, UA) تحتوي على JSON
                for tar_channel_tag in tar_root.findall(".//CHANNEL"):
                    if tar_channel_tag.text:
                        try:
                            tar_js_data = json.loads(tar_channel_tag.text)
                            
                            # معالجة مصفوفة القنوات الحديثة داخل الـ JSON
                            if "legacybroadcast" in tar_js_data and "channelList" in tar_js_data["legacybroadcast"]:
                                ch_list = tar_js_data["legacybroadcast"]["channelList"]
                                for ch in ch_list:
                                    freq = ch.get("frequency")
                                    srv_id = ch.get("SVCID")
                                    if freq and srv_id:
                                        key = f"{int(freq)}_{int(srv_id)}"
                                        if key in ref_channels_order:
                                            # نقل الترتيب الجديد داخل كائن الـ JSON
                                            ch["programNumber"] = int(ref_channels_order[key])
                                            # إعطاء صلاحية للمستخدم لتحريك القناة وتثبيتها
                                            ch["isUserSelCHNo"] = True 
                                            if "mapAttr" in ch:
                                                ch["mapAttr"] = 0 # تصفير القيود الإقليمية التلقائية لقنوات السعودية
                                            updated_count += 1
                                        else:
                                            fallback_count += 1 # Fallback الذكي
                                
                            # إعادة حفظ الـ JSON المعدل داخل الوسم الخاص بالشاشة
                            tar_channel_tag.text = json.dumps(tar_js_data, ensure_ascii=False)
                        except Exception as json_err:
                            st.error(f"خطأ في معالجة كود الجيسون الداخلي: {json_err}")
                
                # إعادة تثبيت قيم بلد البث الأصلية في الـ XML الخارجي للتأكد 100%
                if orig_country_setting and tar_root.find(".//BroadcastCountrySetting") is not None:
                    tar_root.find(".//BroadcastCountrySetting").text = orig_country_setting
                if orig_country and tar_root.find(".//country") is not None:
                    tar_root.find(".//country").text = orig_country
                if orig_model and tar_root.find(".//ModelName") is not None:
                    tar_root.find(".//ModelName").text = orig_model

                # حفظ الملف النهائي في الذاكرة
                out_buffer = io.BytesIO()
                tar_tree.write(out_buffer, encoding="UTF-8", xml_declaration=True)
                new_file_bytes = out_buffer.getvalue()
                
                st.success("🎯 تم حل مشكلة الشاشات الحديثة ونقل الترتيب بنجاح!")
                st.write(f"✅ عدد القنوات المحدثة بنظام الترتيب الجديد: **{updated_count}**")
                st.write(f"🔄 قنوات متبقية آمنة في مكانها الأصلي (Fallback): **{fallback_count}**")
                
                # زر التحميل
                st.download_button(
                    label="📥 تحميل ملف القنوات الجاهز لشاشتك الحديثة",
                    data=new_file_bytes,
                    file_name="GlobalClone00001.TLL",
                    mime="application/octet-stream"
                )
                
        except Exception as e:
            st.error(f"حدث خطأ عام أثناء المعالجة: {e}")
