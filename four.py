import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import collections
import os
import time

class MasterHunter:
    def __init__(self, target):
        self.target = target
        self.domain = urlparse(target).netloc
        self.visited = set()
        self.queue = collections.deque([target])
        self.report_file = "GOOGLE_SUBMIT_READY.txt"

    def notify(self, msg, url):
        # ۱. اعلان در ترمینال
        print(f"\n[!!!] شکار شد: {msg} در {url}")
        
        # ۲. ویبره و نوتیفیکیشن اندروید (بدون نیاز به تنظیمات اضافی)
        os.system("termux-vibrate -d 500")
        os.system(f"termux-notification -t 'Hunter-Dog Alert' -c '{msg}'")
        
        # ۳. نوشتن گزارش آماده برای کپی پیست در سایت گوگل
        with open(self.report_file, "a") as f:
            f.write(f"\n--- NEW BUG REPORT ---\nURL: {url}\nISSUE: {msg}\nGO TO: bughunters.google.com\n")

    def start(self):
        print(f"--- سگ شکارچی بی‌پایان فعال شد در: {self.domain} ---")
        while True:
            if not self.queue: # اگر لینک‌ها تمام شد، دوباره از اول شروع کن
                self.queue.append(self.target)
                self.visited.clear()

            url = self.queue.popleft()
            if url in self.visited: continue
            self.visited.add(url)

            try:
                print(f"[*] بو کشیدن: {url}", end='\r')
                res = requests.get(url, timeout=5)
                
                # بررسی‌های امنیتی
                if 'Content-Security-Policy' not in res.headers:
                    self.notify("Missing CSP (Security Wall)", url)
                
                if "<form" in res.text:
                    self.notify("Input Form Found (Check for Injection)", url)

                # پیدا کردن لینک‌های جدید
                soup = BeautifulSoup(res.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    link = urljoin(url, a['href'])
                    if urlparse(link).netloc == self.domain:
                        self.queue.append(link)
            except:
                continue

if __name__ == "__main__":
    hunter = MasterHunter("https://www.google.com")
    hunter.start()
