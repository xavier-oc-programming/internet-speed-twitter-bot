"""
original/main.py — Internet Speed Twitter Complaint Bot (Day 51)

Flow:
1. Kill all Chrome.
2. Launch Chrome with remote debugging.
3. Attach with Selenium and run M-Lab speed test.
4. Extract download / upload.
5. Build complaint tweet from measured vs promised.
6. Attach again (same debugger) with the Twitter logic.
7. Paste complaint into Twitter home box and click Post.
"""

import os
import time
import subprocess
import selenium
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------------------------------------------
# GLOBAL CONFIG
# -------------------------------------------------
DEBUGGER_PORT = 9222
DEBUGGER_ADDRESS = f"127.0.0.1:{DEBUGGER_PORT}"
USER_DATA_DIR = os.path.expanduser("~/selenium_debug_profile")
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

M_LAB_URL = "https://speed.measurementlab.net/#/"
TWITTER_HOME = "https://twitter.com/home"
CHECK_LOGIN_SELECTOR = "//a[@href='/home' or @href='/i/flow/home']"

# Your plan
PROMISED_DOWN = 150
PROMISED_UP = 10

# Twitter XPaths (your inspected ones)
TWEET_BOX_XPATH = (
    "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/"
    "div[2]/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/"
    "div/div/div[1]/div/div/div/div/div/div[2]/div"
)
POST_BUTTON_XPATH = (
    "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/"
    "div[2]/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div/div/button"
)

REQUIRED_SELENIUM = (4, 25)


# -------------------------------------------------
# UTILITIES
# -------------------------------------------------
def kill_existing_chrome():
    """Kill Chrome and chromedriver so we can start ours clean."""
    print("Terminating all existing Chrome processes...")
    subprocess.run(["pkill", "-9", "Google Chrome"], check=False)
    subprocess.run(["pkill", "-9", "chromedriver"], check=False)
    time.sleep(1)
    print("Chrome processes terminated.")


def launch_chrome_debugger():
    """Launch Chrome with remote debugging enabled, using our profile dir."""
    print("Launching Chrome with remote debugging...")
    os.makedirs(USER_DATA_DIR, exist_ok=True)

    subprocess.Popen(
        [
            CHROME_PATH,
            f"--remote-debugging-port={DEBUGGER_PORT}",
            f"--user-data-dir={USER_DATA_DIR}",
            "--profile-directory=Default",
            "--no-first-run",
            "--no-default-browser-check",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)
    print(f"Chrome launched at {DEBUGGER_ADDRESS}")


# -------------------------------------------------
# PART 1: M-LAB BOT
# -------------------------------------------------
class InternetSpeedTester:
    """Just the speed-test part."""

    def __init__(self, debugger_address=DEBUGGER_ADDRESS):
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.down = 0.0
        self.up = 0.0

    def get_internet_speed(self):
        print("Opening M-Lab speed test...")
        self.driver.get(M_LAB_URL)
        time.sleep(3)

        # Accept
        try:
            consent_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "demo-human"))
            )
            self.driver.execute_script("arguments[0].click();", consent_input)
            print("Consent checkbox clicked.")
        except Exception as e:
            print(f"Could not click consent checkbox: {e}")

        # Begin
        try:
            begin_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.startButton"))
            )
            begin_button.click()
            print("BEGIN button clicked — test running.")
        except Exception as e:
            print(f"Could not click BEGIN button: {e}")

        # Wait for results (use the working 180s pattern)
        print("Waiting for 'Results' section to appear (up to 180 seconds)...")
        try:
            WebDriverWait(self.driver, 180).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//span[contains(text(), 'Results')]")
                )
            )
            print("Results section is visible. Waiting 6 seconds for table to render...")
            time.sleep(6)
        except Exception:
            print("Timed out waiting for the 'Results' section.")
            return

        # Extract
        try:
            download_cell = self.driver.find_element(
                By.XPATH,
                '//*[@id="measurementSpace"]/div[2]/table/tbody/tr[3]/td[3]/strong',
            )
            upload_cell = self.driver.find_element(
                By.XPATH,
                '//*[@id="measurementSpace"]/div[2]/table/tbody/tr[4]/td[3]/strong',
            )

            download_text = download_cell.text.strip()
            upload_text = upload_cell.text.strip()

            self.down = float(download_text.split()[0])
            self.up = float(upload_text.split()[0])

            print(f"Download: {self.down} Mb/s")
            print(f"Upload:   {self.up} Mb/s")

        except Exception as e:
            print(f"Primary extraction failed: {e}")
            try:
                download_el = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="measurementSpace"]/div[2]/table/tbody/tr[3]/td[3]/strong',
                )
                upload_el = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="measurementSpace"]/div[2]/table/tbody/tr[4]/td[3]/strong',
                )
                self.down = float(download_el.text.split()[0])
                self.up = float(upload_el.text.split()[0])
                print(f"Download (fallback): {self.down} Mb/s")
                print(f"Upload (fallback):   {self.up} Mb/s")
            except Exception as e2:
                print(f"Could not extract speed results by any method: {e2}")

    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass


# -------------------------------------------------
# PART 2: TWITTER BOT
# -------------------------------------------------
class TwitterAttachedBot:
    def __init__(self, debugger_address=DEBUGGER_ADDRESS, wait_sec=15):
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, wait_sec)

    def is_logged_in(self) -> bool:
        try:
            self.driver.get(TWITTER_HOME)
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, CHECK_LOGIN_SELECTOR))
            )
            return True
        except Exception:
            return False

    def wait_for_manual_login(self):
        print("\nLog in to Twitter in the attached Chrome window.")
        print("Press Enter here when https://twitter.com/home is loaded.")
        input()

    def post_tweet(self, text: str) -> bool:
        try:
            print("Opening Twitter home page...")
            self.driver.get(TWITTER_HOME)

            tweet_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, TWEET_BOX_XPATH))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tweet_box)
            tweet_box.click()
            time.sleep(0.5)

            # clipboard + paste
            pyperclip.copy(text)
            tweet_box.send_keys(Keys.COMMAND, "v")
            print("Clipboard text pasted.")
            time.sleep(1.2)

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
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    # check selenium version
    ver = tuple(map(int, selenium.__version__.split(".")[:2]))
    if ver < REQUIRED_SELENIUM:
        raise RuntimeError("Update selenium: pip install -U selenium")

    # 1) clean start
    kill_existing_chrome()
    launch_chrome_debugger()

    # 2) run speed test
    speed_bot = InternetSpeedTester()
    speed_bot.get_internet_speed()

    # build complaint from measured speeds
    complaint = (
        f"Hey Internet Provider, why is my internet speed {speed_bot.down}down/{speed_bot.up}up "
        f"when I pay for {PROMISED_DOWN}down/{PROMISED_UP}up?"
    )
    print("Complaint to post:")
    print(complaint)

    # 3) post to twitter using remote debug approach
    twitter_bot = TwitterAttachedBot()
    if not twitter_bot.is_logged_in():
        print("Not logged in or home did not load.")
        twitter_bot.wait_for_manual_login()
        if not twitter_bot.is_logged_in():
            print("Still not logged in. Exiting.")
            twitter_bot.close()
            speed_bot.close()
            raise SystemExit(1)

    twitter_bot.post_tweet(complaint)

    # 4) clean up
    twitter_bot.close()
    speed_bot.close()
