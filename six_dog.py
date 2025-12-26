import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import collections
import os
import time
import datetime

class UltimateHunterDog:
    def __init__(self, target_url):
        self.target_url = target_url
        self.domain = urlparse(target_url).netloc
        self.visited = set()
        self.queue = collections.deque([target_url])
        # فایل گزارش نهایی که گوگل می‌خواد
        self.report_file = f"google_shikar_{self.domain.replace('.', '_')}.txt"
        
        # بوهای حساس (فایل‌هایی که دزدها دنبالشن)
        self.sensitive_scents = ["/.env", "/.git/config", "/phpinfo.php", "/config.php.bak"]

    def bark(self, msg, url, severity="LOW"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        alert = f"[{timestamp}] [{severity}] WOOF! {msg} -> {url}"
        print(alert)

        # ۱. ویبره و نوتیفیکیشن برای اندروید (فرمانده باخبر بشه)
        os.system("termux-vibrate -d 800")
        os.system(f"termux-notification -t 'شکار جدید!' -c '{msg}'")

        # ۲. ثبت در گزارش نهایی برای کپی در سایت گوگل
        with open(self.report_file, "a") as f:
            f.write(f"{alert}\n" + "-"*30 + "\n")

    def sniff_scents(self, url):
        # بررسی فایل‌های حساس در هر دایرکتوری که پیدا میکنه
        base = "/".join(url.split("/")[:4]) 
        for scent in self.sensitive_scents:
            try:
                check_url = urljoin(base, scent)
                res = requests.get(check_url, timeout=3)
                if res.status_code == 200:
                    self.bark("گنج پیدا شد! نشت فایل حساس", check_url, "HIGH")
            except: continue

    def hunt(self):
        print(f"--- ارتش تک‌نفره سگ شکارچی روی {self.domain} رها شد ---")
        
        while True:
            if not self.queue:
                print("\n[*] قلعه کاملاً بو کشیده شد. شروع مجدد برای اطمینان...")
                self.queue.append(self.target_url)
                self.visited.clear()
                time.sleep(10)

            url = self.queue.popleft()
            if url in self.visited: continue
            self.visited.add(url)

            try:
                print(f"[*] در حال بو کشیدن: {url} (تعداد شکار: {len(self.visited)})", end='\r')
                
                # تنظیم Header برای اینکه گوگل فکر کنه ما یک گوشی اندروید معمولی هستیم
                headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 14) Termux/0.118'}
                response = requests.get(url, timeout=7, headers=headers)

                # ۱. شکار نبود دیوار امنیتی (CSP)
                if 'Content-Security-Policy' not in response.headers:
                    self.bark("نبود دیوار CSP (خطر تزریق کد)", url, "MEDIUM")

                # ۲. شکار فرم‌های نفوذ
                if "<form" in response.text.lower():
                    self.bark("در ورودی (Form) پیدا شد! تست نفوذ لازم است", url, "LOW")

                # ۳. بو کشیدن فایل‌های حساس
                self.sniff_scents(url)

                # پیدا کردن لینک‌های جدید برای ادامه دوندگی
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    link = urljoin(url, a['href'])
                    if urlparse(link).netloc == self.domain and link not in self.visited:
                        self.queue.append(link)

            except KeyboardInterrupt:
                print("\n[!] توقف توسط فرمانده. گزارش‌ها در فایل ذخیره شد.")
                break
            except Exception as e:
                continue

if __name__ == "__main__":
    # آدرس قلعه رو اینجا بده
    target = "https://www.google.com"
    dog = UltimateHunterDog(target)
    dog.hunt()
