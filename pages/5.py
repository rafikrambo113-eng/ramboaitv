import os
import streamlit as st
from google import genai
from google.genai import types

st.title("📺 مشغل القنوات الذكي بالذكاء الاصطناعي")

# إدخال اسم القناة من المستخدم
search_query = st.text_input("اكتب اسم القناة أو الحدث (مثلاً: بي ان سبورت 1):")

if search_query:
    # إعداد عميل Gemini API (يفضل وضعه في الـ Secrets في Streamlit Cloud)
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ من فضلك أضف مفتاح الـ GEMINI_API_KEY في إعدادات الـ Secrets الخاصة بالتطبيق.")
    else:
        client = genai.Client(api_key=api_key)

        prompt = (
            f"ابحث في الإنترنت حالياً عن رابط بث مباشر أو ملف قنوات لـ '{search_query}'. "
            "أريد استخراج الروابط المباشرة فقط بجميع الامتدادات المتاحة مثل: (m3u8, mpd, ts, mp4). "
            "أعطني الرابط المباشر الشغال فوراً في أول سطر من إجابتك دون أي مقدمات أو شرح."
        )

        with st.spinner("🤖 الذكاء الاصطناعي يبحث عن روابط البث الآن..."):
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
                
                stream_url = None
                for line in lines:
                    if "http" in line:
                        start_idx = line.find("http")
                        stream_url = line[start_idx:].split()[0].replace('`', '').replace(')', '')
                        break

                if stream_url:
                    st.success(f"✅ تم العثور على رابط البث!")
                    st.code(stream_url, language="text")
                    
                    # تشغيل الفيديو مباشرة داخل صفحة الويب في Streamlit
                    # ملاحظة: st.video يدعم روابط m3u8 و mp4 مباشرة في معظم المتصفحات
                    st.video(stream_url)
                else:
                    st.warning("❌ لم يتم العثور على رابط مباشر واضح، إليك رد الذكاء الاصطناعي:")
                    st.write(ai_output)

            except Exception as e:
                st.error(f"حدث خطأ أثناء البحث: {e}")
