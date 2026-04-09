"""
06_twitter_only.py — Final Version (Clipboard Auto-Post)

Flow:
1. Attach to Chrome already running with --remote-debugging-port=9222
2. Go to Twitter home
3. Focus tweet box
4. Paste clipboard text (Command + V)
5. Automatically click Post button once enabled
"""

import time
import selenium
import pyperclip  # pip install pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------
DEBUGGER_ADDRESS = "127.0.0.1:9222"
HOME_URL = "https://twitter.com/home"
CHECK_LOGIN_SELECTOR = "//a[@href='/home' or @href='/i/flow/home']"

# The tweet text
TEST_TWEET = "Automated tweet posted directly after clipboard paste (Day 51)."

# Your provided XPaths
TWEET_BOX_XPATH = (
    "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/"
    "div[2]/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/"
    "div/div/div[1]/div/div/div/div/div/div[2]/div"
)
POST_BUTTON_XPATH = (
    "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/"
    "div[2]/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div/div/button"
)


# -------------------------------------------------
# TWITTER BOT CLASS
# -------------------------------------------------
class TwitterAttachedBot:
    def __init__(self, debugger_address=DEBUGGER_ADDRESS, wait_sec=15):
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, wait_sec)

    def is_logged_in(self) -> bool:
        """Check if Twitter home is accessible."""
        try:
            self.driver.get(HOME_URL)
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, CHECK_LOGIN_SELECTOR))
            )
            return True
        except Exception:
            return False

    def wait_for_manual_login(self):
        """Prompt user to manually log in (only needed first time)."""
        print("\nLog in to Twitter in the attached Chrome window.")
        print("Press Enter here when https://twitter.com/home is loaded.")
        input()

    def post_tweet(self, text: str) -> bool:
        """Paste clipboard text and click the Post button automatically."""
        try:
            print("Opening Twitter home page...")
            self.driver.get(HOME_URL)

            tweet_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, TWEET_BOX_XPATH))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tweet_box)
            tweet_box.click()
            time.sleep(0.5)

            # Copy and paste clipboard text
            pyperclip.copy(text)
            tweet_box.send_keys(Keys.COMMAND, "v")
            print("Clipboard text pasted.")
            time.sleep(1.2)

            # Click Post button
            post_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, POST_BUTTON_XPATH))
            )
            post_btn.click()
            print("Post button clicked. Waiting briefly for confirmation...")
            time.sleep(2)

            print("Tweet posted successfully.")
            return True

        except Exception as e:
            print(f"Error while posting tweet: {e}")
            return False

    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass


# -------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------
if __name__ == "__main__":
    print(f"Selenium version {selenium.__version__} detected.")
    print(f"Attaching to Chrome debugger at {DEBUGGER_ADDRESS} ...")

    bot = TwitterAttachedBot()

    if not bot.is_logged_in():
        print("Not logged in or home did not load.")
        bot.wait_for_manual_login()
        if not bot.is_logged_in():
            print("Still not logged in. Exiting.")
            bot.close()
            raise SystemExit(1)

    print("Login detected. Posting tweet automatically...")
    bot.post_tweet(TEST_TWEET)

    bot.close()