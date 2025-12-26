import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

class NonStopHunter:
    def __init__(self, max_dogs=10):
        self.db_name = "alphalog_fortress.db"
        self.max_dogs = max_dogs
        self.visited_in_session = set()
        self._init_db()
        self.lock = threading.Lock()

    def _init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS global_registry (url_hash TEXT PRIMARY KEY, visit_time TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS hunts (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, target_url TEXT, threat_type TEXT, danger_level TEXT)')
        conn.commit()
        conn.close()

    def bark(self, msg, url):
        os.system("termux-vibrate -d 200")
        timestamp = time.strftime("%H:%M:%S")
        with self.lock:
            print(f"\n[!!!] {timestamp} - {msg} -> {url}")
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO hunts (timestamp, target_url, threat_type, danger_level) VALUES (?, ?, ?, ?)', 
                           (time.strftime("%Y-%m-%d %H:%M:%S"), url, msg, "ULTRA"))
            conn.commit()
            conn.close()

    def hunt(self, current_url):
        if current_url in self.visited_in_session: return []
        self.visited_in_session.add(current_url)
        
        try:
            # هویت سگ را جعل می‌کنیم تا سایت‌ها شک نکنند
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            print(f"[*] Sniffing: {current_url[:60]}", end="\r")
            
            res = requests.get(current_url, timeout=5, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            # پیدا کردن تله‌های دزدی
            if any(term in res.text.lower() for term in ["login", "password", "sign in"]):
                if soup.find('form'):
                    self.bark("PHISHING FOUND", current_url)

            # استخراج تمام لینک‌ها برای ادامه مسیر
            domain = urlparse(current_url).netloc
            links = []
            for a in soup.find_all('a', href=True):
                full_url = urljoin(current_url, a['href'])
                if urlparse(full_url).netloc == domain:
                    links.append(full_url)
            return links
        except: return []

    def start_patrol(self, initial_targets):
        if not initial_targets:
            print("\n[!] No targets found. Sniffing backup nodes...")
            initial_targets = ["https://www.bing.com", "https://duckduckgo.com"]

        with ThreadPoolExecutor(max_workers=self.max_dogs) as executor:
            future_to_url = {executor.submit(self.hunt, url): url for url in initial_targets}
            while future_to_url:
                done, _ = wait(future_to_url.keys(), return_when=FIRST_COMPLETED)
                for future in done:
                    new_links = future.result()
                    del future_to_url[future]
                    if new_links:
                        for link in new_links:
                            if link not in self.visited_in_session:
                                future_to_url[executor.submit(self.hunt, link)] = link

if __name__ == "__main__":
    os.system('clear')
    print("--- ALPHA DOG v5.1 : NON-STOP MODE ---")
    
    # اینجا چند سایت شروع‌کننده قوی بده که سگ متوقف نشود
    starter_pack = [
        "https://www.blockchain.com", 
        "https://www.binance.com",
        "https://coinmarketcap.com"
    ]
    
    hunter = NonStopHunter(max_dogs=12)
    print("[+] Releasing the pack. No sitting allowed.")
    hunter.start_patrol(starter_pack)
