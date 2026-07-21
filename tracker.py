import os

print("Instagram Tracker başlatıldı")

IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not IG_USERNAME:
    raise Exception("IG_USERNAME bulunamadı")

if not IG_PASSWORD:
    raise Exception("IG_PASSWORD bulunamadı")

if not TELEGRAM_TOKEN:
    raise Exception("TELEGRAM_TOKEN bulunamadı")

if not TELEGRAM_CHAT_ID:
    raise Exception("TELEGRAM_CHAT_ID bulunamadı")

print("Bütün secretlar başarıyla okundu")
