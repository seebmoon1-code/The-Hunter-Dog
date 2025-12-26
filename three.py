import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import collections
import time
import os
import datetime

class HunterDog:
    def __init__(self, base_url):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited = set()
        self.queue = collections.deque([base_url])
        self.findings = [] # برای ذخیره یافته‌ها جهت گزارش نهایی
        self.session = requests.Session() # برای بهینه‌سازی درخواست‌ها
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0',
            'Accept-Language': 'en-US,en;q=0.5'
        }

    def _alert(self, msg, url, vuln_type="General"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_msg = f"[{timestamp}] [!!!] WOOF! {vuln_type} - {msg}\n[LOCATION]: {url}"
        print(alert_msg)
        self.findings.append({"type": vuln_type, "message": msg, "url": url, "timestamp": timestamp})
        
        # ذخیره سریع در فایل
        with open("hunter_dog_report.txt", "a") as f:
            f.write(alert_msg + "\n")
        
        # اعلان و ویبره برای صاحب سگ (اندروید)
        os.system("termux-vibrate -d 1000")
        os.system(f"termux-notification -t 'شکار جدید توسط سگ!' -c '{vuln_type} در {url}'")

    def _crawl_and_sniff(self, url):
        self.visited.add(url)
        
        try:
            print(f"[*] بو کشیدن: {url} (صفحات بازدید شده: {len(self.visited)}, در صف: {len(self.queue)})", end='\r')
            response = self.session.get(url, timeout=10, headers=self.headers)
            
            # 1. بررسی عدم وجود CSP (Content Security Policy)
            if 'Content-Security-Policy' not in response.headers:
                self._alert("دیوار امنیتی (CSP) وجود ندارد! هکر می‌تواند کد مخرب تزریق کند.", url, "Missing_CSP")

            # 2. بررسی عدم وجود X-Frame-Options (برای Clickjacking)
            if 'X-Frame-Options' not in response.headers:
                self._alert("نبود X-Frame-Options! صفحه در iframe قابل نمایش است (Clickjacking).", url, "Clickjacking_Vuln")

            # 3. بررسی وجود فرم‌های ورودی (احتمال Injection, XSS)
            soup = BeautifulSoup(response.text, 'html.parser')
            if soup.find('form'):
                self._alert("فرم ورودی پیدا شد. احتمال XSS/Injection.", url, "Form_Detected")
            
            # اضافه کردن لینک‌های جدید به صف
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                parsed_full_url = urlparse(full_url)
                
                # فقط در همان دامنه اصلی شکار کن
                if parsed_full_url.netloc == self.domain and full_url not in self.visited:
                    self.queue.append(full_url)
            
        except requests.exceptions.Timeout:
            print(f"[-] مهلت تمام شد: {url}", end='\r')
        except requests.exceptions.RequestException as e:
            print(f"[-] خطا در درخواست برای {url}: {e}", end='\r')
        except Exception as e:
            print(f"[-] خطای ناشناخته برای {url}: {e}", end='\r')


    def start_hunt(self):
        print(f"--- سگ شکارچی بی توقف رها شد روی: {self.base_url} ---")
        print("--- برای توقف از Ctrl+C استفاده کنید (ولی سگ هرگز نمی‌خوابد!) ---")
        
        while self.queue:
            current_url = self.queue.popleft()
            if len(self.visited) > 10000: # یک محدودیت برای جلوگیری از مصرف بیش از حد حافظه
                print("\n[!] تعداد صفحات بازدید شده زیاد است. برای جلوگیری از کرش، لیست را خالی می‌کنم.")
                self.queue.clear() # صف را پاک می‌کنیم
                self.visited.clear() # صفحات بازدید شده را پاک می‌کنیم
                self.queue.append(self.base_url) # از اول شروع می‌کنیم
            
            self._crawl_and_sniff(current_url)
            time.sleep(0.1) # یک مکث کوچک برای جلوگیری از بار زیاد روی سرور

        self.generate_final_report()


    def generate_final_report(self):
        report_filename = f"final_google_bug_report_{datetime.date.today()}.txt"
        with open(report_filename, "w") as f:
            f.write(f"--- Hunter Dog Final Vulnerability Report for {self.base_url} ---\n")
            f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Unique Pages Scanned: {len(self.visited)}\n")
            f.write("-" * 50 + "\n\n")

            if not self.findings:
                f.write("No significant vulnerabilities found during this hunt.\n")
            else:
                f.write("Identified Vulnerabilities:\n")
                for finding in self.findings:
                    f.write(f"  Type: {finding['type']}\n")
                    f.write(f"  Message: {finding['message']}\n")
                    f.write(f"  URL: {finding['url']}\n")
                    f.write(f"  Timestamp: {finding['timestamp']}\n")
                    f.write("-" * 20 + "\n")
            f.write("\n--- End of Report ---\n")
        print(f"\n[+] گزارش نهایی با تمام یافته‌ها آماده شد: {report_filename}")
        print("این فایل را می‌توانید مستقیماً در Google Bug Hunters آپلود کنید.")


if __name__ == "__main__":
    # هدف را اینجا مشخص کن
    target_website = "https://www.google.com" # یا هر سایت دیگری که می‌خواهی
    
    # برای اینکه سگ همیشه بیدار بماند
    while True:
        dog = HunterDog(target_website)
        try:
            dog.start_hunt()
        except KeyboardInterrupt:
            print("\n[!] دستور توقف از صاحب سگ دریافت شد. عملیات متوقف شد.")
            break
        except Exception as e:
            print(f"\n[!] خطای غیرمنتظره در سگ: {e}. سگ دوباره شروع به شکار می‌کند...")
            time.sleep(5) # کمی مکث قبل از شروع مجدد
