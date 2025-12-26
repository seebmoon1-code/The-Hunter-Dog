import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time

# لیست حملات آزمایشی برای بریدن نفس دزدها (XSS Payloads)
# اینها فقط برای تست امنیتی هستند تا ببینیم آیا سایت کد رو فیلتر می‌کنه یا نه
TEST_BITES = [
    "<script>alert(1)</script>",
    "';alert(1);",
    "\"><script>confirm(1)</script>",
    "<img src=x onerror=alert(1)>"
]

class AlphaDog:
    def __init__(self, target):
        self.target = target
        self.domain = urlparse(target).netloc
        self.visited = set()
        self.findings_file = "ELIMINATED_THIEVES.txt"

    def bark(self, msg, url, level="CRITICAL"):
        output = f"\n[!!!] {level} WOOF! {msg}\n[TARGET]: {url}\n"
        print(output)
        
        # ثبت شکار در پرونده سیاه دزدها
        with open(self.findings_file, "a") as f:
            f.write(f"{time.ctime()} - {output}\n")
        
        # هشدار لرزشی (اندروید)
        os.system("termux-vibrate -d 1500")
        os.system(f"termux-notification -t 'شکار سنگین!' -c '{msg}'")

    def test_xss(self, url):
        # این بخش دندان‌های سگ است؛ چک می‌کند آیا دزد می‌تواند کد تزریق کند؟
        for bite in TEST_BITES:
            try:
                # تست کردن فرم‌ها با متد GET (بسیار رایج در گوگل)
                test_url = f"{url}?q={bite}" 
                res = requests.get(test_url, timeout=5)
                if bite in res.text:
                    self.bark("شکاف امنیتی XSS پیدا شد! دزد وارد شد!", test_url, "ULTRA-CRITICAL")
                    return True
            except: pass
        return False

    def hunt(self, current_url):
        if current_url in self.visited or len(self.visited) > 5000:
            return
        self.visited.add(current_url)

        try:
            print(f"[*] سگ آلفا در حال دریدن: {current_url}", end='\r')
            response = requests.get(current_url, timeout=10)
            
            # ۱. شکار نبود CSP (دیوار اصلی)
            if 'Content-Security-Policy' not in response.headers:
                self.bark("دیوار امنیتی وجود ندارد! راه باز است.", current_url, "WARNING")

            # ۲. شکار فرم‌ها و تست زدن به آن‌ها
            soup = BeautifulSoup(response.text, 'html.parser')
            if soup.find('form'):
                self.bark("یک در پشتی (Form) پیدا شد. در حال تست نفوذ...", current_url, "HIGH")
                self.test_xss(current_url)

            # ۳. تعقیب دزد در لینک‌های دیگر
            for a in soup.find_all('a', href=True):
                full_url = urljoin(current_url, a['href'])
                if urlparse(full_url).netloc == self.domain:
                    self.hunt(full_url)

        except Exception:
            pass

if __name__ == "__main__":
    target_site = "https://www.google.com"
    # اجرای بی‌پایان برای اینکه دزدها رنگ آرامش رو نبینن
    while True:
        dog = AlphaDog(target_site)
        try:
            dog.hunt(target_site)
        except KeyboardInterrupt:
            print("\n[!] پایان عملیات توسط فرمانده.")
            break
        print("\n[*] یک دور کامل زده شد. سگ در حال نفس‌گیری برای حمله بعدی...")
        time.sleep(30)
