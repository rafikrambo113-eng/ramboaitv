import streamlit as st
import xml.etree.ElementTree as ET
import io
import json

# إعداد الصفحة
st.set_page_config(page_title="LG Ultimate Channel Converter", layout="centered")

st.title("🛠️ محول ومطابق قنوات شاشات LG الذكي الشامل")
st.write("هذه الأداة الذكية تنقل ترتيب القنوات من ملف مرجعي، وتطبقه على ملف شاشتك الأصلي مع الحفاظ الكامل على الموديل وبلد البث.")

# زر إعادة التعيين (Restart)
if st.button("🔄 إعادة تعيين ورفع ملفات جديدة"):
    st.cache_data.clear()
    st.rerun()

# دالة ذكية لقراءة تفاصيل أي ملف LG (القديم والحديث)
def get_file_details(file_bytes):
    try:
        root = ET.fromstring(file_bytes)
        model = root.findtext(".//ModelInfo/ModelName") or "غير معروف"
        country_setting = root.findtext(".//ModelInfo/BroadcastCountrySetting")
        country_tag = root.findtext(".//ModelInfo/country")
        
        # تحديد البلد
        country = country_setting or country_tag or "غير محدد"
        
        # حساب القنوات
        channel_count = 0
        # 1. لو كلاسيكي XML
        channel_count += len(root.findall(".//ITEM"))
        
        # 2. لو حديث JSON
        for channel_tag in root.findall(".//CHANNEL"):
            if channel_tag.text:
                try:
                    js_data = json.loads(channel_tag.text)
                    ch_list = js_data.get("legacybroadcast", {}).get("channelList", [])
                    channel_count += len(ch_list)
                except:
                    pass
        return {"model": model, "country": country, "channels": channel_count, "root": root}
    except Exception as e:
        return None

# مساحة رفع الملفات
st.subheader("1️⃣ ارفع الملفات المطلوبة")
col1, col2 = st.columns(2)

with col1:
    reference_file = st.file_uploader("ارفع الملف المترتب الجاهز (المرجع)", type=["tll", "bak"], key="ref")
with col2:
    target_file = st.file_uploader("ارفع ملف شاشتك الأصلي (الهدف)", type=["tll", "bak"], key="tar")

# عرض معلومات الملفات المرفوعة تلقائياً
ref_details = None
tar_details = None

if reference_file:
    ref_bytes = reference_file.read()
    ref_details = get_file_details(ref_bytes)
    if ref_details:
        st.markdown(f"""
        <div style="background-color:#e1f5fe; padding:10px; border-radius:5px; border-left:5px solid #0288d1;">
        <strong>📋 تفاصيل الملف المترتب (المرجع):</strong><br>
        • الموديل: {ref_details['model']}<br>
        • بلد البث: {ref_details['country']}<br>
        • إجمالي القنوات: {ref_details['channels']} قناة
        </div>
        """, unsafe_allow_html=True)

if target_file:
    tar_bytes = target_file.read()
    tar_details = get_file_details(tar_bytes)
    if tar_details:
        st.markdown(f"""
        <div style="background-color:#e8f5e9; padding:10px; border-radius:5px; border-left:5px solid #388e3c;">
        <strong>🎯 تفاصيل ملف شاشتك الأصلي (الهدف):</strong><br>
        • الموديل: {tar_details['model']}<br>
        • بلد البث: {tar_details['country']}<br>
        • إجمالي القنوات: {tar_details['channels']} قناة
        </div>
        """, unsafe_allow_html=True)

# معالجة نقل الترتيب
if reference_file and target_file and ref_details and tar_details:
    st.subheader("2️⃣ معالجة نقل الترتيب الذكي")
    
    if st.button("بدء نقل الترتيب وتوليد الملف المتوافق ✨"):
        try:
            ref_root = ref_details['root']
            
            # قراءة شجرة ملف الشاشة الأصلي للتعديل عليها مباشرة
            tar_tree = ET.parse(io.BytesIO(tar_bytes))
            tar_root = tar_tree.getroot()
            
            # بناء قاموس للترتيب المرجعي (التردد + معرف الخدمة)
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
                        fallback_count += 1  # الحفاظ عليها في مكانها الافتراضي (Fallback)

            # 2. تحديث القنوات لو ملف الشاشة الأصلي حديث (JSON داخل CHANNEL)
            for tar_channel_tag in tar_root.findall(".//CHANNEL"):
                if tar_channel_tag.text:
                    try:
                        tar_js_data = json.loads(tar_channel_tag.text)
                        if "legacybroadcast" in tar_js_data and "channelList" in tar_js_data["legacybroadcast"]:
                            ch_list = tar_js_data["legacybroadcast"]["channelList"]
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
                                        fallback_count += 1  # Fallback الذكي للأجهزة الحديثة
                                        
                        tar_channel_tag.text = json.dumps(tar_js_data, ensure_ascii=False)
                    except:
                        pass
            
            # حفظ الملف في الذاكرة لتنزيله
            out_buffer = io.BytesIO()
            tar_tree.write(out_buffer, encoding="UTF-8", xml_declaration=True)
            new_file_bytes = out_buffer.getvalue()
            
            st.success("🎯 تم السحر بنجاح وتطابق الترتيب!")
            st.write(f"✅ قنوات تم تحديث ترتيبها بنجاح: **{updated_count}**")
            st.write(f"🔄 قنوات متبقية آمنة في مكانها الأصلي (Fallback): **{fallback_count}**")
            
            # زر التحميل
            st.download_button(
                label="📥 تحميل ملف القنوات الجاهز لشاشتك فوراً",
                data=new_file_bytes,
                file_name="GlobalClone00001.TLL",
                mime="application/octet-stream"
            )
            
            # شرح تفصيلي للملف الناتج للإجابة على سؤالك
            st.subheader("📋 ما هو الملف الآخر الذي خرج الآن؟")
            st.markdown(f"""
            الملف الناتج هو عبارة عن هجين ذكي يحمل المواصفات التالية:
            1. **هوية وتوافق 100%:** الملف يحمل نفس الموديل وحجم البوصة الخاص بشاشتك الأصلي وهو **({tar_details['model']})**.
            2. **بلد البث الأصلي:** تم تثبيت إعدادات بلد البث لتكون تابعة لـ **({tar_details['country']})** كما هي في شاشتك الأصلية تماماً لتجنب أي رسائل خطأ.
            3. **ترتيب القنوات الجديد:** أخذ القنوات المشتركة ورتبها بنفس تنظيم ملف المرجع الممتاز.
            4. **نظام حماية القنوات (Fallback):** القنوات الزائدة أو غير المتطابقة لم تُحذف، بل بقيت في مكانها لكي لا تفقد أي محطة بث.
            """)
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء المعالجة: {e}")
