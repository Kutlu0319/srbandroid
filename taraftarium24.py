from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

def main():
    print("🚀 Taraftarium24 M3U8 Kanal İndirici Başlatılıyor...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Ana sayfaya git
            page.goto("https://taraftarium24.xyz/", timeout=180000, wait_until="load")
            page.wait_for_selector("iframe#customIframe", timeout=180000)
            print("✅ iframe bulundu.")

            iframe = page.query_selector("iframe#customIframe")
            frame = iframe.content_frame()
            if not frame:
                print("❌ iframe içeriği alınamadı.")
                return

            # Kanal elemanlarını seç (örnek selector, sitenin yapısına göre değişebilir)
            channels = frame.query_selector_all("div.channel-item")
            if not channels:
                print("❌ Hiç kanal bulunamadı.")
                return

            # m3u8 dosyasını oluştur
            with open("taraftarium24_kanallar.m3u8", "w") as f:
                f.write("#EXTM3U\n")
                for ch in channels:
                    name = ch.inner_text().strip()
                    url = ch.get_attribute("data-m3u8")  # örnek attribute
                    if name and url:
                        f.write(f"#EXTINF:-1,{name}\n{url}\n")

            print(f"✅ {len(channels)} kanal ile m3u8 dosyası oluşturuldu.")
            browser.close()

    except PlaywrightTimeoutError:
        print("❌ Timeout hatası, işlem sonlandırıldı.")
    except PlaywrightError as e:
        print(f"❌ Playwright hatası: {e}")
        exit(1)

if __name__ == "__main__":
    main()
