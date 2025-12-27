import requests
import re
import json

HEADERS = {"User-Agent": "Mozilla/5.0"}

CHANNELS = [
    {"id": "bein1", "source_id": "selcukbeinsports1", "name": "BeIN Sports 1", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "bein1_obs", "source_id": "selcukobs1", "name": "BeIN Sports 1", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "bein2", "source_id": "selcukbeinsports2", "name": "BeIN Sports 2", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "bein3", "source_id": "selcukbeinsports3", "name": "BeIN Sports 3", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "bein4", "source_id": "selcukbeinsports4", "name": "BeIN Sports 4", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "bein5", "source_id": "selcukbeinsports5", "name": "BeIN Sports 5", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "beinmax1", "source_id": "selcukbeinsportsmax1", "name": "BeIN Sports Max 1", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "beinmax2", "source_id": "selcukbeinsportsmax2", "name": "BeIN Sports Max 2", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "tivibu1", "source_id": "selcuktivibuspor1", "name": "Tivibu Spor 1", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "tivibu2", "source_id": "selcuktivibuspor2", "name": "Tivibu Spor 2", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "tivibu3", "source_id": "selcuktivibuspor3", "name": "Tivibu Spor 3", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "tivibu4", "source_id": "selcuktivibuspor4", "name": "Tivibu Spor 4", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "ssport1", "source_id": "selcukssport", "name": "S Sport 1", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "ssport2", "source_id": "selcukssport2", "name": "S Sport 2", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "smart1", "source_id": "selcuksmartspor", "name": "Smart Spor 1", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "smart2", "source_id": "selcuksmartspor2", "name": "Smart Spor 2", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "aspor", "source_id": "selcukaspor", "name": "A Spor", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "eurosport1", "source_id": "selcukeurosport1", "name": "Eurosport 1", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
    {"id": "eurosport2", "source_id": "selcukeurosport2", "name": "Eurosport 2", "logo": "https://i.hizliresim.com/2noijky.jpg", "group": "Spor"},
]

def get_active_site():
    entry_url = "https://www.selcuksportshd78.is/"
    try:
        entry_source = requests.get(entry_url, headers=HEADERS, timeout=5).text
        match = re.search(r'url=(https:\/\/[^"]+)', entry_source)
        if match:
            print(f"Aktif site: {match.group(1)}")
            return match.group(1)
        else:
            print("Aktif site bulunamadı.")
            return None
    except requests.RequestException as e:
        print("Giriş URL'sine erişilemedi:", e)
        return None

def get_base_url(active_site):
    try:
        source = requests.get(active_site, headers=HEADERS, timeout=5).text
        match = re.search(r'https:\/\/[^"]+\/index\.php\?id=selcuk[a-z0-9]+', source)
        if match:
            base_url = match.group(0).replace(match.group(0).split('id=')[-1], "")
            print(f"Base URL: {base_url}")
            return base_url
        else:
            print("Base URL bulunamadı.")
            return None
    except requests.RequestException as e:
        print("Aktif siteye erişilemedi:", e)
        return None

def fetch_streams(base_url):
    result = []
    for ch in CHANNELS:
        url = f"{base_url}{ch['source_id']}"
        try:
            source = requests.get(url, headers=HEADERS, timeout=5).text
            match = re.search(r'(https:\/\/[^\'"]+\/live\/[^\'"]+\/playlist\.m3u8)', source)
            if match:
                stream_url = match.group(1)
            else:
                match = re.search(r'(https:\/\/[^\'"]+\/live\/)', source)
                if match:
                    stream_url = f"{match.group(1)}{ch['source_id']}/playlist.m3u8"
                else:
                    continue
            stream_url = re.sub(r'[\'";].*$', '', stream_url).strip()
            if stream_url and re.match(r'^https?://', stream_url):
                print(f"{ch['name']} → {stream_url}")
                result.append((ch, stream_url))
        except requests.RequestException:
            continue
    return result

def generate_json(streams, filename="streams.json"):
    print(f"\nJSON dosyası yazılıyor: {filename}")

    data = []
    for ch, url in streams:
        data.append({
            "id": ch["id"],
            "name": ch["name"],
            "logo": ch["logo"],
            "group": ch["group"],
            "source_id": ch["source_id"],
            "stream_url": url
        })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("Tamamlandı. Kanal sayısı:", len(streams))

def main():
    active_site = get_active_site()
    if not active_site:
        return
    base_url = get_base_url(active_site)
    if not base_url:
        return
    streams = fetch_streams(base_url)
    if streams:
        generate_json(streams)
    else:
        print("Hiçbir yayın alınamadı.")

if __name__ == "__main__":
    main()
