import streamlit as st
import requests

st.set_page_config(page_title="Rambo Live TV", page_icon="⚽", layout="wide")

# عنوان الموقع بشكل بسيط
st.title("📺 موقع رامبو للبث المباشر الحّي")
st.write("اختر القناة من القائمة على اليمين، والمشغل هيشتغل تلقائياً على الشمال بدون إعلانات.")

# مصادر سيرفرات القنوات
IPTV_SOURCES = {
    "قنوات الرياضة": "https://raw.githubusercontent.com/mohamedelshamy/egypt-iptv/main/sports.m3u",
    "سيرفر احتياطي": "https://iptv-org.github.io/iptv/categories/sports.m3u"
}

def fetch_live_channels(url):
    channels = []
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            lines = response.text.split('\n')
            current_name = None
            for line in lines:
                line = line.strip()
                if line.startswith('#EXTINF:'):
                    name_part = line.split(',')[-1]
                    current_name = name_part if name_part else "قناة رياضية"
                elif line.startswith('http'):
                    if current_name:
                        channels.append({"name": current_name, "url": line})
                        current_name = None
    except:
        pass
    return channels

if 'all_channels' not in st.session_state or st.button("🔄 تحديث القنوات"):
    with st.spinner("جاري جلب القنوات الحية..."):
        all_found = []
        for src_name, src_url in IPTV_SOURCES.items():
            all_found.extend(fetch_live_channels(src_url))
        
        if not all_found:
            all_found = [
                {"name": "🔥 بي ان سبورت الإخبارية - بث مباشر", "url": "https://beinsports.akamaized.net/hls/live/2013893/news/index.m3u8"},
                {"name": "⚽ قناة الكأس الرياضية HD1", "url": "https://alkass.akamaized.net/hls/live/2016553/alkassone/index.m3u8"},
                {"name": "🏆 الرياضية المغربية المباشرة", "url": "https://snrtlive-hls.secure.footprint.net/hls/live/arryadia/index.m3u8"}
            ]
        st.session_state.all_channels = all_found

# تقسيم الصفحة
col_list, col_player = st.columns([1, 2])

with col_list:
    st.write("### 📥 اختر القناة:")
    channel_names = [ch["name"] for ch in st.session_state.all_channels]
    selected_name = st.selectbox("اختر القناة من هنا:", channel_names)
    
    selected_url = next(ch["url"] for ch in st.session_state.all_channels if ch["name"] == selected_name)

with col_player:
    st.write(f"### 🎬 مشغل الفيديو: {selected_name}")
    if selected_url:
        st.video(selected_url)
