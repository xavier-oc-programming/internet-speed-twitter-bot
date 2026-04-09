# ── URLs ──────────────────────────────────────────────────────────────────────
M_LAB_URL = "https://speed.measurementlab.net/#/"
TWITTER_HOME = "https://x.com/home"
TWITTER_LOGIN_URL = "https://x.com/i/flow/login"

# ── Selenium ──────────────────────────────────────────────────────────────────
# Match your installed Chrome major version.
# Check: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
CHROME_VERSION = 146

WAIT_TIMEOUT = 20       # seconds — for elements that MUST be present
WAIT_TIMEOUT_SPEED = 180  # seconds — M-Lab test can take up to 3 minutes

# Persistent Chrome profile path (Twitter session saved here after first login)
CHROME_PROFILE_DIR = "advanced/chrome_profile"  # relative to project root

# ── Thresholds / ISP contract ─────────────────────────────────────────────────
PROMISED_DOWN = 150   # Mbps — your ISP's promised download speed
PROMISED_UP = 10      # Mbps — your ISP's promised upload speed

# ── Timing ────────────────────────────────────────────────────────────────────
SPEED_TEST_SETTLE = 6    # seconds to wait after results appear for table to render
PASTE_DELAY = 0.5        # seconds between focusing tweet box and pasting
POST_CONFIRM_DELAY = 2   # seconds to wait after clicking Post

# ── XPaths — M-Lab consent + start ───────────────────────────────────────────
# ID of the checkbox that accepts data sharing policy
MLAB_CONSENT_ID = "privacyConsent"  # updated from "demo-human" — inspect DevTools if this breaks again
# CSS selector for the Begin button
MLAB_CSS_START = "a.startButton"
# ID of the results div — becomes visible (display: block) when test completes
MLAB_RESULTS_SECTION_ID = "resultsSection"

# ── XPaths — M-Lab speed extraction ──────────────────────────────────────────
MLAB_XPATH_DOWNLOAD = (
    '//*[@id="measurementSpace"]/div[2]/table/tbody/tr[3]/td[3]/strong'
)
MLAB_XPATH_UPLOAD = (
    '//*[@id="measurementSpace"]/div[2]/table/tbody/tr[4]/td[3]/strong'
)

# ── XPaths — Twitter / X login flow ──────────────────────────────────────────
TWITTER_XPATH_CHECK_LOGIN = "//a[@href='/home' or @href='/i/flow/home']"

# Username / email input on the login page
TWITTER_XPATH_USERNAME_INPUT = "//input[@name='text']"
# "Next" button (appears after username entry)
TWITTER_XPATH_NEXT_BTN = "//span[normalize-space()='Next']"
# Optional: X asks for username confirmation when email was entered
TWITTER_XPATH_USERNAME_CONFIRM = "//input[@data-testid='ocfEnterTextTextInput']"
# Password input
TWITTER_XPATH_PASSWORD_INPUT = "//input[@name='password']"
# Final "Log in" button
TWITTER_XPATH_LOGIN_BTN = "//div[@data-testid='LoginForm_Login_Button']"

# ── XPaths — Google OAuth (Sign in with Google) ───────────────────────────────
# "Sign in with Google" button on the X login page — target the clickable parent, not the inner span
TWITTER_XPATH_GOOGLE_BTN = (
    "//button[contains(.,'Sign in with Google')] | "
    "//a[contains(.,'Sign in with Google')] | "
    "//div[@role='button' and contains(.,'Sign in with Google')]"
)
# Google account picker — the list item for a specific account
GOOGLE_XPATH_ACCOUNT = "//div[@data-identifier='{email}'] | //li[.//*[contains(text(),'{email}')]]"
# Google "Continue" / "Allow" confirmation button (if shown after account selection)
GOOGLE_XPATH_CONTINUE = "//span[normalize-space()='Continue'] | //button[contains(.,'Continue')]"

# ── XPaths — Twitter / X tweet composition ───────────────────────────────────
# The contenteditable div where tweet text is typed
TWITTER_XPATH_TWEET_BOX = (
    "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/"
    "div[2]/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/"
    "div/div/div[1]/div/div/div/div/div/div[2]/div"
)
# The "Post" submit button
TWITTER_XPATH_POST_BUTTON = (
    "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/"
    "div[2]/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div/div/button"
)

# ── Output / formatting ───────────────────────────────────────────────────────
COMPLAINT_TEMPLATE = (
    "Hey Internet Provider, why is my internet speed {down}down/{up}up "
    "when I pay for {promised_down}down/{promised_up}up? #ISP #InternetSpeed"
)
