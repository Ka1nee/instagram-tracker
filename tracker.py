import os
import json
import requests
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("USERNAME =", repr(USERNAME))
print("PASSWORD =", repr(PASSWORD))
print("TOKEN =", "OK" if TELEGRAM_TOKEN else None)
print("CHAT =", repr(CHAT_ID))

TARGET_USERNAME = "aycuccee"

STATE_FILE = "state.json"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )


def load_state():
    if not os.path.exists(STATE_FILE):
        return None

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)


def login(page):
    def login(page):
    page.goto(
        "https://www.instagram.com/accounts/login/",
        wait_until="networkidle"
    )

    page.screenshot(path="login.png")

    print(page.content())
    print(page.title())
    print(page.url)

    page.get_by_placeholder("Mobile number, username or email").fill(USERNAME)
    page.get_by_placeholder("Password").fill(PASSWORD)
    page.get_by_role("button", name="Log in").click()

    page.wait_for_timeout(8000)
    
def get_profile(page):
    page.goto(
        f"https://www.instagram.com/{TARGET_USERNAME}/",
        wait_until="networkidle"
    )
    page.wait_for_timeout(5000)
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

        except:
            pass

    if followers is None or following is None:
        raise Exception("Takipçi veya takip sayısı okunamadı")

    return {
        "followers": int(followers),
        "following": int(following)
    }


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
            f"""✅ İlk kayıt oluşturuldu

Takipçi: {current['followers']}
Takip: {current['following']}"""
        )

    else:

        if previous != current:

            send_telegram(
                f"""🚨 Değişiklik tespit edildi

Takipçi
{previous['followers']} ➜ {current['followers']}

Takip
{previous['following']} ➜ {current['following']}"""
            )

            save_state(current)

    browser.close()
