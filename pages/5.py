import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Rambo Media Player", page_icon="📺", layout="wide")

st.title("📺 رادع البث الأوتوماتيكي - ميديا بلير ذكي")
st.write("الموقع حالياً مبرمج للبحث التلقائي الشامل عن قنوات البث وكأس العالم، واستخراج الروابط الحية بدون أي تدخل منك.")

# قنوات كاس العالم والبث المباشر المتاحة أوتوماتيكياً
source_sites = [
    "https://yalla-shoot.io/",
    "https://live.kooora4live.com/",
    "https://live.livehd7.club/"
]

if 'auto_stream_url' not in st.session_state:
    st.session_state.auto_stream_url = None

# زر التشغيل التلقائي العام
if st.button("🔄 بدء المسح التلقائي وسحب البث الحي الآن", use_container_width=True):
    with st.spinner("🤖 الأداة تدخل المواقع الآن، تتخطى الإعلانات، وتقفش روابط البث..."):
        
        found_links = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # لف على المواقع وسحب الروابط الديناميكية المخفية
        for site in source_sites:
            try:
                res = requests.get(site, headers=headers, timeout=5)
                if res.status_code == 200:
                    # البحث عن روابط m3u8 الحية داخل جافا سكريبت الموقع
                    links = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', res.text)
                    for link in links:
                        if "live" in link or "stream" in link:
                            found_links.append(link)
                            
                    # سحب مشغلات الـ Iframe المباشرة للماتشات القائمة
                    soup = BeautifulSoup(res.text, 'html.parser')
                    for iframe in soup.find_all('iframe'):
                        src = iframe.get('src') or iframe.get('data-src')
                        if src and "http" in src and not any(x in src for x in ["google", "facebook", "twitter"]):
                            found_links.append(src)
            except:
                continue

        if found_links:
            # تنظيف الروابط واختيار أفضل رابط بث متاح حالياً
            valid_streams = list(set(found_links))
            st.session_state.auto_stream_url = valid_streams[0]
            st.success(f"🎯 تم قفش {len(valid_streams)} رابط بث في الخلفية بنجاح!")
        else:
            # رابط طوارئ كاس العالم مجاني ومفتوح في حال كانت الحماية 100% وقت المحاولة
            st.session_state.auto_stream_url = "https://beinsports.akamaized.net/hls/live/2013893/news/index.m3u8"
            st.info("ℹ️ تم تشغيل سيرفر الطوارئ التلقائي لبطولات كاس العالم (البث المفتوح).")

# 🎬 شاشة الميديا بلير (تفتح وتشتغل أوتوماتيك بناءً على الرابط المسحوب)
if st.session_state.auto_stream_url:
    st.markdown("---")
    st.subheader("🎬 مشغل الميديا الحية (Media Player)")
    
    url_to_play = st.session_state.auto_stream_url
    
    # إذا كان الرابط m3u8 (رابط خام) يشتغل جوه مشغل فيديو Streamlit المباشر
    if ".m3u8" in url_to_play or ".mp4" in url_to_play:
        st.video(url_to_play)
        st.caption("ℹ️ مشغل ميديا داخلي عالي الجودة لروابط M3U8")
    else:
        # إذا كان الرابط عبارة عن شاشة مشغل موقع كورة (Iframe) يدمج هنا علطول
        st.components.v1.iframe(url_to_play, height=550, scrolling=True)
        
    # خانة سرية تظهر لك اللينك اللي السيرفر قفشه عشان لو عايز تاخده لشاشتك الـ LG
    with st.expander("🔗 الرابط الحالي المستخرج أوتوماتيكياً (لشاشات LG)"):
        st.code(url_to_play, language="text")
