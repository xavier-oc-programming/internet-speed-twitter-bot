# Internet Speed Twitter Complaint Bot

Selenium bot that measures internet speed via M-Lab and tweets at your ISP when speeds fall below the promised thresholds.

When your ISP promises 150 Mb/s download and 10 Mb/s upload, this bot opens M-Lab's NDT7 speed test in a real Chrome browser, waits for the results, extracts your actual download and upload speeds, and—if they're below the promised values—composes and posts a tweet such as: *"Hey Internet Provider, why is my internet speed 42.3down/3.1up when I pay for 150down/10up? #ISP #InternetSpeed"*. No manual steps are needed after the first run.

This project ships in two builds. The **original build** follows the course approach: it kills all Chrome processes, launches a fresh Chrome instance with remote debugging enabled, attaches Selenium to that debugger session, and posts the tweet through your already-logged-in browser profile. The **advanced build** refactors the logic into clean, separated modules using `undetected-chromedriver` with a persistent profile, centralises all selectors and constants in `config.py`, and guards every browser interaction with proper JS-click fallbacks and short timeouts.

No external API keys are required. Both builds use browser automation against the public M-Lab speed-test page and Twitter's web UI. The first time you run the advanced build, log in to Twitter manually in the Chrome window that opens. Chrome saves the session to a persistent profile — every run after that is fully automatic with no login step.

---

## Table of Contents

