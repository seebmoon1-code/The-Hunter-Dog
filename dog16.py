import requests
from bs4 import BeautifulSoup
import time
import random

# A dynamic list of sources
SOURCES = [
    "https://openphish.com/feed.txt",
    "https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/phishing-links-ACTIVE.txt"
]

def immortal_dog():
    session = requests.Session()
    # A list of different 'masks' (User-Agents) for the dog
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Firefox/120.0',
        'Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0'
    ]

    print("--- THE IMMORTAL DOG IS UNLEASHED ---")
    
    while True: # This loop never ends
        random.shuffle(SOURCES) # Mix the sources to confuse guards
        
        for url in SOURCES:
            # Change mask for every site
            session.headers.update({'User-Agent': random.choice(user_agents)})
            
            print(f"\n[SIGNAL] Dog is patrolling: {url}")
            try:
                response = session.get(url, timeout=15)
                
                if response.status_code == 200:
                    # Save findings to a 'trophy' file
                    with open("caught_scams.txt", "a") as f:
                        if url.endswith('.txt'):
                            new_scams = response.text.split('\n')[:20]
                            for scam in new_scams:
                                if scam:
                                    print(f"!!! BARK !!! Scammer Spotted: {scam}")
                                    f.write(f"{scam}\n")
                else:
                    print(f"[SIGNAL] Guarded: {response.status_code}. Dog is sneaking around...")
                
            except Exception as e:
                print(f"[ERROR] Dog is tired, resting 10 seconds...")
                time.sleep(10)

        # IMPORTANT: This is the heartbeat. 
        # The dog rests for a bit so your phone doesn't explode.
        print("\n[HEARTBEAT] Dog is taking a quick breath before next round...")
        time.sleep(30) 

if __name__ == "__main__":
    immortal_dog()
