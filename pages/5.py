import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="مستخرج القنوات التلقائي", page_icon="📺", layout="wide")

st.title("📺 مستخرج روابط البث التلقائي بضغطة واحدة")
st.write("اختر القناة أو اكتب اسمها، وسيقوم البرنامج بالبحث تلقائياً عن سيرفرات البث الحية وسحبها.")

# قائمة قنوات سريعة جاهزة للاختيار
channels = ["بي ان سبورت 1", "بي ان سبورت 2", "قناة الكأس", "قناة اون تايم سبورت", "اكتب اسم قناة أخرى..."]
selected_channel = st.selectbox("اختر القناة المراد سحب البث لها:", channels)

# لو اختار يكتب اسم قناة بنفسه
if selected_channel == "اكتب اسم قناة أخرى...":
    search_query = st.text_input("اكتب اسم القناة بالتفصيل (مثال: بي ان سبورت بريميوم 1):")
else:
    search_query = selected_channel

if st.button("🚀 اسحب البث تلقائياً الآن"):
    if not search_query:
        st.warning("من فضلك اختر أو اكتب اسم القناة أولاً.")
    else:
        with st.spinner(f"🔄 جاري اختراق حمايات المواقع وسحب بث ({search_query}) تلقائياً..."):
            try:
                # خطوة 1: البحث في محركات البحث المفتوحة عن صفحات البث الحية للقناة
                search_url = f"https://html.duckduckgo.com/html/?q=بث+مباشر+{search_query}+يلا+شوت"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                
                search_response = requests.get(search_url, headers=headers, timeout=10)
                soup = BeautifulSoup(search_response.text, 'html.parser')
                
                # استخراج أول 3 روابط لمواقع بث حقيقية ظهرت في البحث
                links = []
                for a in soup.find_all('a', class_='result__url', href=True):
                    href = a['href']
                    if "yalla" in href or "kora" in href or "live" in href:
                        links.append(href)
                
                if not links:
                    # روابط احتياطية عامة لو البحث مطلعش نتيجة سريعة
                    links = ["https://yalla-shoot.io/", "https://live.kooora4live.com/"]

                # خطوة 2: الدخول على المواقع دي وسحب الروابط المخفية (Iframe أو M3U8)
                found_streams = []
                
                for target_url in links[:3]: # فحص أول 3 مواقع لسرعة الأداء
                    try:
                        page_res = requests.get(target_url, headers=headers, timeout=5)
                        page_soup = BeautifulSoup(page_res.text, 'html.parser')
                        
                        # سحب أي إيفريم (مشغل مدمج)
                        for iframe in page_soup.find_all('iframe'):
                            src = iframe.get('src') or iframe.get('data-src')
                            if src and "http" in src and not "facebook" in src and not "twitter" in src:
                                found_streams.append(("سيرفر مشغل مدمج", src))
                        
                        # سحب روابط m3u8 المباشرة من الأكواد
                        scripts = page_soup.find_all('script')
                        for script in scripts:
                            if script.string:
                                m3u8_links = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', script.string)
                                for m3u8 in m3u8_links:
                                    found_streams.append(("رابط بث مباشر M3U8", m3u8))
                    except:
                        continue # لو موقع معلق يدخل على اللي بعده

                # خطوة 3: عرض النتيجة وتشغيلها أوتوماتيك
                if found_streams:
                    # إزالة التكرار
                    found_streams = list(set(found_streams))
                    st.success(f"🎉 نجح السحب التلقائي! تم العثور على {len(found_streams)} سيرفرات شغالة.")
                    
                    # تشغيل أول سيرفر تم سحبه تلقائياً كعينة
                    best_stream = found_streams[0][1]
                    st.subheader("📺 مشغل البث التلقائي:")
                    
                    if ".m3u8" in best_stream:
                        st.video(best_stream)
                    else:
                        st.components.v1.iframe(best_stream, height=500, scrolling=True)
                        
                    # عرض باقي السيرفرات لو حابب تبدل بينهم
                    with st.expander("🔗 عرض باقي الروابط المستخرجة يدويًا:"):
                        for title, url in found_streams:
                            st.write(f"**{title}:**")
                            st.code(url, language="text")
                else:
                    st.warning("⚠️ المواقع قافلة السحب التلقائي حالياً بسبب الحماية الزائدة، جرب قناة أخرى أو أعد المحاولة وقت المباراة.")
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء السحب التلقائي: {e}")
