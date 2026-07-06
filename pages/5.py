import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="جدول مباريات اليوم والبث المباشر", page_icon="⚽", layout="wide")

st.title("⚽ جدول مباريات اليوم والبث المباشر الذكي")
st.write("يتم الآن جلب مباريات اليوم المباشرة وتجهيز أزرار التشغيل تلقائياً بدون الحاجة للبحث يدوياً.")

# 🔴 حط المفتاح بتاعك هنا مباشرة بين علامات التنصيص
api_key = "هنا_حط_المفتاح_بتاعك"

if api_key == "هنا_حط_المفتاح_بتاعك" or not api_key:
    st.error("⚠️ من فضلك اكتب مفتاح الـ API الحقيقي داخل الكود (مكان: هنا_حط_المفتاح_بتاعك) ليشتغل التطبيق تلقائياً.")
else:
    client = genai.Client(api_key=api_key)

    # أمر برمجت فيه الـ AI يدور على مباريات اليوم ومواعيدها وسيرفراتها لوحده
    prompt = (
        "ابحث في الإنترنت حالياً عن جدول مباريات كرة القدم الجارية أو الملعوبة اليوم ومواعيدها، "
        "واستخرج روابط البث المباشر أو المشغلات (iframe أو m3u8) المتاحة لها من مواقع البث (مثل يلا شوت، كورة لايف، الأسطورة). "
        "أعطني النتيجة في أسطر واضحة ومحددة بهذا الشكل فقط دون أي كلام آخر:\n"
        "اسم المباراة ووقتها | الرابط المباشر\n"
        "مثال:\n"
        "البرتغال ضد فرنسا (9:00 مساءً) | https://example.com/embed/stream1\n"
        "إسبانيا ضد ألمانيا (6:00 مساءً) | https://example.com/live.m3u8"
    )

    # حفظ حالة السيرفر المختار في الـ Session State لمنع اختفاء الفيديو عند الضغط
    if 'selected_url' not in st.session_state:
        st.session_state.selected_url = None
    if 'selected_match' not in st.session_state:
        st.session_state.selected_match = None

    # تشغيل البحث التلقائي بمجرد فتح الصفحة
    with st.spinner("🔄 جاري سحب جدول مباريات اليوم وسيرفرات البث الحية..."):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.2
                )
            )

            ai_output = response.text.strip()
            lines = ai_output.split('\n')
            
            matches_found = []
            for line in lines:
                if "|" in line and "http" in line:
                    parts = line.split("|")
                    match_info = parts[0].strip().replace("-", "").replace("*", "")
                    url = parts[1].strip().replace('`', '').replace(')', '')
                    matches_found.append((match_info, url))

            if matches_found:
                st.success(f"📅 تم العثور على {len(matches_found)} مباريات متاحة اليوم!")
                
                st.write("### 📺 اضغط على المباراة لمشاهدة البث المباشر:")
                
                # إنشاء زرار لكل مباراة تحت بعضها بشكل منظم
                for idx, (match_info, url) in enumerate(matches_found):
                    if st.button(f"⚽ {match_info}", key=f"match_{idx}", use_container_width=True):
                        st.session_state.selected_url = url
                        st.session_state.selected_match = match_info

                # إذا ضغط المستخدم على أي مباراة، يفتح المشغل هنا فوراً
                if st.session_state.selected_url:
                    st.markdown("---")
                    st.subheader(f"🎬 مشغل البث الحالي: {st.session_state.selected_match}")
                    
                    # التضمين الذكي للمشغل حسب نوع الرابط المستخرج
                    if ".m3u8" in st.session_state.selected_url or ".mp4" in st.session_state.selected_url:
                        st.video(st.session_state.selected_url)
                    else:
                        st.components.v1.iframe(st.session_state.selected_url, height=550, scrolling=True)
            else:
                st.warning("⚠️ لم يعثر الذكاء الاصطناعي على مباريات بث مباشر نشطة في هذه اللحظة، قد يكون الجدول فارغاً الآن.")
                with st.expander("بيانات جلب الصفحة (للتحقق):"):
                    st.write(ai_output)

        except Exception as e:
            st.error(f"حدث خطأ أثناء جلب البيانات التلقائي: {e}")
