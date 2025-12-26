import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time

# رنگ‌ها برای زیباتر شدن محیط (ANSI Escape Codes)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

DOG_AVATAR = f"""
{BLUE}
      __
     /  \\
    / .. \\      {RESET}{BOLD}AlphaDog v2.0{RESET}{BLUE}
   (_\  /_)     {YELLOW}Status: Hunting...{RESET}{BLUE}
     /  \\
    /____\\      {RED}Ready to Bite!{RESET}
{BLUE}   /      \\
{RESET}
"""

TEST_BITES = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>"
]

class AlphaDog:
    def __init__(self, target):
        self.target = target
        self.domain = urlparse(target).netloc
        self.visited = set()
        self.findings_file = "ELIMINATED_THIEVES.txt"
        os.system('clear')
        print(DOG_AVATAR)
        print(f"{BLUE}[*] شروع گشت‌زنی در قلمرو: {target}{RESET}\n")

    def bark(self, msg, url, level="CRITICAL"):
        color = RED if level == "CRITICAL" else YELLOW
        output = f"\n{color}{BOLD}[!!!] {level} WOOF! {msg}{RESET}\n{BLUE}[TARGET]: {url}{RESET}\n"
        print(output)
        
        with open(self.findings_file, "a") as f:
            f.write(f"{time.ctime()} - {output}\n")
        
        # لرزش و اعلان اندروید
        os.system("termux-vibrate -d 500")
        os.system(f"termux-notification -t 'شکار شد!' -c '{msg}'")

    def hunt(self, current_url):
        if current_url in self.visited or len(self.visited) > 100: # محدودیت برای تست
            return
        self.visited.add(current_url)

        try:
            # نمایش وضعیت به صورت زنده و متحرک
            print(f"{GREEN} 🐾 بو کشیدن: {current_url[-40:]}{RESET}", end='\r')
            response = requests.get(current_url, timeout=5)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # تست XSS اگر فرم پیدا شد
            if soup.find('form'):
                print(f"\n{YELLOW} 🦴 یک استخوان (Form) پیدا شد! در حال جویدن...{RESET}")
                self.test_xss(current_url)

            # ادامه تعقیب
            for a in soup.find_all('a', href=True):
                full_url = urljoin(current_url, a['href'])
                if urlparse(full_url).netloc == self.domain:
                    self.hunt(full_url)

        except: pass

    def test_xss(self, url):
        for bite in TEST_BITES:
            try:
                test_url = f"{url}?q={bite}" 
                res = requests.get(test_url, timeout=5)
                if bite in res.text:
                    self.bark("دزد پیدا شد! شکاف XSS!", test_url)
            except: pass

if __name__ == "__main__":
    target = "https://example.com" # آدرس هدف
    dog = AlphaDog(target)
    try:
        dog.hunt(target)
    except KeyboardInterrupt:
        print(f"\n{BLUE}[!] سگ به لانه بازگشت.{RESET}")
