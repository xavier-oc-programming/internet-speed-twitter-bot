# Day 51 — Internet Speed Twitter Complaint Bot

## Original course exercise

Build a bot that:
1. Automatically runs a speed test using a website like [fast.com](https://fast.com) or [M-Lab](https://speed.measurementlab.net/#/).
2. Checks the measured download and upload speeds against promised ISP thresholds.
3. If speeds are below the promised values, automatically logs in to Twitter and tweets a complaint at the ISP.

### Tools used in the course
- **Selenium** — browser automation
- **WebDriverWait / EC** — waiting for elements to load
- Standard `chromedriver` (via `webdriver.Chrome()`)
- Remote debugging (`--remote-debugging-port=9222`) to avoid Twitter login automation issues

### Original approach (course solution)
Rather than automating the Twitter login flow (which is heavily guarded against bots), the course used Chrome's **remote debugging protocol**:
1. Kill all Chrome processes.
2. Launch Chrome manually with `--remote-debugging-port=9222`.
3. Attach Selenium to the already-running Chrome session using `debuggerAddress`.
4. Because the user's real Chrome profile is used, Twitter (and any other site) is already logged in.

This sidesteps the Twitter login automation problem entirely — the human logs in once, and the bot reuses the authenticated session.

### Speed test site used
[M-Lab NDT7](https://speed.measurementlab.net/#/) — chosen because:
- It's a free, browser-based speed test.
- Results are extracted from a `<table>` in `#measurementSpace`.
- The page requires accepting a consent checkbox before starting.

### Files created during the course
| File | Description |
|---|---|
| `00_day51_goals.py` | Empty placeholder for daily goals |
| `01_setup_twitter_account.py` | Config constants (credentials redacted, moved to old_files/) |
| `02_create_class.py` | Initial class skeleton with placeholder methods |
| `03_get_internet_speeds.py` | Speed test implementation only |
| `04_twitter_bot_to_complain.py` | Complete combined implementation (final) |
| `06_twitter_only.py` | Isolated Twitter posting bot (helper reference) |

> Note: Files `01`, `02`, `03` contained hardcoded test credentials and were excluded from the repository. They are kept locally in `old_files/` only.
