import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="مستخرج القنوات الاحترافي", page_icon="📺", layout="wide")

st.title("📺 مستخرج روابط البث التلقائي (نسخة تخطي الحماية)")
st.write("اختر القناة، وسيقوم البرنامج بمحاكاة متصفح حقيقي لجلب سيرفرات البث الحية المتاحة الآن.")

# قائمة القنوات
channels = ["بي ان سبورت 1", "بي ان سبورت 2", "قناة الكأس", "قناة اون تايم سبورت", "اكتب اسم قناة أخرى..."]
selected_channel = st.selectbox("اختر القناة:", channels)

if selected_channel == "اكتب اسم قناة أخرى...":
    search_query = st.text_input("اكتب اسم القناة بالتفصيل:")
else:
    search_query = selected_channel

if st.button("🚀 سحب البث تلقائياً"):
    if not search_query:
        st.warning("من فضلك حدد القناة أولاً.")
    else:
        with st.spinner(f"🔄 جاري فحص شبكات البث وتخطي الحمايات لـ ({search_query})..."):
            try:
                # استخدام محرك بحث بديل يعطي نتائج مباشرة بدون حماية كابتشا
                search_url = f"https://html.duckduckgo.com/html/?q=بث+مباشر+{search_query}+live"
                
                # إرسال طلب بحزمة بيانات (Headers) متكاملة تحاكي متصفح كروم حديث تماماً
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
                    'Connection': 'keep-alive'
                }
                
                search_response = requests.get(search_url, headers=headers, timeout=10)
                soup = BeautifulSoup(search_response.text, 'html.parser')
                
                links = []
                for a in soup.find_all('a', class_='result__url', href=True):
                    href = a['href']
                    # تصفية الروابط للوصول لمواقع البث الرياضية فقط
                    if any(keyword in href for keyword in ["yalla", "kora", "live", "match", "shoot", "tv"]):
                        links.append(href)
                
                # إذا لم يجد نتائج في البحث، يتوجه مباشرة لأشهر خوادم البث المفتوحة حالياً كخطة بديلة
                if not links:
                    links = [
                        "https://yalla-shoot.io/",
                        "https://live.kooora4live.com/",
                        "https://live.livehd7.club/"
                    ]

                found_streams = []
                
                # فحص المواقع المستخرجة بعمق أكبر
                for target_url in links[:3]:
                    try:
                        page_res = requests.get(target_url, headers=headers, timeout=5)
                        page_soup = BeautifulSoup(page_res.text, 'html.parser')
                        
                        # 1. سحب وسوم التضمين (Iframes)
                        for iframe in page_soup.find_all('iframe'):
                            src = iframe.get('src') or iframe.get('data-src') or iframe.get('content')
                            if src and "http" in src and not any(x in src for x in ["facebook", "twitter", "instagram", "google"]):
                                found_streams.append(("سيرفر مشغل تلقائي", src))
                        
                        # 2. البحث عن روابط البث الخام (m3u8) المستضافة في أكواد الجافا سكربت
                        scripts = page_soup.find_all('script')
                        for script in scripts:
                            if script.string:
                                m3u8_links = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', script.string)
                                for m3u8 in m3u8_links:
                                    found_streams.append(("رابط بث مباشر M3U8", m3u8))
                    except:
                        continue

                if found_streams:
                    found_streams = list(set(found_streams)) # إزالة الروابط المكررة
                    st.success(f"🎉 تم اختراق الحماية بنجاح والعثور على {len(found_streams)} سيرفر!")
                    
                    # تشغيل أول سيرفر تم العثور عليه تلقائياً
                    best_stream = found_streams[0][1]
                    st.subheader("🎬 شاشة العرض التلقائية:")
                    
                    if ".m3u8" in best_stream:
                        st.video(best_stream)
                    else:
                        st.components.v1.iframe(best_stream, height=550, scrolling=True)
                        
                    # عرض باقي السيرفرات المتاحة للاختيار بينها
                    with st.expander("🔗 عرض الروابط المستخرجة الأخرى يدويًا:"):
                        for title, url in found_streams:
                            st.write(f"**{title}:**")
                            st.code(url, language="text")
                else:
                    # حل أوتوماتيكي أخير: توجيه المستخدم لصفحة البث المباشر المفتوحة للمباراة مباشرة
                    st.warning("⚠️ حماية الموقع قوية جداً في هذه اللحظة لمنع تشغيل الفيديو مدمجاً.")
                    st.write("اضغط على الزر بالأسفل لفتح صفحة البث المباشر التلقائية للقناة مباشرة لتجنب الحماية:")
                    direct_view_url = links[0] if links else "https://yalla-shoot.io/"
                    st.link_button(f"🌐 فتح بث {search_query} في صفحة مستقلة فوراً", direct_view_url, use_container_width=True)
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال التلقائي: {e}")
