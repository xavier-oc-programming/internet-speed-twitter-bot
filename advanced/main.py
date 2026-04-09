import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

import config
from bot import InternetSpeedTwitterBot


def main():
    profile_dir = (Path(__file__).parent.parent / config.CHROME_PROFILE_DIR).resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)

    bot = InternetSpeedTwitterBot(profile_dir)

    try:
        # ── Step 1: measure speed ──────────────────────────────────────────────
        try:
            bot.get_internet_speed()
        except RuntimeError as exc:
            print(f"Speed test failed: {exc}")
            return

        print(f"\nResults: {bot.down} Mb/s down  /  {bot.up} Mb/s up")
        print(f"Promised: {config.PROMISED_DOWN} Mb/s down  /  {config.PROMISED_UP} Mb/s up")

        # ── Step 2: check against promised speeds ──────────────────────────────
        if bot.down >= config.PROMISED_DOWN and bot.up >= config.PROMISED_UP:
            print("Speeds are at or above promised thresholds — no tweet needed.")
            return

        complaint = config.COMPLAINT_TEMPLATE.format(
            down=bot.down,
            up=bot.up,
            promised_down=config.PROMISED_DOWN,
            promised_up=config.PROMISED_UP,
        )
        print(f"\nComplaint: {complaint}")

        # ── Step 3: check Twitter login ────────────────────────────────────────
        if not bot.is_logged_in_to_twitter():
            twitter_user = os.getenv("TWITTER_USERNAME", "")
            twitter_pass = os.getenv("TWITTER_PASSWORD", "")

            if twitter_user and twitter_pass:
                print("\nNot logged in — attempting automated login...")
                try:
                    bot.login(twitter_user, twitter_pass)
                except Exception as exc:
                    print(f"Automated login failed: {exc}")

            if not bot.is_logged_in_to_twitter():
                print("\nNot logged in to Twitter/X (automated login failed or no credentials).")
                print("Log in manually in the Chrome window, then press Enter here.")
                input("Press Enter when logged in: ")
                if not bot.is_logged_in_to_twitter():
                    print("Login still not detected. Exiting without tweeting.")
                    return

        # ── Step 4: post tweet ─────────────────────────────────────────────────
        success = bot.tweet_at_provider(complaint)
        if not success:
            print("Tweet could not be posted. Check XPaths in config.py.")

    finally:
        bot.quit()


if __name__ == "__main__":
    main()
