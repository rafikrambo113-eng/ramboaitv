import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

st.set_page_config(page_title="مستخرج المشغلات الذكي", page_icon="⚽", layout="wide")

st.title("⚽ مستخرج ومضمن مشغلات البث المباشر")
st.write("أدخل رابط صفحة مباراة أو قناة من موقع بث حقيقي لسحب المشغل وتضمينه.")

page_url = st.text_input("أدخل رابط صفحة البث المباشر الحقيقية:")

if st.button("🔍 سحب وتضمين المشغل"):
    if not page_url:
        st.warning("من فضلك أدخل رابطاً أولاً.")
    else:
        # استخدام User-Agent يحاكي متصفح حقيقي لتخطي الحمايات البسيطة
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': page_url
        }
        
        with st.spinner("جاري فحص الصفحة بعمق وسحب المشغلات..."):
            try:
                response = requests.get(page_url, headers=headers, timeout=12)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    found_links = []

                    # 1. فحص وسوم الـ iframe بالكامل
                    iframes = soup.find_all('iframe')
                    for iframe in iframes:
                        src = iframe.get('src') or iframe.get('data-src') # بعض المواقع تؤجل تحميل السورس
                        if src:
                            full_url = urljoin(page_url, src)
                            found_links.append(("Iframe Player (مشغل مدمج)", full_url))

                    # 2. فحص الأزرار والروابط التي قد تفتح المشغل
                    a_tags = soup.find_all('a', href=True)
                    for a in a_tags:
                        href = a['href']
                        if 'player' in href or 'embed' in href or '.m3u8' in href:
                            full_url = urljoin(page_url, href)
                            found_links.append(("رابط مشغل خارجي", full_url))

                    # 3. فحص النصوص داخل السكربتات عن روابط البث (m3u8 أو المشغلات المخفية)
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string:
                            # البحث عن روابط m3u8
                            streams = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', script.string)
                            for stream in streams:
                                found_links.append(("رابط بث مباشر M3U8", stream))
                            
                            # البحث عن روابط تابعة لمشغلات شهيرة مثل ok.ru أو yalla-shoot إلخ
                            embeds = re.findall(r'(https?://[^\s"\']+(?:embed|player|static)[^\s"\']*)', script.string)
                            for embed in embeds:
                                found_links.append(("مشغل مخفي في السكربت", embed))

                    # عرض وتضمين المشغلات المستخرجة
                    if found_links:
                        # إزالة التكرار
                        found_links = list(set(found_links))
                        st.success(f"🎉 تم العثور على {len(found_links)} مصدر محتمل للبث!")
                        
                        for index, (source_type, link) in enumerate(found_links):
                            st.subheader(f"📺 المصدر رقم {index+1} - {source_type}")
                            st.code(link, language="text")
                            
                            # إذا كان مشغل أو إيفريم نقوم بتضمينه فوراً جوه الموقع
                            if "Iframe" in source_type or "مشغل" in source_type:
                                st.components.v1.iframe(link, height=480, scrolling=True)
                            elif "M3U8" in source_type:
                                st.video(link)
                    else:
                        st.warning("⚠️ لم يتم العثور على أي مشغلات أو روابط بث في هذه الصفحة. تأكد أن الصفحة تحتوي على بث مباشر نشط حالياً.")
                else:
                    st.error(f"❌ الموقع رفض الاتصال أو محمي بشكل قوي. كود الاستجابة: {response.status_code}")
            except Exception as e:
                st.error(f"حدث خطأ أثناء محاولة السحب: {e}")
