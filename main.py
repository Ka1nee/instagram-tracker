import os
import requests
import json

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TARGET_USER = os.environ.get("IG_USERNAME", "instagram")

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

def get_instagram_followers(username):
    # Public profil verisini çekmek için alternatif endpoint
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "X-IG-App-ID": "936619743392459"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data["data"]["user"]["edge_followed_by"]["count"]
        else:
            print(f"HTTP Hata Kodu: {response.status_code}")
            return None
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return None

def main():
    print(f"Hedef hesap kontrol ediliyor: @{TARGET_USER}")
    current_followers = get_instagram_followers(TARGET_USER)
    
    if current_followers is None:
        print("❌ Instagram verisi anlık olarak çekilemedi. Bir sonraki periyot bekleniyor.")
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

    # İlk başarılı kurulum mesajı
    if old_followers is None or old_followers == 0:
        message = f"🎉 **Sistem Tamamen Hazır!**\n\n👤 **Hedef:** @{TARGET_USER}\n📊 **Başlangıç Takipçisi:** {current_followers:,}"
        send_telegram_message(message)
    # Takipçi sayısı değiştiyse bildirim gönder
    elif current_followers != old_followers:
        diff = current_followers - old_followers
        change_text = f"+{diff}" if diff > 0 else f"{diff}"
        message = f"📢 **Takipçi Sayısı Değişti!**\n\n👤 **Hedef:** @{TARGET_USER}\n📊 **Yeni Takipçi:** {current_followers:,} ({change_text})"
        send_telegram_message(message)
    else:
        print("Takipçi sayısında değişiklik yok.")

    # Güncel sayıyı kaydet
    with open(FILE_PATH, "w") as f:
        f.write(str(current_followers))

if __name__ == "__main__":
    main()
