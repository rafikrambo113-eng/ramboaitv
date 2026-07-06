import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="جدول مباريات اليوم", page_icon="⚽", layout="wide")

st.title("⚽ جدول مباريات اليوم التلقائي")
st.write("الصفحة دي بتدخل تسحب الماتشات الملعوبة النهاردة ومواعيدها من يلا كورة بشكل حي وتلقائي.")

# رابط صفحة المباريات في موقع يلا كورة
YALLAKORA_URL = "https://www.yallakora.com/match-center/%D9%85%D8%B1%D9%83%D8%B2-%D8%A7%D9%84%D9%85%D8%A8%D8%A7%D8%B1%D9%8A%D8%A7%D8%AA"

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
}

with st.spinner("🔄 جاري سحب جدول مباريات اليوم من يلا كورة..."):
    try:
        response = requests.get(YALLAKORA_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # البحث عن أجزاء المباريات في الصفحة
            match_cards = soup.find_all('div', class_='matchCard')
            
            matches_list = []
            
            for card in match_cards:
                # اسم البطولة
                tournament = card.find('div', class_='title').text.strip() if card.find('div', class_='title') else "بطولة غير محددة"
                
                # تفاصيل الماتشات جوه البطولة
                all_matches = card.find_all('div', class_='allMatchs')
                for match in all_matches:
                    team_a = match.find('div', class_='teamA').text.strip() if match.find('div', class_='teamA') else ""
                    team_b = match.find('div', class_='teamB').text.strip() if match.find('div', class_='teamB') else ""
                    match_time = match.find('span', class_='matchTime').text.strip() if match.find('span', class_='matchTime') else "غير محدد"
                    match_status = match.find('div', class_='matchStatus').text.strip() if match.find('div', class_='matchStatus') else ""
                    
                    if team_a and team_b:
                        matches_list.append({
                            "البطولة": tournament,
                            "المباراة": f"{team_a} 🆚 {team_b}",
                            "الموعد": match_time,
                            "الحالة": match_status if match_status else "لم تبدأ بعد"
                        })
            
            if matches_list:
                st.success(f"📅 تم تحديث الجدول بنجاح! تم العثور على {len(matches_list)} مباراة اليوم.")
                
                # عرض الماتشات بشكل منظم
                for index, match_item in enumerate(matches_list):
                    with st.container():
                        col1, col2, col3 = st.columns([2, 4, 2])
                        
                        with col1:
                            st.caption(f"🏆 {match_item['البطولة']}")
                        with col2:
                            st.markdown(f"### {match_item['المباراة']}")
                            st.write(f"⏰ الموعد: **{match_item['الموعد']}** | الحالة: `{match_item['الحالة']}`")
                        with col3:
                            # زرار ذكي ينقلك لجوجل يبحث لك عن البث المباشر للماتش ده فوراً بضغطة واحدة
                            search_url = f"https://www.google.com/search?q=بث+مباشر+{match_item['المباراة'].replace('🆚', 'ضد')}+يلا+شوت"
                            st.link_button("📺 شاهد البث الآن", search_url, use_container_width=True)
                        
                        st.markdown("---")
            else:
                st.warning("⚠️ مفيش ماتشات متاح سحبها حالياً في هذه اللحظة، جرب وقت الماتشات.")
                
        else:
            st.error("الموقع رافض السحب حالياً، جرب كمان دقيقة.")
            
    except Exception as e:
        st.error(f"حصلت مشكلة بسيطة أثناء جلب البيانات: {e}")
