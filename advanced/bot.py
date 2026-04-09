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
