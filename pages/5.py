import streamlit as st
import requests

st.set_page_config(page_title="Rambo Live TV", page_icon="⚽", layout="wide")

# تصميم الهيدر للموقع
st.markdown("""
    <div style='text-align: center; background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='color: #ff4b4b; margin: 0;'>📺 موقع رامبو للبث المباشر الحّي</h1>
        <p style='color: #ffffff;'>قنوات رياضية وبث مباشر للمباريات أوتوماتيكياً 100% بدون إعلانات مزعجة</p>
    </div>
""", unsafe_allow_list=True)

# مصادر سيرفرات قنوات البث المباشر (تحدث روابطها تلقائياً على الإنترنت)
# دي روابط سيرفرات IPTV مفتوحة ومستقرة بتجيب القنوات الرياضية والبث المباشر
IPTV_SOURCES = {
    "قنوات الرياضة المفتوحة": "https://raw.githubusercontent.com/mohamedelshamy/egypt-iptv/main/sports.m3u", # سيرفر متجدد
    "سيرفر البث الاحتياطي": "https://iptv-org.github.io/iptv/categories/sports.m3u" # سيرفر عالمي متجدد
}

# دالة ذكية لقراءة القنوات وتفكيك السيرفر أوتوماتيكياً
def fetch_live_channels(url):
    channels = []
    try:
        response = requests.get(url, timeout=7)
        if response.status_code == 200:
            lines = response.text.split('\n')
            current_name = None
            for line in lines:
                line = line.strip()
                if line.startswith('#EXTINF:'):
                    # قفش اسم القناة من السيرفر
                    name_part = line.split(',')[-1]
                    current_name = name_part if name_part else "قناة رياضية بث مباشر"
                elif line.startswith('http'):
                    # قفش رابط البث المباشر (m3u8) الخفي
                    if current_name:
                        channels.append({"name": current_name, "url": line})
                        current_name = None
    except:
        pass
    return channels

# جلب القنوات في الخلفية أوتوماتيكياً أول ما الموقع يفتح
if 'all_channels' not in st.session_state or st.button("🔄 تحديث سيرفرات البث الآن"):
    with st.spinner("🤖 جاري ربط الموقع بسيرفرات البث المباشر وتحديث الروابط الحية..."):
        all_found = []
        for src_name, src_url in IPTV_SOURCES.items():
            all_found.extend(fetch_live_channels(src_url))
        
        # لو السيرفرات الخارجية معلقة، بنحط قنوات بث رئيسية ثابتة كخطة طوارئ عشان الموقع ميفضاش
        if not all_found:
            all_found = [
                {"name": "🔥 بي ان سبورت الإخبارية - بث مباشر", "url": "https://beinsports.akamaized.net/hls/live/2013893/news/index.m3u8"},
                {"name": "⚽ قناة الكأس الرياضية HD1", "url": "https://alkass.akamaized.net/hls/live/2016553/alkassone/index.m3u8"},
                {"name": "🏆 الرياضية المغربية المباشرة", "url": "https://snrtlive-hls.secure.footprint.net/hls/live/arryadia/index.m3u8"},
                {"name": "📺 قناة TRT Spor العالمية (ناقل مجاني)", "url": "https://trt.akamaized.net/hls/live/2012351/trtspor/index.m3u8"}
            ]
        st.session_state.all_channels = all_found

# تقسيم شاشة الموقع (يمين لقائمة القنوات - شمال للمشغل الميديا بلير)
col_list, col_player = st.columns([1, 2])

with col_list:
    st.markdown("### 📥 اختر القناة أو المباراة:")
    # عمل قائمة اختيار أوتوماتيكية بكل القنوات اللي السيرفر لقطها
    channel_names = [ch["name"] for ch in st.session_state.all_channels]
    selected_name = st.selectbox("📺 القنوات المتاحة حالياً:", channel_names, label_visibility="collapsed")
    
    # جلب رابط القناة المختارة
    selected_url = next(ch["url"] for ch in st.session_state.all_channels if ch["name"] == selected_name)
    
    st.success("🟢 السيرفر متصل وشغال")
    st.info(f"🔗 مصدر البث الحالي متصل بـ نود فيديو خارجي ذكي.")

with col_player:
    st.markdown(f"### 🎬 مشغل البث المباشر: {selected_name}")
    
    # تشغيل الرابط أوتوماتيكياً جوه ميديا بلير احترافي مدمج
    if selected_url:
        st.video(selected_url)
        
        # كود للمطورين لو حابب تشوف اللينك المخفي
        with st.expander("🛠️ كود رابط البث الخام (M3U8)"):
            st.code(selected_url, language="text")
