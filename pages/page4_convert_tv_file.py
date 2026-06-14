import streamlit as st
import xml.etree.ElementTree as ET
import io
import json
import re

# إعداد الصفحة وتثبيت المظهر
st.set_page_config(page_title="LG Ultimate Channel Converter", layout="centered")

st.title("🛠️ محول ومطابق قنوات شاشات LG الذكي الشامل")
st.write("تنقل هذه الأداة الترتيب من ملف مرجعي وتطبقه على ملف شاشتك الأصلي مع الحفاظ على التوافق التام.")

# زر إعادة التعيين (Restart) لإعادة تحميل الصفحة من أول وجديد
if st.button("🔄 إعادة تعيين ورفع ملفات جديدة"):
    st.cache_data.clear()
    st.rerun()

# دالة ذكية لتنظيف أسماء القنوات لضمان أعلى نسبة تطابق
def clean_channel_name(name_str):
    if not name_str:
        return ""
    # فك التشفير الصيني/الغريب الناتج عن الـ UTF-16 في الشاشات القديمة إذا وجد
    try:
        # محاولة تنظيف النصوص والرموز والمساحات الزائدة وتحويلها لحروف صغيرة
        name = name_str.strip().lower()
        # إزالة المسافات وعلامات مثل HD أو SD لتسهيل المطابقة (مثال: MBC HD تصبح mbc)
        name = re.sub(r'\s+|hd|sd|\-|_|\.', '', name)
        return name
    except:
        return name_str.strip().lower()

# دالة قراءة تفاصيل الملف
def get_file_details(file_bytes):
    try:
        text_content = file_bytes.decode('utf-8', errors='ignore')
        model = "غير معروف"
        country = "غير محدد"
        
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

# معالجة نقل الترتيب
if reference_file and target_file and 'ref_details' in locals() and 'tar_details' in locals():
    if ref_details and tar_details:
        st.subheader("2️⃣ معالجة نقل الترتيب الذكي")
        
        if st.button("بدء نقل الترتيب وتوليد الملف المتوافق ✨"):
            try:
                ref_root = ref_details['root']
                tar_tree = ET.parse(io.BytesIO(tar_bytes))
                tar_root = tar_tree.getroot()
                
                # قاموس يعتمد على اسم القناة كـ مفتاح ربط أساسي فريد
                name_to_prNum = {}
                
                # 1. سحب الترتيب من المرجع (XML كلاسيكي) لو كان قديم
                for item in ref_root.findall(".//ITEM"):
                    vchName = item.findtext("vchName")
                    pr_num = item.findtext("prNum")
                    if vchName and pr_num:
                        clean_name = clean_channel_name(vchName)
                        if clean_name:
                            name_to_prNum[clean_name] = int(pr_num)
                
                # 2. سحب الترتيب من المرجع (JSON حديث) - زي ملفك الـ 55 الحالي
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
                                    chName = ch.get("chName")
                                    pr_num = ch.get("programNumber")
                                    if chName and pr_num:
                                        clean_name = clean_channel_name(chName)
                                        if clean_name:
                                            name_to_prNum[clean_name] = int(pr_num)
                        except:
                            pass

                updated_count = 0
                fallback_count = 0
                
                # 3. تحديث ملف شاشتك الأصلي (الهدف) - الـ 32 بوصة الكلاسيكي
                for item in tar_root.findall(".//ITEM"):
                    vchName = item.findtext("vchName")
                    pr_num_tag = item.find("prNum")
                    
                    if vchName and pr_num_tag is not None:
                        clean_name = clean_channel_name(vchName)
                        
                        # مطابقة مباشرة بالاسم النظيف
                        if clean_name in name_to_prNum:
                            pr_num_tag.text = str(name_to_prNum[clean_name])
                            item.find("isUserSelCHNo").text = "1" if item.find("isUserSelCHNo") is not None else "1"
                            updated_count += 1
                        else:
                            fallback_count += 1

                # 4. احتياطياً لو كان الملف المستهدف حديث
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
                                        chName = ch.get("chName")
                                        if chName:
                                            clean_name = clean_channel_name(chName)
                                            if clean_name in name_to_prNum:
                                                ch["programNumber"] = int(name_to_prNum[clean_name])
                                                ch["isUserSelCHNo"] = True
                                                if "mapAttr" in ch:
                                                    ch["mapAttr"] = 0
                                                updated_count += 1
                                            else:
                                                fallback_count += 1
                                tar_channel_tag.text = prefix + json.dumps(tar_js_data, ensure_ascii=False) + suffix
                        except:
                            pass
                
                # توليد الملف النهائي في الذاكرة
                out_buffer = io.BytesIO()
                tar_tree.write(out_buffer, encoding="UTF-8", xml_declaration=True)
                new_file_bytes = out_buffer.getvalue()
                
                st.success("🎯 تم سحق مشكلة التوافق ونقل الترتيب بالأسماء الذكية!")
                st.write(f"✅ قنوات تم مطابقتها ونقل ترتيبها الجديد: **{updated_count}** قناة")
                st.write(f"🔄 قنوات حافظت على مكانها القديم (Fallback): **{fallback_count}** قناة")
                
                st.download_button(
                    label="📥 تحميل ملف القنوات الجاهز فوراً لشاشتك الـ 32",
                    data=new_file_bytes,
                    file_name="GlobalClone00001.TLL",
                    mime="application/octet-stream"
                )
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")
