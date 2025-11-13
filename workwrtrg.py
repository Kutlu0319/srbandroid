import requests
import re
import sys

# Terminal renkleri
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Kanallar listesi (sizin orijinal liste)
KANALLAR = [
    {"dosya": "yayinzirve.m3u8", "tvg_id": "BeinSports1.tr", "kanal_adi": "Bein Sports 1 HD (VIP)"},
    {"dosya": "yayin1.m3u8", "tvg_id": "BeinSports1.tr", "kanal_adi": "Bein Sports 1 HD"},
    {"dosya": "yayinb2.m3u8", "tvg_id": "BeinSports2.tr", "kanal_adi": "Bein Sports 2 HD"},
    # ... diğer kanallar
]

# API URL
API_URL = "https://paneltrgool.corepanel.pro/api/verirepo.php"

def find_baseurl(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"{RED}[-] URL erişilemedi: {e}{RESET}")
        return None

    match = re.search(r'baseurl\s*[:=]\s*["\']([^"\']+)["\']', r.text)
    if match:
        return match.group(1)
    return None

def generate_m3u(base_url, referer, user_agent):
    lines = ["#EXTM3U"]
    for idx, k in enumerate(KANALLAR, start=1):
        name = k['kanal_adi']
        lines.append(f'#EXTINF:-1 tvg-id="{k["tvg_id"]}" tvg-name="{name}",{name}')
        lines.append(f'#EXTVLCOPT:http-user-agent={user_agent}')
        lines.append(f'#EXTVLCOPT:http-referrer={referer}')
        lines.append(base_url + k["dosya"])
        print(f"  ✔ {idx:02d}. {name}")
    return "\n".join(lines)

if __name__ == "__main__":
    print(f"{GREEN}[*] API üzerinden base URL alınıyor...{RESET}")
    base_url = find_baseurl(API_URL)
    if not base_url:
        print(f"{RED}[HATA] Base URL bulunamadı.{RESET}")
        sys.exit(1)

    playlist = generate_m3u(base_url, API_URL, "Mozilla/5.0")
    with open("workwrtrg.m3u", "w", encoding="utf-8") as f:
        f.write(playlist)

    print(f"{GREEN}[OK] Playlist oluşturuldu: trgoalas.m3u{RESET}")
