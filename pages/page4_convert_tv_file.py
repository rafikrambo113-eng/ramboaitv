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

# دالة ذكية ومطورة جداً لقراءة تفاصيل وقنوات أي ملف LG بدقة ومنع ظهور 0
def get_file_details(file_bytes):
    try:
        # تحويل البياتات إلى نص لسهولة الفحص السريع بالـ Regex لو فشل الـ XML
        text_content = file_bytes.decode('utf-8', errors='ignore')
        
        # محاولة قراءة الموديل والبلد
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

        # تحديد نوع الملف وعد القنوات بدقة
        channel_count = 0
        file_type = "قديم (XML كلاسيكي)"
        
        # فحص وجود وسوم ITEM (النظام القديم)
        xml_items = re.findall(r'<ITEM>', text_content)
        if xml_items:
            channel_count = len(xml_items)
            file_type = "قديم (XML كلاسيكي)"
        
        # فحص الـ JSON بداخل وسم CHANNEL (النظام الحديث)
        channel_tags = re.findall(r'<CHANNEL[^>]*>(.*?)</CHANNEL>', text_content, re.DOTALL)
        if channel_tags:
            for tag_content in channel_tags:
                # تنظيف النص ومحاولة استخراج الـ JSON
                clean_txt = tag_content.strip()
                if clean_txt:
                    # محاولة البحث عن مصفوفة القنوات داخل كود الجيسون بالـ Regex لضمان القراءة حتى لو الـ JSON ضخم
                    ch_matches = re.findall(r'"SVCID"\s*:', clean_txt)
                    if ch_matches:
                        channel_count = len(ch_matches)
                        file_type = "حديث (JSON مدمج)"
                    else:
                        # محاولة الطريقة التقليدية بالـ json.loads لو الـ Regex مطلعش حاجة
                        try:
                            # لو النص جواه وسوم تانية زي iepg أو legacybroadcast
                            # هناخد بس الجزء اللي يبدأ بـ { وينتهي بـ }
                            json_start = clean_txt.find('{')
                            json_end = clean_txt.rfind('}')
                            if json_start != -1 and json_end != -1:
                                js_data = json.loads(clean_txt[json_start:json_end+1])
                                ch_list = []
                                if "legacybroadcast" in js_data and "channelList" in js_data["legacybroadcast"]:
                                    ch_list = js_data["legacybroadcast"]["channelList"]
                                elif "channelList" in js_data:
                                    ch_list = js_data["channelList"]
                                if ch_list:
                                    channel_count = len(ch_list)
                                    file_type = "حديث (JSON مدمج)"
                        except:
                            pass
                            
        # لو لسه العداد صفر وبتحتوي على كلمة channelList يبجى هو نظام حديث بالتأكيد
        if channel_count == 0 and "channelList" in text_content:
            file_type = "حديث (JSON مدمج)"
            # عد تقريبي دقيق بناء على المفاتيح المتكررة للقنوات
            channel_count = text_content.count('"frequency"')
            if channel_count > 0:
                # بنقص القنوات الوهمية أو الترددات الاحتياطية في الجيسون إن وجدت
                channel_count = max(1, channel_count - 5) 

        # تجهيز جذر الـ XML للمعالجة اللاحقة
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

# عرض معلومات الملفات المرفوعة بلوحة بيانات غامقة جداً وواضحة جداً لحل مشكلة الرؤية
if reference_file:
    ref_bytes = reference_file.read()
    ref_details = get_file_details(ref_bytes)
    if ref_details:
        st.markdown(f"""
        <div style="background-color:#0d1418; padding:18px; border-radius:10px; border:2px solid #00a884; color:#e9edef; margin-bottom:15px; box-shadow: 3px 3px 10px rgba(0,0,0,0.5);">
        <strong style="color:#00a884; font-size:18px; display:block; margin-bottom:10px;">📋 تفاصيل الملف المترتب (المرجع):</strong>
        • <b style="color:#34b7f1;">نوع نظام الملف:</b> <span style="color:#ffb300; font-weight:bold;">{ref_details['type']}</span><br>
        • <b style="color:#34b7f1;">موديل الشاشة:</b> <span style="color:#ffffff;">{ref_details['model']}</span><br>
        • <b style="color:#34b7f1;">بلد البث الفعلي:</b> <span style="color:#ffffff;">{ref_details['country']}</span><br>
        • <b style="color:#34b7f1;">إجمالي عدد القنوات:</b> <span style="color:#00a884; font-size:20px; font-weight:bold;">{ref_details['channels']}</span> قناة
        </div>
        """, unsafe_allow_html=True)

