import streamlit as st
import xml.etree.ElementTree as ET
import io
import json
import re

# إعداد الصفحة وتثبيت المظهر
st.set_page_config(page_title="LG Ultimate Channel Converter", layout="centered")

st.title("🛠️ محول ومطابق قنوات شاشات LG الذكي الشامل")
st.write("تنقل هذه الأداة الترتيب من ملف مرجعي وتطبقه على ملف شاشتك الأصلي مع الحفاظ على التوافق التام.")

# زر إعادة التعيين (Restart)
if st.button("🔄 إعادة تعيين ورفع ملفات جديدة"):
    st.cache_data.clear()
    st.rerun()

# دالة قراءة تفاصيل وقنوات أي ملف LG بدقة
def get_file_details(file_bytes):
    try:
        text_content = file_bytes.decode('utf-8', errors='ignore')
        model = "غير معروف"
        country = "غير حدد"
        
        model_match = re.search(r'<ModelName[^>]*>([^<]+)</ModelName>', text_content)
        if model_match:
            model = model_match.group(1).strip()
            
        country_match = re.search(r'<BroadcastCountrySetting[^>]*>([^<]+)</BroadcastCountrySetting>', text_content)
        if country_match:
            country = country_match.group(1).strip()
        else:
            country_match2 = re.search(r'<country[^>]*>([^<]+)</country>', text_content)
            if country_match2:
                country = country_match2.group(1).strip()

        channel_count = 0
        file_type = "قديم (XML كلاسيكي)"
        
        xml_items = re.findall(r'<ITEM>', text_content)
        if xml_items:
            channel_count = len(xml_items)
            file_type = "قديم (XML كلاسيكي)"
        
        channel_tags = re.findall(r'<CHANNEL[^>]*>(.*?)</CHANNEL>', text_content, re.DOTALL)
        if channel_tags:
            for tag_content in channel_tags:
                clean_txt = tag_content.strip()
                if clean_txt:
                    ch_matches = re.findall(r'"SVCID"\s*:', clean_txt)
                    if ch_matches:
                        channel_count = len(ch_matches)
                        file_type = "حديث (JSON مدمج)"
                    else:
                        try:
                            json_start = clean_txt.find('{')
                            json_end = clean_txt.rfind('}')
                            if json_start != -1 and json_end != -1:
                                js_data = json.loads(clean_txt[json_start:json_end+1])
                                ch_list = js_data.get("legacybroadcast", {}).get("channelList", []) or js_data.get("channelList", [])
                                if ch_list:
                                    channel_count = len(ch_list)
                                    file_type = "حديث (JSON مدمج)"
                        except:
                            pass
                            
        if channel_count == 0 and "channelList" in text_content:
            file_type = "حديث (JSON مدمج)"
            channel_count = max(1, text_content.count('"frequency"') - 5)

        root = ET.fromstring(file_bytes)
        return {"model": model, "country": country, "channels": channel_count, "type": file_type, "root": root}
    except Exception as e:
        return None

# مساحة رفع الملفات
st.subheader("1️⃣ ارفع الملفات المطلوبة")
col1, col2 = st.columns(2)

with col1:
    reference_file = st.file_uploader("ارفع الملف المترتب الجاهز (المرجع)", type=["tll", "bak"], key="ref")
with col2:
    target_file = st.file_uploader("ارفع ملف شاشتك الأصلي (الهدف)", type=["tll", "bak"], key="tar")

if reference_file:
    ref_bytes = reference_file.read()
    ref_details = get_file_details(ref_bytes)
    if ref_details:
        st.markdown(f"""
        <div style="background-color:#0d1418; padding:18px; border-radius:10px; border:2px solid #00a884; color:#e9edef; margin-bottom:15px;">
        <strong style="color:#00a884; font-size:18px; display:block; margin-bottom:10px;">📋 تفاصيل الملف المترتب (المرجع):</strong>
        • <b>نوع نظام الملف:</b> <span style="color:#ffb300; font-weight:bold;">{ref_details['type']}</span><br>
        • <b>موديل الشاشة:</b> {ref_details['model']}<br>
        • <b>بلد البث الفعلي:</b> {ref_details['country']}<br>
        • <b>إجمالي عدد القنوات:</b> <span style="color:#00a884; font-size:20px; font-weight:bold;">{ref_details['channels']}</span> قناة
        </div>
        """, unsafe_allow_html=True)

if target_file:
    tar_bytes = target_file.read()
    tar_details = get_file_details(tar_bytes)
    if tar_details:
        st.markdown(f"""
        <div style="background-color:#16161a; padding:18px; border-radius:10px; border:2px solid #ff4b4b; color:#ffffff; margin-bottom:15px;">
        <strong style="color:#ff4b4b; font-size:18px; display:block; margin-bottom:10px;">🎯 تفاصيل ملف شاشتك الأصلي (الهدف):</strong>
        • <b>نوع نظام الملف:</b> <span style="color:#ffb300; font-weight:bold;">{tar_details['type']}</span><br>
        • <b>موديل الشاشة:</b> {tar_details['model']}<br>
        • <b>بلد البث الفعلي:</b> {tar_details['country']}<br>
        • <b>إجمالي عدد القنوات:</b> <span style="color:#ff4b4b; font-size:20px; font-weight:bold;">{tar_details['channels']}</span> قناة
        </div>
        """, unsafe_allow_html=True)

