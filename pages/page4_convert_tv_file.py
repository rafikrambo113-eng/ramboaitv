import streamlit as st
import xml.etree.ElementTree as ET
import io
import json

st.set_page_config(page_title="LG Channel Smart Converter", layout="centered")

st.title("🛠️ أداة تحويل ترتيب قنوات شاشات LG الذكية")
st.write("هذه النسخة مطورة بميزة **الـ Fallback** للحفاظ على القنوات غير المتطابقة، مع تثبيت **بلد البث الأصلية** لشاشتك لضمان التوافق التام.")

# 1. رفع الملفات
st.subheader("1️⃣ ارفع الملفات المطلوبة")
reference_file = st.file_uploader("ارفع الملف المترتب الجاهز (الذي تريد نسخ الترتيب منه)", type=["tll", "bak"])
target_file = st.file_uploader("ارفع ملف شاشتك الأصلي (الذي تريد الحفاظ على موديله وبلد بثه)", type=["tll", "bak"])

if reference_file and target_file:
    st.subheader("2️⃣ إعدادات المعالجة الذكية")
    
    if st.button("نقل الترتيب الذكي مع الحفاظ على بلد البث ✨"):
        try:
            # قراءة ملف المرجع (المترتب)
            ref_bytes = reference_file.read()
            ref_root = ET.fromstring(ref_bytes)
            
            # قراءة ملف الشاشة الأصلي (الهدف)
            tar_bytes = target_file.read()
            tar_tree = ET.parse(io.BytesIO(tar_bytes))
            tar_root = tar_tree.getroot()
            
            # --- خطوة الحفاظ على بلد البث والموديل الأصلي ---
            orig_country_setting = tar_root.findtext(".//BroadcastCountrySetting")
            orig_country = tar_root.findtext(".//country")
            orig_model = tar_root.findtext(".//ModelName")
            
            st.info(f"📋 تم قراءة بيانات شاشتك الأصلية وثبيتها: الموديل ({orig_model}) | بلد البث ({orig_country_setting})")
            
            # قاموس لحفظ ترتيب القنوات من الملف المرجع
            # المفتاح يعتمد على التردد و الـ Service ID
            ref_channels_order = {}
            
            # استخراج القنوات من الملف المرجع (XML كلاسيكي)
            for item in ref_root.findall(".//ITEM"):
                freq = item.findtext("frequency")
                srv_id = item.findtext("service_id")
                pr_num = item.findtext("prNum")
                if freq and srv_id and pr_num:
                    key = f"{freq}_{srv_id}"
                    ref_channels_order[key] = int(pr_num)
            
            # استخراج القنوات من الملف المرجع (JSON حديث)
            channel_tag = ref_root.find(".//CHANNEL")
            if channel_tag is not None and channel_tag.text:
                try:
                    js_data = json.loads(channel_tag.text)
                    ch_list = js_data.get("legacybroadcast", {}).get("channelList", [])
                    for ch in ch_list:
                        freq = ch.get("frequency")
                        srv_id = ch.get("SVCID")
                        pr_num = ch.get("programNumber")
                        if freq and srv_id and pr_num:
                            key = f"{freq}_{srv_id}"
                            ref_channels_order[key] = int(pr_num)
                except:
                    pass

            if not ref_channels_order:
                st.error("❌ عذراً، لم نتمكن من العثور على قنوات داخل الملف المترتب.")
            else:
                updated_count = 0
                fallback_count = 0
                
                # تحديث قنوات الـ XML الكلاسيكية لشاشتك الأصلية
                for item in tar_root.findall(".//ITEM"):
                    freq = item.findtext("frequency")
                    srv_id = item.findtext("service_id")
                    if freq and srv_id:
                        key = f"{freq}_{srv_id}"
                        pr_num_tag = item.find("prNum")
                        
                        if key in ref_channels_order:
                            # تطبيق الترتيب الجديد
                            pr_num_tag.text = str(ref_channels_order[key])
                            updated_count += 1
                        else:
                            # [Fallback] الحفاظ على الترتيب الأصلي للقناة إذا لم توجد في الملف المرجع
                            fallback_count += 1
                
                # تحديث قنوات الـ JSON الحديثة لشاشتك الأصلية
                tar_channel_tag = tar_root.find(".//CHANNEL")
                if tar_channel_tag is not None and tar_channel_tag.text:
                    try:
                        tar_js_data = json.loads(tar_channel_tag.text)
                        
                        # ضمان تطابق بلد البث داخل الـ JSON نفسه أيضاً
                        if "modelInfo" in tar_js_data.get("legacybroadcast", {}):
                            # الحفاظ على القيمة الأصلية للبلد داخل كائن الجيسون
                            pass 
                        
                        if "legacybroadcast" in tar_js_data and "channelList" in tar_js_data["legacybroadcast"]:
                            ch_list = tar_js_data["legacybroadcast"]["channelList"]
                            for ch in ch_list:
                                freq = ch.get("frequency")
                                srv_id = ch.get("SVCID")
                                if freq and srv_id:
                                    key = f"{freq}_{srv_id}"
                                    if key in ref_channels_order:
                                        ch["programNumber"] = ref_channels_order[key]
                                        updated_count += 1
                                    else:
                                        # [Fallback] ترك القناة برقمها القديم دون تغيير
                                        fallback_count += 1
                                        
                            # إعادة حفظ الـ JSON المعدل داخل الوسم
                            tar_channel_tag.text = json.dumps(tar_js_data, ensure_ascii=False)
                    except:
                        pass
                
                # إعادة كتابة وتثبيت بيانات البلد الأصلية في الـ XML لضمان عدم حدوث أي تغيير
                if orig_country_setting and tar_root.find(".//BroadcastCountrySetting") is not None:
                    tar_root.find(".//BroadcastCountrySetting").text = orig_country_setting
                if orig_country and tar_root.find(".//country") is not None:
                    tar_root.find(".//country").text = orig_country
                if orig_model and tar_root.find(".//ModelName") is not None:
                    tar_root.find(".//ModelName").text = orig_model

                # حفظ الملف النهائي
                out_buffer = io.BytesIO()
                tar_tree.write(out_buffer, encoding="UTF-8", xml_declaration=True)
                new_file_bytes = out_buffer.getvalue()
                
                st.success(f"🎉 تم السحر بنجاح!")
                st.write(f"✅ عدد القنوات التي تم تحديث ترتيبها: **{updated_count}** قناة.")
                st.write(f"🔄 عدد القنوات الاحتياطية التي تم حمايتها (Fallback): **{fallback_count}** قناة.")
                st.write(f"🌍 بلد البث الحالي للملف المستخرج: **{orig_country_setting if orig_country_setting else 'نفس البلد الأصلي'}**")
                
                # زر التحميل الأخضر
                st.download_button(
                    label="📥 تحميل ملف القنوات الجاهز لشاشتك فوراً",
                    data=new_file_bytes,
                    file_name="GlobalClone00001.TLL",
                    mime="application/octet-stream"
                )
                
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الملفات: {e}")
