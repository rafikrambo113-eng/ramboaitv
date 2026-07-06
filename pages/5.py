import os
import streamlit as st
from google import genai
from google.genai import types

# إعدادات واجهة التطبيق
st.set_page_config(page_title="مشغل القنوات الذكي", page_icon="📺", layout="centered")

st.title("📺 مشغل القنوات الذكي بالذكاء الاصطناعي")
st.write("اكتب اسم القناة أو الحدث الرياضي، وسيقوم الذكاء الاصطناعي بالبحث عن روابط البث بجميع الامتدادات وتشغيلها فوراً.")

# إدخال اسم القناة من المستخدم
search_query = st.text_input("اكتب اسم القناة أو الحدث (مثلاً: بي ان سبورت 1، قناة الجزيرة):", placeholder="ابحث هنا...")

if search_query:
    # 🔴 حط المفتاح بتاعك هنا مباشرة بين علامات التنصيص بدلاً من الـ Secrets
    api_key = "هنا_حط_المفتاح_بتاعك"
    
    if api_key == "هنا_حط_المفتاح_بتاعك" or not api_key:
        st.error("⚠️ من فضلك اكتب مفتاح الـ API الحقيقي داخل الكود لتفعيل البحث.")
    else:
        # إنشاء عميل الذكاء الاصطناعي
        client = genai.Client(api_key=api_key)

        # صياغة أمر البحث الشامل لجميع الامتدادات
        prompt = (
            f"ابحث في الإنترنت حالياً عن رابط بث مباشر أو ملف قنوات لـ '{search_query}'. "
            "أريد استخراج الروابط المباشرة فقط بجميع الامتدادات المتاحة مثل: (m3u8, mpd, ts, mp4, m3u). "
            "أعطني الرابط المباشر الشغال فوراً في أول سطر من إجابتك دون أي مقدمات أو شرح."
        )

        with st.spinner("🤖 الذكاء الاصطناعي يبحث في الويب عن روابط البث الآن..."):
            try:
                # استدعاء نموذج Gemini مع تفعيل ميزة البحث الحي في جوجل
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
                
                # استخراج أول رابط متوفر في النتيجة
                stream_url = None
                for line in lines:
                    if "http" in line:
                        start_idx = line.find("http")
                        stream_url = line[start_idx:].split()[0].replace('`', '').replace(')', '')
                        break

                if stream_url:
                    st.success(f"✅ تم العثور على رابط البث!")
                    
                    # عرض الرابط للمستخدم في حال أراد نسخه للمشغلات الخارجية
                    st.text_input("رابط البث المستخرج:", stream_url)
                    
                    # تشغيل الفيديو مباشرة داخل المتصفح عبر Streamlit
                    st.video(stream_url)
                else:
                    st.warning("❌ لم يتم العثور على رابط مباشر واضح، إليك رد الذكاء الاصطناعي بالكامل للتحقق:")
                    st.code(ai_output, language="text")

            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")
