"""
advanced/bot.py — InternetSpeedTwitterBot

Handles all browser automation:
  - Runs the M-Lab speed test and extracts download/upload speeds.
  - Posts a tweet on Twitter/X with the complaint message.

Uses undetected-chromedriver with a persistent Chrome profile so Twitter
session is preserved between runs (manual login only required once).
"""

import time
from pathlib import Path

import pyperclip
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config


class InternetSpeedTwitterBot:
    """
    Automates M-Lab speed testing and Twitter complaint posting.

    Attributes:
        down (float): Measured download speed in Mbps.
        up (float):   Measured upload speed in Mbps.
        driver:       undetected-chromedriver Chrome instance.
        wait:         WebDriverWait with global timeout.
    """

    def __init__(self, profile_dir: Path):
        self.down = 0.0
        self.up = 0.0
        self.driver = self._create_driver(profile_dir)
        self.wait = WebDriverWait(self.driver, config.WAIT_TIMEOUT)

    # ── Driver setup ──────────────────────────────────────────────────────────

    def _create_driver(self, profile_dir: Path) -> uc.Chrome:
        """Launch Chrome with persistent profile using undetected-chromedriver."""
        options = uc.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument(f"--user-data-dir={profile_dir}")
        return uc.Chrome(options=options, version_main=config.CHROME_VERSION)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _js_click(self, element) -> None:
        """Click an element via JS as fallback for intercepted clicks."""
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    # ── Speed test ────────────────────────────────────────────────────────────

    def get_internet_speed(self) -> None:
        """
        Open M-Lab, accept consent, run speed test, store results in self.down / self.up.
        Raises RuntimeError if results could not be extracted.
        """
        print("Opening M-Lab speed test...")
        self.driver.get(config.M_LAB_URL)
        time.sleep(3)

        # Accept data-sharing consent — try input click, then label click, then JS
        print("Looking for consent checkbox...")
        try:
            consent = self.wait.until(
                EC.presence_of_element_located((By.ID, config.MLAB_CONSENT_ID))
            )
            # Real .click() triggers React/Vue state; fall back to label click then JS
            try:
                consent.click()
            except Exception:
                try:
                    label = self.driver.find_element(
                        By.CSS_SELECTOR, f"label[for='{config.MLAB_CONSENT_ID}']"
                    )
                    label.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", consent)
            print("Consent checkbox accepted.")
            time.sleep(1)
        except TimeoutException:
            print("Consent checkbox not found — may already be accepted.")

        # Click BEGIN
        print("Looking for BEGIN button...")
        try:
            begin = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, config.MLAB_CSS_START))
            )
            self._js_click(begin)
            print("BEGIN clicked — speed test running.")
        except TimeoutException as exc:
            raise RuntimeError("BEGIN button not found — M-Lab layout may have changed.") from exc

        # Wait for resultsSection div to become visible (display: block)
        print(f"Waiting up to {config.WAIT_TIMEOUT_SPEED}s for results...")
        try:
            WebDriverWait(self.driver, config.WAIT_TIMEOUT_SPEED).until(
                EC.visibility_of_element_located((By.ID, "resultsSection"))
            )
            print(f"Results visible. Settling for {config.SPEED_TEST_SETTLE}s...")
            time.sleep(config.SPEED_TEST_SETTLE)
        except TimeoutException as exc:
            raise RuntimeError("Timed out waiting for M-Lab results.") from exc

        # Extract speeds
        try:
            dl = self.driver.find_element(By.XPATH, config.MLAB_XPATH_DOWNLOAD)
            ul = self.driver.find_element(By.XPATH, config.MLAB_XPATH_UPLOAD)
            self.down = float(dl.text.strip().split()[0])
            self.up = float(ul.text.strip().split()[0])
            print(f"Download: {self.down} Mb/s  |  Upload: {self.up} Mb/s")
        except Exception as exc:
            raise RuntimeError(
                f"Could not extract speed values — XPaths may need updating: {exc}"
            ) from exc

    # ── Twitter posting ───────────────────────────────────────────────────────

    def is_logged_in_to_twitter(self) -> bool:
        """Return True if the Twitter/X home timeline is accessible."""
        try:
            self.driver.get(config.TWITTER_HOME)
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, config.TWITTER_XPATH_CHECK_LOGIN)
                )
            )
            return True
        except TimeoutException:
            return False

    def login(self, username: str, password: str) -> None:
        """
        Automate Twitter/X login.
        Session is saved in the persistent Chrome profile — only runs when not already logged in.
        Falls back gracefully if blocked by CAPTCHA or 2FA (handled in main.py).
        """
        print("Navigating to Twitter/X login...")
        self.driver.get(config.TWITTER_LOGIN_URL)
        time.sleep(2)

        # Step 1 — enter username or email
        username_input = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, config.TWITTER_XPATH_USERNAME_INPUT)
            )
        )
        username_input.send_keys(username)
        time.sleep(0.5)
        next_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, config.TWITTER_XPATH_NEXT_BTN))
        )
        self._js_click(next_btn)
        time.sleep(1.5)

        # Step 2 — optional: X asks to confirm username when email was entered
        short_wait = WebDriverWait(self.driver, 5)
        try:
            confirm = short_wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, config.TWITTER_XPATH_USERNAME_CONFIRM)
                )
            )
            confirm.send_keys(username)
            next_btn2 = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, config.TWITTER_XPATH_NEXT_BTN))
            )
            self._js_click(next_btn2)
            time.sleep(1.5)
        except TimeoutException:
            pass  # no confirmation step needed

        # Step 3 — enter password
        password_input = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, config.TWITTER_XPATH_PASSWORD_INPUT)
            )
        )
        password_input.send_keys(password)
        time.sleep(0.5)
        login_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, config.TWITTER_XPATH_LOGIN_BTN))
        )
        self._js_click(login_btn)
        time.sleep(3)
        print("Login submitted.")

    def login_with_google(self, google_email: str) -> None:
        """
        Sign in to Twitter/X via Google OAuth.
        Handles both popup and same-tab redirect flows.
        Session saved in persistent profile — only runs when not already logged in.
        """
        print("Navigating to Twitter/X login...")
        self.driver.get(config.TWITTER_LOGIN_URL)
        time.sleep(2)

        # Click "Sign in with Google"
        google_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, config.TWITTER_XPATH_GOOGLE_BTN))
        )
        original_window = self.driver.current_window_handle
        self._js_click(google_btn)
        time.sleep(1.5)

        # Google OAuth may open in a new popup window or redirect in the same tab
        short_wait = WebDriverWait(self.driver, 6)
        try:
            short_wait.until(EC.number_of_windows_to_be(2))
            for handle in self.driver.window_handles:
                if handle != original_window:
                    self.driver.switch_to.window(handle)
                    break
            print("Switched to Google OAuth window.")
        except TimeoutException:
            pass  # same-tab redirect — already on Google page

        time.sleep(2)

        # Select the correct Google account from the picker
        account_xpath = config.GOOGLE_XPATH_ACCOUNT.replace("{email}", google_email)
        try:
            account = short_wait.until(
                EC.element_to_be_clickable((By.XPATH, account_xpath))
            )
            self._js_click(account)
            print(f"Selected Google account: {google_email}")
            time.sleep(2)
        except TimeoutException:
            print("Account picker not shown — may already be pre-selected.")

        # Handle "Continue" confirmation page if shown
        try:
            continue_btn = short_wait.until(
                EC.element_to_be_clickable((By.XPATH, config.GOOGLE_XPATH_CONTINUE))
            )
            self._js_click(continue_btn)
            print("Confirmed Google account.")
            time.sleep(2)
        except TimeoutException:
            pass

        # If Google opened a popup, switch back to the main X window
        if self.driver.current_window_handle != original_window:
            self.driver.switch_to.window(original_window)

        time.sleep(3)
        print("Google login submitted.")

    def tweet_at_provider(self, text: str) -> bool:
        """
        Post a tweet with the given text.
        Returns True on success, False on failure.
        """
        try:
            print("Navigating to Twitter home...")
            self.driver.get(config.TWITTER_HOME)

            tweet_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, config.TWITTER_XPATH_TWEET_BOX)
                )
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tweet_box)
            self._js_click(tweet_box)
            time.sleep(config.PASTE_DELAY)

            # Paste via clipboard (handles special characters and long text reliably)
            pyperclip.copy(text)
            tweet_box.send_keys(Keys.COMMAND, "v")
            print("Tweet text pasted from clipboard.")
            time.sleep(1.2)

            post_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, config.TWITTER_XPATH_POST_BUTTON)
                )
            )
            self._js_click(post_btn)
            print("Post button clicked.")
            time.sleep(config.POST_CONFIRM_DELAY)

            print("Tweet posted successfully.")
            return True

        except Exception as exc:
            print(f"Failed to post tweet: {exc}")
            return False

    # ── Teardown ──────────────────────────────────────────────────────────────

    def quit(self) -> None:
        """Close the browser cleanly."""
        try:
            self.driver.quit()
        except Exception:
            pass
