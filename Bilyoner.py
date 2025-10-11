import requests, re, os

def aktif_domain_bul():
    for i in range(1, 200):
        domain = f"https://bilyonersport{i}.com/"
        try:
            r = requests.get(domain, timeout=3)
            print(f"Trying {domain} - Status: {r.status_code}")
            if r.status_code == 200 and "channel-list" in r.text:
                print(f"Active domain found: {domain}")
                return domain
        except Exception as e:
            print(f"Failed to reach {domain} - Error: {e}")
    print("No active domain found.")
    return None

def kanallari_cek(domain):
    r = requests.get(domain, timeout=5)
    html = r.text
    hrefs = re.findall(r'href="([^"]+index\.m3u8[^"]*)"', html)
    names = re.findall(r'<div class="channel-name">(.*?)</div>', html)

    if not hrefs or not names:
        print("No channels found.")
        return []

    kanallar = []
    for name, link in zip(names, hrefs):
        kanallar.append((name.strip(), link.strip()))
    return kanallar

def m3u_olustur(kanallar, referer):
    os.makedirs("output", exist_ok=True)
    path = os.path.join("output", "bilyoner_kanallar.m3u")
    with open(path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, url in kanallar:
            f.write(f'#EXTINF:-1 tvg-name="{name}" group-title="BilyonerSport",{name}\n')
            f.write(f'#EXTVLCOPT:http-referrer={referer}\n')
            f.write(f"{url}\n\n")
    print(f"M3U file saved: {path}, total channels: {len(kanallar)}")

aktif = aktif_domain_bul()
if aktif:
    kanallar = kanallari_cek(aktif)
    if kanallar:
        m3u_olustur(kanallar, aktif)
    else:
        print("No channels found.")
else:
    print("No active domain found.")
