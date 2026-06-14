import streamlit as st
import xml.etree.ElementTree as ET
import io
import json

# إعداد الصفحة
st.set_page_config(page_title="LG Ultimate Channel Converter", layout="centered")

st.title("🛠️ محول ومطابق قنوات شاشات LG الذكي الشامل")
st.write("تنقل هذه الأداة الترتيب من ملف مرجعي وتطبقه على ملف شاشتك الأصلي مع الحفاظ على التوافق التام.")

# زر إعادة التعيين (Restart)
if st.button("🔄 إعادة تعيين ورفع ملفات جديدة"):
    st.cache_data.clear()
    st.rerun()

# دالة ذكية ومعدلة لقراءة تفاصيل أي ملف LG بدقة
def get_file_details(file_bytes):
    try:
        root = ET.fromstring(file_bytes)
        model = root.findtext(".//ModelInfo/ModelName") or "غير معروف"
        country_setting = root.findtext(".//ModelInfo/BroadcastCountrySetting")
        country_tag = root.findtext(".//ModelInfo/country")
        
        # تحديد البلد
        country = country_setting or country_tag or "غير محدد"
        
        channel_count = 0
        file_type = "قديم (XML كلاسيكي)"
        
        # 1. حساب القنوات لو كلاسيكي XML
        xml_items = root.findall(".//ITEM")
        if xml_items:
            channel_count = len(xml_items)
            file_type = "قديم (XML كلاسيكي)"
        
        # 2. حساب القنوات لو حديث JSON (تحديث مخصص لضمان الوصول للمصفوفة)
        for channel_tag in root.findall(".//CHANNEL"):
            if channel_tag.text:
                try:
                    js_data = json.loads(channel_tag.text)
                    # فحص كافة المسارات المحتملة للـ channelList في الملفات الحديثة
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

# عرض معلومات الملفات المرفوعة بلوحة بيانات غامقة وواضحة جداً
if reference_file:
    ref_bytes = reference_file.read()
    ref_details = get_file_details(ref_bytes)
    if ref_details:
        st.markdown(f"""
        <div style="background-color:#111b21; padding:15px; border-radius:8px; border-left:6px solid #00a884; color:#e9edef; margin-bottom:15px;">
        <strong style="color:#00a884; font-size:16px;">📋 تفاصيل الملف المترتب (المرجع):</strong><br><br>
        • <b>نوع الملف:</b> <span style="color:#34b7f1;">{ref_details['type']}</span><br>
        • <b>الموديل:</b> {ref_details['model']}<br>
        • <b>بلد البث:</b> {ref_details['country']}<br>
        • <b>إجمالي القنوات:</b> <span style="color:#00a884; font-size:16px; font-weight:bold;">{ref_details['channels']}</span> قناة
        </div>
        """, unsafe_allow_html=True)

if target_file:
    tar_bytes = target_file.read()
    tar_details = get_file_details(tar_bytes)
    if tar_details:
        st.markdown(f"""
        <div style="background-color:#1a1a24; padding:15px; border-radius:8px; border-left:6px solid #ff4b4b; color:#ffffff; margin-bottom:15px;">
        <strong style="color:#ff4b4b; font-size:16px;">🎯 تفاصيل ملف شاشتك الأصلي (الهدف):</strong><br><br>
        • <b>نوع الملف:</b> <span style="color:#34b7f1;">{tar_details['type']}</span><br>
        • <b>الموديل:</b> {tar_details['model']}<br>
        • <b>بلد البث:</b> {tar_details['country']}<br>
        • <b>إجمالي القنوات:</b> <span style="color:#ff4b4b; font-size:16px; font-weight:bold;">{tar_details['channels']}</span> قناة
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
                            js_data = json.loads(channel_tag.text)
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
                            tar_js_data = json.loads(tar_channel_tag.text)
                            
                            ch_list = []
                            is_legacy_path = False
                            if "legacybroadcast" in tar_js_data and "channelList" in tar_js_data["legacybroadcast"]:
                                ch_list = tar_js_data["legacybroadcast"]["channelList"]
                                is_legacy_path = True
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
                                            
                            tar_channel_tag.text = json.dumps(tar_js_data, ensure_ascii=False)
                        except:
                            pass
                
                # حفظ واستخراج الملف
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
                
                # شرح مواصفات الملف الخارج للمستخدم
                st.subheader("📋 ما هو الملف الناتج المُنزل الآن؟")
                st.markdown(f"""
                <div style="background-color:#1e1e1e; padding:15px; border-radius:8px; color:#ffffff; border:1px solid #333;">
                1. <b>الهوية والتوافق:</b> يحمل بصمة وموديل شاشتك الأصلي تماماً وهو <b>({tar_details['model']})</b> ونوع الملف <b>({tar_details['type']})</b>.<br>
                2. <b>بلد البث الثابت:</b> يلتزم 100% بإعدادات بلد بث شاشتك وهو <b>({tar_details['country']})</b> لتقبله الشاشة فوراً.<br>
                3. <b>الترتيب المطور:</b> تم تطبيق خريطة قنوات الملف المرجع الممتاز عليه، وحماية القنوات غير المشتركة عبر نظام (Fallback).
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")
