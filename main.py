import os
import requests
import instaloader

# GitHub Secrets veya Çevre Değişkenlerinden (Environment Variables) bilgileri alıyoruz
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TARGET_USER = os.environ.get("INSTAGRAM_USER", "instagram") # Varsayılan: instagram hesabı

FILE_PATH = "follower_count.txt"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Telegram mesaj hatası: {e}")
        return None

def get_instagram_followers(username):
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        return profile.followers
    except Exception as e:
        print(f"Instagram verisi çekilemedi: {e}")
        return None

def main():
    current_followers = get_instagram_followers(TARGET_USER)
    
    if current_followers is None:
        print("Takipçi sayısı alınamadı, işlem atlanıyor.")
        return

    # Önceki kaydedilmiş takipçi sayısını oku
    old_followers = None
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            content = f.read().strip()
            if content.isdigit():
                old_followers = int(content)

    print(f"Eski Sayı: {old_followers} | Yeni Sayı: {current_followers}")

    # İlk defa çalışıyorsa veya sayı değiştiyse Telegram mesajı at
    if old_followers is None:
        message = f"🔔 Takipçi takip sistemi başlatıldı!\n\n👤 Hesabı: @{TARGET_USER}\n📊 Mevcut Takipçi: {current_followers}"
        send_telegram_message(message)
    elif current_followers != old_followers:
        diff = current_followers - old_followers
        change_text = f"+{diff}" if diff > 0 else f"{diff}"
        message = f"📢 Takipçi Sayısı Değişti!\n\n👤 Hesabı: @{TARGET_USER}\n📊 Yeni Takipçi: {current_followers} ({change_text})"
        send_telegram_message(message)

    # Yeni sayıyı dosyaya kaydet
    with open(FILE_PATH, "w") as f:
        f.write(str(current_followers))

if __name__ == "__main__":
    main()