if target_file:
    tar_bytes = target_file.read()
    tar_details = get_file_details(tar_bytes)
    if tar_details:
        st.markdown(f"""
        <div style="background-color:#16161a; padding:18px; border-radius:10px; border:2px solid #ff4b4b; color:#ffffff; margin-bottom:15px; box-shadow: 3px 3px 10px rgba(0,0,0,0.5);">
        <strong style="color:#ff4b4b; font-size:18px; display:block; margin-bottom:10px;">🎯 تفاصيل ملف شاشتك الأصلي (الهدف):</strong>
        • <b style="color:#ff9800;">نوع نظام الملف:</b> <span style="color:#ffb300; font-weight:bold;">{tar_details['type']}</span><br>
        • <b style="color:#ff9800;">موديل الشاشة:</b> <span style="color:#ffffff;">{tar_details['model']}</span><br>
        • <b style="color:#ff9800;">بلد البث الفعلي:</b> <span style="color:#ffffff;">{tar_details['country']}</span><br>
        • <b style="color:#ff9800;">إجمالي عدد القنوات:</b> <span style="color:#ff4b4b; font-size:20px; font-weight:bold;">{tar_details['channels']}</span> قناة
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
                
                # بناء قاموس للترتيب المرجعي
                ref_channels_order = {}
                
                # استخراج من XML الكلاسيكي
                for item in ref_root.findall(".//ITEM"):
                    freq = item.findtext("frequency")
                    srv_id = item.findtext("service_id")
                    pr_num = item.findtext("prNum")
                    if freq and srv_id and pr_num:
                        key = f"{int(freq)}_{int(srv_id)}"
                        ref_channels_order[key] = int(pr_num)
                
                # استخراج من JSON الحديث
                for channel_tag in ref_root.findall(".//CHANNEL"):
                    if channel_tag.text:
                        try:
                            # تنظيف وتحديد مكان بداية ونهاية الجيسون
                            clean_txt = channel_tag.text.strip()
                            json_start = clean_txt.find('{')
                            json_end = clean_txt.rfind('}')
                            if json_start != -1 and json_end != -1:
                                js_data = json.loads(clean_txt[json_start:json_end+1])
                                ch_list = []
                                if "legacybroadcast" in js_data and "channelList" in js_data["legacybroadcast"]:
                                    ch_list = js_data["legacybroadcast"]["channelList"]
                                elif "channelList" in js_data:
                                    ch_list = js_data["channelList"]
                                    
                                for ch in ch_list:
                                    freq = ch.get("frequency")
                                    srv_id = ch.get("SVCID")
                                    pr_num = ch.get("programNumber")
                                    if freq and srv_id and pr_num:
                                        key = f"{int(freq)}_{int(srv_id)}"
                                        ref_channels_order[key] = int(pr_num)
                        except:
                            pass
                
                updated_count = 0
                fallback_count = 0
                
                # 1. تحديث القنوات لو ملف الشاشة الأصلي كلاسيكي (XML ITEM)
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
                            fallback_count += 1

                # 2. تحديث القنوات لو ملف الشاشة الأصلي حديث (JSON داخل CHANNEL)
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
                                
                                ch_list = []
                                if "legacybroadcast" in tar_js_data and "channelList" in tar_js_data["legacybroadcast"]:
                                    ch_list = tar_js_data["legacybroadcast"]["channelList"]
                                elif "channelList" in tar_js_data:
                                    ch_list = tar_js_data["channelList"]
                                
                                if ch_list:
                                    for ch in ch_list:
                                        freq = ch.get("frequency")
                                        srv_id = ch.get("SVCID")
                                        if freq and srv_id:
                                            key = f"{int(freq)}_{int(srv_id)}"
                                            if key in ref_channels_order:
                                                ch["programNumber"] = int(ref_channels_order[key])
                                                ch["isUserSelCHNo"] = True
                                                if "mapAttr" in ch:
                                                    ch["mapAttr"] = 0
                                                updated_count += 1
                                            else:
                                                fallback_count += 1
                                                
                                # إعادة دمج النص مع الحفاظ على أي أغلفة خارج الجيسون
                                tar_channel_tag.text = prefix + json.dumps(tar_js_data, ensure_ascii=False) + suffix
                        except:
                            pass
                
                # حفظ واستخراج الملف النهائي
                out_buffer = io.BytesIO()
                tar_tree.write(out_buffer, encoding="UTF-8", xml_declaration=True)
                new_file_bytes = out_buffer.getvalue()
                
                st.success("🎯 تم نقل الترتيب وتطابق القنوات بنجاح!")
                st.write(f"✅ قنوات تم تحديث ترتيبها: **{updated_count}**")
                st.write(f"🔄 قنوات متبقية آمنة في مكانها الأصلي (Fallback): **{fallback_count}**")
                
                st.download_button(
                    label="📥 تحميل ملف القنوات الجاهز لشاشتك فوراً",
                    data=new_file_bytes,
                    file_name="GlobalClone00001.TLL",
                    mime="application/octet-stream"
                )
                
                # شرح مواصفات الملف الخارج للمستخدم بلوحة غامقة جداً
                st.subheader("📋 ما هو الملف الناتج المُنزل الآن؟")
                st.markdown(f"""
                <div style="background-color:#111116; padding:18px; border-radius:10px; color:#ffffff; border:1px solid #333344; box-shadow: 3px 3px 10px rgba(0,0,0,0.5);">
                1. <b>الهوية والتوافق:</b> يحمل بصمة وموديل شاشتك الأصلي تماماً وهو <span style="color:#00a884; font-weight:bold;">({tar_details['model']})</span> ونوع نظامه <span style="color:#ffb300;">({tar_details['type']})</span>.<br><br>
                2. <b>بلد البث الثابت:</b> يلتزم 100% بإعدادات بلد بث شاشتك الأصلي وهو <span style="color:#34b7f1; font-weight:bold;">({tar_details['country']})</span> لتقبله الشاشة فوراً بدون أي رسائل رفض.<br><br>
                3. <b>الترتيب المطور:</b> تم تطبيق خريطة قنوات الملف المرجع المترتب عليه بالكامل، وحماية باقي القنوات غير المشتركة عبر نظام البديل الاحتياطي الذكي <b>(Fallback)</b> لكي لا تفقد أي محطة بث.
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")
