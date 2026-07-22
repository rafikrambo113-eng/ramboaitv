"""
سكربت مساعد — يبني app.py جديد بضغطة واحدة، مش محتاج تعدل أي حاجة يدوي.

الاستخدام (على جهازك، أو في نفس مجلد المشروع على GitHub):
    python rebuild_app.py

بيحتاج 3 ملفات في نفس المجلد:
  1. app.py            -> ملف الموقع الحالي بتاعك (اللي فيه _HTML_B64)
  2. rambo-ai-tv.html  -> النسخة الجديدة من الأداة (نزّلها من هنا وحطها في نفس المجلد)
  3. rebuild_app.py    -> السكربت ده نفسه

وبينتج:
  app.py (جديد)  -> بنفس الاسم، هيستبدل القديم (بياخد نسخة احتياطية باسم app.py.bak الأول)
"""
import re
import base64
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
APP_PATH = HERE / "app.py"
HTML_PATH = HERE / "rambo-ai-tv.html"

if not APP_PATH.exists():
    print("❌ مش لاقي app.py في نفس المجلد. حط الملف ده جنب السكربت وجرّب تاني.")
    sys.exit(1)
if not HTML_PATH.exists():
    print("❌ مش لاقي rambo-ai-tv.html في نفس المجلد. نزّله وحطه جنب السكربت.")
    sys.exit(1)

app_src = APP_PATH.read_text(encoding="utf-8")
html_src = HTML_PATH.read_text(encoding="utf-8")

# Re-encode the tool as base64, wrapped at 76 chars/line like the original file
b64 = base64.b64encode(html_src.encode("utf-8")).decode("ascii")
wrapped = [b64[i:i + 76] for i in range(0, len(b64), 76)]
new_block_body = "\n".join('"' + line + '"' for line in wrapped)
new_block = "_HTML_B64 = (\n" + new_block_body + "\n)"

pattern = re.compile(r"_HTML_B64 = \(\n(?:\"[^\"\n]*\"\n)+\)", re.MULTILINE)
match = pattern.search(app_src)
if not match:
    print("❌ مش لاقي بلوك _HTML_B64 جوه app.py — اتأكد إن الملف صح.")
    sys.exit(1)

new_app_src = app_src[:match.start()] + new_block + app_src[match.end():]

backup_path = HERE / "app.py.bak"
shutil.copy(APP_PATH, backup_path)
APP_PATH.write_text(new_app_src, encoding="utf-8")

print("✅ تم تحديث app.py بنجاح.")
print(f"   نسخة احتياطية من القديم اتحفظت في: {backup_path.name}")
print("   دلوقتي ارفع app.py الجديد على GitHub / Streamlit وهيشتغل بالتعريب الكامل.")
