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

# ASCII Art for the Dog
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

    def show_header(self):
        # Professional Header - All English
        header_text = Text.assemble(
            (DOG_ART, "bold blue"),
            ("\n[ ALPHADOG SECURITY SYSTEM v3.2 ]\n", "bold yellow"),
            (f"TARGET: {self.domain}\n", "cyan"),
            (f"STATUS: ACTIVE\n", "bold green"),
            (f"TIME: {self.start_time}", "dim white")
        )
        console.print(Panel(header_text, border_style="bold blue", title="[bold red] SENTRY [/]"))

    def bark(self, msg, url, level="HIGH"):
        # Android Integration
        os.system("termux-vibrate -d 300")
        os.system(f"termux-notification -t 'AlphaDog ALERT' -c '{msg}'")
        
        self.findings.append({
            "time": time.strftime("%H:%M:%S"),
            "msg": msg,
            "level": level
        })

    def make_table(self):
        # Clean Table - No Persian characters to avoid bugs
        table = Table(title="[bold red] HUNTING LOG [/]", border_style="blue")
        table.add_column("TIME", style="dim", width=10)
        table.add_column("EVENT / VULNERABILITY", style="bold white")
        table.add_column("RISK", justify="center")

        if not self.findings:
            table.add_row("-", "Scanning target environment...", "INIT")
        else:
            for f in self.findings[-6:]:
                style = "bold red" if f["level"] == "ULTRA" else "bold yellow"
                table.add_row(f["time"], f["msg"], f"[{style}]{f['level']}[/]")
        return table

    def hunt(self, current_url):
        if current_url in self.visited or len(self.visited) > 100:
            return
        self.visited.add(current_url)

        try:
            # Live Sniffing Status
            console.print(f"[bold green]>> SNIFFING:[/] [blue]{current_url[:40]}...[/]", end="\r")
            
            res = requests.get(current_url, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')

            # 1. Check Security Headers
            if 'Content-Security-Policy' not in res.headers:
                self.bark("MISSING CSP", current_url, "MID")

            # 2. Check Forms for XSS
            if soup.find('form'):
                self.test_xss(current_url)

            # 3. Follow Links
            for a in soup.find_all('a', href=True):
                full_url = urljoin(current_url, a['href'])
                if urlparse(full_url).netloc == self.domain:
                    self.hunt(full_url)
        except:
            pass

    def test_xss(self, url):
        payload = "<script>alert(1)</script>"
        try:
            if payload in requests.get(f"{url}?q={payload}", timeout=5).text:
                self.bark("XSS DETECTED!", url, "ULTRA")
        except: pass

if __name__ == "__main__":
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
            console.print("\n[bold red][!] OPERATION STOPPED BY USER.[/]")
