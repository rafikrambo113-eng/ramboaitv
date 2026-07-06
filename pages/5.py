import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="جدول مباريات اليوم", page_icon="⚽", layout="wide")

st.title("⚽ جدول مباريات اليوم التلقائي")
st.write("الصفحة دي بتدخل تسحب الماتشات الملعوبة النهاردة ومواعيدها بشكل حي وتلقائي.")

# السحب من موقع كورة المستقر
KOOORA_URL = "https://www.kooora.com/?c=0"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3'
}

with st.spinner("🔄 جاري تحديث جدول المباريات الآن..."):
    try:
        response = requests.get(KOOORA_URL, headers=headers, timeout=10)
        response.encoding = 'utf-8' # لضمان قراءة اللغة العربية بشكل صحيح
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن جدول المباريات في موقع كورة
            match_rows = soup.find_all('tr', class_='match_row')
            
            if match_rows:
                st.success(f"📅 تم تحديث الجدول! تم العثور على مباريات جارية اليوم.")
                
                for row in match_rows:
                    # استخراج أسماء الفرق والموعد
                    team_a = row.find('td', class_='team_a').text.strip() if row.find('td', class_='team_a') else ""
                    team_b = row.find('td', class_='team_b').text.strip() if row.find('td', class_='team_b') else ""
                    match_time = row.find('td', class_='match_time').text.strip() if row.find('td', class_='match_time') else "غير محدد"
                    tournament = row.find_previous('tr', class_='tournament_title').text.strip() if row.find_previous('tr', class_='tournament_title') else "بطولة يومية"
                    
                    if team_a and team_b:
                        with st.container():
                            col1, col2, col3 = st.columns([2, 4, 2])
                            
                            with col1:
                                st.caption(f"🏆 {tournament}")
                            with col2:
                                match_name = f"{team_a} ضد {team_b}"
                                st.markdown(f"### {team_a} 🆚 {team_b}")
                                st.write(f"⏰ الموعد: **{match_time}**")
                            with col3:
                                # الزرار الذكي للمشاهدة
                                search_url = f"https://www.google.com/search?q=بث+مباشر+{team_a}+و+{team_b}+يلا+شوت"
                                st.link_button("📺 شاهد البث الآن", search_url, use_container_width=True)
                            
                            st.markdown("---")
            else:
                # حل بديل إذا كانت الحماية نشطة
                st.warning("⚠️ الموقع في وضع الحماية أو لا توجد مباريات نشطة حالياً. يمكنك استخدام الزر بالأسفل للانتقال لصفحة البث مباشرة:")
                st.link_button("🌐 فتح موقع يلا شوت للبث المباشر فوراً", "https://yallashoot.com", use_container_width=True)
        else:
            st.error("الموقع حالياً لا يستجيب، جرب بعد قليل.")
            
    except Exception as e:
        st.error(f"حدث خطأ بسيط أثناء الاتصال: {e}")
