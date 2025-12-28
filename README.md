# Mobile Testing Framework

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Appium](https://img.shields.io/badge/appium-3.1-green.svg)](https://appium.io/)

> Appium-based framework for testing iOS and Android apps

I built this to automate mobile app testing across both iOS and Android. Mobile testing has its own challenges (gestures, device differences, slower execution), so I focused on making the framework handle those gracefully.

---

## What's Different About Mobile Testing?

Mobile isn't just "small screen web testing." There are unique challenges:

**Gestures matter** - Swipe, pinch, long-press are first-class interactions
**Slower execution** - Devices/simulators are slower than browsers
**Platform differences** - iOS and Android work differently
**Device fragmentation** - Many screen sizes, OS versions
**App state** - Apps can be backgrounded, killed, or interrupted

This framework handles these realities.

---

## Quick Start

### Prerequisites

You'll need:
- **Python 3.8+**
- **Appium Server** - `npm install -g appium`
- **Platform-specific tools**:
  - Android: Android SDK, ADB
  - iOS: Xcode (Mac only)

### Install

```bash
# Clone
git clone https://github.com/JasonTeixeira/Mobile-Testing-Framework.git
cd Mobile-Testing-Framework

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies
pip install -r requirements.txt
```

### Start Appium Server

```bash
# In a separate terminal
appium

# Should see: "Appium REST http interface listener started on 0.0.0.0:4723"
```

### Run Tests

```bash
# Make sure your app path is set in config/capabilities.yaml
pytest tests/

# Or specific platform
pytest tests/android/
pytest tests/ios/
```

---

## How It Works

### Driver Manager

Handles the differences between iOS and Android:

```python
from framework.core.driver_manager import DriverManager

# Create Android driver
manager = DriverManager()
driver = manager.create_android_driver(
    app_path="/path/to/app.apk",
    device_name="Pixel 6"
)

# Or iOS
driver = manager.create_ios_driver(
    app_path="/path/to/app.app",
    device_name="iPhone 14"
)
```

The manager reads capabilities from `config/capabilities.yaml` so you're not hardcoding settings.

### Base Page with Gestures

Mobile interactions are different from web. The `BasePage` class handles mobile-specific stuff:

```python
from framework.core.base_page import BasePage

page = BasePage(driver)

# Mobile gestures
page.swipe_up()              # Scroll down
page.swipe_left()            # Navigate carousel
page.scroll_to_element(...)  # Scroll until element visible
page.long_press(...)         # Context menu

# App management  
page.background_app(5)       # Send to background for 5 seconds
page.hide_keyboard()         # Dismiss keyboard

# Normal stuff still works
page.tap(locator)
page.send_keys(locator, "text")
page.get_text(locator)
```

---

## Project Structure

```
Mobile-Testing-Framework/
├── framework/
│   ├── core/
│   │   ├── driver_manager.py   # iOS/Android driver setup
│   │   └── base_page.py        # Mobile interactions & gestures
│   ├── pages/                  # Page objects
│   └── utils/                  # Helper utilities
│
├── tests/
│   ├── android/                # Android-specific tests
│   ├── ios/                    # iOS-specific tests
│   └── conftest.py            # Pytest fixtures
│
├── config/
│   └── capabilities.yaml       # Device/app configuration
│
├── screenshots/                # Failure screenshots
├── logs/                      # Test logs
└── requirements.txt           # Dependencies
```

---

## Configuration

Edit `config/capabilities.yaml` for your app:

```yaml
android:
  app: /path/to/your/app.apk
  deviceName: Android Emulator
  platformVersion: "13.0"
  
  # Or test installed app
  appPackage: com.your.app
  appActivity: .MainActivity

ios:
  app: /path/to/your/app.app
  deviceName: iPhone 14
  platformVersion: "16.0"
  
  # Or test installed app
  bundleId: com.your.app
```

---

## Writing Tests

### Page Object Pattern

Keep tests clean by using page objects:

```python
# framework/pages/login_page.py
from framework.core.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy

class LoginPage(BasePage):
    # Locators
    USERNAME = (AppiumBy.ID, "com.app:id/username")
    PASSWORD = (AppiumBy.ID, "com.app:id/password")
    LOGIN_BTN = (AppiumBy.ID, "com.app:id/login")
    
    def login(self, username, password):
        self.send_keys(self.USERNAME, username)
        self.send_keys(self.PASSWORD, password)
        self.hide_keyboard()  # Mobile-specific!
        self.tap(self.LOGIN_BTN)
```

### Tests

```python
# tests/android/test_login.py
import pytest
from framework.pages.login_page import LoginPage

def test_login(android_driver):
    login_page = LoginPage(android_driver)
    login_page.login("user@test.com", "password")
    
    # Assert something
    assert login_page.is_element_present(...)
```

---

## Common Challenges & Solutions

### "Element not found"

Mobile elements can be tricky:
- Use **Appium Inspector** to find correct locators
- Elements might be off-screen - try scrolling to them
- Wait for elements with `wait_for_element_visible()`

### "Tests are slow"

Yes, mobile tests are slower than web:
- Real devices are faster than emulators
- Run tests in parallel: `pytest -n 4`
- Use `noReset: true` to avoid reinstalling app each time

### "Different behavior on iOS vs Android"

That's reality. You might need platform-specific tests:
```python
@pytest.mark.android
def test_android_specific():
    ...

@pytest.mark.ios  
def test_ios_specific():
    ...
```

### "Flaky tests"

Mobile tests can be flaky:
- Use explicit waits (not fixed sleep)
- Handle unexpected alerts/popups
- Screenshot on failure to debug
- Use `pytest-rerunfailures` to auto-retry

---

## Tips

### Do:
✅ Use explicit waits everywhere
✅ Test on real devices when possible
✅ Handle both portrait and landscape
✅ Test with poor network conditions
✅ Clean up test data between runs

### Don't:
❌ Use `time.sleep()` - use `WebDriverWait` instead
❌ Hardcode element coordinates
❌ Test only on latest OS version
❌ Ignore platform differences
❌ Run tests on your only device (get a test device!)

---

## Setup Guides

### Android Setup

1. Install Android Studio
2. Setup Android SDK
3. Enable developer options on device/emulator
4. Verify: `adb devices` shows your device

### iOS Setup (Mac only)

1. Install Xcode
2. Install Xcode Command Line Tools
3. For real devices: Register device UDID with Apple
4. Verify: `xcrun simctl list` shows simulators

### Appium Doctor

Check your setup:
```bash
npm install -g appium-doctor
appium-doctor --android
appium-doctor --ios
```

Fix any red ❌ items it finds.

---

## What I Learned

Building this taught me:

**About Mobile Testing:**
- Mobile gestures are more complex than they seem
- iOS and Android locators work differently
- Real devices behave differently than emulators
- App lifecycle (background, foreground, killed) matters

**About Appium:**
- It's slower than Selenium (that's normal)
- Element location strategies differ by platform
- XPath is slow on mobile - use IDs when possible
- Session management is tricky with multiple devices

**About Test Design:**
- Parallel execution saves time but needs isolated tests
- Screenshots are critical for debugging failures
- Test data cleanup matters more on mobile
- Network conditions affect behavior significantly

---

## Troubleshooting

**"Could not start a new session"**
- Is Appium server running? (`appium` in terminal)
- Check logs at `~/.appium/logs`

**"App not installed"**
- Verify app path in capabilities.yaml
- For Android: Check if app is signed
- For iOS: Check provisioning profile

**"Session not created"**
- Device might be locked
- Wrong platform version specified
- USB debugging not enabled (Android)

---

## Contributing

Found bugs or improvements? Open an issue or PR!

---

## Author

**Jason Teixeira**
- GitHub: [@JasonTeixeira](https://github.com/JasonTeixeira)
- Email: sage@sageideas.org

---

## License

MIT License - use however you want.

---

## Why Appium?

I chose Appium because:
- **Cross-platform** - One framework for iOS and Android
- **Open source** - No licensing costs
- **Standard WebDriver** - If you know Selenium, you know Appium
- **Active community** - Lots of support and documentation

It's not perfect (slower than native tools), but the cross-platform benefit is huge.
