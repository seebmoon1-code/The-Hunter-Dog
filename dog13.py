import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

console = Console()

class AlphaSquad:
    def __init__(self, targets, max_dogs=5):
        self.targets = targets
        self.findings = []
        self.db_name = "alphalog_fortress.db"
        self.max_dogs = max_dogs
        self._init_db()
        self.lock = threading.Lock()
        self.visited_in_session = set()

    def _init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS global_registry 
                          (url_hash TEXT PRIMARY KEY, visit_time TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS hunts 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, 
                           target_url TEXT, threat_type TEXT, danger_level TEXT)''')
        conn.commit()
        conn.close()

    def is_already_sniffed(self, url):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM global_registry WHERE url_hash = ?', (url,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except: return False

    def register_visit(self, url):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO global_registry VALUES (?, ?)', (url, time.ctime()))
            conn.commit()
            conn.close()
        except: pass

    def bark(self, msg, url, level="HIGH"):
        os.system("termux-vibrate -d 300")
        timestamp = time.strftime("%H:%M:%S")
        with self.lock:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO hunts (timestamp, target_url, threat_type, danger_level) VALUES (?, ?, ?, ?)', 
                           (time.strftime("%Y-%m-%d %H:%M:%S"), url, msg, level))
            conn.commit()
            conn.close()
            self.findings.append({"time": timestamp, "msg": msg, "level": level, "url": url[:30]})

    def hunt(self, current_url):
        domain = urlparse(current_url).netloc
        if self.is_already_sniffed(current_url) or current_url in self.visited_in_session:
            return []
        
        self.visited_in_session.add(current_url)
        self.register_visit(current_url)

        try:
            with self.lock:
                console.print(f"[bold yellow]🐾 Sniffing:[/] [blue]{current_url[:45]}...[/]")
            
            res = requests.get(current_url, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')

            if soup.find('form'):
                for form in soup.find_all('form'):
                    action = form.get('action', '').lower()
                    if "login" in action or "pwd" in action:
                        self.bark("PHISHING TRAP", current_url, "ULTRA")

            links = []
            for a in soup.find_all('a', href=True):
                full_url = urljoin(current_url, a['href'])
                if urlparse(full_url).netloc == domain:
                    links.append(full_url)
            return links
        except:
            return []

    def run_squad(self):
        # اصلاح متد wait برای جلوگیری از ارور
        with ThreadPoolExecutor(max_workers=self.max_dogs) as executor:
            future_to_url = {executor.submit(self.hunt, url): url for url in self.targets}
            
            while future_to_url:
                done, not_done = wait(future_to_url.keys(), return_when=FIRST_COMPLETED)
                for future in done:
                    new_links = future.result()
                    del future_to_url[future]
                    if new_links:
                        for link in new_links:
                            if not self.is_already_sniffed(link) and link not in self.visited_in_session:
                                future_to_url[executor.submit(self.hunt, link)] = link

def make_table(findings):
    table = Table(title="[bold red]🛡️ ALPHA SQUAD COORDINATOR 🛡️[/]", border_style="red")
    table.add_column("TIME", style="dim")
    table.add_column("TARGET", style="cyan")
    table.add_column("THREAT", style="bold white")
    table.add_column("LEVEL", justify="center")

    for f in findings[-6:]:
        style = "bold red" if f["level"] == "ULTRA" else "yellow"
        table.add_row(f["time"], f["url"], f["msg"], f"[{style}]{f['level']}[/]")
    return table

if __name__ == "__main__":
    target_site = "https://example.com" # هدف را اینجا بگذار
    squad = AlphaSquad([target_site])
    
    os.system('clear')
    console.print(Panel("[SQUAD ONLINE]\nManaging 5 dogs. Database Ready. Bug Fixed.", style="bold blue"))

    patrol_thread = threading.Thread(target=squad.run_squad)
    patrol_thread.daemon = True
    patrol_thread.start()

    with Live(make_table(squad.findings), refresh_per_second=1) as live:
        try:
            while True:
                live.update(make_table(squad.findings))
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold red] Returning to fortress. [/]")
