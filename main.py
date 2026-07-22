import os
import requests
import instaloader

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TARGET_USER = os.environ.get("IG_USERNAME", "instagram")

FILE_PATH = "follower_count.txt"

def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram Token veya Chat ID eksik!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram mesaj hatası: {e}")

def get_instagram_followers(username):
    L = instaloader.Instaloader()
    # Tarayıcı gibi görünmek için User-Agent ekliyoruz
    L.context._session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        return profile.followers
    except Exception as e:
        print(f"Instagram hatası ({username}): {e}")
        return None

def main():
    print(f"Hedef hesap kontrol ediliyor: {TARGET_USER}")
    current_followers = get_instagram_followers(TARGET_USER)
    
    # Instagram veriyi engellediyse Telegram'a haber ver
    if current_followers is None:
        error_msg = f"⚠️ **Instagram Takip Sıkıntısı**\n\n@{TARGET_USER} hesabının takipçi sayısı Instagram engelinden (Rate Limit) dolayı çekilemedi. Bir sonraki periyotta tekrar denenecek."
        send_telegram_message(error_msg)
        
        # Git hatası almamak için dosya yoksa varsayılan dosya oluştur
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

    # İlk başarılı çalıştırma
    if old_followers is None or old_followers == 0:
        message = f"🔔 **Takipçi Takip Sistemi Aktif!**\n\n👤 Hedef: @{TARGET_USER}\n📊 Başlangıç Takipçisi: {current_followers}"
        send_telegram_message(message)
    # Takipçi sayısı değiştiyse
    elif current_followers != old_followers:
        diff = current_followers - old_followers
        change_text = f"+{diff}" if diff > 0 else f"{diff}"
        message = f"📢 **Takipçi Sayısı Değişti!**\n\n👤 Hedef: @{TARGET_USER}\n📊 Yeni Takipçi: {current_followers} ({change_text})"
        send_telegram_message(message)

    with open(FILE_PATH, "w") as f:
        f.write(str(current_followers))

if __name__ == "__main__":
    main()
