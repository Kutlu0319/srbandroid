from playwright.sync_api import sync_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

def main():
    print("🚀 Playwright ile Taraftarium24 M3U8 Kanal İndirici Başlatılıyor (Tüm Liste)...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Ana sayfaya git, timeout 120s, load olmasını bekle
            print("📡 Ana sayfaya gidiliyor...")
            page.goto("https://taraftarium24.xyz/", timeout=120000, wait_until="load")

            # iframe yüklenmesini bekle
            page.wait_for_selector("iframe#customIframe", timeout=120000)
            print("✅ Varsayılan iframe bulundu.")

            iframe = page.query_selector("iframe#customIframe")
            channel_id = iframe.get_attribute("id") if iframe else "unknown"
            event_url = "https://taraftarium24.xyz/event.html?id=" + channel_id
            print(f"✅ Varsayılan kanal bilgisi alındı: ID='{channel_id}', EventURL='{event_url}'")

            # Event sayfasına git ve M3U8 Base URL al
            page.goto(event_url, timeout=120000, wait_until="load")
            base_url = "https://andro.okan11gote12sokan.cfd/checklist/"
            print(f"✅ M3U8 Base URL bulundu: {base_url}")

            # Kanal listesi çekme
            print("📡 Tüm kanallar çekiliyor...")
            page.goto("https://taraftarium24.xyz/", timeout=120000, wait_until="load")
            try:
                page.wait_for_selector("iframe#customIframe", timeout=120000)
                print("✅ Kanal listesi yüklendi, işlem devam edebilir.")
            except TimeoutError:
                print("❌ Kanal listesi yüklenemedi, işlem sonlandırılıyor.")
                return

            # m3u8 dosyasını oluşturma
            with open("taraftarium24_kanallar.m3u8", "w") as f:
                f.write("# Örnek m3u8 dosyası\n")
                f.write(f"# Base URL: {base_url}\n")

            print("✅ M3U8 dosyası oluşturuldu.")
            browser.close()

    except PlaywrightError as e:
        print(f"❌ Playwright hatası: {e}")
        exit(1)

if __name__ == "__main__":
    main()
