from __future__ import annotations

import os
from selenium.common.exceptions import TimeoutException

from pages.auth_pages import AuthLandingPage
from core.browser import get_base_url
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 1: Switch languages on the first auth page and verify UI changes."""
    page = AuthLandingPage(driver).open()

    if DRY_RUN:
        # In dry mode we only verify that page opens without interacting
        return

    # Use the visible language dropdown first, then fall back to URL locales
    try:
        # Ensure on landing
        page = AuthLandingPage(driver).open()
        page.dismiss_cookies()

        # Try to ensure dropdown is visible quickly
        try:
            WebDriverWait(driver, 3).until(EC.visibility_of_element_located(AuthLandingPage.LANG_DROPDOWN))
        except Exception:
            pass

        def lang_label():
            return page.get_language_label()
        initial_label = lang_label()
        initial_title = page.get_title_text()
        print(f"[lang] initial label='{initial_label}', title='{initial_title}'")

        # UI-only checks with assertions
        try:
            page.select_language("English")
            WebDriverWait(driver, 4).until(lambda d: lang_label() and lang_label() != initial_label)
            print(f"[lang] switched to English via dropdown -> '{lang_label()}'")
        except Exception as e:
            raise AssertionError(f"Language dropdown failed to switch to English: {e}")

        before_label = lang_label()
        try:
            page.select_language("Русский")
            WebDriverWait(driver, 4).until(lambda d: lang_label() and lang_label() != before_label)
            print(f"[lang] switched back to Russian via dropdown -> '{lang_label()}'")
        except Exception as e:
            raise AssertionError(f"Language dropdown failed to switch back to Russian: {e}")

        # Restore RU via URL just to normalize state (non-blocking)
        try:
            from core.browser import get_base_url
            base = get_base_url().rstrip('/')
            driver.get(f"{base}/ru")
        except Exception:
            pass
    except TimeoutException as e:
        raise AssertionError(f"Language step timeout: {e}")
