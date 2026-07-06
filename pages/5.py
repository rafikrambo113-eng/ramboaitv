import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="مستخرج ومضمن الروابط الذكي", page_icon="⚽", layout="wide")

st.title("⚽ أداة سحب وتضمين روابط البث والمشغلات")
st.write("هذه الأداة تحاكي مواقع الرياضة عبر فحص المواقع وجلب روابط التشغيل (Embed/Iframe) وعرضها مباشرة.")

# قائمة بالمواقع المستهدفة (يمكنك تعديلها بمواقع تبث المباريات أو الأفلام)
TARGET_SITES = {
    "موقع بث تجريبي 1": "https://example-sports-site.com",
    "مدونة بث مفتوحة": "https://free-live-stream-blog.blogspot.com"
}

# خانة إدخال الرابط المباشر للمباراة أو الصفحة المراد فحصها
page_url = st.text_input("أدخل رابط صفحة المباراة/القناة المراد سحب المشغل منها:")

if st.button("🔍 سحب وتضمين الرابط الآن"):
    if not page_url:
        st.warning("من فضلك أدخل رابطاً أولاً.")
    else:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        with st.spinner("جاري فحص الصفحة وسحب الروابط والمشغلات..."):
            try:
                response = requests.get(page_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    found_embeds = []
                    
                    # 1. البحث عن وسوم الـ iframe (وهي الطريقة الأشهر لتضمين المشغلات في مواقع الكورة)
                    iframes = soup.find_all('iframe')
                    for iframe in iframes:
                        src = iframe.get('src')
                        if src and src.startswith('http'):
                            found_embeds.append(("Iframe Player", src))
                    
                    # 2. البحث عن روابط البث المباشر (m3u8) المخفية في أكواد السكربت
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string:
                            # البحث عن روابط m3u8 داخل ملفات الجافا سكربت
                            m3u8_links = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', script.string)
                            for link in m3u8_links:
                                found_embeds.append(("M3U8 Stream", link))
                    
                    # عرض النتائج وتضمينها
                    if found_embeds:
                        st.success(f"🎉 تم العثور على {len(found_embeds)} مشغلات وروابط بث!")
                        
                        # إزالة التكرار
                        found_embeds = list(set(found_embeds))
                        
                        for index, (source_type, link) in enumerate(found_embeds):
                            st.subheader(f"📺 مشغل رقم {index+1} ({source_type})")
                            st.code(link, language="text")
                            
                            if source_type == "Iframe Player":
                                # تضمين الـ iframe داخل الـ Streamlit كـ HTML
                                st.components.v1.iframe(link, height=450, scrolling=True)
                            elif source_type == "M3U8 Stream":
                                # تشغيل رابط الـ m3u8 المباشر
                                st.video(link)
                    else:
                        st.warning("لم يتم العثور على روابط تضمين (Iframe) أو روابط m3u8 مباشرة في هذه الصفحة. قد تكون المحتويات محمية أو تعتمد على جافا سكربت معقد.")
                else:
                    st.error(f"فشل الاتصال بالموقع. كود الاستجابة: {response.status_code}")
            except Exception as e:
                st.error(f"حدث خطأ أثناء السحب: {e}")
