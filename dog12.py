import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import sqlite3 # قلعه ذخیره اطلاعات
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

class MemoryHound:
    def __init__(self, targets):
        self.targets = targets
        self.visited = set()
        self.findings = []
        self.db_name = "alphalog_fortress.db"
        self._init_db()
        self.lock = threading.Lock()

    def _init_db(self):
        # ایجاد دیتابیس و جدول شکارها اگر وجود نداشته باشد
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hunts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                target_url TEXT,
                threat_type TEXT,
                danger_level TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def bark(self, msg, url, level="CRITICAL"):
        os.system("termux-vibrate -d 500")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # ذخیره در حافظه دائمی (Database)
        with self.lock:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO hunts (timestamp, target_url, threat_type, danger_level)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, url, msg, level))
            conn.commit()
            conn.close()
            
            self.findings.append({"time": timestamp.split()[1], "msg": msg, "level": level, "url": url[:30]})

    def hunt(self, current_url, domain):
        if current_url in self.visited or len(self.visited) > 150:
            return
        self.visited.add(current_url)

        try:
            res = requests.get(current_url, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')

            # بو کشیدن دزدهای فیشینگ
            if soup.find('form'):
                for form in soup.find_all('form'):
                    action = form.get('action', '').lower()
                    if "login" in action or "pwd" in action:
                        if domain not in action and "http" in action:
                            self.bark("PHISHING DATABASE ENTRY", current_url, "ULTRA")

            # تعقیب لینک‌ها
            for a in soup.find_all('a', href=True):
                full_url = urljoin(current_url, a['href'])
                if urlparse(full_url).netloc == domain:
                    self.hunt(full_url, domain)
        except:
            pass

    def start_patrol(self):
        for target in self.targets:
            domain = urlparse(target).netloc
            threading.Thread(target=self.hunt, args=(target, domain)).start()

def make_table(findings):
    table = Table(title="[bold blue]🏰 ALPHA FORTRESS - PERSISTENT MEMORY 🏰[/]", border_style="blue")
    table.add_column("TIME", style="dim")
    table.add_column("TARGET", style="cyan")
    table.add_column("THREAT IDENTIFIED", style="bold white")
    table.add_column("DANGER", justify="center")

    for f in findings[-7:]:
        style = "bold red" if f["level"] == "ULTRA" else "yellow"
        table.add_row(f["time"], f["url"], f["msg"], f"[{style}]{f['level']}[/]")
    return table

if __name__ == "__main__":
    targets = ["https://example.com", "https://another-site.net"]
    
    dog = MemoryHound(targets)
    os.system('clear')
    console.print(Panel(DOG_ART + "\n[DATABASE ACTIVE]\nMemory is the best weapon against rich thieves.", style="bold cyan"))

    dog.start_patrol()

    with Live(make_table(dog.findings), refresh_per_second=1) as live:
        try:
            while True:
                live.update(make_table(dog.findings))
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold green] Shield active. Database saved in alphalog_fortress.db [/]")
