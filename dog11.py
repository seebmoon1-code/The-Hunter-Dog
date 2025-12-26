import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import threading
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

console = Console()

DOG_ART = """
      __
     /  \\
    / .. \\   
   (_\\  /_)  
     /  \\    
    /____\\   
   /      \\  
"""

class ThiefCrusher:
    def __init__(self, targets):
        self.targets = targets
        self.visited = set()
        self.findings = []
        self.report_file = "THIEVES_ELIMINATED.txt"
        self.lock = threading.Lock()

    def bark(self, msg, url, level="CRITICAL"):
        # هشدار لرزشی شدید برای دزدهای خطرناک
        os.system("termux-vibrate -d 1000")
        os.system(f"termux-notification -t 'THIEF DETECTED!' -c '{msg}'")
        
        timestamp = time.strftime("%H:%M:%S")
        with self.lock:
            self.findings.append({"time": timestamp, "msg": msg, "level": level, "url": url[:30]})
            with open(self.report_file, "a") as f:
                f.write(f"[{timestamp}] [{level}] {msg} | TARGET: {url}\n")

    def sniff_thief(self, current_url, domain):
        if current_url in self.visited or len(self.visited) > 200:
            return
        self.visited.add(current_url)

        try:
            res = requests.get(current_url, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')

            # ۱. بو کشیدن فیشینگ (بررسی فرم‌های مخفی که پسورد می‌خواهند)
            forms = soup.find_all('form')
            for form in forms:
                action = form.get('action', '').lower()
                # اگر فرمی پسورد بگیرد ولی به آدرس مشکوکی بفرستد
                if "login" in action or "password" in action:
                    if domain not in action and "http" in action:
                        self.bark("PHISHING TRAP FOUND! (Fake Login)", current_url, "ULTRA")

            # ۲. بو کشیدن فایل‌های مخرب (بدافزارها)
            bad_extensions = [".exe", ".apk", ".bat", ".zip", ".scr"]
            for a in soup.find_all('a', href=True):
                link = a['href'].lower()
                if any(ext in link for ext in bad_extensions):
                    self.bark("MALWARE LINK DETECTED!", link, "CRITICAL")

            # ادامه تعقیب دزد در لینک‌های دیگر
            for a in soup.find_all('a', href=True):
                full_url = urljoin(current_url, a['href'])
                if urlparse(full_url).netloc == domain:
                    self.sniff_thief(full_url, domain)
        except:
            pass

    def start_hunt(self):
        threads = []
        for target in self.targets:
            domain = urlparse(target).netloc
            t = threading.Thread(target=self.sniff_thief, args=(target, domain))
            threads.append(t)
            t.start()

def make_table(findings):
    table = Table(title="[bold red]💀 THIEF CRUSHER SQUAD 💀[/]", border_style="red")
    table.add_column("TIME", style="dim")
    table.add_column("LOCATION (URL)", style="cyan")
    table.add_column("THIEF ACTIVITY", style="bold white")
    table.add_column("DANGER", justify="center")

    for f in findings[-8:]:
        style = "bold red" if f["level"] == "ULTRA" else "bold yellow"
        table.add_row(f["time"], f["url"], f["msg"], f"[{style}]{f['level']}[/]")
    return table

if __name__ == "__main__":
    # آدرس سایت‌هایی که دزدها معمولاً در آن‌ها کمین می‌کنند
    targets = ["https://example-phishing-site.com", "https://suspicious-link.net"]
    
    crusher = ThiefCrusher(targets)
    os.system('clear')
    console.print(Panel(DOG_ART + "\n[DEATH TO THIEVES]\nSniffing out scammers and malware...", style="bold red"))

    crusher.start_hunt()

    with Live(make_table(crusher.findings), refresh_per_second=1) as live:
        try:
            while True:
                live.update(make_table(crusher.findings))
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold yellow] Hunter is resting. Thieves are still in danger. [/]")
