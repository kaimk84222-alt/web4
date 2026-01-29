import os
import random
import string
import re
import time
from datetime import datetime, timedelta

# ==============================================================================
# GENERATOR PRO - MULTI-TEMPLATE & AUTO-SCHEDULER
# - إنشاء 200 صفحة كل 10 دقائق
# - دعم 3 قوالب مختلفة (test, test1, test2) بشكل عشوائي
# - إدارة ذكية للمجلدات والروابط النظيفة
# ==============================================================================

class ContinuousGenerator:
    def __init__(self):
        self.templates = {} # قاموس لتخزين محتويات القوالب
        self.template_names = ["test.html", "test1.html", "test2.html"]
        self.keywords_ar = []
        self.keywords_en = []
        self.max_files_per_folder = 500
        self.emojis = ["🔥", "🎥", "🔞", "😱", "✅", "🌟", "📺", "🎬", "✨", "💎", "⚡"]
        
        self.load_all_templates()
        self.load_keywords()

    def load_all_templates(self):
        """تحميل محتويات القوالب الثلاثة في الذاكرة"""
        for t_name in self.template_names:
            if os.path.exists(t_name):
                try:
                    with open(t_name, "r", encoding="utf-8") as f:
                        self.templates[t_name] = f.read()
                    print(f"[*] Template {t_name} loaded successfully.")
                except Exception as e:
                    print(f"[!] Error reading {t_name}: {e}")
            else:
                # محتوى افتراضي في حال عدم وجود الملف
                self.templates[t_name] = f"<html><body><h1>Default {t_name}</h1>{{{{TITLE}}}}<br>{{{{DESCRIPTION}}}}<br>{{{{INTERNAL_LINKS}}}}</body></html>"

    def load_keywords(self):
        ar_files = ["keywords_ar.txt"]
        en_files = ["keywords_en.txt"]
        
        for file in ar_files:
            if os.path.exists(file):
                with open(file, "r", encoding="utf-8") as f:
                    self.keywords_ar.extend([l.strip() for l in f if l.strip()])
                    
        for file in en_files:
            if os.path.exists(file):
                with open(file, "r", encoding="utf-8") as f:
                    self.keywords_en.extend([l.strip() for l in f if l.strip()])
        
        print(f"[*] Loaded {len(self.keywords_ar)} Arabic and {len(self.keywords_en)} English keywords.")

    def build_text(self, min_words, max_words, mode="ar"):
        target_length = random.randint(min_words, max_words)
        source = self.keywords_ar if mode == "ar" else self.keywords_en
        if not source: source = ["Keyword", "Trending", "Video"]
        words = []
        while len(words) < target_length:
            chunk = random.choice(source).split()
            words.extend(chunk)
        return " ".join(words[:target_length])

    def get_target_path(self, total_count):
        base_root = "."
        files_remaining = total_count
        paths = []
        while files_remaining > 0:
            first_folder = ''.join(random.choices(string.ascii_lowercase, k=3))
            second_folder = ''.join(random.choices(string.ascii_lowercase, k=3))
            full_path = os.path.join(base_root, first_folder, second_folder)
            os.makedirs(full_path, exist_ok=True)
            paths.append(full_path)
            chunk = min(files_remaining, self.max_files_per_folder)
            files_remaining -= chunk
        return paths

    def run_single_cycle(self, count=200):
        """دورة واحدة لتوليد الملفات"""
        folder_paths = self.get_target_path(count)
        generated_files = []
        half = count // 2
        modes = (['ar'] * half) + (['en'] * (count - half))
        random.shuffle(modes)

        base_time = datetime.utcnow()
        file_index = 0
        
        # 1. تجهيز بيانات الملفات
        for folder in folder_paths:
            current_chunk = min(len(modes) - file_index, self.max_files_per_folder)
            for i in range(current_chunk):
                current_mode = modes[file_index]
                file_time = base_time - timedelta(seconds=random.randint(0, 3600))

                formatted_date_iso = file_time.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                formatted_date_sql = file_time.strftime("%Y-%m-%d %H:%M:%S")

                title_len = random.choice([5, 7, 9, 11])
                raw_title = self.build_text(title_len, title_len + 2, mode=current_mode)
                display_title = f"{random.choice(self.emojis)} {raw_title} {random.choice(self.emojis)}"

                clean_name = re.sub(r'[^\w\s-]', '', raw_title.lower())
                slug = re.sub(r'[-\s]+', '-', clean_name).strip('-')[:80]
                filename = f"{slug}.html"

                generated_files.append({
                    "display_title": display_title,
                    "filename": filename,
                    "desc": self.build_text(120, 350, mode=current_mode),
                    "keys": self.build_text(3, 8, mode=current_mode),
                    "mode": current_mode,
                    "date_iso": formatted_date_iso,
                    "date_sql": formatted_date_sql,
                    "folder": folder,
                    "template_to_use": random.choice(self.template_names) # اختيار قالب عشوائي
                })
                file_index += 1

        # 2. كتابة الملفات فعلياً
        for i, file_data in enumerate(generated_files):
            # اختيار المحتوى من القالب المخصص لهذا الملف
            content = self.templates[file_data['template_to_use']]

            # توليد روابط داخلية
            other_files = [f for j, f in enumerate(generated_files) if i != j]
            same_lang_files = [f for f in other_files if f['mode'] == file_data['mode']]
            source_for_links = same_lang_files if len(same_lang_files) >= 3 else other_files
            links_sample = random.sample(source_for_links, min(len(source_for_links), random.randint(3, 6)))

            links_html = "<div class='internal-links'><ul>"
            for link in links_sample:
                links_html += f"<li><a href='{link['filename']}'>{link['display_title']}</a></li>"
            links_html += "</ul></div>"

            # استبدال الكلمات المحجوزة
            content = content.replace("{{TITLE}}", file_data['display_title'])
            content = content.replace("{{DESCRIPTION}}", file_data['desc'])
            content = content.replace("{{KEYWORDS}}", file_data['keys'])
            content = content.replace("{{DATE}}", file_data['date_iso'])
            content = content.replace("{{DATE_SQL}}", file_data['date_sql'])
            
            if "{{INTERNAL_LINKS}}" in content:
                content = content.replace("{{INTERNAL_LINKS}}", links_html)
            else:
                content += f"\n{links_html}"

            try:
                file_path = os.path.join(file_data['folder'], file_data['filename'])
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                print(f"[!] Failed to write file: {e}")
        
        print(f"✅ {datetime.now().strftime('%H:%M:%S')} | Created {count} files using random templates.")

    def start_infinite_loop(self, interval_seconds=600, count_per_cycle=200):
        """تشغيل المولد بشكل مستمر"""
        print(f"🚀 Generator started. Working every {interval_seconds/60} minutes...")
        try:
            while True:
                self.run_single_cycle(count=count_per_cycle)
                print(f"😴 Sleeping for {interval_seconds/60} minutes...")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n[!] Generator stopped by user.")

if __name__ == "__main__":
    bot = ContinuousGenerator()
    # تشغيل: 200 صفحة كل 600 ثانية (10 دقائق)
    bot.start_infinite_loop(interval_seconds=600, count_per_cycle=200)
