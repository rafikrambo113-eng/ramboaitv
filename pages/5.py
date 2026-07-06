import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="رادع البث المباشر الذكي", page_icon="⚽", layout="wide")

st.title("⚽ مشغل مباريات اليوم الذكي بالأزرار")
st.write("اكتب اسم المباراة الجارية حالياً، وسيقوم الذكاء الاصطناعي بالبحث في مواقع البث الحية وجلب مشغلات ومنافذ العرض فوراً على شكل أزرار لتشغيلها.")

# إدخال اسم المباراة أو الفريقين
match_query = st.text_input("اكتب اسم المباراة (مثلاً: الأهلي والزمالك، ريال مدريد ضد برشلونة):", placeholder="ابحث عن مباراة اليوم...")

if match_query:
    # جلب مفتاح الـ API (حط مفتاحك هنا مباشرة بين علامات التنصيص لو مش عايز تستخدم الـ Secrets)
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "هنا_حط_المفتاح_بتاعك")
    
    if api_key == "هنا_حط_المفتاح_بتاعك" or not api_key:
        st.error("⚠️ من فضلك ضع مفتاح الـ GEMINI_API_KEY لتفعيل ميزة البحث الذكي.")
    else:
        client = genai.Client(api_key=api_key)

        # أمر صارم للذكاء الاصطناعي يستخرج الروابط فقط مقسمة ومجهزة للأزرار
        prompt = (
            f"ابحث في الإنترنت حالياً في مواقع بث المباريات الشهيرة (مثل كورة لايف، يلا شوت، الأسطورة، ماي كورة) "
            f"عن روابط بث مباشر أو مشغلات إيفريم (iframe) لمباراة '{match_query}' الجارية اليوم. "
            "أريد منك إعطائي الروابط الشغالة فقط. "
            "قم بصياغة الإجابة على شكل أسطر واضحة ومحددة كالتالي فقط دون أي كلام جانبي:\n"
            "اسم السيرفر أو الجودة | الرابط المباشر\n"
            "مثال:\n"
            "سيرفر متعدد الجودات | https://example.com/embed/stream1\n"
            "جودة متوسطة | https://example.com/live.m3u8"
        )

        with st.spinner("🤖 الذكاء الاصطناعي يكتسح مواقع البث الآن ويستخرج المشغلات..."):
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
                
                # تصفية الروابط وبناء الأزرار
                streams_found = []
                for line in lines:
                    if "|" in line and "http" in line:
                        parts = line.split("|")
                        title = parts[0].strip().replace("-", "").replace("*", "")
                        url = parts[1].strip().replace('`', '').replace(')', '')
                        streams_found.append((title, url))

                if streams_found:
                    st.success(f"🎉 تم العثور على {len(streams_found)} سيرفرات بث للمباراة!")
                    
                    # إنشاء الأزرار بشكل تفاعلي
                    st.write("### 📺 اختر سيرفر التشغيل:")
                    
                    # استخدام الـ Session State لحفظ السيرفر المختار عشان الصفحة متعملش ريفريش وتختفي النتيجة
                    if 'selected_url' not in st.session_state:
                        st.session_state.selected_url = None
                    if 'selected_title' not in st.session_state:
                        st.session_state.selected_title = None

                    # عرض الأزرار بجانب بعضها
                    cols = st.columns(len(streams_found))
                    for idx, (title, url) in enumerate(streams_found):
                        with cols[idx]:
                            if st.button(f"🟢 {title}", key=f"btn_{idx}"):
                                st.session_state.selected_url = url
                                st.session_state.selected_title = title

                    # تشغيل السيرفر المختار أسفل الأزرار
                    if st.session_state.selected_url:
                        st.markdown("---")
                        st.subheader(f"🎬 عرض البث: {st.session_state.selected_title}")
                        st.code(st.session_state.selected_url, language="text")
                        
                        # التضمين الذكي: إذا كان الرابط m3u8 يشغله بمشغل الفيديو، وإذا كان موقع يفتحه كـ iframe
                        if ".m3u8" in st.session_state.selected_url or ".mp4" in st.session_state.selected_url:
                            st.video(st.session_state.selected_url)
                        else:
                            st.components.v1.iframe(st.session_state.selected_url, height=500, scrolling=True)
                else:
                    st.warning("❌ لم يعثر الذكاء الاصطناعي على روابط مباشرة ومفتوحة حالياً لهذه المباراة. قد تكون المباراة لم تبدأ بعد أو المواقع محمية بالكامل.")
                    with st.expander("رؤية تحليل الذكاء الاصطناعي للصفحات:"):
                        st.write(ai_output)

            except Exception as e:
                st.error(f"حدث خطأ أثناء البحث: {e}")
