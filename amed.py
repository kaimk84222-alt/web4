import os
import random
import string
import re
from datetime import datetime, timedelta

# ==============================================================================
# GENERATOR PRO - GITHUB ACTIONS OPTIMIZED
# - تم تحسين الأداء ليعمل ضمن بيئة GitHub Actions بدون توقف (Hang)
# - دعم القوالب المتعددة (test.html, test1.html, test2.html)
# - إنشاء مجلدات فرعية وتوليد 200 صفحة في الدورة الواحدة
# ==============================================================================

class ContinuousGenerator:
    def __init__(self):
        self.templates = {}
        self.template_names = ["test.html", "test1.html", "test2.html"]
        self.keywords_ar = []
        self.keywords_en = []
        self.max_files_per_folder = 500
        self.emojis = ["🔥", "🎥", "🔞", "😱", "✅", "🌟", "📺", "🎬", "✨", "💎", "⚡"]
        
        self.load_all_templates()
        self.load_keywords()

    def load_all_templates(self):
        """تحميل القوالب مع معالجة حالة عدم الوجود"""
        for t_name in self.template_names:
            if os.path.exists(t_name):
                try:
                    with open(t_name, "r", encoding="utf-8") as f:
                        self.templates[t_name] = f.read()
                    print(f"[*] Template {t_name} loaded.")
                except Exception as e:
                    print(f"[!] Error reading {t_name}: {e}")
            else:
                # محتوى افتراضي بسيط لتجنب توقف السكربت
                self.templates[t_name] = "<html><head><title>{{TITLE}}</title></head><body><h1>{{TITLE}}</h1><p>{{DESCRIPTION}}</p>{{INTERNAL_LINKS}}</body></html>"
                print(f"[!] Warning: {t_name} not found. Using fallback layout.")

    def load_keywords(self):
        """تحميل الكلمات المفتاحية مع التحقق من وجود الملفات"""
        ar_file = "keywords_ar.txt"
        en_file = "keywords_en.txt"
        
        if os.path.exists(ar_file):
            with open(ar_file, "r", encoding="utf-8") as f:
                self.keywords_ar = [l.strip() for l in f if l.strip()]
        
        if os.path.exists(en_file):
            with open(en_file, "r", encoding="utf-8") as f:
                self.keywords_en = [l.strip() for l in f if l.strip()]

        # إذا كانت القوائم فارغة، نضع كلمات افتراضية لمنع الحلقات اللانهائية
        if not self.keywords_ar: self.keywords_ar = ["محتوى", "تقني", "تحديث"]
        if not self.keywords_en: self.keywords_en = ["tech", "update", "news"]
        
        print(f"[*] Keywords Loaded: AR({len(self.keywords_ar)}), EN({len(self.keywords_en)})")

    def build_text(self, min_words, max_words, mode="ar"):
        target_length = random.randint(min_words, max_words)
        source = self.keywords_ar if mode == "ar" else self.keywords_en
        words = []
        
        # حماية من الحلقات اللانهائية: محاولة بحد أقصى 1000 مرة
        attempts = 0
        while len(words) < target_length and attempts < 1000:
            chunk = random.choice(source).split()
            words.extend(chunk)
            attempts += 1
            
        return " ".join(words[:target_length])

    def get_target_path(self, total_count):
        paths = []
        files_remaining = total_count
        while files_remaining > 0:
            d1 = ''.join(random.choices(string.ascii_lowercase, k=3))
            d2 = ''.join(random.choices(string.ascii_lowercase, k=3))
            full_path = os.path.join(d1, d2)
            os.makedirs(full_path, exist_ok=True)
            paths.append(full_path)
            files_remaining -= self.max_files_per_folder
        return paths

    def run_single_cycle(self, count=200):
        folder_paths = self.get_target_path(count)
        generated_files = []
        half = count // 2
        modes = (['ar'] * half) + (['en'] * (count - half))
        random.shuffle(modes)

        base_time = datetime.utcnow()
        file_index = 0
        
        # تجهيز البيانات
        for folder in folder_paths:
            chunk_size = min(len(modes) - file_index, self.max_files_per_folder)
            for i in range(chunk_size):
                current_mode = modes[file_index]
                file_time = base_time - timedelta(seconds=random.randint(0, 86400)) # تاريخ عشوائي خلال يوم

                title_text = self.build_text(5, 10, mode=current_mode)
                display_title = f"{random.choice(self.emojis)} {title_text} {random.choice(self.emojis)}"
                
                clean_name = re.sub(r'[^\w\s-]', '', title_text.lower())
                slug = re.sub(r'[-\s]+', '-', clean_name).strip('-')[:80]
                if not slug: slug = ''.join(random.choices(string.ascii_lowercase, k=10))
                
                generated_files.append({
                    "display_title": display_title,
                    "filename": f"{slug}.html",
                    "desc": self.build_text(100, 250, mode=current_mode),
                    "keys": self.build_text(3, 8, mode=current_mode),
                    "mode": current_mode,
                    "date_iso": file_time.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                    "date_sql": file_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "folder": folder,
                    "template": random.choice(self.template_names)
                })
                file_index += 1

        # كتابة الملفات
        for i, file_data in enumerate(generated_files):
            template_content = self.templates.get(file_data['template'], "")
            
            # روابط داخلية ذكية
            links_sample = random.sample(generated_files, min(len(generated_files), 5))
            links_html = "<ul>"
            for lnk in links_sample:
                # الرابط يؤدي للمجلد الصحيح
                full_link = f"/{lnk['folder']}/{lnk['filename']}"
                links_html += f"<li><a href='{full_link}'>{lnk['display_title']}</a></li>"
            links_html += "</ul>"

            content = template_content.replace("{{TITLE}}", file_data['display_title'])
            content = content.replace("{{DESCRIPTION}}", file_data['desc'])
            content = content.replace("{{KEYWORDS}}", file_data['keys'])
            content = content.replace("{{DATE}}", file_data['date_iso'])
            content = content.replace("{{DATE_SQL}}", file_data['date_sql'])
            content = content.replace("{{INTERNAL_LINKS}}", links_html)

            try:
                target_file = os.path.join(file_data['folder'], file_data['filename'])
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                print(f"[!] Error writing file: {e}")

        print(f"✅ Successfully generated {len(generated_files)} pages.")

if __name__ == "__main__":
    generator = ContinuousGenerator()
    generator.run_single_cycle(count=200)
