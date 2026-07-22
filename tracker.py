import os
import json
import requests
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("USERNAME =", repr(USERNAME))
print("PASSWORD =", "OK" if PASSWORD else None)
print("TOKEN =", "OK" if TELEGRAM_TOKEN else None)
print("CHAT =", repr(CHAT_ID))

TARGET_USERNAME = "aycuccee"
STATE_FILE = "state.json"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})


def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)


def dismiss_cookie_banner(page):
    # Instagram bazı bölgelerde çerez onay ekranı gösteriyor, varsa kapat
    for text in ["Allow all cookies", "Only allow essential cookies", "Accept All", "Kabul et"]:
        try:
            btn = page.get_by_role("button", name=text)
            if btn.is_visible(timeout=3000):
                btn.click()
                page.wait_for_timeout(1000)
                return
        except Exception:
            pass


def login(page):
    page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
    dismiss_cookie_banner(page)
    page.screenshot(path="login.png")
    print("PAGE TITLE:", page.title())
    print("PAGE URL:", page.url)

    # placeholder yerine name attribute'una göre seç (daha sağlam)
    page.wait_for_selector('input[name="username"]', timeout=30000)
    page.locator('input[name="username"]').fill(USERNAME)
    page.locator('input[name="password"]').fill(PASSWORD)
    page.screenshot(path="before_login_click.png")
    page.get_by_role("button", name="Log in", exact=False).click()
    page.wait_for_timeout(8000)
    page.screenshot(path="after_login.png")
    print("AFTER LOGIN URL:", page.url)


def get_profile(page):
    page.goto(f"https://www.instagram.com/{TARGET_USERNAME}/", wait_until="networkidle")
    page.wait_for_timeout(5000)
    page.screenshot(path="profile.png")


def get_counts(page):
    followers = None
    following = None
    links = page.locator("a")
    for i in range(links.count()):
        try:
            text = links.nth(i).inner_text().lower()
            if "followers" in text or "takipçi" in text:
                followers = "".join(c for c in text if c.isdigit())
            if "following" in text or "takip" in text:
                following = "".join(c for c in text if c.isdigit())
        except Exception:
            pass
    if not followers or not following:
        raise Exception("Takipçi veya takip sayısı okunamadı")
    return {"followers": int(followers), "following": int(following)}


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    login(page)
    get_profile(page)
    current = get_counts(page)
    previous = load_state()

    if previous is None:
        save_state(current)
        send_telegram(
            f"✅ İlk kayıt oluşturuldu\nTakipçi: {current['followers']}\nTakip: {current['following']}"
        )
    else:
        if previous != current:
            send_telegram(
                f"🚨 Değişiklik tespit edildi\n"
                f"Takipçi\n{previous['followers']} ➜ {current['followers']}\n"
                f"Takip\n{previous['following']} ➜ {current['following']}"
            )
            save_state(current)

    browser.close()
