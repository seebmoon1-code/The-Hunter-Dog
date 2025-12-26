import requests
from urllib.parse import urljoin, urlparse

class HunterDog:
    def __init__(self, target):
        self.target = target
        self.visited = set()
        self.vulnerabilities = []

    def bark(self, msg):
        print(f"[!] WOOF! {msg}")
        # ویبره برای باخبر کردن تو در اندروید
        import os
        os.system("termux-vibrate -d 500")

    def sniff(self, url):
        if url in self.visited or len(self.visited) > 100:
            return
        self.visited.add(url)
        
        try:
            print(f"[*] بو کشیدن: {url}")
            response = requests.get(url, timeout=5)
            
            # شکار ۱: پیدا کردن فرم‌های آسیب‌پذیر
            if "password" in response.text.lower() or "input" in response.text:
                self.bark(f"یک در ورودی (Form) در {url} پیدا شد. احتمال نفوذ!")

            # شکار ۲: بررسی امنیت پروتکل
            if not url.startswith("https"):
                self.bark(f"خطر! این مسیر امن نیست (No SSL): {url}")

            # پیدا کردن لینک‌های جدید برای تعقیب دزدها
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                new_url = urljoin(url, a['href'])
                if urlparse(new_url).netloc == urlparse(self.target).netloc:
                    self.sniff(new_url)

        except Exception as e:
            pass

# شروع شکار
if __name__ == "__main__":
    target_site = "https://www.google.com"
    hunter = HunterDog(target_site)
    print(f"--- سگ شکارچی رها شد روی: {target_site} ---")
    hunter.sniff(target_site)
