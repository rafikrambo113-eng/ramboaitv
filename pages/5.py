import os
import time
import vlc
from google import genai
from google.genai import types

def search_and_play_with_ai(search_query):
    # 1. إعداد عميل Gemini API
    api_key = os.environ.get("GEMINI_API_KEY", "ضع_مفتاح_الـ_API_هنا")
    if api_key == "ضع_مفتاح_الـ_API_هنا":
        print("⚠️ من فضلك ضع مفتاح الـ Gemini API أولاً.")
        return

    client = genai.Client(api_key=api_key)

    # 2. صياغة أمر شامل يبحث عن كل الامتدادات والأنواع
    prompt = (
        f"ابحث في الإنترنت حالياً عن رابط بث مباشر أو ملف قنوات لـ '{search_query}'. "
        "أريد استخراج الروابط المباشرة فقط بجميع الامتدادات المتاحة مثل: "
        "(m3u8, m3u, mpd, ts, rtmp) أو بيانات سيرفر Xtream (Host, Port, User, Pass). "
        "أعطني الرابط المباشر الشغال فوراً في أول سطر من إجابتك دون أي مقدمات أو شرح، "
        "وإذا لم تجد رابطاً مباشراً، أعطني رابط الصفحة التي تحتوي على البث المباشر."
    )

    print(f"🤖 الذكاء الاصطناعي يبحث الآن عن كل امتدادات البث لـ ({search_query})...")

    try:
        # استدعاء النموذج مع تفعيل البحث الحي في جوجل
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2
            )
        )

        # تنظيف النص المستخرج للحصول على الرابط
        ai_output = response.text.strip()
        lines = ai_output.split('\n')
        
        # محاولة التقاط أول رابط يظهر في النتيجة
        stream_url = None
        for line in lines:
            if "http" in line:
                # استخراج الرابط فقط من السطر
                start_idx = line.find("http")
                stream_url = line[start_idx:].split()[0].replace('`', '').replace(')', '')
                break

        if not stream_url:
            print("❌ للأسف، الذكاء الاصطناعي لم يجد رابط بث مباشر واضح ومفتوح حالياً.")
            print("رد الذكاء الاصطناعي كاملاً للرجوع إليه:")
            print(ai_output)
            return

        print(f"✅ تم العثور على رابط البث: {stream_url}")
        
        # 3. تشغيل الرابط فوراً باستخدام مشغل VLC (يدعم m3u8, mpd, ts, m3u وكل الامتدادات)
        print("📺 جاري فتح المشغل... انتظر ثواني لبدء البث المباشر...")
        instance = vlc.Instance('--no-video-title-show --quiet')
        player = instance.media_player_new()
        media = instance.media_new(stream_url)
        player.set_media(media)
        player.play()

        # الحفاظ على تشغيل السكربت طالما الفيديو شغال
        print("💡 اضغط Ctrl+C في أي وقت لإغلاق القناة.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            player.stop()
            print("\n⏹️ تم إيقاف التشغيل.")

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    # تأكد من تثبيت المكتبات: pip install google-genai python-vlc
    # وتأكد من تثبيت برنامج VLC Media Player على جهازك
    
    channel_to_search = input("اكتب اسم القناة أو الحدث (مثلاً: بي ان سبورت 1، القناة الأولى، إلخ): ")
    if channel_to_search.strip():
        search_and_play_with_ai(channel_to_search)