# معالجة نقل الترتيب الذكي
if reference_file and target_file and 'ref_details' in locals() and 'tar_details' in locals():
    if ref_details and tar_details:
        st.subheader("2️⃣ معالجة نقل الترتيب الذكي")
        
        if st.button("بدء نقل الترتيب وتوليد الملف المتوافق ✨"):
            try:
                ref_root = ref_details['root']
                tar_tree = ET.parse(io.BytesIO(tar_bytes))
                tar_root = tar_tree.getroot()
                
                # قاموس يعتمد على الـ Service ID كـ مِفتاح ربط مطلق غير قابل للفشل
                svcid_to_prNum = {}
                
                # 1. جمع البيانات من المرجع الكلاسيكي (إن وجد كمرجع)
                for item in ref_root.findall(".//ITEM"):
                    srv_id = item.findtext("service_id")
                    pr_num = item.findtext("prNum")
                    if srv_id and pr_num:
                        svcid_to_prNum[int(srv_id)] = int(pr_num)
                
                # 2. جمع البيانات من المرجع الحديث (مثل ملفك الـ 55 بوصة الحالي)
                for channel_tag in ref_root.findall(".//CHANNEL"):
                    if channel_tag.text:
                        try:
                            clean_txt = channel_tag.text.strip()
                            json_start = clean_txt.find('{')
                            json_end = clean_txt.rfind('}')
                            if json_start != -1 and json_end != -1:
                                js_data = json.loads(clean_txt[json_start:json_end+1])
                                ch_list = js_data.get("legacybroadcast", {}).get("channelList", []) or js_data.get("channelList", [])
                                for ch in ch_list:
                                    srv_id = ch.get("SVCID")
                                    pr_num = ch.get("programNumber")
                                    if srv_id is not None and pr_num is not None:
                                        svcid_to_prNum[int(srv_id)] = int(pr_num)
                        except:
                            pass

                updated_count = 0
                fallback_count = 0
                
                # 3. تحديث ملف شاشتك الـ 32 الكلاسيكي المستهدف (Target) بناء على الـ Service ID
                for item in tar_root.findall(".//ITEM"):
                    srv_id_tag = item.findtext("service_id")
                    pr_num_tag = item.find("prNum")
                    
                    if srv_id_tag is not None and pr_num_tag is not None:
                        s_id = int(srv_id_tag)
                        
                        # المطابقة الفتاكة بالـ Service ID المباشر
                        if s_id in svcid_to_prNum:
                            pr_num_tag.text = str(svcid_to_prNum[s_id])
                            
                            # تفعيل خيار قناة مخصصة من قبل المستخدم لتثبيتها بالشاشة
                            is_user_sel = item.find("isUserSelCHNo")
                            if is_user_sel is not None:
                                is_user_sel.text = "1"
                            updated_count += 1
                        else:
                            fallback_count += 1

                # 4. احتياطياً لو كان المستهدف نظام حديث
                for tar_channel_tag in tar_root.findall(".//CHANNEL"):
                    if tar_channel_tag.text:
                        try:
                            clean_txt = tar_channel_tag.text.strip()
                            json_start = clean_txt.find('{')
                            json_end = clean_txt.rfind('}')
                            if json_start != -1 and json_end != -1:
                                prefix = clean_txt[:json_start]
                                suffix = clean_txt[json_end+1:]
                                tar_js_data = json.loads(clean_txt[json_start:json_end+1])
                                
                                ch_list = tar_js_data.get("legacybroadcast", {}).get("channelList", []) or tar_js_data.get("channelList", [])
                                if ch_list:
                                    for ch in ch_list:
                                        srv_id = ch.get("SVCID")
                                        if srv_id is not None:
                                            s_id = int(srv_id)
                                            if s_id in svcid_to_prNum:
                                                ch["programNumber"] = int(svcid_to_prNum[s_id])
                                                ch["isUserSelCHNo"] = True
                                                if "mapAttr" in ch:
                                                    ch["mapAttr"] = 0
                                                updated_count += 1
                                            else:
                                                fallback_count += 1
                                tar_channel_tag.text = prefix + json.dumps(tar_js_data, ensure_ascii=False) + suffix
                        except:
                            pass
                
                # تصدير الملف النهائي الجاهز
                out_buffer = io.BytesIO()
                tar_tree.write(out_buffer, encoding="UTF-8", xml_declaration=True)
                new_file_bytes = out_buffer.getvalue()
                
                st.success("🎯 تم بنجاح فك العقدة ومطابقة القنوات بالمعرف الرقمي المطلق!")
                st.write(f"✅ قنوات تم نقل ترتيبها الجديد لشاشتك: **{updated_count}** قناة")
                st.write(f"🔄 قنوات متبقية في مكانها الآمن (Fallback): **{fallback_count}** قناة")
                
                st.download_button(
                    label="📥 تحميل ملف القنوات المترتب الجاهز لشاشتك الـ 32 فوراً",
                    data=new_file_bytes,
                    file_name="GlobalClone00001.TLL",
                    mime="application/octet-stream"
                )
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة التقنية: {e}")
