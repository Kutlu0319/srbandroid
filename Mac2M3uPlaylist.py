import requests
import re
import sys
import os

def print_colored(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m",
    }
    print(f"{colors.get(color, '')}{text}\033[0m")

def get_token(session, base_url, mac):
    url = f"{base_url}/portal.php?action=handshake&type=stb&token=&JsHttpRequest=1-xml"
    headers = {"Authorization": f"MAC {mac}"}
    print_colored(f"Requesting token from: {url}", "cyan")
    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        token = data["js"]["token"]
        print_colored(f"Token received: {token}", "green")
        return token
    except Exception as e:
        print_colored(f"Token error: {e}", "red")
        return None

def get_subscription(session, base_url, token):
    url = f"{base_url}/portal.php?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
    headers = {"Authorization": f"Bearer {token}"}
    print_colored(f"Requesting subscription info from: {url}", "cyan")
    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        mac = data["js"]["mac"]
        expiry = data.get("js", {}).get("phone", "N/A")
        print_colored(f"MAC = {mac}\nExpiry = {expiry}", "green")
        return True
    except Exception as e:
        print_colored(f"Subscription error: {e}", "red")
        return False

def get_channel_list(session, base_url, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        url_genre = f"{base_url}/server/load.php?type=itv&action=get_genres&JsHttpRequest=1-xml"
        print_colored(f"Requesting genres from: {url_genre}", "cyan")
        res_genre = session.get(url_genre, headers=headers, timeout=10)
        res_genre.raise_for_status()
        genre_data = res_genre.json()["js"]
        group_info = {group["id"]: group["title"] for group in genre_data}

        url_channels = f"{base_url}/portal.php?type=itv&action=get_all_channels&JsHttpRequest=1-xml"
        print_colored(f"Requesting channels from: {url_channels}", "cyan")
        res_channels = session.get(url_channels, headers=headers, timeout=10)
        res_channels.raise_for_status()
        channels_data = res_channels.json()["js"]["data"]

        print_colored(f"Channels received: {len(channels_data)}", "green")
        return channels_data, group_info
    except Exception as e:
        print_colored(f"Channel list error: {e}", "red")
        return None, None

def save_channel_list(base_url, channels_data, group_info, mac):
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, "Mac2M3uPlaylist.m3u")
    count = 0
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for channel in channels_data:
                group_id = channel.get("tv_genre_id", "0")
                group_name = group_info.get(group_id, "General")
                name = channel.get("name", "Unknown Channel")
                logo = channel.get("logo", "")
                cmd_url_raw = channel.get("cmds", [{}])[0].get("url", "")
                cmd_url = cmd_url_raw.replace("ffmpeg ", "")
                if "localhost" in cmd_url:
                    m = re.search(r"/ch/(\d+)", cmd_url)
                    if m:
                        ch_id = m.group(1)
                        cmd_url = f"{base_url}/play/live.php?mac={mac}&stream={ch_id}&extension=ts"
                if not cmd_url:
                    continue
                f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_name}",{name}\n')
                f.write(cmd_url + "\n")
                count += 1
        print_colored(f"Total channels written: {count}", "green")
        print_colored(f"Playlist saved at: {filename}", "blue")
    except Exception as e:
        print_colored(f"Saving file error: {e}", "red")

def main():
    base_url = "http://saray68.darktv.nl/c"
    mac = "00:1A:79:04:0F:AD"

    session = requests.Session()
    session.cookies.update({"mac": mac})
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Referer": f"{base_url}/c/",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    })

    token = get_token(session, base_url, mac)
    if not token:
        print_colored("Failed to get token. Exiting.", "red")
        sys.exit(1)

    if not get_subscription(session, base_url, token):
        print_colored("Failed to get subscription info. Exiting.", "red")
        sys.exit(1)

    channels_data, group_info = get_channel_list(session, base_url, token)
    if not channels_data or not group_info:
        print_colored("Failed to get channels. Exiting.", "red")
        sys.exit(1)

    save_channel_list(base_url, channels_data, group_info, mac)

if __name__ == "__main__":
    main()
