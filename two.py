import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import collections
import time
import os

class SentinelHunter:
    def __init__(self, base_url):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited = set()
        self.queue = collections.deque([base_url])
        self.start_time = time.time()

    def bark(self, msg, url):
        alert = f"\n[!!!] WOOF! WOOF! شکار پیدا شد: {msg}\n[LOCATION]: {url}\n"
        print(alert)
        
        # ذخیره سریع در فایل (حافظه سگ)
        with open("shikar_report.txt", "a") as f:
            f.write(f"{time.ctime()} - {alert}\n")
        
        # بیدار کردن صاحب سگ (ویبره و نوتیفیکیشن اندروید)
        os.system("termux-vibrate -d 1000")
        os.system(f"termux-notification -t 'شکار جدید!' -c '{msg}'")

    def sniff(self):
        print(f"--- سگ شکارچی رها شد روی دامنه: {self.domain} ---")
        print("--- برای توقف دکمه Ctrl+C را بزنید (ولی سگ بیدار می‌ماند!) ---")
        
        while self.queue:
            url = self.queue.popleft()
            
            if url in self.visited:
                continue
                
            self.visited.add(url)
            
            try:
                # لاگ کردن برای اینکه بدانی سگ زنده است
                print(f"[*] در حال بو کشیدن: {url} (کل صفحات دیده شده: {len(self.visited)})", end='\r')
                
                response = requests.get(url, timeout=7, headers={
                    'User-Agent': 'Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0'
                })
                
                # بررسی ۱: وجود فرم (در ورودی دزدها)
                if "<form" in response.text.lower():
                    self.bark("یک در ورودی (Form) پیدا شد! احتمال تزریق کد.", url)

                # بررسی ۲: امنیت لایه‌ها (CSP)
                if 'Content-Security-Policy' not in response.headers:
                    self.bark("دیوار امنیتی (CSP) وجود ندارد! هکر می‌تواند وارد شود.", url)

                # پیدا کردن لینک‌های جدید و اضافه کردن به صف برای ادامه بی‌پایان
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    
                    # سگ فقط در محدوده قلعه (دامنه اصلی) شکار می‌کند
                    if urlparse(full_url).netloc == self.domain:
                        if full_url not in self.visited:
                            self.queue.append(full_url)

            except KeyboardInterrupt:
                print("\n[!] صاحب سگ دستور توقف داد. خدانگهدار!")
                break
            except Exception:
                # سگ در صورت خطا (مثل قطعی اینترنت موقت) نباید متوقف شود
                continue

if __name__ == "__main__":
    # هدف را اینجا مشخص کن
    target = "https://www.google.com"
    dog = SentinelHunter(target)
    dog.sniff()
