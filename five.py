import requests
import os

# این سگ فقط دنبال بوهای خاص (فایل‌های حساس) می‌گردد
SENSITIVE_SCENTS = [
    "/.env", "/.git/config", "/config.php", 
    "/wp-config.php", "/admin/config.json", "/backup.sql"
]

def drug_sniffer(base_url):
    print(f"--- سگ موادیاب رها شد در: {base_url} ---")
    for scent in SENSITIVE_SCENTS:
        url = base_url.rstrip('/') + scent
        try:
            print(f"[*] در حال بو کشیدن بوی: {scent}", end='\r')
            res = requests.get(url, timeout=5)
            
            # اگر فایل وجود داشت و حجمش زیاد بود، یعنی دزدها به گنج رسیدن!
            if res.status_code == 200 and len(res.content) > 0:
                msg = f"پیدا شد! فایل حساس لو رفته: {scent}"
                print(f"\n[!!!] WOOF! {msg}")
                
                # لرزش گوشی برای خبردار کردن فرمانده
                os.system("termux-vibrate -d 2000")
                os.system(f"termux-notification -t 'گنج پیدا شد!' -c '{scent}'")
                
                with open("treasure_found.txt", "a") as f:
                    f.write(f"URL: {url}\n")
        except:
            continue

if __name__ == "__main__":
    drug_sniffer("https://www.google.com")
