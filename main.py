import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TARGET_USER = os.environ.get("IG_USERNAME", "instagram")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

FILE_PATH = "follower_count.txt"

def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram Token veya Chat ID eksik!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram mesaj hatası: {e}")

def get_instagram_followers_rapidapi(username):
    if not RAPIDAPI_KEY:
        print("RapidAPI anahtarı bulunamadı!")
        return None

    # Seçtiğin RapidAPI servisinin URL ve Header yapılandırması
    url = f"https://instagram-data1.p.rapidapi.com/user/info"
    querystring = {"username": username}

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "instagram-data1.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Servisin döndürdüğü JSON yapısına göre takipçi alanını seçiyoruz
            return data.get("follower_count") or data.get("followers")
        else:
            print(f"RapidAPI Hata Kodu: {response.status_code}")
            return None
    except Exception as e:
        print(f"API isteği başarısız: {e}")
        return None

def main():
    print(f"Hedef hesap kontrol ediliyor: @{TARGET_USER}")
    current_followers = get_instagram_followers_rapidapi(TARGET_USER)
    
    if current_followers is None:
        print("❌ Takipçi verisi çekilemedi.")
        if not os.path.exists(FILE_PATH):
            with open(FILE_PATH, "w") as f:
                f.write("0")
        return

    old_followers = None
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            content = f.read().strip()
            if content.isdigit():
                old_followers = int(content)

    print(f"Eski Sayı: {old_followers} | Yeni Sayı: {current_followers}")

    if old_followers is None or old_followers == 0:
        message = f"🎉 **Sistem Aktif!**\n\n👤 **Hedef:** @{TARGET_USER}\n📊 **Başlangıç Takipçisi:** {current_followers:,}"
        send_telegram_message(message)
    elif current_followers != old_followers:
        diff = current_followers - old_followers
        change_text = f"+{diff}" if diff > 0 else f"{diff}"
        message = f"📢 **Takipçi Sayısı Değişti!**\n\n👤 **Hedef:** @{TARGET_USER}\n📊 **Yeni Takipçi:** {current_followers:,} ({change_text})"
        send_telegram_message(message)

    with open(FILE_PATH, "w") as f:
        f.write(str(current_followers))

if __name__ == "__main__":
    main()
