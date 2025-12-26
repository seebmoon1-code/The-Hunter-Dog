import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

console = Console()

# ASCII Art
DOG_ART = """
      __
     /  \\
    / .. \\   
   (_\\  /_)  
     /  \\    
    /____\\   
   /      \\  
"""

class AlphaDog:
    def __init__(self, target):
        self.target = target
        self.domain = urlparse(target).netloc
        self.visited = set()
        self.findings = []
        self.start_time = time.ctime()
        # ایجاد فایل گزارش اختصاصی برای این دامنه
        self.report_file = f"HUNT_{self.domain.replace('.', '_')}.txt"

    def show_header(self):
        header_text = Text.assemble(
            (DOG_ART, "bold blue"),
            ("\n[ ALPHADOG SECURITY SYSTEM v3.3 ]\n", "bold yellow"),
            (f"TARGET: {self.domain}\n", "cyan"),
            (f"REPORT: {self.report_file}\n", "magenta"),
            (f"STATUS: ACTIVE\n", "bold green"),
            (f"TIME: {self.start_time}", "dim white")
        )
        console.print(Panel(header_text, border_style="bold blue", title="[bold red] SENTRY [/]"))

    def bark(self, msg, url, level="HIGH"):
        # هماهنگی با اندروید
        os.system("termux-vibrate -d 300")
        os.system(f"termux-notification -t 'AlphaDog ALERT' -c '{msg}'")
        
        timestamp = time.strftime("%H:%M:%S")
        self.findings.append({"time": timestamp, "msg": msg, "level": level})

        # ذخیره خودکار در فایل (Auto-Save)
        with open(self.report_file, "a") as f:
            f.write(f"[{timestamp}] [{level}] {msg}\nURL: {url}\n{'-'*30}\n")

    def make_table(self):
        table = Table(title="[bold red] HUNTING LOG [/]", border_style="blue")
        table.add_column("TIME", style="dim", width=10)
        table.add_column("EVENT / VULNERABILITY", style="bold white")
        table.add_column("RISK", justify="center")

        if not self.findings:
            table.add_row("-", "Sniffing for vulnerabilities...", "INIT")
        else:
            for f in self.findings[-6:]:
                style = "bold red" if f["level"] == "ULTRA" else "bold yellow"
                table.add_row(f["time"], f["msg"], f"[{style}]{f['level']}[/]")
        return table

    def hunt(self, current_url):
        if current_url in self.visited or len(self.visited) > 150: # افزایش قدرت گشت‌زنی
            return
        self.visited.add(current_url)

        try:
            console.print(f"[bold green]>> SNIFFING:[/] [blue]{current_url[:40]}...[/]", end="\r")
            
            res = requests.get(current_url, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')

            # ۱. بررسی هدرهای امنیتی
            if 'Content-Security-Policy' not in res.headers:
                self.bark("MISSING CSP", current_url, "MID")

            # ۲. بررسی فرم‌ها برای XSS
            if soup.find('form'):
                self.test_xss(current_url)

            # ۳. تعقیب لینک‌های داخلی
            for a in soup.find_all('a', href=True):
                full_url = urljoin(current_url, a['href'])
                if urlparse(full_url).netloc == self.domain:
                    self.hunt(full_url)
        except:
            pass

    def test_xss(self, url):
        payloads = ["<script>alert(1)</script>", "'><img src=x onerror=alert(1)>"]
        for p in payloads:
            try:
                if p in requests.get(f"{url}?q={p}", timeout=5).text:
                    self.bark(f"XSS DETECTED! (Payload: {p[:10]}...)", url, "ULTRA")
                    break 
            except: pass

if __name__ == "__main__":
    # آدرس سایت هدف را اینجا وارد کنید
    target_site = "https://www.google.com" 
    dog = AlphaDog(target_site)
    
    os.system('clear')
    dog.show_header()

    with Live(dog.make_table(), refresh_per_second=1) as live:
        try:
            dog.hunt(target_site)
            while True:
                live.update(dog.make_table())
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold red][!] SESSION ENDED. REPORT SAVED.[/]")