0. [Prerequisites](#0-prerequisites)
1. [Quick start](#1-quick-start)
2. [Builds comparison](#2-builds-comparison)
3. [Usage](#3-usage)
4. [Data flow](#4-data-flow)
5. [Features](#5-features)
6. [Navigation flow](#6-navigation-flow)
7. [Architecture](#7-architecture)
8. [Module reference](#8-module-reference)
9. [Configuration reference](#9-configuration-reference)
10. [Environment variables](#10-environment-variables)
11. [Design decisions](#11-design-decisions)
12. [Course context](#12-course-context)
13. [Dependencies](#13-dependencies)

---

## 0. Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | Required for modern type hints |
| Google Chrome | Advanced build auto-manages ChromeDriver via UC |
| Twitter / X account | Log in manually the first time; session saved automatically after that |
| Internet connection | Bot measures your real connection speed |

No Twitter API keys needed — the bot interacts with the Twitter web UI directly.

---

## 1. Quick start

```bash
# Clone
git clone https://github.com/xavier-oc-programming/internet-speed-twitter-bot.git
cd internet-speed-twitter-bot

# Install dependencies
pip install -r requirements.txt

# Run the menu
python menu.py
```

On first run, Chrome opens — log in to Twitter/X manually (use "Sign in with Google" or any method). The session is saved to `advanced/chrome_profile/`. Every run after that is fully automatic — no login needed.

Update `CHROME_VERSION` in `advanced/config.py` to match your installed Chrome major version if UC raises a version mismatch error.

---

## 2. Builds comparison

| Feature | Original | Advanced |
|---|---|---|
| Browser driver | `selenium.webdriver.Chrome` + remote debugging | `undetected-chromedriver` + persistent profile |
| Architecture | Single script | `config.py` + `bot.py` + `main.py` |
| Constants | Inline | Centralised in `config.py` |
| XPaths | Inline | Grouped in `config.py` by page area |
| JS click fallback | Partial | All non-trivial clicks |
| Error handling | `try/except` with prints | Raises `RuntimeError`; orchestrator catches |
| Twitter login | Manual via debugger session | Manual on first run; fully automatic after (persistent profile) |
| Threshold check | Always tweets | Only tweets if speeds are below promised |

---

## 3. Usage

### Menu

```
python menu.py
```

```
 ____  _  _  ____  ____  ____  _  _  ____  ____    ___  ____  ____  ____  ____  ____
(_  _)( \( )(_  _)( ___)(  _ \( \( )( ___)(_  _)  / __)(  _ \( ___)( ___)( ___)(  _ \
 _)(_  )  (   )(   )__)  )   / )  (  )__)   )(    \__ \ )___/ )__)  )__)  )__)  )(_) )
(____)(_)\_) (__) (____)(_)\_)(_)\_)(____) (__)   (___/(__)  (____)(____)(____)(____/
 ____  _    _  ____  ____  ____  ____  ____     ___  _____  __  __  ____  __      __    ____  _  _  ____
(_  _)( \/\/ )(_  _)(_  _)(_  _)( ___)(  _ \   / __)(  _  )(  \/  )(  _ \(  )    /__\  (_  _)( \( )(_  _)
  )(   )    (  _)(_   )(    )(   )__)  )   /  ( (__  )(_)(  )    (  )___/ )(__  /(__)\  _)(_  )  (   )(
 (__) (__/\__)(____) (__)  (__) (____)(_)\_)   \___)(_____)(_/\/\_)(__)  (____)(__)(__)(____)(_)\_) (__) 
 ____  _____  ____
(  _ \(  _  )(_  _)
 ) _ < )(_)(   )(
(____/(_____) (__)

  1. Original build  — course solution (remote debug approach)
  2. Advanced build  — undetected-chromedriver + clean architecture
  q. Quit
```

### Advanced build — example terminal output

```
Opening M-Lab speed test...
Consent checkbox accepted.
BEGIN clicked — speed test running.
Waiting up to 180s for results...
Results visible. Settling for 6s...
Download: 42.3 Mb/s  |  Upload: 3.1 Mb/s

Results: 42.3 Mb/s down  /  3.1 Mb/s up
Promised: 150 Mb/s down  /  10 Mb/s up

Complaint: Hey Internet Provider, why is my internet speed 42.3down/3.1up when I pay for 150down/10up? #ISP #InternetSpeed
Navigating to Twitter home...
Tweet text pasted from clipboard.
Post button clicked.
Tweet posted successfully.
```

---

## 4. Data flow

```
Input                 Fetch                 Process               Output
─────────────────     ─────────────────     ─────────────────     ──────────────────
PROMISED_DOWN   ──→   M-Lab NDT7 page  ──→  Compare measured  ──→  Tweet on X/Twitter
PROMISED_UP           (Selenium)             vs promised            if below threshold
                       ↓
                      Extract down/up
                      from results table
```

---

## 5. Features

### Both builds
- Runs the M-Lab NDT7 speed test in a real Chrome browser
- Accepts the data-sharing consent checkbox via JavaScript click
- Waits up to 180 seconds for test completion
- Extracts download and upload speeds from the results table
- Builds a complaint tweet with actual vs promised speeds
- Posts the tweet using clipboard paste (handles special characters)

### Advanced build only
- Only tweets if speeds are actually below promised thresholds
- All selectors, URLs, and constants in one file (`config.py`)
- Persistent Chrome profile — Twitter session survives across runs
- `undetected-chromedriver` avoids bot-detection fingerprinting
- JS-click fallback on every browser interaction
- Clean class-based architecture with separated concerns
- Raises exceptions on failure instead of silent exits

---

## 6. Navigation flow

```
python menu.py
    │
    ├─ 1 → python original/main.py
    │         └─ Kill Chrome → Launch Chrome (debug) → Speed test → Build tweet → Post tweet
    │
    ├─ 2 → python advanced/main.py
    │         └─ Open Chrome (UC) → Speed test → Check threshold → Post tweet (if slow)
    │
    └─ q → Exit
```

---

## 7. Architecture

```
internet-speed-twitter-bot/
│
├── menu.py                    # Top-level launcher — prints logo, routes to builds
├── art.py                     # ASCII art LOGO constant
├── requirements.txt           # pip dependencies
├── .gitignore
├── README.md
│
├── original/
│   └── main.py                # Verbatim course solution (remote debug approach)
│
├── advanced/
│   ├── config.py              # All constants, URLs, timeouts, XPaths
│   ├── bot.py                 # InternetSpeedTwitterBot — Selenium automation
│   └── main.py                # Orchestrator — wires config, bot, flow logic
│
└── docs/
    └── COURSE_NOTES.md        # Original exercise description and course approach
```

---

## 8. Module reference

### `advanced/bot.py` — `InternetSpeedTwitterBot`

| Method | Returns | Description |
|---|---|---|
| `__init__(profile_dir)` | `None` | Creates UC Chrome driver with persistent profile |
| `get_internet_speed()` | `None` | Runs M-Lab test; sets `self.down` and `self.up`; raises `RuntimeError` on failure |
| `is_logged_in_to_twitter()` | `bool` | Navigates to X home; returns True if timeline loads |
| `tweet_at_provider(text)` | `bool` | Pastes and posts `text`; returns True on success |
| `login(username, password)` | `None` | Automates username/password login (fallback) |
| `login_with_google(email)` | `None` | Automates Google OAuth login; handles account picker and popup/redirect |
| `quit()` | `None` | Closes the browser cleanly |
| `_js_click(element)` | `None` | Tries normal click; falls back to JS click |
| `_create_driver(profile_dir)` | `uc.Chrome` | Configures and returns UC Chrome instance |

---

## 9. Configuration reference

All constants live in `advanced/config.py`.

| Constant | Default | Description |
|---|---|---|
| `M_LAB_URL` | `https://speed.measurementlab.net/#/` | M-Lab NDT7 speed test URL |
| `TWITTER_HOME` | `https://x.com/home` | Twitter/X home timeline URL |
| `CHROME_VERSION` | `146` | Must match your installed Chrome major version |
| `WAIT_TIMEOUT` | `20` | Seconds for standard element waits |
| `WAIT_TIMEOUT_SPEED` | `180` | Seconds to wait for M-Lab test completion |
| `CHROME_PROFILE_DIR` | `advanced/chrome_profile` | Persistent Chrome profile path (relative to project root) |
| `PROMISED_DOWN` | `150` | Your ISP's promised download speed in Mbps |
| `PROMISED_UP` | `10` | Your ISP's promised upload speed in Mbps |
| `SPEED_TEST_SETTLE` | `6` | Seconds to wait after results appear for table to render |
| `PASTE_DELAY` | `0.5` | Seconds between focusing tweet box and pasting |
| `POST_CONFIRM_DELAY` | `2` | Seconds to wait after clicking Post |
| `MLAB_CONSENT_ID` | `privacyConsent` | HTML ID of the M-Lab consent checkbox |
| `MLAB_CSS_START` | `a.startButton` | CSS selector for the Begin button |
| `COMPLAINT_TEMPLATE` | See config.py | f-string template for the complaint tweet |

---

## 10. Environment variables

No API keys required. Copy `.env.example` to `.env` and fill in your Gmail address:

```bash
cp .env.example .env
```

```
# Option A — Sign in with Google (preferred)
GOOGLE_EMAIL=your_gmail@gmail.com

# Option B — Twitter username + password (fallback if Google OAuth fails)
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password
```

The `.env` file is gitignored and never committed. These variables are only used if the bot detects you are not logged in. On first run, log in manually in the Chrome window regardless — after that the session is saved and `.env` credentials are not needed again.

---

## 11. Design decisions

**`undetected-chromedriver` over `selenium.webdriver.Chrome`**
Standard ChromeDriver is fingerprinted and blocked by many modern login systems. UC patches the Chrome binary to remove automation signatures, which helps with Twitter's bot-detection.

**`CHROME_VERSION` pinned in `config.py`**
UC needs the exact major version to download the correct driver patch. Update this constant whenever Chrome auto-updates.

**`--disable-notifications` over `add_experimental_option("prefs", ...)`**
UC does not support `add_experimental_option` and silently crashes Chrome when it is used. Notification suppression is done via `options.add_argument("--disable-notifications")` instead.

**First login is manual; all subsequent runs are automatic**
Twitter/X blocks fully automated login. On the first run, Chrome opens and the user logs in manually (via "Sign in with Google" or username/password). Chrome saves the authenticated session to `advanced/chrome_profile/`. Every subsequent run calls `is_logged_in_to_twitter()` first — if the session is still valid, the login step is skipped entirely and the bot goes straight to the speed test.

**JS click with normal click fallback**
Overlapping elements, animations, and edge-of-viewport positions all cause `ElementClickInterceptedException`. Every non-trivial click uses `_js_click()` which tries normal click first and falls back to `driver.execute_script("arguments[0].click();", el)`.

**Clipboard paste (`pyperclip` + Cmd+V) instead of `send_keys(text)`**
Twitter's React-based tweet box ignores `send_keys()` for long or special-character strings. Copying to clipboard and pasting is the only reliable method.

**Persistent Chrome profile over remote debugging**
The course original uses remote debugging (launch Chrome externally, attach Selenium). The advanced build uses UC with a persistent profile directory instead. This means: no need to kill Chrome first, no need to launch a separate process, and the session is preserved between Python runs.

**Threshold check before tweeting**
The advanced build only posts a tweet if the measured speeds are actually below the promised thresholds, avoiding spam if your connection is performing fine.

**`SPEED_TEST_SETTLE` sleep after results appear**
M-Lab renders the results header before populating the speed table. Without a 6-second settle, the XPaths find empty cells.

**All XPaths in `config.py`**
Twitter and M-Lab both change their DOM periodically. Centralising all selectors means a broken XPath requires changing exactly one line.

---

## 12. Course context

**Course:** 100 Days of Code — The Complete Python Pro Bootcamp  
**Day:** 51  
**Topic:** Browser automation with Selenium — intermediate project  
**Difficulty:** Intermediate (Selenium, remote debugging, UI automation)

The key insight from this day is that automating login-protected sites (Twitter, Google) is hard because they actively detect and block bots. The course solution sidesteps this by using Chrome's remote debugging protocol to attach Selenium to a browser session where the user is already logged in — a practical real-world pattern.

---

## 13. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `undetected-chromedriver` | `advanced/bot.py` | Bot-detection-resistant Chrome driver |
| `selenium` | Both builds | Browser automation framework |
| `python-dotenv` | `advanced/main.py` | Load `.env` file (optional config) |
| `pyperclip` | Both builds | Clipboard access for reliable tweet pasting |
| `pathlib` | All files | Cross-platform path handling |
| `subprocess` | `original/main.py` | Launch Chrome with remote debugging flags |
| `time` | Both builds | Settle sleeps after page actions |
